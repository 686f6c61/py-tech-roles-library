"""Jerarquía de excepciones de la librería."""

from __future__ import annotations

import difflib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


class TechRolesError(Exception):
    """Error base de tech-roles-library."""


class InvalidLanguageError(TechRolesError):
    """El idioma solicitado no está soportado."""

    def __init__(self, language: str, valid: Iterable[str]) -> None:
        self.language = language
        self.valid = tuple(valid)
        super().__init__(
            f"Unsupported language: {language!r}. Valid languages: {', '.join(self.valid)}"
        )


class RoleNotFoundError(TechRolesError):
    """El rol (por nombre o por código) no existe en el catálogo."""

    def __init__(self, role: str, known: Iterable[str] = ()) -> None:
        self.role = role
        self.suggestions = tuple(difflib.get_close_matches(role, list(known), n=3, cutoff=0.6))
        message = f"Role not found: {role!r}"
        if self.suggestions:
            message += f". Did you mean: {', '.join(self.suggestions)}?"
        super().__init__(message)


class LevelNotFoundError(TechRolesError):
    """El nivel no existe para el rol indicado."""

    def __init__(self, role: str, level: object) -> None:
        self.role = role
        self.level = level
        super().__init__(f"Level {level!r} not found for role {role!r}")


class InvalidLevelError(TechRolesError):
    """El identificador de nivel no es interpretable."""

    def __init__(self, level: object) -> None:
        self.level = level
        super().__init__(
            f"Invalid level identifier: {level!r}. "
            "Use 1-9, 'L1'-'L9' or a full level name like 'L3 - Junior II'"
        )


class ExportFormatError(TechRolesError):
    """Formato de exportación no soportado."""

    def __init__(self, fmt: str) -> None:
        self.format = fmt
        super().__init__(f"Unsupported export format: {fmt!r}. Use 'json' or 'markdown'")
