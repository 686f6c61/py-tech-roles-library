import json

import pytest

from tech_roles_library import ExportFormatError, TechRoles, TechRolesError


class TestSearch:
    def test_squashed_match(self, en: TechRoles):
        results = en.search("fullstack")
        assert results[0].role == "Full-Stack Developer"
        assert results[0].matched_in == "role"

    def test_hyphenated_query(self, en: TechRoles):
        assert en.search("full-stack")[0].role == "Full-Stack Developer"

    def test_category_match(self, en: TechRoles):
        results = en.search("security")
        assert any(r.matched_in in ("category", "both") for r in results)

    def test_spanish(self, es: TechRoles):
        roles = [r.role for r in es.search("seguridad")]
        assert "Arquitecto de Seguridad" in roles

    def test_limit(self, en: TechRoles):
        assert len(en.search("engineer", limit=5)) == 5

    def test_no_results(self, en: TechRoles):
        assert en.search("zzzz") == []

    def test_empty_query_raises(self, en: TechRoles):
        with pytest.raises(TechRolesError):
            en.search("  ")

    def test_scores_sorted_descending(self, en: TechRoles):
        scores = [r.score for r in en.search("data engineer")]
        assert scores == sorted(scores, reverse=True)


class TestFilter:
    def test_by_category(self, en: TechRoles):
        entries = list(en.filter(category="Security"))
        assert entries
        assert all(e.category == "Security" for e in entries)

    def test_by_level(self, en: TechRoles):
        entries = list(en.filter(level=5))
        assert all(e.level_number == 5 for e in entries)
        assert len(entries) == len(en.roles())

    def test_combined(self, en: TechRoles):
        entries = list(en.filter(category="Design", level="L3"))
        assert all(e.category == "Design" and e.level_number == 3 for e in entries)

    def test_no_filters_returns_all(self, en: TechRoles):
        assert len(list(en.filter())) == en.statistics().total_entries


class TestExport:
    def test_json_roundtrip(self, en: TechRoles):
        comps = en.get_competencies("Backend Developer", 3)
        data = json.loads(en.export(comps, "json"))
        assert data["role"] == "Backend Developer"
        assert isinstance(data["core"], list)

    def test_json_of_role_level(self, en: TechRoles):
        entry = en.get_role("BE-L9")
        data = json.loads(en.export(entry, "json"))
        assert data["years_range"]["max"] is None

    def test_markdown_competencies(self, en: TechRoles):
        md = en.export(en.get_competencies("Backend Developer", 3), "markdown")
        assert md.startswith("# Backend Developer")
        assert "### Core competencies" in md
        assert "- " in md

    def test_markdown_role_level(self, en: TechRoles):
        md = en.export(en.get_role("BE-L3"), "markdown")
        assert "(BE-L3)" in md
        assert "Years of experience: 2-3" in md

    def test_markdown_career_path(self, en: TechRoles):
        md = en.export(en.get_career_path("Backend Developer", 5), "markdown")
        assert "Career path" in md
        assert "Growth path" in md

    def test_unsupported_format_raises(self, en: TechRoles):
        with pytest.raises(ExportFormatError):
            en.export({}, "yaml")
