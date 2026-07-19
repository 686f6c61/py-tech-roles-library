"""Búsqueda de roles con puntuación de coincidencia.

Reproduce la semántica de la versión JS: 10 puntos por coincidencia en el nombre
del rol y 5 por coincidencia en la categoría, por cada término de la consulta.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .exceptions import TechRolesError
from .models import SearchResult

if TYPE_CHECKING:
    from .database import Database

_TOKEN_RE = re.compile(r"[a-z0-9áéíóúüñ/+#.-]+")
_SQUASH_RE = re.compile(r"[^a-z0-9áéíóúüñ]+")

ROLE_MATCH_SCORE = 10
CATEGORY_MATCH_SCORE = 5


def _squash(text: str) -> str:
    """Normaliza para comparar: minúsculas y sin separadores ("Full-Stack" -> "fullstack")."""
    return _SQUASH_RE.sub("", text.lower())


def search(db: Database, query: str, limit: int = 20) -> list[SearchResult]:
    if not query or not query.strip():
        message = "Search query must be a non-empty string"
        raise TechRolesError(message)
    if limit < 1:
        message = f"limit must be >= 1, got {limit}"
        raise TechRolesError(message)

    terms = [_squash(term) for term in _TOKEN_RE.findall(query.lower())]
    terms = [term for term in terms if term]
    results: dict[str, SearchResult] = {}

    for role, levels in db.by_role.items():
        category = levels[0].category
        role_text = _squash(role)
        category_text = _squash(category)
        score = 0
        in_role = in_category = False
        for term in terms:
            if term in role_text:
                score += ROLE_MATCH_SCORE
                in_role = True
            if term in category_text:
                score += CATEGORY_MATCH_SCORE
                in_category = True
        if score > 0:
            matched_in = "both" if in_role and in_category else "role" if in_role else "category"
            results[role] = SearchResult(
                role=role, category=category, score=score, matched_in=matched_in
            )

    ordered = sorted(results.values(), key=lambda r: (-r.score, r.role))
    return ordered[:limit]
