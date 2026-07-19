"""tech-roles-library: catálogo de roles técnicos con niveles y competencias, EN/ES.

Uso básico::

    from tech_roles_library import TechRoles

    lib = TechRoles(language="es")
    role = lib.get_role("BE-L3")
    print(role.role, role.level)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import export as _export
from . import queries as _queries
from . import search as _search
from .database import SUPPORTED_LANGUAGES, Database, normalize_level
from .exceptions import (
    ExportFormatError,
    InvalidLanguageError,
    InvalidLevelError,
    LevelNotFoundError,
    RoleNotFoundError,
    TechRolesError,
)
from .models import (
    CareerPath,
    Competencies,
    LevelComparison,
    NextLevel,
    RoleComparison,
    RoleLevel,
    SearchResult,
    Statistics,
    YearsRange,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

__version__ = "1.0.1"

__all__ = [
    "SUPPORTED_LANGUAGES",
    "CareerPath",
    "Competencies",
    "ExportFormatError",
    "InvalidLanguageError",
    "InvalidLevelError",
    "LevelComparison",
    "LevelNotFoundError",
    "NextLevel",
    "RoleComparison",
    "RoleLevel",
    "RoleNotFoundError",
    "SearchResult",
    "Statistics",
    "TechRoles",
    "TechRolesError",
    "YearsRange",
    "normalize_level",
]


class TechRoles:
    """Punto de entrada de la librería. La carga de datos es perezosa."""

    def __init__(self, language: str = "en") -> None:
        if language not in SUPPORTED_LANGUAGES:
            raise InvalidLanguageError(language, SUPPORTED_LANGUAGES)
        self.language = language
        self._db: Database | None = None

    @property
    def _database(self) -> Database:
        if self._db is None:
            self._db = Database(self.language)
        return self._db

    # -- Consulta de roles ---------------------------------------------------

    def roles(self) -> tuple[str, ...]:
        """Nombres de todos los roles del catálogo, ordenados alfabéticamente."""
        return tuple(self._database.by_role)

    def categories(self) -> tuple[str, ...]:
        """Nombres de todas las categorías, ordenados alfabéticamente."""
        return tuple(self._database.by_category)

    def get_role(self, code: str) -> RoleLevel:
        """Entrada rol-nivel por código (por ejemplo ``"BE-L3"``)."""
        return self._database.get_by_code(code)

    def get_role_by_name(self, role: str, level: int | str) -> RoleLevel:
        """Entrada rol-nivel por nombre de rol y nivel (``3``, ``"L3"``...)."""
        return self._database.get_level(role, level)

    def get_levels(self, role: str) -> tuple[RoleLevel, ...]:
        """Las 9 entradas de nivel de un rol, ordenadas de L1 a L9."""
        return self._database.get_levels(role)

    # -- Competencias y carrera ----------------------------------------------

    def get_competencies(self, role: str, level: int | str) -> Competencies:
        """Competencias (core, complementarias, indicadores) de un rol y nivel."""
        return _queries.get_competencies(self._database, role, level)

    def get_accumulated(self, role: str, level: int | str) -> Competencies:
        """Competencias acumuladas desde L1 hasta el nivel indicado, sin duplicados."""
        return _queries.get_accumulated(self._database, role, level)

    def get_career_path(self, role: str, current_level: int | str) -> CareerPath:
        """Vista completa de carrera: niveles dominados, actual y crecimiento."""
        return _queries.get_career_path(self._database, role, current_level)

    def get_next_level(self, role: str, current_level: int | str) -> NextLevel | None:
        """Siguiente nivel y competencias nuevas; ``None`` si ya está en L9."""
        return _queries.get_next_level(self._database, role, current_level)

    def get_by_experience(self, role: str, years: float) -> RoleLevel:
        """Nivel recomendado para unos años de experiencia."""
        return _queries.get_by_experience(self._database, role, years)

    def get_years_range(self, role: str, level: int | str) -> YearsRange:
        """Rango de años de experiencia de un rol y nivel."""
        return self._database.get_level(role, level).years_range

    # -- Búsqueda y filtrado -------------------------------------------------

    def search(self, query: str, limit: int = 20) -> list[SearchResult]:
        """Busca roles por nombre o categoría, con puntuación de coincidencia."""
        return _search.search(self._database, query, limit=limit)

    def filter(
        self, *, category: str | None = None, level: int | str | None = None
    ) -> Iterator[RoleLevel]:
        """Itera las entradas que cumplen los filtros de categoría y/o nivel."""
        number = normalize_level(level) if level is not None else None
        for entry in self._database.entries:
            if category is not None and entry.category != category:
                continue
            if number is not None and entry.level_number != number:
                continue
            yield entry

    # -- Comparaciones -------------------------------------------------------

    def compare_levels(self, role: str, level_a: int | str, level_b: int | str) -> LevelComparison:
        """Compara dos niveles del mismo rol: añadidas, retiradas y compartidas."""
        return _queries.compare_levels(self._database, role, level_a, level_b)

    def compare_roles(self, role_a: str, role_b: str, level: int | str) -> RoleComparison:
        """Compara dos roles al mismo nivel: comunes y exclusivas de cada uno."""
        return _queries.compare_roles(self._database, role_a, role_b, level)

    # -- Utilidades ----------------------------------------------------------

    def statistics(self) -> Statistics:
        """Estadísticas globales del catálogo cargado."""
        return self._database.statistics()

    def validate_role(self, role: str) -> bool:
        """``True`` si el nombre de rol existe en el catálogo."""
        return role in self._database.by_role

    def validate_level(self, role: str, level: int | str) -> bool:
        """``True`` si el nivel existe para el rol."""
        try:
            self._database.get_level(role, level)
        except TechRolesError:
            return False
        return True

    @staticmethod
    def export(data: Any, fmt: str = "json") -> str:  # noqa: ANN401 - acepta cualquier resultado de la API
        """Exporta cualquier resultado de la API a ``"json"`` o ``"markdown"``."""
        return _export.export(data, fmt)
