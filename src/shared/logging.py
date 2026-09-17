"""Configuration du logging partagé par les sujets."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Retourne un logger configuré avec le nom fourni."""
    return logging.getLogger(name)
