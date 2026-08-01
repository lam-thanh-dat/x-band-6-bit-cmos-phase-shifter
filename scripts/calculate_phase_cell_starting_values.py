#!/usr/bin/env python3
"""Calculate first-order component values for the six phase-cell topologies."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Iterable


def calculate_starting_values(
    *,
    center_frequency_hz: float = 10e9,
    reference_impedance_ohm: float = 50.0,
) -> list[dict[str, float | str]]:
    """Return the analytical starting values in SI units."""

    if not math.isfinite(center_frequency_hz) or center_frequency_hz <= 0:
        raise ValueError("Center frequency must be finite and positive.")
    if (
        not math.isfinite(reference_impedance_ohm)
        or reference_impedance_ohm <= 0
    ):
        raise ValueError("Reference impedance must be finite and positive.")

    omega = 2.0 * math.pi * center_frequency_hz
    rows: list[dict[str, float | str]] = []

    def add(
        phase_increment_deg: float,
        topology: str,
        parameter: str,
        value_si: float,
        si_unit: str,
    ) -> None:
        rows.append(
            {
                "phase_increment_deg": phase_increment_deg,
                "topology": topology,
                "parameter": parameter,
                "value_si": value_si,
                "si_unit": si_unit,
            }
        )

    for phase_deg in (5.625, 11.25, 22.5):
        phase_rad = math.radians(phase_deg)
        tangent = math.tan(phase_rad / 2.0)
        topology = "switched_low_pass_band_pass_t"
        add(
            phase_deg,
            topology,
            "L1",
            2.0 * reference_impedance_ohm * tangent / omega,
            "H",
        )
        add(
            phase_deg,
            topology,
            "C1",
            1.0 / (2.0 * omega * reference_impedance_ohm * tangent),
            "F",
        )
        add(
            phase_deg,
            topology,
            "L2",
            reference_impedance_ohm * tangent / omega,
            "H",
        )
        add(
            phase_deg,
            topology,
            "C2",
            math.sin(phase_rad) / (omega * reference_impedance_ohm),
            "F",
        )

    for phase_deg in (45.0, 90.0):
        phase_rad = math.radians(phase_deg)
        topology = "bridged_t"
        l1 = (
            reference_impedance_ohm
            * math.tan(phase_rad / 2.0)
            / omega
        )
        coff2 = math.sin(phase_rad) / (
            omega * reference_impedance_ohm
        )
        coff3 = 2.0 * l1 / reference_impedance_ohm**2
        l2 = 1.0 / (omega**2 * coff3)
        add(phase_deg, topology, "L1", l1, "H")
        add(phase_deg, topology, "Coff2_ideal", coff2, "F")
        add(phase_deg, topology, "Coff3_ideal", coff3, "F")
        add(phase_deg, topology, "L2", l2, "H")

    branch_phase_rad = math.radians(90.0)
    l_branch = (
        reference_impedance_ohm
        * (1.0 - math.cos(branch_phase_rad))
        / (omega * math.sin(branch_phase_rad))
    )
    c_branch = 1.0 / (
        omega * reference_impedance_ohm * math.sin(branch_phase_rad)
    )
    topology = "parallel_high_pass_low_pass"
    add(180.0, topology, "L_low_pass_1", l_branch, "H")
    add(180.0, topology, "L_low_pass_2", l_branch, "H")
    add(180.0, topology, "C_low_pass", c_branch, "F")
    add(180.0, topology, "L_high_pass", l_branch, "H")
    add(180.0, topology, "C_high_pass_1", c_branch, "F")
    add(180.0, topology, "C_high_pass_2", c_branch, "F")

    return rows


def write_csv(
    rows: Iterable[dict[str, float | str]],
    output_path: Path,
) -> None:
    rows = list(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "phase_increment_deg",
                "topology",
                "parameter",
                "value_si",
                "si_unit",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_arguments() -> argparse.Namespace:
    repository_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center-frequency-ghz", type=float, default=10.0)
    parser.add_argument("--reference-impedance-ohm", type=float, default=50.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=repository_root
        / "results"
        / "phase_cell_starting_values.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    rows = calculate_starting_values(
        center_frequency_hz=args.center_frequency_ghz * 1e9,
        reference_impedance_ohm=args.reference_impedance_ohm,
    )
    write_csv(rows, args.output)
    print(f"Wrote {len(rows)} analytical component values to {args.output}.")


if __name__ == "__main__":
    main()
