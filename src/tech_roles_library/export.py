"""Exportación de resultados a JSON y Markdown."""

from __future__ import annotations

import dataclasses
import json
from typing import Any

from .exceptions import ExportFormatError
from .models import CareerPath, Competencies, RoleLevel


def _to_plain(data: Any) -> Any:  # noqa: ANN401 - acepta cualquier resultado de la API
    if dataclasses.is_dataclass(data) and not isinstance(data, type):
        return dataclasses.asdict(data)
    if isinstance(data, (list, tuple)):
        return [_to_plain(item) for item in data]
    return data


def export(data: Any, fmt: str = "json") -> str:  # noqa: ANN401 - acepta cualquier resultado de la API
    if fmt == "json":
        return json.dumps(_to_plain(data), ensure_ascii=False, indent=2)
    if fmt == "markdown":
        return to_markdown(data)
    raise ExportFormatError(fmt)


def _competencies_md(item: Competencies) -> str:
    lines = [f"# {item.role}", "", f"## {item.level}", ""]
    for title, values in (
        ("Core competencies", item.core),
        ("Complementary competencies", item.complementary),
        ("Indicators", item.indicators),
    ):
        if values:
            lines += [f"### {title}", "", *[f"- {value}" for value in values], ""]
    return "\n".join(lines)


def _role_level_md(item: RoleLevel) -> str:
    header = [
        f"# {item.role}",
        "",
        f"## {item.level} ({item.code})",
        "",
        f"- Category: {item.category}",
        f"- Years of experience: {item.years_range.min}"
        + (f"-{item.years_range.max}" if item.years_range.max is not None else "+"),
        "",
    ]
    body = _competencies_md(
        Competencies(
            role=item.role,
            level=item.level,
            core=item.core_competencies,
            complementary=item.complementary_competencies,
            indicators=item.indicators,
        )
    )
    # _competencies_md repite el encabezado de rol y nivel; nos quedamos con las secciones
    sections = body.split("\n")[4:]
    return "\n".join(header + sections)


def _career_path_md(item: CareerPath) -> str:
    lines = [f"# Career path: {item.role}", ""]
    lines += [f"## Current level: {item.current.level}", ""]
    if item.mastered:
        lines += ["## Mastered levels", "", *[f"- {e.level}" for e in item.mastered], ""]
    if item.growth:
        lines += ["## Growth path", "", *[f"- {e.level}" for e in item.growth], ""]
    return "\n".join(lines)


def to_markdown(data: Any) -> str:  # noqa: ANN401 - acepta cualquier resultado de la API
    if isinstance(data, Competencies):
        return _competencies_md(data)
    if isinstance(data, RoleLevel):
        return _role_level_md(data)
    if isinstance(data, CareerPath):
        return _career_path_md(data)
    if isinstance(data, (list, tuple)):
        return "\n".join(to_markdown(item) for item in data)
    message = f"Cannot render {type(data).__name__} as markdown"
    raise ExportFormatError(message)
