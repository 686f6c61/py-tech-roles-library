import pytest

from tech_roles_library import TechRoles


@pytest.fixture(scope="session")
def en() -> TechRoles:
    return TechRoles(language="en")


@pytest.fixture(scope="session")
def es() -> TechRoles:
    return TechRoles(language="es")
