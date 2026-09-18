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
