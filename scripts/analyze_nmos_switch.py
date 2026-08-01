#!/usr/bin/env python3
"""Recalculate NMOS switch quantities from historically reported samples."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Mapping, Sequence


def _finite_float(value: str, *, context: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid numeric value {value!r} in {context}.") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"Non-finite numeric value {value!r} in {context}.")
    return parsed


def load_characterization_summary(
    path: Path,
) -> list[dict[str, float]]:
    """Load the transcribed historical samples and derive switch quantities."""

    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {
            "frequency_ghz",
            "reported_real_z11_on_ohm",
            "reported_imag_y11_off_ms",
        }
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path} is missing required columns.")

        rows: list[dict[str, float]] = []
        frequencies: set[float] = set()
        for row_number, row in enumerate(reader, start=2):
            frequency_ghz = _finite_float(
                row["frequency_ghz"],
                context=f"{path.name}, row {row_number}, frequency",
            )
            if frequency_ghz in frequencies:
                raise ValueError(
                    f"Duplicate frequency {frequency_ghz:g} GHz in {path}."
                )
            frequencies.add(frequency_ghz)

            ron_ohm = _finite_float(
                row["reported_real_z11_on_ohm"],
                context=f"{path.name}, row {row_number}, real Z11",
            )
            imag_y11_ms = _finite_float(
                row["reported_imag_y11_off_ms"],
                context=f"{path.name}, row {row_number}, imaginary Y11",
            )
            frequency_hz = frequency_ghz * 1e9
            susceptance_s = imag_y11_ms * 1e-3
            coff_f = susceptance_s / (2.0 * math.pi * frequency_hz)
            rows.append(
                {
                    "frequency_ghz": frequency_ghz,
                    "ron_ohm": ron_ohm,
                    "imag_y11_off_ms": imag_y11_ms,
                    "coff_ff": coff_f * 1e15,
                    "off_state_reactance_ohm": 1.0
                    / (2.0 * math.pi * frequency_hz * coff_f),
                }
            )

    if frequencies != {9.0, 10.0, 11.0}:
        raise ValueError(
            f"{path} must contain the reported 9, 10, and 11 GHz samples."
        )
    return sorted(rows, key=lambda row: row["frequency_ghz"])


def write_processed_summary(
    rows: Sequence[Mapping[str, float]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_arguments() -> argparse.Namespace:
    repository_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=repository_root
        / "data"
        / "reference"
        / "historical_nmos_characterization.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repository_root
        / "data"
        / "processed"
        / "nmos_switch_characterization.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    rows = load_characterization_summary(args.input)
    write_processed_summary(rows, args.output)
    print(
        "Recalculated NMOS quantities from three historically reported "
        f"samples and wrote {args.output}."
    )


if __name__ == "__main__":
    main()
