#!/usr/bin/env python3

import json
from pathlib import Path

PKG_DIR = Path(__file__).parent.parent.absolute()
acks_path = PKG_DIR / "src" / "neosca" / "ns_data" / "acks.json"
with open(acks_path, encoding="utf-8") as f:
    ack_data = json.load(f)
acknowledgment, projects = ack_data.values()

filepath = PKG_DIR / "ACKNOWLEDGMENTS.md"
with open(filepath, "w", encoding="utf-8") as f:
    title = "# Acknowledgments\n\n"
    header = "||Name|Version|Authors|License|\n"
    separator = "|-|-|:-:|-|:-:|\n"
    f.writelines((title, f"{acknowledgment}\n\n", header, separator))

    for i, project in enumerate(projects, start=1):
        cols = (
            str(i),
            f"<a href='{project['homepage']}'>{project['name']}</a>",
            project["version"],
            project["authors"],
            f"<a href='{project['license_file']}'>{project['license']}</a>"
            if project["license_file"]
            else f"{project['license']}",
        )
        f.write(f"|{'|'.join(cols)}|\n")
