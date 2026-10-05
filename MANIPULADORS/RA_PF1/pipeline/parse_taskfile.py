#!/usr/bin/env python3
"""Parse a task XML file into a sequential list of steps."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List


def _parse_conf_text(text: str) -> List[float]:
    parts = text.split()
    values = [float(value) for value in parts]
    # UR3 joint positions are entries 10..15 (1-based) in this task format.
    if len(values) >= 15:
        return values[9:15]
    return values


def parse_task_file(file_path: str) -> List[Dict[str, Any]]:
    path = Path(file_path).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    tree = ET.parse(path)
    root = tree.getroot()

    sequence: List[Dict[str, Any]] = []
    viene_de_transfer = False

    for child in root:
        if child.tag not in {"Transit", "Transfer"}:
            continue

        confs: List[List[float]] = []
        for conf in child.findall("Conf"):
            if conf.text is None:
                continue
            confs.append(_parse_conf_text(conf.text))

        # --- Lógica de decisión de filtrado ---
        aplicar_filtro = False

        if child.tag == "Transfer":
            aplicar_filtro = True
            viene_de_transfer = True
        elif child.tag == "Transit":
            if not viene_de_transfer:
                aplicar_filtro = True
            viene_de_transfer = False

        # --- Aplicación del filtro (10 primeras, 1 de cada 3 intermedias, 5 últimas) ---
        if aplicar_filtro and len(confs) > 15:
            primeras_diez = confs[:3]
            ultimas_cinco = confs[-3:]
            
            # Cambiado a [::3] para tomar una de cada tres
            medio_filtrado = confs[3:-3][::5]
            
            confs = primeras_diez + medio_filtrado + ultimas_cinco
        # ---------------------------------------------------------------------

        sequence.append({"type": child.tag.lower(), "confs": confs})

    return sequence


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse a task XML file into a sequential list of steps."
    )
    parser.add_argument("file", help="Path to the task XML file")
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print output"
    )
    args = parser.parse_args()

    sequence = parse_task_file(args.file)
    if args.pretty:
        output = json.dumps(sequence, indent=2)
    else:
        output = json.dumps(sequence)
    print("sequence = " + output)

    return 0


if __name__ == "__main__":
    sys.exit(main())