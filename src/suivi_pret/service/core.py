"""Logique métier de gestion des matériels."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any, Mapping

from ..storage.base import Storage


class SuiviPretService:
    """Valide les entrées de l'interface et orchestre leur persistance."""

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def lister_materiels(self) -> list[dict[str, Any]]:
        """Retourne les matériels disponibles."""
        return self.storage.lister_materiels()

    def recuperer_photos(self, materiel_id: int) -> list[dict[str, Any]]:
        """Retourne les photos de référence d'un matériel."""
        return self.storage.recuperer_photos(int(materiel_id))

    def supprimer_materiel(self, materiel_id: int) -> None:
        """Supprime un matériel après normalisation de son identifiant."""
        self.storage.supprimer_materiel(int(materiel_id))

    def creer_materiel(
        self,
        nom: str,
        modele: str,
        annee: float | int | None,
        etiquette_ulco: str,
        etat: str,
        localisation: str,
        descriptif: str,
        remarque: str,
        entite_id: float | int | None,
        photos: Mapping[str, str | None] | None,
    ) -> None:
        """Valide et normalise le formulaire avant de le transmettre au stockage."""
        nom = (nom or "").strip()
        localisation = (localisation or "").strip()

        if not nom:
            raise ValueError("Le nom de l'ordinateur est obligatoire.")
        if not localisation:
            raise ValueError("La localisation est obligatoire.")
        if entite_id is None:
            raise ValueError("L'identifiant de l'entité est obligatoire.")

        photos_data = []
        for type_photo, image_path in (photos or {}).items():
            if image_path:
                photos_data.append(
                    {
                        "type_photo": type_photo,
                        "image_data": Path(image_path).read_bytes(),
                        "image_type": mimetypes.guess_type(image_path)[0]
                        or "application/octet-stream",
                    }
                )

        self.storage.creer_materiel(
            {
                "nom": nom,
                "modele": (modele or "").strip() or None,
                "annee": int(annee) if annee is not None else None,
                "etiquette_ulco": (etiquette_ulco or "").strip() or None,
                "etat": etat,
                "localisation": localisation,
                "descriptif": (descriptif or "").strip() or None,
                "remarque": (remarque or "").strip() or None,
                "entite_id": int(entite_id),
                "photos": photos_data,
            }
        )
