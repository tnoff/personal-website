#!/usr/bin/env python3
"""Generate Hugo content files from Tyler_North_CV.yaml."""

import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

YAML_FILE = Path("Tyler_North_CV.yaml")
RESUME_OUT = Path("hugo-site/content/resume.html")
PROJECTS_OUT = Path("hugo-site/content/projects.html")
PDF_SRC = Path("rendercv_output/Tyler_Daniel_North_CV.pdf")
PDF_DST = Path("hugo-site/static/Tyler_Daniel_North_CV.pdf")

MONTHS = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December",
}

AUTO_COMMENT = "<!-- AUTO-GENERATED from Tyler_North_CV.yaml — do not edit directly -->\n"


def fmt_date(d):
    if not d:
        return ""
    d = str(d)
    if d == "present":
        return "present"
    parts = d.split("-")
    if len(parts) >= 2:
        return f"{MONTHS.get(parts[1], parts[1])} {parts[0]}"
    return d


def parse_markdown_link(text):
    """Return (display_text, url) from '[text](url)', or (text, None)."""
    m = re.match(r'^\[(.+?)\]\((.+?)\)$', text.strip())
    if m:
        return m.group(1), m.group(2)
    return text, None


def generate_resume(cv):
    lines = [AUTO_COMMENT]
    lines.append('<h1 class="header" align="center">My Resume</h1>\n')
    lines.append('<p align="center"><a href="/Tyler_Daniel_North_CV.pdf" download>Download PDF</a></p>\n\n')

    # Skills
    lines.append('<h2 class="header">Skills</h2>\n<hr>\n<ul>\n')
    for skill in cv["sections"].get("skills", []):
        label = html.escape(skill["label"])
        details = html.escape(skill["details"])
        lines.append(f'    <li><b>{label}:</b> {details}</li>\n')
    lines.append('</ul>\n\n')

    # Experience — group consecutive entries with the same company under one h3
    lines.append('<h2 class="header">Work Experience</h2>\n<hr>\n')
    prev_company = None
    for exp in cv["sections"].get("experience", []):
        company = exp["company"]
        position = html.escape(exp["position"])
        start = fmt_date(exp.get("start_date") or "")
        end = fmt_date(exp.get("end_date") or "")
        date_str = f"{start} to {end}" if start else ""

        if company != prev_company:
            lines.append(f'<h3>{html.escape(company)}</h3>\n')
            prev_company = company

        lines.append(f'<h5>{position} - {date_str}</h5>\n')
        highlights = exp.get("highlights") or []
        if highlights:
            lines.append('<ul>\n')
            for h in highlights:
                lines.append(f'    <li>{html.escape(h)}</li>\n')
            lines.append('</ul>\n')

    lines.append('\n')

    # Education
    lines.append('<h2 class="header">Education</h2>\n<hr>\n')
    for edu in cv["sections"].get("education", []):
        institution = html.escape(edu["institution"])
        degree = html.escape(edu.get("degree") or "")
        area = html.escape(edu.get("area") or "")
        start = fmt_date(edu.get("start_date") or "")
        end = fmt_date(edu.get("end_date") or "")
        lines.append(f'<h3>{institution}</h3>\n')
        lines.append(f'<h5>{degree} in {area} - {start} to {end}</h5>\n')
        highlights = edu.get("highlights") or []
        if highlights:
            lines.append('<ul>\n')
            for h in highlights:
                lines.append(f'    <li>{html.escape(h)}</li>\n')
            lines.append('</ul>\n')

    lines.append('\n')
    return "".join(lines)


def generate_projects(cv):
    lines = [AUTO_COMMENT]
    lines.append('<h1 class="header" align="center">Coding Projects</h1>\n\n')

    for proj in cv["sections"].get("projects", []):
        display, url = parse_markdown_link(proj["name"])
        display = html.escape(display)
        if url:
            lines.append(f'<h2 class="header"><a href="{url}">{display}</a></h2>\n')
        else:
            lines.append(f'<h2 class="header">{display}</h2>\n')

        summary = proj.get("summary") or ""
        if summary:
            lines.append(f'<p>{html.escape(summary)}</p>\n')

        highlights = proj.get("highlights") or []
        if highlights:
            lines.append('<ul>\n')
            for h in highlights:
                lines.append(f'    <li>{html.escape(h)}</li>\n')
            lines.append('</ul>\n')

    return "".join(lines)


def main():
    with open(YAML_FILE) as f:
        data = yaml.safe_load(f)
    cv = data["cv"]

    RESUME_OUT.parent.mkdir(parents=True, exist_ok=True)
    RESUME_OUT.write_text(generate_resume(cv))
    print(f"Written {RESUME_OUT}")

    PROJECTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    PROJECTS_OUT.write_text(generate_projects(cv))
    print(f"Written {PROJECTS_OUT}")

    result = subprocess.run(
        ["rendercv", "render", str(YAML_FILE), "--output-folder", "rendercv_output"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"rendercv failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    print("rendercv completed (with phone, for repo)")

    # Generate a phone-free PDF for the website
    import tempfile
    with open(YAML_FILE) as f:
        cv_data = yaml.safe_load(f)
    cv_data["cv"].pop("phone", None)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_yaml = Path(tmpdir) / YAML_FILE.name
        tmp_yaml.write_text(yaml.dump(cv_data, allow_unicode=True))
        result2 = subprocess.run(
            ["rendercv", "render", str(tmp_yaml), "--output-folder", tmpdir],
            capture_output=True, text=True,
        )
        if result2.returncode != 0:
            print(f"rendercv (no-phone) failed:\n{result2.stderr}", file=sys.stderr)
            sys.exit(1)
        print("rendercv completed (without phone, for website)")
        PDF_DST.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(tmpdir) / PDF_SRC.name, PDF_DST)
        print(f"Copied phone-free PDF to {PDF_DST}")


if __name__ == "__main__":
    main()
