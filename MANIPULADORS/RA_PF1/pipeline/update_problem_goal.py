#!/usr/bin/env python3
"""Update the init block of the batteryreplacer problem based on exact position states."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

FILE_PATH = (
    Path.cwd()
    / "RA_PF1"
    / "battery_replacer"
    / "ff-domains"
    / "manipulation_problem_bateries"
)

INIT_START_RE = re.compile(r"^\s*\(:init\s*$")


def update_problem(pos1_status: str, pos2_status: str) -> None:
    text = FILE_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()

    output_lines = []
    in_init = False

    for line in lines:
        if INIT_START_RE.match(line):
            in_init = True
            output_lines.append(line)
            
            # Dynamically reconstruct the internal facts of the (:init) block
            indent = "    "
            
            # --- Handle pos1 & bat1 ---
            if pos1_status == "good":
                output_lines.append(f"{indent}(in bat1 pos1)")
                output_lines.append(f"{indent}(not (clear pos1))")

            elif pos1_status == "defective":
                output_lines.append(f"{indent}(in bat1 pos1)")
                output_lines.append(f"{indent}(consumed bat1)")
                output_lines.append(f"{indent}(not (clear pos1))")
            elif pos1_status == "unknown":
                output_lines.append(f"{indent}(clear pos1)")

            # --- Handle pos2 & bat2 ---
            if pos2_status == "good":
                output_lines.append(f"{indent}(in bat2 pos2)")
                output_lines.append(f"{indent}(not (clear pos2))")
            elif pos2_status == "defective":
                output_lines.append(f"{indent}(in bat2 pos2)")
                output_lines.append(f"{indent}(consumed bat2)")
                output_lines.append(f"{indent}(not (clear pos2))")
            elif pos2_status == "unknown":
                output_lines.append(f"{indent}(clear pos2)")

            # --- Standard elements that always persist ---
            output_lines.append(f"{indent}(in bat3 buffer)")
            output_lines.append(f"{indent}(in bat4 buffer)")
            output_lines.append(f"{indent}(handEmpty ur3a)")
            output_lines.append(f"{indent}(is-graveyard graveyard)")
            continue

        if in_init:
            # Skip all original lines inside the old init block until we hit the closing parenthesis
            if line.strip() == ")":
                in_init = False
                output_lines.append(line)
            continue

        output_lines.append(line)

    FILE_PATH.write_text("\n".join(output_lines) + "\n", encoding="utf-8")