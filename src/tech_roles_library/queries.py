"""Consultas de carrera y comparaciones sobre la base de datos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .database import MAX_LEVEL
from .exceptions import TechRolesError
from .models import CareerPath, Competencies, LevelComparison, NextLevel, RoleComparison

if TYPE_CHECKING:
    from .database import Database
    from .models import RoleLevel


def _dedup(items: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """Elimina duplicados conservando el orden de aparición."""
    return tuple(dict.fromkeys(items))


def get_competencies(db: Database, role: str, level: int | str) -> Competencies:
    entry = db.get_level(role, level)
    return Competencies(
        role=entry.role,
        level=entry.level,
        core=entry.core_competencies,
        complementary=entry.complementary_competencies,
        indicators=entry.indicators,
    )


def get_accumulated(db: Database, role: str, level: int | str) -> Competencies:
    target = db.get_level(role, level)
    levels = [e for e in db.get_levels(role) if e.level_number <= target.level_number]
    return Competencies(
        role=target.role,
        level=target.level,
        core=_dedup([c for e in levels for c in e.core_competencies]),
        complementary=_dedup([c for e in levels for c in e.complementary_competencies]),
        indicators=target.indicators,
    )


def get_career_path(db: Database, role: str, current_level: int | str) -> CareerPath:
    current = db.get_level(role, current_level)
    levels = db.get_levels(role)
    return CareerPath(
        role=current.role,
        mastered=tuple(e for e in levels if e.level_number < current.level_number),
        current=current,
        growth=tuple(e for e in levels if e.level_number > current.level_number),
    )


def get_next_level(db: Database, role: str, current_level: int | str) -> NextLevel | None:
    current = db.get_level(role, current_level)
    if current.level_number >= MAX_LEVEL:
        return None
    nxt = db.get_level(role, current.level_number + 1)
    comparison = compare_levels(db, role, current.level_number, nxt.level_number)
    return NextLevel(current=current, next=nxt, new_competencies=comparison.added)


def get_by_experience(db: Database, role: str, years: float) -> RoleLevel:
    if years < 0:
        message = f"Years must be a non-negative number, got {years!r}"
        raise TechRolesError(message)
    levels = db.get_levels(role)
    for entry in levels:
        if entry.years_range.contains(years):
            return entry
    return levels[-1]


def compare_levels(
    db: Database, role: str, level_a: int | str, level_b: int | str
) -> LevelComparison:
    from_level = db.get_level(role, level_a)
    to_level = db.get_level(role, level_b)
    from_all = set(from_level.core_competencies + from_level.complementary_competencies)
    to_all = to_level.core_competencies + to_level.complementary_competencies
    from_ordered = from_level.core_competencies + from_level.complementary_competencies
    return LevelComparison(
        role=from_level.role,
        from_level=from_level,
        to_level=to_level,
        added=_dedup([c for c in to_all if c not in from_all]),
        removed=_dedup([c for c in from_ordered if c not in set(to_all)]),
        shared=_dedup([c for c in to_all if c in from_all]),
    )


def compare_roles(db: Database, role_a: str, role_b: str, level: int | str) -> RoleComparison:
    entry_a = db.get_level(role_a, level)
    entry_b = db.get_level(role_b, level)
    all_a = entry_a.core_competencies + entry_a.complementary_competencies
    all_b = entry_b.core_competencies + entry_b.complementary_competencies
    set_a, set_b = set(all_a), set(all_b)
    return RoleComparison(
        level_number=entry_a.level_number,
        role_a=entry_a,
        role_b=entry_b,
        shared=_dedup([c for c in all_a if c in set_b]),
        only_a=_dedup([c for c in all_a if c not in set_b]),
        only_b=_dedup([c for c in all_b if c not in set_a]),
    )
