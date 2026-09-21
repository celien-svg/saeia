"""Implémentation PostgreSQL du contrat de persistance."""

from __future__ import annotations

from typing import Any, Mapping

import psycopg
from psycopg.rows import DictRow, dict_row

from ..config import Settings
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
        self.config = config if config is not None else Settings()  # pyright: ignore[reportCallIssue]

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
                    """SELECT id_materiel, nom, modele, annee, etiquette_ulco,
                              etat, localisation, descriptif, remarque, entite_id
                       FROM materiels
                       WHERE id_materiel = %s""",
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
                                         image_type = EXCLUDED.image_type""",
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
