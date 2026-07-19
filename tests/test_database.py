import pytest

from tech_roles_library import (
    InvalidLanguageError,
    InvalidLevelError,
    RoleNotFoundError,
    TechRoles,
    normalize_level,
)

TOTAL_ROLES = 99
TOTAL_CATEGORIES = 9
TOTAL_ENTRIES = TOTAL_ROLES * 9


class TestLoading:
    def test_lazy_initialization(self):
        lib = TechRoles()
        assert lib._db is None  # noqa: SLF001

    def test_first_query_loads_data(self, en: TechRoles):
        assert len(en.roles()) == TOTAL_ROLES

    def test_invalid_language_raises(self):
        with pytest.raises(InvalidLanguageError):
            TechRoles(language="fr")

    def test_statistics(self, en: TechRoles):
        stats = en.statistics()
        assert stats.total_roles == TOTAL_ROLES
        assert stats.total_categories == TOTAL_CATEGORIES
        assert stats.total_entries == TOTAL_ENTRIES
        assert stats.average_entries_per_role == 9.0
        assert sum(stats.by_category.values()) == TOTAL_ENTRIES

    def test_both_languages_have_same_shape(self, en: TechRoles, es: TechRoles):
        assert len(en.roles()) == len(es.roles())
        assert len(en.categories()) == len(es.categories())
        en_codes = {e.code for e in en.filter()}
        es_codes = {e.code for e in es.filter()}
        assert en_codes == es_codes


class TestGetByCode:
    def test_known_code(self, en: TechRoles):
        entry = en.get_role("BE-L3")
        assert entry.role == "Backend Developer"
        assert entry.level_number == 3
        assert entry.code == "BE-L3"

    def test_code_is_case_insensitive(self, en: TechRoles):
        assert en.get_role("be-l3").code == "BE-L3"

    def test_unknown_code_raises(self, en: TechRoles):
        with pytest.raises(RoleNotFoundError):
            en.get_role("XX-L1")

    def test_codes_are_unique(self, en: TechRoles):
        codes = [e.code for e in en.filter()]
        assert len(codes) == len(set(codes))


class TestGetByName:
    def test_known_role(self, en: TechRoles):
        entry = en.get_role_by_name("Backend Developer", "L3")
        assert entry.code == "BE-L3"

    def test_level_variants(self, en: TechRoles):
        for level in (3, "3", "L3", "l3", "L3 - Junior II"):
            assert en.get_role_by_name("Backend Developer", level).code == "BE-L3"

    def test_unknown_role_suggests(self, en: TechRoles):
        with pytest.raises(RoleNotFoundError, match="Did you mean"):
            en.get_role_by_name("Backend Develper", 3)

    def test_spanish_names_in_spanish_catalog(self, es: TechRoles):
        entry = es.get_role_by_name("Desarrollador de Backend", "L3")
        assert entry.code == "BE-L3"

    def test_get_levels_returns_nine_sorted(self, en: TechRoles):
        levels = en.get_levels("Backend Developer")
        assert [e.level_number for e in levels] == list(range(1, 10))


class TestNormalizeLevel:
    def test_valid_inputs(self):
        assert normalize_level(1) == 1
        assert normalize_level("9") == 9
        assert normalize_level("L5") == 5
        assert normalize_level("L8 - Staff/Principal") == 8

    @pytest.mark.parametrize("bad", [0, 10, "L10", "", "senior", "LL3"])
    def test_invalid_inputs(self, bad):
        with pytest.raises(InvalidLevelError):
            normalize_level(bad)


class TestValidation:
    def test_validate_role(self, en: TechRoles):
        assert en.validate_role("Backend Developer") is True
        assert en.validate_role("No Existe") is False

    def test_validate_level(self, en: TechRoles):
        assert en.validate_level("Backend Developer", "L9") is True
        assert en.validate_level("Backend Developer", "L10") is False
        assert en.validate_level("No Existe", "L1") is False
