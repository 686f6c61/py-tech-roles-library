# Diseño: tech-roles-library para PyPI

Fecha: 2026-07-19. Diseño validado con el usuario por secciones.

## Origen y objetivo

Port a Python del paquete npm `npm-tech-roles-library` (78 roles técnicos × 9 niveles,
bilingüe EN/ES, cero dependencias). Decisiones del usuario:

- API pythónica (no espejo 1:1 de la API JS).
- Repo nuevo independiente: `py-tech-roles-library`, autoría 686f6c61 (sin referencias a "sparring").
- Nombre en PyPI: `tech-roles-library` (import `tech_roles_library`). Verificado libre el 2026-07-19.
- Paridad funcional completa con la versión JS.
- Catálogo ampliado y taxonomía saneada, solo en la versión Python (el repo npm no se toca).

## Catálogo de datos

Base: los 78 roles del repo npm. Cambios:

**Fusiones (−3):**
- MLOps Specialist + MLOps Architect + MLOps Engineer → `MLOps Engineer` (categoría AI/ML).
- Reliability Engineer → se funde en `Site Reliability Engineer`.

**Recategorización:** Cloud Engineer, DevOps Engineer, Site Reliability Engineer,
Platform Engineer, Network Engineer, Infrastructure Engineer, SysAdmin y Database
Administrator pasan de Software Engineering a Infrastructure (ES: Infraestructura),
junto a FinOps Engineer y Kubernetes Engineer que ya estaban.

**Roles nuevos (+14),** justificados por la auditoría de mercado 2026:

| Rol | Categoría |
|---|---|
| AI Agent Engineer | AI/ML |
| LLMOps Engineer | AI/ML |
| Forward Deployed Engineer | Software Engineering |
| Analytics Engineer | Data |
| Data Product Manager | Product |
| Technical Writer | Product |
| DevSecOps Engineer | Security |
| Security Architect | Security |
| Incident Responder | Security |
| Product Designer | Design (nueva) |
| UX Designer | Design (nueva) |
| UX Researcher | Design (nueva) |
| Solutions Engineer | Sales |
| Customer Success Engineer | Sales |

Resultado: **89 roles, 8 categorías, 801 entradas rol-nivel** (89 × 9), en EN y ES
(178 ficheros JSON de datos + role_names.json).

## Arquitectura

```
src/tech_roles_library/
├── __init__.py      # TechRoles + exports públicos
├── models.py        # dataclasses frozen+slots: YearsRange, RoleLevel, ...
├── database.py      # carga perezosa (importlib.resources), índices en memoria
├── queries.py       # consultas, career path, comparaciones
├── search.py        # búsqueda con puntuación
├── export.py        # export JSON / Markdown
├── exceptions.py    # TechRolesError → RoleNotFoundError, LevelNotFoundError, InvalidLanguageError
└── data/{en,es}/    # 89 JSON por idioma + role_names.json
```

- Cero dependencias de runtime (solo stdlib).
- Python >= 3.11.
- Carga perezosa: `TechRoles()` no lee disco hasta la primera consulta.
- Errores "no encontrado" con sugerencias vía `difflib`.

## Superficie de API

`TechRoles(language="en")` con: `get_role`, `get_role_by_name`, `get_levels`, `roles()`,
`categories()`, `get_competencies`, `get_accumulated`, `get_career_path`, `get_next_level`,
`get_by_experience`, `get_years_range`, `search`, `filter`, `compare_levels`,
`compare_roles`, `statistics`, `validate_role`, `validate_level`, `export`.

## Tooling y entrega

- uv + uv_build, ruff (select ALL), ty, pytest con cobertura >= 80%.
- Tests portados de las 6 suites JS + validación estructural de los 178 JSON
  (esquema, 9 niveles por rol, códigos únicos, sin contaminación de idiomas).
- CI: GitHub Actions con matriz 3.11/3.12/3.13 (lint + typecheck + test).
- Publicación: workflow al crear release, con trusted publishing de PyPI y
  validación tag == versión (mismo patrón que el repo npm).
