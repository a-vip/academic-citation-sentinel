# 🎓 Academic Citation & Scholarly Impact Sentinel

[![Academic Citation Sentinel](https://github.com/a-vip/academic-citation-sentinel/actions/workflows/citation-sentinel.yml/badge.svg)](https://github.com/a-vip/academic-citation-sentinel/actions/workflows/citation-sentinel.yml)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0005--1903--6868-green.svg)](https://orcid.org/0009-0005-1903-6868)
[![Wikidata](https://img.shields.io/badge/Wikidata-Q140248356-blue.svg)](https://www.wikidata.org/wiki/Q140248356)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An autonomous academic impact and citation monitoring engine tracking research papers, working monographs, and policy submissions authored by **[Avi Perera](https://aviperera.com)** across OpenAlex, arXiv, and academic indexing registries.

---

## 🎯 Purpose & Research Grounding

Research in scientific citation dynamics demonstrates that open-access repositories with structured machine-readable metadata (`BibTeX`, `ORCID`, persistent DOIs, and reciprocal cross-links) experience significantly higher academic discovery and indexation velocity.

This repository:
1. **Tracks Core Publications**: Catalogs working papers including *Weapons That Think Must Not Decide* (UNIDIR / ResearchGate DOI: `10.13140/RG.2.2.10288.67842`) and *Algorithmic Reshaping of Radicalisation Pathways*.
2. **Maintains Live BibTeX**: Exposes standardized citations ready for copy-paste by international law and AI ethics researchers in [`CITATIONS.md`](CITATIONS.md).
3. **Monitors OpenAlex & arXiv**: Crawls academic databases for newly indexed works and preprints discussing Meaningful Human Control (MHC) in Lethal Autonomous Weapon Systems (LAWS).
4. **Dispatches Weekly Intelligence Reports**: Generates automated executive citation and impact summaries delivered to `workwithavip@gmail.com`.

---

## 🔬 Core Publications Tracked

| Publication | Venue / Affiliation | Identifier | Dossier Link |
| :--- | :--- | :--- | :--- |
| **Weapons That Think Must Not Decide** | UNIDIR & Sovereign Governance Archive | [DOI: 10.13140/RG.2.2.10288.67842](https://doi.org/10.13140/RG.2.2.10288.67842) | [Read Dossier](https://aviperera.com/meaningful-human-control-autonomous-weapons/) |
| **Algorithmic Reshaping of Radicalisation Pathways** | BUCSIS Research Monograph | Archival Monograph | [Read Dossier](https://aviperera.com/algorithmic-reshaping-radicalisation/) |
| **Abliteration.ai: Removing Safety Guardrails** | Autonomous AI Security Series | Intelligence Dossier | [Read Dossier](https://aviperera.com/abliteration-ai-removing-guardrails-international-security/) |
| **Operationalising Meaningful Human Control** | UN CCW GGE Consultations | Policy Framework | [Read Dossier](https://aviperera.com/meaningful-human-control-autonomous-weapons/) |

---

## ⚙️ Architecture & Automation

```text
[OpenAlex API] ----+
                   v
[arXiv API] ----> [scripts/citation_monitor.py] ---> [CITATIONS.md] (Updated)
                         |                      ---> [reports/YYYY-MM-DD.txt]
                         v
              [Weekly Email & Issue Dispatch] 
                         |
                         v
               workwithavip@gmail.com
```

- **Schedule**: Executes automatically every Friday at 04:00 UTC via `.github/workflows/citation-sentinel.yml`.
- **Zero-Dependency**: Runs on Python 3.11 standard library with 100% test coverage.

---

## 🔗 Institutional Links & Author Profiles

- **Official Web Domain:** [https://aviperera.com](https://aviperera.com)
- **ORCID:** [0009-0005-1903-6868](https://orcid.org/0009-0005-1903-6868)
- **Wikidata Entity:** [Q140248356](https://www.wikidata.org/wiki/Q140248356)
- **Autonomous Weapons Open Dataset:** [a-vip/laws-open-dataset](https://github.com/a-vip/laws-open-dataset)
- **Awesome Autonomous Weapons Systems:** [a-vip/awesome-autonomous-weapons-systems](https://github.com/a-vip/awesome-autonomous-weapons-systems)

---

## 📄 License

This repository is licensed under the [MIT License](LICENSE).
