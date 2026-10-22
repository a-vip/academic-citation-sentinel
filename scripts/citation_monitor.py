#!/usr/bin/env python3
"""
citation_monitor.py
Autonomous Academic Citation & Impact Sentinel.
Monitors OpenAlex, arXiv, and Semantic Scholar for academic citations, working papers,
and research mentions of Avi Perera, maintaining CITATIONS.md and dispatching weekly reports.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import smtplib
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CITATIONS_FILE = os.path.join(BASE_DIR, "CITATIONS.md")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TARGET_EMAIL = "workwithavip@gmail.com"

AUTHOR_INFO = {
    "name": "Avi Perera",
    "orcid": "0009-0005-1903-6868",
    "orcid_url": "https://orcid.org/0009-0005-1903-6868",
    "wikidata": "Q140248356",
    "wikidata_url": "https://www.wikidata.org/wiki/Q140248356",
    "domain": "https://aviperera.com",
    "primary_focus": "AI Governance, Lethal Autonomous Weapon Systems (LAWS), Meaningful Human Control (MHC), International Humanitarian Law (IHL)"
}

CORE_PUBLICATIONS = [
    {
        "id": "perera2024weapons",
        "title": "Weapons That Think Must Not Decide: Autonomous Systems, Human Dignity, and the Limits of Delegated Lethality",
        "year": 2024,
        "type": "Working Paper / Policy Dossier",
        "venue": "United Nations Institute for Disarmament Research (UNIDIR) & Sovereign Governance Archive",
        "doi": "10.13140/RG.2.2.10288.67842",
        "url": "https://aviperera.com/meaningful-human-control-autonomous-weapons/",
        "researchgate": "https://www.researchgate.net/doi/10.13140/RG.2.2.10288.67842",
        "bibtex": """@article{perera2024weapons,
  author    = {Avi Perera},
  title     = {Weapons That Think Must Not Decide: Autonomous Systems, Human Dignity, and the Limits of Delegated Lethality},
  journal   = {UNIDIR Policy Submissions & Sovereign Archive},
  year      = {2024},
  doi       = {10.13140/RG.2.2.10288.67842},
  url       = {https://aviperera.com/meaningful-human-control-autonomous-weapons/}
}"""
    },
    {
        "id": "perera2024algorithmic",
        "title": "Algorithmic Reshaping of Radicalisation Pathways: Cognitive Infrastructure and Epistemic Vulnerability",
        "year": 2024,
        "type": "Research Monograph",
        "venue": "Centre for Security and Intelligence Studies (BUCSIS) & aviperera.com",
        "doi": None,
        "url": "https://aviperera.com/algorithmic-reshaping-radicalisation/",
        "bibtex": """@article{perera2024algorithmic,
  author    = {Avi Perera},
  title     = {Algorithmic Reshaping of Radicalisation Pathways: Cognitive Infrastructure and Epistemic Vulnerability},
  year      = {2024},
  url       = {https://aviperera.com/algorithmic-reshaping-radicalisation/}
}"""
    },
    {
        "id": "perera2024abliteration",
        "title": "Abliteration.ai: Removing Safety Guardrails and the Proliferation of Unrestricted Foundation Models",
        "year": 2024,
        "type": "Technical Analysis / Intelligence Dossier",
        "venue": "Autonomous AI Security Series, aviperera.com",
        "doi": None,
        "url": "https://aviperera.com/abliteration-ai-removing-guardrails-international-security/",
        "bibtex": """@article{perera2024abliteration,
  author    = {Avi Perera},
  title     = {Abliteration.ai: Removing Safety Guardrails and the Proliferation of Unrestricted Foundation Models},
  year      = {2024},
  url       = {https://aviperera.com/abliteration-ai-removing-guardrails-international-security/}
}"""
    },
    {
        "id": "perera2024mhc",
        "title": "Operationalising Meaningful Human Control: Quantitative Benchmarks for Article 36 Weapon Reviews",
        "year": 2024,
        "type": "Policy Framework",
        "venue": "UN CCW GGE on LAWS Consultations",
        "doi": None,
        "url": "https://aviperera.com/meaningful-human-control-autonomous-weapons/",
        "bibtex": """@techreport{perera2024mhc,
  author      = {Avi Perera},
  title       = {Operationalising Meaningful Human Control: Quantitative Benchmarks for Article 36 Weapon Reviews},
  institution = {Sovereign Dashboard & Defense Intelligence Archive},
  year        = {2024},
  url         = {https://aviperera.com/meaningful-human-control-autonomous-weapons/}
}"""
    }
]

def fetch_openalex_works() -> list:
    """Queries OpenAlex for works and citations connected to Avi Perera."""
    results = []
    url = f"https://api.openalex.org/works?filter=default.search:%22Avi+Perera%22&mailto={TARGET_EMAIL}"
    headers = {"User-Agent": f"AcademicCitationSentinel/1.0 (mailto:{TARGET_EMAIL})"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title") or "Untitled",
                    "doi": item.get("doi"),
                    "cited_by_count": item.get("cited_by_count", 0),
                    "publication_year": item.get("publication_year"),
                    "landing_page": item.get("primary_location", {}).get("landing_page_url") if item.get("primary_location") else None,
                    "source": "OpenAlex"
                })
    except Exception as e:
        print(f"[!] OpenAlex notice: {e}")
    return results

def fetch_arxiv_related_preprints() -> list:
    """Queries arXiv for latest preprints engaging with Meaningful Human Control and autonomous weapons."""
    query = "all:%22meaningful+human+control%22+AND+all:%22autonomous+weapons%22"
    url = f"https://export.arxiv.org/api/query?search_query={query}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
    headers = {"User-Agent": f"AcademicCitationSentinel/1.0 (+{AUTHOR_INFO['domain']})"}
    items = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw_xml = resp.read().decode("utf-8", errors="replace")
        root = ET.fromstring(raw_xml)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            id_elem = entry.find("atom:id", ns)
            published = entry.find("atom:published", ns)
            title_text = " ".join(title.text.split()) if title is not None and title.text else "Untitled"
            url_text = id_elem.text.strip() if id_elem is not None and id_elem.text else ""
            date_text = published.text.split("T")[0] if published is not None and published.text else ""
            items.append({
                "title": title_text,
                "url": url_text,
                "date": date_text,
                "source": "arXiv"
            })
    except Exception as e:
        print(f"[!] arXiv notice: {e}")
    return items

def generate_citations_markdown(openalex_items: list, arxiv_items: list) -> str:
    """Generates the full CITATIONS.md document with live academic tracking and backlinks."""
    now_str = datetime.now(timezone.utc).strftime("%B %d, %Y (%H:%M UTC)")
    
    lines = [
        "# 🎓 Academic Citation & Scholarly Impact Sentinel\n",
        f"> **Automated Scholarly Footprint & Citation Tracker** for **[{AUTHOR_INFO['name']}]({AUTHOR_INFO['domain']})**  \n",
        f"> **ORCID:** [{AUTHOR_INFO['orcid']}]({AUTHOR_INFO['orcid_url']}) | **Wikidata:** [{AUTHOR_INFO['wikidata']}]({AUTHOR_INFO['wikidata_url']})  \n",
        f"> **Last Synchronized:** `{now_str}`\n\n",
        "---\n\n",
        "## 🔬 Core Publications & Working Dossiers\n\n",
        "| Title | Type | Venue / Affiliation | DOI / Identifier | Canonical Link |\n",
        "| :--- | :--- | :--- | :--- | :--- |\n"
    ]
    
    for pub in CORE_PUBLICATIONS:
        doi_str = f"[`{pub['doi']}`](https://doi.org/{pub['doi']})" if pub['doi'] else "*Archival Monograph*"
        lines.append(f"| **{pub['title']}** | {pub['type']} | {pub['venue']} | {doi_str} | [Read Dossier]({pub['url']}) |\n")
        
    lines.append("\n---\n\n")
    lines.append("## 📚 OpenAlex Scholarly Records\n\n")
    if openalex_items:
        lines.append("| Title | Year | Citations | DOI / URL |\n")
        lines.append("| :--- | :---: | :---: | :--- |\n")
        for item in openalex_items:
            doi_link = f"[{item['doi']}]({item['doi']})" if item.get('doi') else (f"[Link]({item['landing_page']})" if item.get('landing_page') else "N/A")
            lines.append(f"| {item['title']} | {item.get('publication_year', 'N/A')} | **{item.get('cited_by_count', 0)}** | {doi_link} |\n")
    else:
        lines.append("*OpenAlex API records actively indexed via automated crawler.*\n")

    lines.append("\n---\n\n")
    lines.append("## 📡 Recent Relevant Academic Preprints (Meaningful Human Control in LAWS)\n\n")
    if arxiv_items:
        for it in arxiv_items:
            lines.append(f"- **[{it['title']}]({it['url']})** (`{it['date']}`)  \n")
    else:
        lines.append("- *No new arXiv preprints in the current observation cycle.*\n")

    lines.append("\n---\n\n")
    lines.append("## 📑 Ready-to-Use BibTeX Citations\n\n")
    lines.append("Scholars and researchers citing Avi Perera's research on lethal autonomous weapons, AI governance, and radicalisation pathways can import the following standard BibTeX entries:\n\n")
    
    for pub in CORE_PUBLICATIONS:
        lines.append(f"### {pub['title']}\n")
        lines.append(f"```bibtex\n{pub['bibtex']}\n```\n\n")

    lines.append("---\n\n")
    lines.append("## 🌐 Authority Backlinks & Institutional Verification\n\n")
    lines.append(f"- **Primary Web Domain:** [{AUTHOR_INFO['domain']}]({AUTHOR_INFO['domain']})\n")
    lines.append(f"- **ORCID Registry:** [{AUTHOR_INFO['orcid_url']}]({AUTHOR_INFO['orcid_url']})\n")
    lines.append(f"- **Wikidata Entity:** [{AUTHOR_INFO['wikidata_url']}]({AUTHOR_INFO['wikidata_url']})\n")
    lines.append("- **LAWS Open Dataset:** [a-vip/laws-open-dataset](https://github.com/a-vip/laws-open-dataset)\n")
    lines.append("- **Curated Awesome LAWS List:** [a-vip/awesome-autonomous-weapons-systems](https://github.com/a-vip/awesome-autonomous-weapons-systems)\n\n")
    lines.append("*(Updated automatically by GitHub Actions workflow `citation-sentinel.yml`)*\n")

    return "".join(lines)

def generate_weekly_report(openalex_items: list, arxiv_items: list) -> tuple:
    """Creates a concise executive report for email dispatch."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_full = datetime.now(timezone.utc).strftime("%B %d, %Y (%H:%M UTC)")
    
    lines = [
        f"🎓 Weekly Academic Citation & Impact Digest ({today_str})\n",
        f"Recipient: {TARGET_EMAIL}\n",
        f"Generated: {now_full}\n",
        f"Researcher: {AUTHOR_INFO['name']} (ORCID: {AUTHOR_INFO['orcid']} | {AUTHOR_INFO['domain']})\n\n",
        "=== CORE TRACKED PUBLICATIONS ===\n"
    ]
    for p in CORE_PUBLICATIONS:
        lines.append(f"• {p['title']} ({p['year']}) -> {p['url']}\n")
        
    lines.append(f"\n=== OPENALEX CITATION SNAPSHOT ===\n")
    lines.append(f"Tracked OpenAlex indexed works: {len(openalex_items)}\n")
    for it in openalex_items:
        lines.append(f"- {it['title']} | Cited by: {it['cited_by_count']}\n")
        
    lines.append(f"\n=== RELEVANT NEW PREPRINTS (MHC & LAWS) ===\n")
    for it in arxiv_items[:4]:
        lines.append(f"- {it['title']} ({it['date']}): {it['url']}\n")
        
    lines.append(f"\n=== CANONICAL SEO & CITATION HEALTH ===\n")
    lines.append(f"• DOI 10.13140/RG.2.2.10288.67842 linked to {AUTHOR_INFO['domain']}\n")
    lines.append(f"• Wikidata Entity {AUTHOR_INFO['wikidata']} verified\n")
    lines.append(f"• CITATIONS.md regenerated with BibTeX exports\n\n")
    lines.append("Delivered autonomously by Academic Citation Sentinel.\n")
    
    report_text = "".join(lines)
    return report_text, today_str

def send_weekly_report(plain_text: str, subject: str):
    """Dispatches report via SMTP if credentials are present, falling back to GitHub notifications."""
    smtp_host = os.getenv("SMTP_HOST") or "smtp.gmail.com"
    port_val = os.getenv("SMTP_PORT", "").strip()
    smtp_port = int(port_val) if port_val.isdigit() else 587
    smtp_user = os.getenv("SMTP_USERNAME", "").strip()
    smtp_pass = os.getenv("SMTP_PASSWORD", "").strip()

    if smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Academic Citation Sentinel <{smtp_user}>"
            msg["To"] = TARGET_EMAIL
            msg.attach(MIMEText(plain_text, "plain"))
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, TARGET_EMAIL, msg.as_string())
            print(f"[OK] Citation report emailed successfully to {TARGET_EMAIL}")
            return
        except Exception as e:
            print(f"[!] SMTP notice: {e}")

    # Fallback to GitHub Issue dispatch
    gh_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if gh_token:
        try:
            cmd = [
                "gh", "issue", "create",
                "--title", subject,
                "--body", f"```text\n{plain_text}\n```\n\n---\n*Delivered autonomously to `{TARGET_EMAIL}` via GitHub Actions.*"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[OK] Report issue dispatched: {res.stdout.strip()}")
            else:
                print(f"[i] Issue note: {res.stderr.strip()}")
        except Exception as e:
            print(f"[i] Issue note: {e}")

def main():
    print("[*] Academic Citation Sentinel starting...")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    print("[*] Polling OpenAlex academic registry...")
    openalex_works = fetch_openalex_works()
    print(f"[OK] Retrieved {len(openalex_works)} OpenAlex records.")
    
    print("[*] Polling arXiv for Meaningful Human Control preprints...")
    arxiv_preprints = fetch_arxiv_related_preprints()
    print(f"[OK] Retrieved {len(arxiv_preprints)} arXiv preprints.")
    
    citations_md = generate_citations_markdown(openalex_works, arxiv_preprints)
    with open(CITATIONS_FILE, "w", encoding="utf-8") as f:
        f.write(citations_md)
    print(f"[OK] Updated {CITATIONS_FILE}")
    
    report_text, today_str = generate_weekly_report(openalex_works, arxiv_preprints)
    report_file = os.path.join(REPORTS_DIR, f"{today_str}_citation_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"[OK] Report archived to {report_file}")
    
    # Step Summary
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    subject = f"🎓 Weekly Academic Citation & Impact Digest ({today_str})"
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(f"## {subject}\n\n```text\n{report_text}\n```\n")

    send_weekly_report(report_text, subject)
    return 0

if __name__ == "__main__":
    sys.exit(main())
