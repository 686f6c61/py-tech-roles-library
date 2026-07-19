"""Validación estructural y lingüística de los 178 ficheros de datos.

Equivalente a la suite de "pre-publication validation" del paquete npm original,
ampliada con las lecciones aprendidas de sus bugs: códigos duplicados entre roles
y categorías inconsistentes en español.
"""

import json
import re
from pathlib import Path

import pytest

DATA = Path(__file__).parent.parent / "src" / "tech_roles_library" / "data"

EXPECTED_ROLES = 99

LEVEL_NAMES = {
    "en": [
        "L1 - Trainee",
        "L2 - Junior I",
        "L3 - Junior II",
        "L4 - Mid-Level I",
        "L5 - Mid-Level II",
        "L6 - Senior I",
        "L7 - Senior II",
        "L8 - Staff/Principal",
        "L9 - VP/CTO",
    ],
    "es": [
        "L1 - Aprendiz",
        "L2 - Junior I",
        "L3 - Junior II",
        "L4 - Nivel Medio I",
        "L5 - Nivel Medio II",
        "L6 - Senior I",
        "L7 - Senior II",
        "L8 - Staff/Principal",
        "L9 - Vicepresidente o Director de Tecnología",
    ],
}

CATEGORIES = {
    "en": {
        "AI/ML",
        "Data",
        "Design",
        "Infrastructure",
        "Product",
        "Sales",
        "Security",
        "Software Engineering",
        "Support",
    },
    "es": {
        "IA/ML",
        "Datos",
        "Diseño",
        "Infraestructura",
        "Producto",
        "Ventas",
        "Seguridad",
        "Ingeniería de Software",
        "Soporte",
    },
}

# Palabras funcionales inglesas que no deben aparecer en textos en español
EN_CONTAMINATION = re.compile(r"\b(the|with|and|ability|knowledge|understanding|skills)\b")
# Palabras españolas que no deben aparecer en textos en inglés
ES_CONTAMINATION = re.compile(r"\b(capacidad|conocimiento|dominio|básico|avanzado|habilidad)\b")


def load(lang: str) -> dict[str, dict]:
    return {
        p.stem: json.loads(p.read_text(encoding="utf-8"))
        for p in sorted((DATA / lang).glob("*.json"))
    }


@pytest.fixture(scope="module")
def catalogs() -> dict[str, dict[str, dict]]:
    return {"en": load("en"), "es": load("es")}


class TestStructure:
    @pytest.mark.parametrize("lang", ["en", "es"])
    def test_role_count(self, catalogs, lang):
        assert len(catalogs[lang]) == EXPECTED_ROLES

    @pytest.mark.parametrize("lang", ["en", "es"])
    def test_every_role_has_nine_levels(self, catalogs, lang):
        for slug, data in catalogs[lang].items():
            assert len(data["levels"]) == 9, f"{lang}/{slug}"
            numbers = sorted(lv["levelNumber"] for lv in data["levels"].values())
            assert numbers == list(range(1, 10)), f"{lang}/{slug}"

    @pytest.mark.parametrize("lang", ["en", "es"])
    def test_level_names_canonical(self, catalogs, lang):
        for slug, data in catalogs[lang].items():
            names = [
                lv["level"]
                for lv in sorted(data["levels"].values(), key=lambda x: x["levelNumber"])
            ]
            assert names == LEVEL_NAMES[lang], f"{lang}/{slug}"

    @pytest.mark.parametrize("lang", ["en", "es"])
    def test_categories_canonical(self, catalogs, lang):
        found = {data["category"] for data in catalogs[lang].values()}
        assert found == CATEGORIES[lang]

    def test_codes_globally_unique_and_shared_between_languages(self, catalogs):
        en_codes: list[str] = []
        for data in catalogs["en"].values():
            en_codes.extend(data["levels"].keys())
        assert len(en_codes) == len(set(en_codes)), "códigos duplicados en EN"

        for slug, data in catalogs["es"].items():
            assert set(data["levels"].keys()) == set(catalogs["en"][slug]["levels"].keys()), slug

    @pytest.mark.parametrize("lang", ["en", "es"])
    def test_code_prefix_consistent_within_role(self, catalogs, lang):
        for slug, data in catalogs[lang].items():
            prefixes = {code.rsplit("-", 1)[0] for code in data["levels"]}
            assert len(prefixes) == 1, f"{lang}/{slug}: {prefixes}"

    @pytest.mark.parametrize("lang", ["en", "es"])
    def test_years_ranges_progress(self, catalogs, lang):
        for slug, data in catalogs[lang].items():
            levels = sorted(data["levels"].values(), key=lambda x: x["levelNumber"])
            mins = [lv["yearsRange"]["min"] for lv in levels]
            assert mins == sorted(mins), f"{lang}/{slug}"
            assert levels[-1]["yearsRange"]["max"] is None, f"{lang}/{slug}: L9 debe ser abierto"
            for lv in levels[:-1]:
                assert lv["yearsRange"]["max"] is not None, f"{lang}/{slug} L{lv['levelNumber']}"
                assert lv["yearsRange"]["min"] < lv["yearsRange"]["max"], f"{lang}/{slug}"

    @pytest.mark.parametrize("lang", ["en", "es"])
    def test_competency_counts(self, catalogs, lang):
        for slug, data in catalogs[lang].items():
            for code, lv in data["levels"].items():
                assert 4 <= len(lv["coreCompetencies"]) <= 12, f"{lang}/{slug}/{code}"
                assert 2 <= len(lv["complementaryCompetencies"]) <= 6, f"{lang}/{slug}/{code}"
                assert 2 <= len(lv["indicators"]) <= 5, f"{lang}/{slug}/{code}"


class TestLanguageQuality:
    def test_no_english_contamination_in_spanish(self, catalogs):
        for slug, data in catalogs["es"].items():
            for code, lv in data["levels"].items():
                texts = lv["coreCompetencies"] + lv["complementaryCompetencies"] + lv["indicators"]
                for text in texts:
                    match = EN_CONTAMINATION.search(text.lower())
                    assert match is None, (
                        f"es/{slug}/{code}: {match.group() if match else ''!r} en {text!r}"
                    )

    def test_no_spanish_contamination_in_english(self, catalogs):
        for slug, data in catalogs["en"].items():
            for code, lv in data["levels"].items():
                texts = lv["coreCompetencies"] + lv["complementaryCompetencies"] + lv["indicators"]
                for text in texts:
                    match = ES_CONTAMINATION.search(text.lower())
                    assert match is None, (
                        f"en/{slug}/{code}: {match.group() if match else ''!r} en {text!r}"
                    )


class TestRoleNames:
    def test_role_names_file_covers_catalog(self, catalogs):
        role_names = json.loads((DATA / "role_names.json").read_text(encoding="utf-8"))
        en_roles = {data["role"] for data in catalogs["en"].values()}
        assert en_roles == set(role_names), (
            "role_names.json desincronizado con el catálogo EN: "
            f"faltan {en_roles - set(role_names)}, sobran {set(role_names) - en_roles}"
        )

    def test_role_names_map_to_spanish_catalog(self, catalogs):
        role_names = json.loads((DATA / "role_names.json").read_text(encoding="utf-8"))
        es_roles = {data["role"] for data in catalogs["es"].values()}
        mapped = {entry["es"] for entry in role_names.values()}
        assert mapped == es_roles
