"""Modelos de datos inmutables de la librería."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class YearsRange:
    """Rango de años de experiencia de un nivel. ``max`` es ``None`` en L9 (sin tope)."""

    min: int
    max: int | None

    def contains(self, years: float) -> bool:
        if self.max is None:
            return years >= self.min
        return self.min <= years <= self.max


@dataclass(frozen=True, slots=True)
class RoleLevel:
    """Una entrada rol-nivel del catálogo (por ejemplo, Backend Developer L3)."""

    code: str
    role: str
    category: str
    level: str
    level_number: int
    years_range: YearsRange
    core_competencies: tuple[str, ...]
    complementary_competencies: tuple[str, ...]
    indicators: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Competencies:
    """Competencias de un rol en un nivel (o acumuladas hasta un nivel)."""

    role: str
    level: str
    core: tuple[str, ...]
    complementary: tuple[str, ...]
    indicators: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CareerPath:
    """Vista completa de carrera: niveles dominados, nivel actual y camino de crecimiento."""

    role: str
    mastered: tuple[RoleLevel, ...]
    current: RoleLevel
    growth: tuple[RoleLevel, ...]


@dataclass(frozen=True, slots=True)
class NextLevel:
    """Salto al siguiente nivel: entrada actual, siguiente y competencias nuevas."""

    current: RoleLevel
    next: RoleLevel
    new_competencies: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LevelComparison:
    """Comparación entre dos niveles del mismo rol."""

    role: str
    from_level: RoleLevel
    to_level: RoleLevel
    added: tuple[str, ...]
    removed: tuple[str, ...]
    shared: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RoleComparison:
    """Comparación entre dos roles al mismo nivel."""

    level_number: int
    role_a: RoleLevel
    role_b: RoleLevel
    shared: tuple[str, ...]
    only_a: tuple[str, ...]
    only_b: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Resultado de búsqueda de roles con puntuación de coincidencia."""

    role: str
    category: str
    score: int
    matched_in: str  # "role", "category" o "both"


@dataclass(frozen=True, slots=True)
class Statistics:
    """Estadísticas globales del catálogo."""

    total_roles: int
    total_categories: int
    total_entries: int
    average_entries_per_role: float
    by_category: dict[str, int] = field(hash=False)
