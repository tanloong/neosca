#!/usr/bin/env python3

import json
from pathlib import Path

acks_path = Path(__file__).parent.parent.absolute() / "data" / "acks.json"
with open(acks_path, encoding="utf-8") as f:
    acks = json.load(f)

filepath = "../ACKNOWLEDGMENTS.md"
with open(filepath, "w", encoding="utf-8") as f:
    title = "# Acknowledgments\n\n"
    thanks = """NeoSCA is greatly indebted to the open source projects below without which it could never have been possible. As the project is a fork of L2SCA and LCA, I want to express my sincere gratitude to the original author Xiaofei Lu (陆小飞) for his expertise and efforts, and I am grateful for the opportunity to build upon his work.\n\n"""
    header = "||Name|Version|Authors|License|\n"
    separator = "|-|-|:-:|-|:-:|\n"
    f.writelines((title, thanks, header, separator))

    for i, ack in enumerate(acks, start=1):
        cols = (
            str(i),
            f"<a href='{ack['homepage']}'>{ack['name']}</a>",
            ack["version"],
            ack["authors"],
            f"<a href='{ack['license_file']}'>{ack['license']}</a>"
            if ack["license_file"]
            else f"{ack['license']}",
        )
        f.write(f"|{'|'.join(cols)}|\n")
