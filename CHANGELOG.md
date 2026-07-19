# Changelog

All notable changes to this project will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-07-19

### Added

- Initial release: Python port of [npm-tech-roles-library](https://github.com/686f6c61/npm-tech-roles-library).
- Catalog of 99 technical roles × 9 career levels (891 role-level definitions) in English and Spanish.
- 25 new roles over the npm catalog: AI Agent Engineer, LLMOps Engineer, Forward Deployed Engineer, Analytics Engineer, Data Product Manager, Technical Writer, DevSecOps Engineer, Security Architect, Incident Responder, Product Designer, UX Designer, UX Researcher, Solutions Engineer, Customer Success Engineer, AI Product Manager, Scrum Master, Agile Coach, Support Engineer, GRC Specialist, Technical Account Manager, Content Designer, Accessibility Specialist, Cloud Architect, Hardware Engineer, Developer Experience Engineer.
- New Design and Support categories; rebalanced Infrastructure, Product, Sales and Security categories.
- Pythonic typed API: queries by code/name, competencies (single, accumulated), career paths, next level, experience-based recommendation, scored search, filters, level and role comparisons, statistics, JSON/Markdown export.
- Not-found errors with did-you-mean suggestions.

### Changed

- Taxonomy cleanup versus the npm catalog: MLOps Specialist, MLOps Architect and MLOps Engineer merged into a single MLOps Engineer (AI/ML); Reliability Engineer merged into Site Reliability Engineer; Big Data Engineer retired (its content is a subset of Data Engineer); AI Researcher, Machine Learning Engineer and NLP Engineer moved to AI/ML; Security Engineer moved to Security; infrastructure roles (Cloud, DevOps, SRE, Platform, Network, Infrastructure, SysAdmin, DBA) moved to the Infrastructure category.
- Content audit and rewrite: 10 AI roles inherited from npm were byte-identical clones of a generic template and were fully rewritten with domain-specific competencies (agents, LLMOps-adjacent domains, RL, recommenders, AI governance under the EU AI Act, and more); 17 additional skeletal roles were enriched; executive filler ("Fortune 500 scale management", "creation of paradigms", "planetary vision") was replaced with domain-anchored leadership content across the catalog.
- Overlapping roles differentiated with explicit boundaries: QA Engineer (quality strategy) vs Test Automation Engineer (automation engineering), Security Engineer (platform security generalist) vs AppSec/SecOps specialists, Data Platform Engineer (internal platform) vs Data Engineer (pipelines and modeling).
- Level names normalized to a canonical set per language.

### Fixed

- 45 duplicate role-level codes inherited from the npm data (prefixes CE, DA, IE, PE, SA shared by several roles) resolved with unique prefixes: CPE (Compiler Engineer), DVA (Developer Advocate), INT (Integration Engineer), PLE (Platform Engineer), PRE (Prompt Engineer), SYS (SysAdmin).
- Inconsistent Spanish category names ("IA/AM", "Inteligencia Artificial y Aprendizaje Automático", English "Software Engineering") normalized.
- English role names and level names inside the Spanish catalog translated.
- role-names mapping desynchronized with the catalog ("Sysadmin" vs "SysAdmin", "Full Stack Developer" vs "Full-Stack Developer").
