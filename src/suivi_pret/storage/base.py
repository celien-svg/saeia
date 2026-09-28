"""Contrats abstraits de la couche de persistance."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class StorageError(RuntimeError):
    """Erreur technique rencontrée pendant une opération de persistance."""


class DuplicateMaterielError(StorageError):
    """Une contrainte d'unicité empêche la création du matériel."""


class EntityNotFoundError(StorageError):
    """L'entité associée au matériel n'existe pas."""


class MaterielNotFoundError(StorageError):
    """Le matériel à modifier n'existe pas."""


class Storage(ABC):
    """Définit les opérations de persistance requises par le métier."""

    @abstractmethod
    def lister_materiels(self) -> list[dict[str, Any]]:
        """Retourne les matériels du plus récent au plus ancien."""
        raise NotImplementedError

    def recuperer_materiel(self, materiel_id: int) -> dict[str, Any] | None:
        """Retourne les données complètes d'un matériel."""
        raise NotImplementedError

    def recuperer_photos(self, materiel_id: int) -> list[dict[str, Any]]:
        """Retourne les photos de référence (est_avant=TRUE) d'un matériel."""
        raise NotImplementedError

    def recuperer_photos_analyse(self, materiel_id: int) -> list[dict[str, Any]]:
        """Retourne les photos après prêt (est_avant=FALSE) d'un matériel."""
        raise NotImplementedError

    def enregistrer_rapport(self, materiel_id: int, contenu: str) -> None:
        """Enregistre le dernier rapport IA d'un matériel."""
        raise NotImplementedError

    def recuperer_photos_comparaison(
        self, materiel_id: int, type_photo: str | None = None,
    ) -> list[dict[str, Any]]:
        """Retourne les photos avant/après, avec leur id_photo et est_avant."""
        raise NotImplementedError

    def enregistrer_image_annotee(self, id_photo: int, image_data: bytes) -> None:
        """Remplace la photo indiquée par son annotation au format PNG."""
        raise NotImplementedError

    def recuperer_rapport(self, materiel_id: int) -> str | None:
        """Retourne le dernier rapport IA d'un matériel, s'il existe."""
        raise NotImplementedError

    def lister_rapports(self, materiel_id: int) -> list[dict[str, Any]]:
        """Retourne l'historique des rapports IA d'un matériel."""
        raise NotImplementedError

    @abstractmethod
    def creer_materiel(self, donnees: Mapping[str, Any]) -> None:
        """Persiste un nouveau matériel."""
        raise NotImplementedError

    @abstractmethod
    def modifier_materiel(self, materiel_id: int, donnees: Mapping[str, Any]) -> None:
        """Met à jour un matériel existant."""
        raise NotImplementedError

    def ajouter_photos_analyse(
        self, materiel_id: int, photos: list[dict[str, Any]]
    ) -> None:
        """Insère les photos d'analyse (est_avant=FALSE) pour un matériel."""
        raise NotImplementedError

    @abstractmethod
    def supprimer_materiel(self, materiel_id: int) -> None:
        """Supprime le matériel correspondant à l'identifiant."""
        raise NotImplementedError
