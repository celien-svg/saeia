"""Implémentation PostgreSQL du contrat de persistance."""

from __future__ import annotations

from typing import Any, Mapping

import psycopg
from psycopg.rows import DictRow, dict_row

from ..config import Settings, get_settings
from .base import (
    DuplicateMaterielError,
    EntityNotFoundError,
    MaterielNotFoundError,
    Storage,
    StorageError,
)


class PostgresStorage(Storage):
    """Stocke les matériels dans la base PostgreSQL configurée."""

    def __init__(self, config: Settings | None = None) -> None:
        self.config = config if config is not None else get_settings()

    def _connexion(self) -> psycopg.Connection[DictRow]:
        """Ouvre une connexion produisant des lignes sous forme de dictionnaires."""
        return psycopg.Connection[DictRow].connect(
            host=self.config.POSTGRES_HOST,
            port=self.config.POSTGRES_PORT,
            user=self.config.POSTGRES_USER,
            password=self.config.POSTGRES_PASSWORD,
            dbname=self.config.POSTGRES_DB,
            row_factory=dict_row,
        )

    def lister_entites(self) -> list[dict[str, Any]]:
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute("SELECT id, nom FROM entites ORDER BY nom, id")
                return cur.fetchall()
        except psycopg.Error as exc:
            raise StorageError("Impossible de récupérer les entités.") from exc

    def lister_materiels(self) -> list[dict[str, Any]]:
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """SELECT id_materiel, nom, modele, annee, etiquette_ulco,
                              etat, localisation
                       FROM materiels
                       ORDER BY id_materiel DESC"""
                )
                return cur.fetchall()
        except psycopg.Error as exc:
            raise StorageError("Impossible de récupérer les matériels.") from exc

    def recuperer_materiel(self, materiel_id: int) -> dict[str, Any] | None:
        """Retourne toutes les données d'un matériel (pour pré-remplir le formulaire)."""
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """SELECT m.id_materiel, m.nom, m.modele, m.annee, m.etiquette_ulco,
                              m.etat, m.localisation, m.descriptif, m.remarque,
                              m.entite_id, e.nom AS entite_nom
                       FROM materiels m
                       JOIN entites e ON e.id = m.entite_id
                       WHERE m.id_materiel = %s""",
                    (materiel_id,),
                )
                return cur.fetchone()
        except psycopg.Error as exc:
            raise StorageError("Impossible de récupérer le matériel.") from exc

    def recuperer_photos(self, materiel_id: int) -> list[dict[str, Any]]:
        """Retourne les photos de référence (est_avant=TRUE) d'un matériel."""
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """SELECT type_photo, image_data, image_type
                       FROM photos_materiels
                       WHERE id_materiel = %s AND est_avant = TRUE""",
                    (materiel_id,),
                )
                return cur.fetchall()
        except psycopg.Error as exc:
            raise StorageError("Impossible de récupérer les photos.") from exc

    def recuperer_photos_analyse(self, materiel_id: int) -> list[dict[str, Any]]:
        """Retourne les photos après prêt, éventuellement annotées par l'IA."""
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                          """SELECT type_photo, COALESCE(image_annotee, image_data) AS image_data,
                                        CASE WHEN image_annotee IS NOT NULL THEN 'image/png'
                                              ELSE image_type END AS image_type
                       FROM photos_materiels
                       WHERE id_materiel = %s AND est_avant = FALSE""",
                    (materiel_id,),
                )
                return cur.fetchall()
        except psycopg.Error as exc:
            raise StorageError("Impossible de récupérer les photos d'analyse.") from exc

    def recuperer_photos_comparaison(
        self, materiel_id: int, type_photo: str | None = None,
    ) -> list[dict[str, Any]]:
        """Charge les photos avant/après, éventuellement pour une seule zone."""
        requete = (
            "SELECT id_photo, type_photo, image_data, image_type, est_avant, image_annotee "
            "FROM photos_materiels WHERE id_materiel = %s"
        )
        parametres: tuple[Any, ...] = (materiel_id,)
        if type_photo:
            requete += " AND type_photo = %s"
            parametres += (type_photo,)

        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(requete, parametres)
                return cur.fetchall()
        except psycopg.Error as exc:
            raise StorageError("Impossible de récupérer les photos en base.") from exc

    def enregistrer_image_annotee(self, id_photo: int, image_data: bytes) -> None:
        """Enregistre une copie annotée sans modifier la photo originale."""
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """UPDATE photos_materiels
                       SET image_annotee = %s
                       WHERE id_photo = %s""",
                    (image_data, id_photo),
                )
        except psycopg.Error as exc:
            raise StorageError("Impossible d'enregistrer l'image annotée en base.") from exc

    def enregistrer_rapport(
        self,
        materiel_id: int,
        contenu: str,
        origine: str = "ia",
        photos_rapport_id: int | None = None,
    ) -> int:
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO rapports_ia (id_materiel, contenu, origine)
                       VALUES (%s, %s, %s)
                       RETURNING id_rapport""",
                    (materiel_id, contenu, origine),
                )
                rapport_id = cur.fetchone()["id_rapport"]
                if photos_rapport_id is not None:
                    cur.execute(
                        """INSERT INTO photos_rapports (
                               id_rapport, type_photo, est_avant, image_data, image_type
                           )
                           SELECT %s, type_photo, est_avant, image_data, image_type
                           FROM photos_rapports
                           WHERE id_rapport = %s""",
                        (rapport_id, photos_rapport_id),
                    )
                return rapport_id
        except psycopg.Error as exc:
            raise StorageError("Impossible d'enregistrer le rapport IA.") from exc

    def enregistrer_analyse(
        self,
        materiel_id: int,
        contenu: str,
        photos: list[dict[str, Any]],
        promouvoir_photos: bool,
    ) -> int:
        """Enregistre le résultat et les photos comparées dans une seule transaction."""
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO rapports_ia (id_materiel, contenu, origine)
                       VALUES (%s, %s, 'ia')
                       RETURNING id_rapport""",
                    (materiel_id, contenu),
                )
                rapport_id = cur.fetchone()["id_rapport"]

                for photo in photos:
                    cur.execute(
                        """INSERT INTO photos_rapports (
                               id_rapport, type_photo, est_avant, image_data, image_type
                           ) VALUES (%s, %s, %s, %s, %s)""",
                        (
                            rapport_id,
                            photo["type_photo"],
                            photo["est_avant"],
                            photo["image_data"],
                            photo["image_type"],
                        ),
                    )

                if promouvoir_photos:
                    types_comparables = {
                        photo["type_photo"]
                        for photo in photos
                        if not photo["est_avant"]
                        and any(
                            autre["type_photo"] == photo["type_photo"]
                            and autre["est_avant"]
                            for autre in photos
                        )
                    }
                    for type_photo in types_comparables:
                        cur.execute(
                            """DELETE FROM photos_materiels
                               WHERE id_materiel = %s AND type_photo = %s
                                 AND est_avant = TRUE""",
                            (materiel_id, type_photo),
                        )
                        cur.execute(
                            """UPDATE photos_materiels
                               SET est_avant = TRUE, image_annotee = NULL
                               WHERE id_materiel = %s AND type_photo = %s
                                 AND est_avant = FALSE""",
                            (materiel_id, type_photo),
                        )

                return rapport_id
        except psycopg.Error as exc:
            raise StorageError("Impossible d'enregistrer l'analyse et ses photos.") from exc

    def lister_photos_rapport(self, rapport_id: int) -> list[dict[str, Any]]:
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """SELECT type_photo, est_avant, image_data, image_type
                       FROM photos_rapports
                       WHERE id_rapport = %s
                       ORDER BY type_photo, est_avant DESC""",
                    (rapport_id,),
                )
                return cur.fetchall()
        except psycopg.Error as exc:
            raise StorageError("Impossible de récupérer les photos du rapport.") from exc

    def enregistrer_validation_humaine(
        self,
        rapport_id: int,
        decision: str,
        type_anomalie: str | None,
        gravite: str | None,
        remarque: str | None,
    ) -> None:
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO validations_humaines (
                           id_rapport, decision, type_anomalie, gravite, remarque
                       )
                       VALUES (%s, %s, %s, %s, %s)""",
                    (rapport_id, decision, type_anomalie, gravite, remarque),
                )
        except psycopg.Error as exc:
            raise StorageError("Impossible d'enregistrer la validation humaine.") from exc

    def lister_validations_humaines(self, materiel_id: int) -> list[dict[str, Any]]:
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """SELECT v.id_validation, v.id_rapport, v.decision,
                              v.type_anomalie, v.gravite, v.remarque, v.cree_le
                       FROM validations_humaines v
                       JOIN rapports_ia r ON r.id_rapport = v.id_rapport
                       WHERE r.id_materiel = %s
                       ORDER BY v.cree_le DESC, v.id_validation DESC""",
                    (materiel_id,),
                )
                return cur.fetchall()
        except psycopg.Error as exc:
            raise StorageError("Impossible de récupérer les validations humaines.") from exc

    def recuperer_rapport(self, materiel_id: int) -> str | None:
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """SELECT contenu FROM rapports_ia
                       WHERE id_materiel = %s
                       ORDER BY cree_le DESC, id_rapport DESC
                       LIMIT 1""",
                    (materiel_id,),
                )
                rapport = cur.fetchone()
                return rapport["contenu"] if rapport else None
        except psycopg.Error as exc:
            raise StorageError("Impossible de récupérer le rapport IA.") from exc

    def lister_rapports(self, materiel_id: int) -> list[dict[str, Any]]:
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    """SELECT id_rapport, contenu, origine, cree_le
                       FROM rapports_ia
                       WHERE id_materiel = %s
                       ORDER BY cree_le DESC, id_rapport DESC""",
                    (materiel_id,),
                )
                return cur.fetchall()
        except psycopg.Error as exc:
            raise StorageError("Impossible de récupérer les rapports IA.") from exc

    def creer_materiel(self, donnees: Mapping[str, Any]) -> None:
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM entites WHERE id = %s",
                    (donnees["entite_id"],),
                )
                if cur.fetchone() is None:
                    raise EntityNotFoundError("L'entité indiquée n'existe pas.")

                cur.execute(
                    """INSERT INTO materiels (
                           nom, modele, annee, etiquette_ulco, etat, localisation,
                           descriptif, remarque, entite_id
                       )
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                       RETURNING id_materiel""",
                    (
                        donnees["nom"],
                        donnees["modele"],
                        donnees["annee"],
                        donnees["etiquette_ulco"],
                        donnees["etat"],
                        donnees["localisation"],
                        donnees["descriptif"],
                        donnees["remarque"],
                        donnees["entite_id"],
                    ),
                )
                id_materiel = cur.fetchone()["id_materiel"]
                # Photos de référence : est_avant = TRUE
                for photo in donnees.get("photos", []):
                    cur.execute(
                        """INSERT INTO photos_materiels (
                               id_materiel, type_photo, est_avant, image_data, image_type
                           ) VALUES (%s, %s, TRUE, %s, %s)
                           ON CONFLICT (id_materiel, type_photo, est_avant)
                           DO UPDATE SET image_data = EXCLUDED.image_data,
                                         image_type = EXCLUDED.image_type""",
                        (
                            id_materiel,
                            photo["type_photo"],
                            photo["image_data"],
                            photo["image_type"],
                        ),
                    )
        except (DuplicateMaterielError, EntityNotFoundError):
            raise
        except psycopg.errors.UniqueViolation as exc:
            raise DuplicateMaterielError("Cette étiquette ULCO existe déjà.") from exc
        except psycopg.Error as exc:
            raise StorageError("Impossible d'enregistrer le matériel.") from exc

    def modifier_materiel(self, materiel_id: int, donnees: Mapping[str, Any]) -> None:
        """Met à jour les données d'un matériel et remplace ses photos de référence si fournies."""
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM materiels WHERE id_materiel = %s",
                    (materiel_id,),
                )
                if cur.fetchone() is None:
                    raise MaterielNotFoundError("Le matériel à modifier n'existe pas.")

                cur.execute(
                    "SELECT 1 FROM entites WHERE id = %s",
                    (donnees["entite_id"],),
                )
                if cur.fetchone() is None:
                    raise EntityNotFoundError("L'entité indiquée n'existe pas.")

                cur.execute(
                    """UPDATE materiels SET
                           nom = %s, modele = %s, annee = %s,
                           etiquette_ulco = %s, etat = %s, localisation = %s,
                           descriptif = %s, remarque = %s, entite_id = %s
                       WHERE id_materiel = %s""",
                    (
                        donnees["nom"],
                        donnees["modele"],
                        donnees["annee"],
                        donnees["etiquette_ulco"],
                        donnees["etat"],
                        donnees["localisation"],
                        donnees["descriptif"],
                        donnees["remarque"],
                        donnees["entite_id"],
                        materiel_id,
                    ),
                )
                # Met à jour les photos de référence si fournies
                for photo in donnees.get("photos", []):
                    cur.execute(
                        """INSERT INTO photos_materiels (
                               id_materiel, type_photo, est_avant, image_data, image_type
                           ) VALUES (%s, %s, TRUE, %s, %s)
                           ON CONFLICT (id_materiel, type_photo, est_avant)
                           DO UPDATE SET image_data = EXCLUDED.image_data,
                                         image_type = EXCLUDED.image_type""",
                        (
                            materiel_id,
                            photo["type_photo"],
                            photo["image_data"],
                            photo["image_type"],
                        ),
                    )
        except (MaterielNotFoundError, EntityNotFoundError):
            raise
        except psycopg.errors.UniqueViolation as exc:
            raise DuplicateMaterielError("Cette étiquette ULCO existe déjà.") from exc
        except psycopg.Error as exc:
            raise StorageError("Impossible de modifier le matériel.") from exc

    def ajouter_photos_analyse(
        self, materiel_id: int, photos: list[dict[str, Any]]
    ) -> None:
        """Insère ou remplace les photos d'analyse (est_avant=FALSE)."""
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                for photo in photos:
                    cur.execute(
                        """INSERT INTO photos_materiels (
                               id_materiel, type_photo, est_avant, image_data, image_type
                           ) VALUES (%s, %s, FALSE, %s, %s)
                           ON CONFLICT (id_materiel, type_photo, est_avant)
                           DO UPDATE SET image_data = EXCLUDED.image_data,
                                         image_type = EXCLUDED.image_type,
                                         image_annotee = NULL""",
                        (
                            materiel_id,
                            photo["type_photo"],
                            photo["image_data"],
                            photo["image_type"],
                        ),
                    )
        except psycopg.Error as exc:
            raise StorageError("Impossible d'enregistrer les photos d'analyse.") from exc

    def supprimer_materiel(self, materiel_id: int) -> None:
        try:
            with self._connexion() as conn, conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM materiels WHERE id_materiel = %s",
                    (materiel_id,),
                )
        except psycopg.Error as exc:
            raise StorageError("Impossible de supprimer le matériel.") from exc
