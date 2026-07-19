# tech-roles-library

[![PyPI version](https://img.shields.io/pypi/v/tech-roles-library.svg)](https://pypi.org/project/tech-roles-library/)
[![CI](https://github.com/686f6c61/py-tech-roles-library/actions/workflows/ci.yml/badge.svg)](https://github.com/686f6c61/py-tech-roles-library/actions/workflows/ci.yml)
[![License: PolyForm Noncommercial](https://img.shields.io/badge/License-PolyForm_Noncommercial_1.0.0-blue.svg)](https://polyformproject.org/licenses/noncommercial/1.0.0/)
[![Python](https://img.shields.io/pypi/pyversions/tech-roles-library.svg)](https://pypi.org/project/tech-roles-library/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/686f6c61/py-tech-roles-library/blob/main/notebooks/tech_roles_library_demo.ipynb)

**Demo and usage guide**: [tech-library.686f6c61.dev](https://tech-library.686f6c61.dev/)

A comprehensive library of **99 technical roles** with **9 career levels** each (891 role-level definitions), including detailed competencies, career progression paths and role comparisons, with full bilingual support (English/Spanish).

Python port and evolution of [npm-tech-roles-library](https://github.com/686f6c61/npm-tech-roles-library), with an expanded 2026 catalog (AI Agent Engineer, LLMOps Engineer, AI Product Manager, Cloud Architect, GRC Specialist, Design and Support roles...), a cleaned-up taxonomy and a fully typed Pythonic API.

## Features

- **99 roles × 9 levels = 891 definitions**, from L1 (Trainee) to L9 (VP/CTO)
- **9 categories**: AI/ML, Data, Design, Infrastructure, Product, Sales, Security, Software Engineering, Support
- **Bilingual**: complete English and Spanish catalogs
- **Zero runtime dependencies**: standard library only
- **Fully typed**: frozen dataclasses, `py.typed` marker
- **Lazy loading**: no disk access until the first query
- **Helpful errors**: "role not found" exceptions include *did-you-mean* suggestions

## Installation

```bash
pip install tech-roles-library
# or
uv add tech-roles-library
```

Requires Python 3.11 or later. No runtime dependencies.

## Quick start

```python
from tech_roles_library import TechRoles

lib = TechRoles(language="en")   # or language="es"

role = lib.get_role("BE-L3")
print(role.role)                  # Backend Developer
print(role.level)                 # L3 - Junior II
print(role.core_competencies[0])  # Mastery of RESTful API design and best practices

print(lib.get_by_experience("Backend Developer", 5).level)   # L4 - Mid-Level I
print(lib.search("fullstack")[0].role)                       # Full-Stack Developer
```

## Usage guide

### Choosing a language

Each language has its own complete catalog. Role names, categories, competencies and level names are localized; role codes are identical in both languages, so they work as stable cross-language identifiers.

```python
en = TechRoles(language="en")
es = TechRoles(language="es")

en.get_role("PT-L5").role   # Penetration Tester
es.get_role("PT-L5").role   # Pentester

es.roles()[:3]
# ('Administrador de Bases de Datos', 'Administrador de Sistemas', 'Agile Coach')
```

An unsupported language raises `InvalidLanguageError`. Data loads lazily: creating `TechRoles()` reads nothing from disk until the first query.

### Listing roles and categories

```python
lib = TechRoles()

len(lib.roles())    # 99
lib.roles()[:3]     # ('AI Agent Engineer', 'AI Engineer', 'AI Ethics & Governance Specialist')

lib.categories()
# ('AI/ML', 'Data', 'Design', 'Infrastructure', 'Product', 'Sales',
#  'Security', 'Software Engineering', 'Support')
```

### Getting a role

By code, or by name plus level. Levels accept several formats: `3`, `"3"`, `"L3"`, `"l3"` or the full name `"L3 - Junior II"`.

```python
role = lib.get_role("AAG-L5")            # by code (case-insensitive)
role.role                                # AI Agent Engineer
role.level                               # L5 - Mid-Level II
role.years_range                         # YearsRange(min=5, max=7)
role.core_competencies[0]
# Expertise in designing production-grade autonomous agent platforms

lib.get_role_by_name("Backend Developer", 3)        # same as "L3"
lib.get_role_by_name("Backend Developer", "L3 - Junior II")

[e.code for e in lib.get_levels("Data Engineer")]
# ['DE-L1', 'DE-L2', ..., 'DE-L9']
```

### Competencies

Each role-level has core competencies, complementary competencies and indicators (observable behaviors).

```python
c = lib.get_competencies("Backend Developer", "L3")
len(c.core), len(c.complementary), len(c.indicators)   # (8, 3, 3)
c.indicators[0]   # Completes complex features with minimal supervision

# Everything mastered from L1 up to a level, deduplicated:
acc = lib.get_accumulated("Backend Developer", 5)
len(acc.core)     # 40
```

### Career progression

```python
path = lib.get_career_path("Backend Developer", "L5")
[e.level_number for e in path.mastered]   # [1, 2, 3, 4]
path.current.level                        # L5 - Mid-Level II
[e.level_number for e in path.growth]     # [6, 7, 8, 9]

nxt = lib.get_next_level("Backend Developer", "L3")
nxt.next.code               # BE-L4
len(nxt.new_competencies)   # 11
nxt.new_competencies[0]     # Ability to design distributed systems and microservices

lib.get_next_level("Backend Developer", 9)   # None (top of the ladder)

# Recommended level for years of experience:
lib.get_by_experience("Backend Developer", 5).level   # L4 - Mid-Level I
lib.get_years_range("Backend Developer", 9)           # YearsRange(min=15, max=None)
```

### Search

Scored search over role names and categories. Hyphens and spacing are normalized, so `"fullstack"` finds `Full-Stack Developer`.

```python
for r in lib.search("data", limit=3):
    print(r.role, r.score, r.matched_in)
# Data Analyst 15 both
# Data Architect 15 both
# Data Engineer 15 both
```

An empty query or a `limit` below 1 raises `TechRolesError`.

### Filtering

`filter()` returns an iterator over role-level entries matching a category, a level, or both.

```python
[e.code for e in lib.filter(category="Design", level=3)]
# ['ACC-L3', 'CD-L3', 'PD-L3', 'UXD-L3', 'UXR-L3']

sum(1 for _ in lib.filter(level=9))       # 99 (one L9 per role)
sum(1 for _ in lib.filter())              # 891 (every entry)
```

### Comparisons

```python
# Between two levels of the same role:
cmp = lib.compare_levels("Backend Developer", 3, 4)
len(cmp.added)   # 11
cmp.added[0]     # Ability to design distributed systems and microservices

# Between two roles at the same level:
cmp = lib.compare_roles("Data Engineer", "Analytics Engineer", 3)
len(cmp.only_a), len(cmp.only_b)   # competencies exclusive to each role
```

Note: `shared` compares exact competency texts. Competencies are written per role, so overlaps between roles are intentionally rare — `only_a`/`only_b` are the useful views.

### Statistics

```python
s = lib.statistics()
s.total_roles, s.total_categories, s.total_entries   # (99, 9, 891)
s.by_category["Design"]                              # 45  (5 roles × 9 levels)
```

### Export

Any API result can be serialized to JSON or Markdown.

```python
comps = lib.get_competencies("Backend Developer", 3)

lib.export(comps, "json")       # pretty-printed JSON string
print(lib.export(comps, "markdown"))
# # Backend Developer
#
# ## L3 - Junior II
#
# ### Core competencies
# - ...
```

An unsupported format raises `ExportFormatError`.

### Error handling

All exceptions derive from `TechRolesError`. Not-found errors include *did-you-mean* suggestions:

```python
from tech_roles_library import RoleNotFoundError, LevelNotFoundError

try:
    lib.get_role_by_name("Bakcend Developer", 3)
except RoleNotFoundError as e:
    print(e)
# Role not found: 'Bakcend Developer'.
# Did you mean: Backend Developer, Game Developer, Blockchain Developer?

lib.validate_role("Backend Developer")        # True (no exception)
lib.validate_level("Backend Developer", 10)   # False
```

### Data model

All results are frozen (immutable) dataclasses with full type hints:

| Class | Returned by |
|---|---|
| `RoleLevel` | `get_role`, `get_role_by_name`, `get_levels`, `filter`, `get_by_experience` |
| `Competencies` | `get_competencies`, `get_accumulated` |
| `CareerPath` | `get_career_path` |
| `NextLevel` | `get_next_level` |
| `LevelComparison` / `RoleComparison` | `compare_levels` / `compare_roles` |
| `SearchResult` | `search` |
| `Statistics` | `statistics` |
| `YearsRange` | `get_years_range` and the `years_range` field |

## API reference

| Method | Description |
|---|---|
| `roles()` / `categories()` | All role / category names |
| `get_role(code)` | Role-level entry by code (`"BE-L3"`) |
| `get_role_by_name(role, level)` | Entry by role name and level |
| `get_levels(role)` | All 9 level entries for a role |
| `get_competencies(role, level)` | Core, complementary and indicators |
| `get_accumulated(role, level)` | Competencies accumulated from L1 |
| `get_career_path(role, level)` | Mastered + current + growth view |
| `get_next_level(role, level)` | Next level and new competencies (`None` at L9) |
| `get_by_experience(role, years)` | Recommended level for years of experience |
| `get_years_range(role, level)` | Experience range for a level |
| `search(query, limit=20)` | Scored search by role name or category |
| `filter(category=..., level=...)` | Iterator over matching entries |
| `compare_levels(role, a, b)` | Added / removed / shared competencies |
| `compare_roles(a, b, level)` | Shared and exclusive competencies |
| `statistics()` | Catalog totals |
| `validate_role(name)` / `validate_level(role, level)` | Existence checks |
| `export(data, "json" \| "markdown")` | Serialize any API result |

## Career levels

| Level | Name | Years |
|---|---|---|
| L1 | Trainee | 0-1 |
| L2 | Junior I | 1-2 |
| L3 | Junior II | 2-3 |
| L4 | Mid-Level I | 3-5 |
| L5 | Mid-Level II | 5-7 |
| L6 | Senior I | 7-10 |
| L7 | Senior II | 10-12 |
| L8 | Staff/Principal | 12-15 |
| L9 | VP/CTO | 15+ |

## Categories

| Category | Roles | Highlights |
|---|---|---|
| AI/ML | 21 | AI Agent Engineer, LLMOps Engineer, Foundation Models Engineer, MLOps Engineer |
| Data | 11 | Data Engineer, Analytics Engineer, Data Scientist, Data Architect |
| Design | 5 | Product Designer, UX Designer, UX Researcher, Content Designer, Accessibility Specialist |
| Infrastructure | 11 | Cloud Architect, DevOps Engineer, Site Reliability Engineer, Platform Engineer |
| Product | 12 | Product Manager, AI Product Manager, Scrum Master, Agile Coach, Technical Writer |
| Sales | 4 | Solutions Engineer, Technical Account Manager, Customer Success Engineer, SDR |
| Security | 9 | Security Architect, DevSecOps Engineer, Incident Responder, Pentester, GRC Specialist |
| Software Engineering | 25 | Backend, Frontend, Full-Stack, Mobile, Hardware Engineer, DevEx Engineer, Tech Lead |
| Support | 1 | Support Engineer |

## Differences with the npm package

This package started as a port of [npm-tech-roles-library](https://github.com/686f6c61/npm-tech-roles-library) and evolves the catalog:

- **+25 new roles** (2026 market): AI Agent Engineer, LLMOps Engineer, Forward Deployed Engineer, Analytics Engineer, Data Product Manager, Technical Writer, DevSecOps Engineer, Security Architect, Incident Responder, Product Designer, UX Designer, UX Researcher, Solutions Engineer, Customer Success Engineer, AI Product Manager, Scrum Master, Agile Coach, Support Engineer, GRC Specialist, Technical Account Manager, Content Designer, Accessibility Specialist, Cloud Architect, Hardware Engineer, Developer Experience Engineer
- **Cleaned-up taxonomy**: the three overlapping MLOps roles merged into one, Reliability Engineer merged into Site Reliability Engineer, Big Data Engineer retired (absorbed by Data Engineer), ML/NLP/AI research roles moved to AI/ML, infrastructure roles moved to the Infrastructure category, new Design and Support categories
- **Fixed inherited data bugs**: 45 duplicate role codes, inconsistent Spanish category names, English role and level names inside the Spanish catalog
- **Rewritten content**: 27 roles whose npm data was template filler ("Implementation of complex systems", "Fortune 500 scale management") now have domain-specific competencies per level, and executive-level fluff was replaced with domain-anchored leadership across the whole catalog
- **Differentiated overlapping roles**: QA Engineer vs Test Automation Engineer, Security Engineer vs AppSec/SecOps, Data Platform Engineer vs Data Engineer, Cloud Architect vs Cloud Engineer/Solutions Architect
- **Canonical level names** across all roles in both languages

## Development

```bash
git clone https://github.com/686f6c61/py-tech-roles-library
cd py-tech-roles-library
make dev     # uv sync --all-groups
make lint    # ruff + ty
make test    # pytest with coverage
make build   # uv build
```

## License

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — free for personal, educational, research and nonprofit use. Commercial use requires a separate license: contact [686f6c61](https://github.com/686f6c61).

Note: version 1.0.0 was briefly published under MIT and has been yanked; from 1.0.1 onwards the package is PolyForm Noncommercial.
