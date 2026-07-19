"""Carga de datos e índices en memoria.

Los datos viven como ficheros JSON dentro del paquete (``data/en`` y ``data/es``)
y se leen con :mod:`importlib.resources`, por lo que funcionan también cuando el
paquete se instala como wheel.
"""

from __future__ import annotations

import json
import re
from importlib.resources import files
from typing import TYPE_CHECKING, Any

from .exceptions import (
    InvalidLanguageError,
    InvalidLevelError,
    LevelNotFoundError,
    RoleNotFoundError,
)
from .models import RoleLevel, Statistics, YearsRange

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

SUPPORTED_LANGUAGES = ("en", "es")
MIN_LEVEL = 1
MAX_LEVEL = 9

_LEVEL_RE = re.compile(r"^[Ll]?([1-9])$")


def normalize_level(level: int | str) -> int:
    """Convierte un identificador de nivel (``3``, ``"L3"``, ``"L3 - Junior II"``) en 1-9."""
    if isinstance(level, int):
        if MIN_LEVEL <= level <= MAX_LEVEL:
            return level
        raise InvalidLevelError(level)
    text = level.strip()
    match = _LEVEL_RE.match(text)
    if match is None:
        match = _LEVEL_RE.match(text.split(" - ", maxsplit=1)[0])
    if match is not None:
        return int(match.group(1))
    raise InvalidLevelError(level)


class Database:
    """Catálogo cargado para un idioma, con índices por código, rol y categoría."""

    def __init__(self, language: str) -> None:
        if language not in SUPPORTED_LANGUAGES:
            raise InvalidLanguageError(language, SUPPORTED_LANGUAGES)
        self.language = language
        self.entries: tuple[RoleLevel, ...] = ()
        self.by_code: dict[str, RoleLevel] = {}
        self.by_role: dict[str, tuple[RoleLevel, ...]] = {}
        self.by_category: dict[str, tuple[str, ...]] = {}
        self._load()

    def _data_dir(self) -> Traversable:
        return files("tech_roles_library").joinpath("data", self.language)

    def _load(self) -> None:
        entries: list[RoleLevel] = []
        by_role: dict[str, list[RoleLevel]] = {}
        categories: dict[str, list[str]] = {}

        resources = sorted(
            (r for r in self._data_dir().iterdir() if r.name.endswith(".json")),
            key=lambda r: r.name,
        )
        for resource in resources:
            data = json.loads(resource.read_text(encoding="utf-8"))
            role_levels = [
                self._build_entry(data["role"], data["category"], code, raw)
                for code, raw in data["levels"].items()
            ]
            role_levels.sort(key=lambda e: e.level_number)
            entries.extend(role_levels)
            by_role[data["role"]] = role_levels
            categories.setdefault(data["category"], []).append(data["role"])

        self.entries = tuple(entries)
        self.by_code = {entry.code: entry for entry in entries}
        self.by_role = {role: tuple(levels) for role, levels in sorted(by_role.items())}
        self.by_category = {
            category: tuple(sorted(roles)) for category, roles in sorted(categories.items())
        }

    @staticmethod
    def _build_entry(role: str, category: str, code: str, raw: dict[str, Any]) -> RoleLevel:
        years: dict[str, Any] = raw["yearsRange"]
        raw_max = years["max"]
        return RoleLevel(
            code=code,
            role=role,
            category=category,
            level=str(raw["level"]),
            level_number=int(raw["levelNumber"]),
            years_range=YearsRange(
                min=int(years["min"]),
                max=int(raw_max) if raw_max is not None else None,
            ),
            core_competencies=tuple(raw.get("coreCompetencies", ())),
            complementary_competencies=tuple(raw.get("complementaryCompetencies", ())),
            indicators=tuple(raw.get("indicators", ())),
        )

    # -- Acceso básico -------------------------------------------------------

    def get_by_code(self, code: str) -> RoleLevel:
        entry = self.by_code.get(code.strip().upper())
        if entry is None:
            raise RoleNotFoundError(code, self.by_code)
        return entry

    def get_levels(self, role: str) -> tuple[RoleLevel, ...]:
        levels = self.by_role.get(role)
        if levels is None:
            raise RoleNotFoundError(role, self.by_role)
        return levels

    def get_level(self, role: str, level: int | str) -> RoleLevel:
        number = normalize_level(level)
        for entry in self.get_levels(role):
            if entry.level_number == number:
                return entry
        raise LevelNotFoundError(role, level)

    def statistics(self) -> Statistics:
        total_roles = len(self.by_role)
        return Statistics(
            total_roles=total_roles,
            total_categories=len(self.by_category),
            total_entries=len(self.entries),
            average_entries_per_role=len(self.entries) / total_roles if total_roles else 0.0,
            by_category={
                category: sum(len(self.by_role[role]) for role in roles)
                for category, roles in self.by_category.items()
            },
        )
