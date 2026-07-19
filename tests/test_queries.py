import pytest

from tech_roles_library import TechRoles, TechRolesError


class TestCompetencies:
    def test_basic(self, en: TechRoles):
        comps = en.get_competencies("Backend Developer", 3)
        assert comps.role == "Backend Developer"
        assert len(comps.core) > 0
        assert len(comps.complementary) > 0
        assert len(comps.indicators) > 0

    def test_accumulated_grows_and_dedups(self, en: TechRoles):
        l1 = en.get_accumulated("Backend Developer", 1)
        l5 = en.get_accumulated("Backend Developer", 5)
        assert len(l5.core) > len(l1.core)
        assert len(l5.core) == len(set(l5.core))

    def test_accumulated_contains_lower_levels(self, en: TechRoles):
        l3 = en.get_competencies("Backend Developer", 1)
        acc = en.get_accumulated("Backend Developer", 3)
        for comp in l3.core:
            assert comp in acc.core


class TestCareerPath:
    def test_middle_level(self, en: TechRoles):
        path = en.get_career_path("Backend Developer", 5)
        assert [e.level_number for e in path.mastered] == [1, 2, 3, 4]
        assert path.current.level_number == 5
        assert [e.level_number for e in path.growth] == [6, 7, 8, 9]

    def test_extremes(self, en: TechRoles):
        first = en.get_career_path("Backend Developer", 1)
        assert first.mastered == ()
        last = en.get_career_path("Backend Developer", 9)
        assert last.growth == ()


class TestNextLevel:
    def test_returns_next(self, en: TechRoles):
        nxt = en.get_next_level("Backend Developer", 3)
        assert nxt is not None
        assert nxt.next.level_number == 4
        assert len(nxt.new_competencies) > 0

    def test_none_at_top(self, en: TechRoles):
        assert en.get_next_level("Backend Developer", 9) is None


class TestExperience:
    @pytest.mark.parametrize(
        ("years", "expected"),
        [(0, 1), (1, 1), (2, 2), (5, 4), (8, 6), (20, 9), (100, 9)],
    )
    def test_mapping(self, en: TechRoles, years, expected):
        assert en.get_by_experience("Backend Developer", years).level_number == expected

    def test_negative_raises(self, en: TechRoles):
        with pytest.raises(TechRolesError):
            en.get_by_experience("Backend Developer", -1)

    def test_years_range(self, en: TechRoles):
        rng = en.get_years_range("Backend Developer", 9)
        assert rng.min == 15
        assert rng.max is None


class TestComparisons:
    def test_compare_levels(self, en: TechRoles):
        cmp = en.compare_levels("Backend Developer", 3, 4)
        assert cmp.from_level.level_number == 3
        assert cmp.to_level.level_number == 4
        assert len(cmp.added) > 0
        all_new = set(cmp.to_level.core_competencies + cmp.to_level.complementary_competencies)
        assert set(cmp.added) <= all_new

    def test_compare_roles(self, en: TechRoles):
        cmp = en.compare_roles("Backend Developer", "Frontend Developer", 3)
        assert cmp.role_a.role == "Backend Developer"
        assert cmp.role_b.role == "Frontend Developer"
        assert set(cmp.only_a).isdisjoint(cmp.only_b)
        assert set(cmp.shared).isdisjoint(cmp.only_a)
