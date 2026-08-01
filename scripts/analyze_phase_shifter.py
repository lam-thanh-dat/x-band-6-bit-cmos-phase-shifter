#!/usr/bin/env python3
"""Analyze 64-state Cadence exports for the 6-bit X-band phase shifter.

The script converts the original wide Cadence CSV exports into a tidy dataset,
computes phase, insertion-loss, and return-loss statistics, and optionally
generates publication-ready plots.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


PHASE_FILE = "phase_shifter_s21_phase_deg.csv"
INSERTION_LOSS_FILE = "phase_shifter_s21_magnitude_db.csv"
RETURN_LOSS_FILE = "phase_shifter_s11_magnitude_db.csv"

BIT_ANGLES_DEG: tuple[float, ...] = (5.625, 11.25, 22.5, 45.0, 90.0, 180.0)
CONTROL_COLUMN_TO_ANGLE: Mapping[str, float] = {
    "V_ctrl5625": 5.625,
    "V_ctrl1125": 11.25,
    "V_ctrl225": 22.5,
    "V_ctrl45": 45.0,
    "V_ctrl90": 90.0,
    "V_ctrl180": 180.0,
}


@dataclass(frozen=True)
class CadenceState:
    """One control state and its simulated values at each frequency."""

    state_index: int
    controls: Mapping[float, int]
    values_by_frequency_ghz: Mapping[float, float]

    @property
    def ideal_phase_deg(self) -> float:
        """Return the ideal binary-weighted phase for this control state."""

        return sum(
            angle * self.controls[angle]
            for angle in BIT_ANGLES_DEG
        )


def _parse_float(value: str, *, context: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid numeric value {value!r} in {context}.") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"Non-finite numeric value {value!r} in {context}.")
    return parsed


def _control_to_bit(value: str, *, context: str) -> int:
    voltage = _parse_float(value, context=context)
    if math.isclose(voltage, 0.0, abs_tol=1e-9):
        return 0
    if math.isclose(voltage, 1.8, abs_tol=1e-9):
        return 1
    raise ValueError(
        f"Expected a control voltage of 0 or 1.8 V in {context}; "
        f"received {voltage} V."
    )


def wrap_angle_deg(angle_deg: float) -> float:
    """Wrap an angle to the half-open interval [-180, 180) degrees."""

    return (angle_deg + 180.0) % 360.0 - 180.0


def read_cadence_export(path: Path) -> dict[int, CadenceState]:
    """Read one native Cadence CSV export and validate all 64 states."""

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream))

    if len(rows) < 4:
        raise ValueError(f"{path} does not contain the expected header and data.")

    header = rows[0]
    frequency_row = rows[1]
    if len(header) != len(frequency_row):
        raise ValueError(f"Header width mismatch in {path}.")

    control_indices: dict[float, int] = {}
    for column_name, angle_deg in CONTROL_COLUMN_TO_ANGLE.items():
        try:
            control_indices[angle_deg] = header.index(column_name)
        except ValueError as exc:
            raise ValueError(
                f"Required control column {column_name!r} is missing from {path}."
            ) from exc

    frequency_indices: dict[float, int] = {}
    for index, raw_frequency in enumerate(frequency_row):
        if not raw_frequency.strip():
            continue
        try:
            frequency_hz = float(raw_frequency)
        except ValueError:
            continue
        if not math.isfinite(frequency_hz):
            raise ValueError(
                f"Non-finite frequency {raw_frequency!r} in {path}."
            )
        frequency_ghz = frequency_hz / 1e9
        if frequency_ghz in frequency_indices:
            raise ValueError(
                f"Duplicate frequency {frequency_ghz:g} GHz in {path}."
            )
        frequency_indices[frequency_ghz] = index

    expected_frequencies = {9.0, 10.0, 11.0}
    if set(frequency_indices) != expected_frequencies:
        raise ValueError(
            f"{path} must contain 9, 10, and 11 GHz data; "
            f"found {sorted(frequency_indices)} GHz."
        )

    states: dict[int, CadenceState] = {}
    for row_number, row in enumerate(rows[3:], start=4):
        if not row or not any(cell.strip() for cell in row):
            continue
        if len(row) != len(header):
            raise ValueError(
                f"Row {row_number} in {path} has {len(row)} columns; "
                f"expected {len(header)}."
            )

        controls = {
            angle_deg: _control_to_bit(
                row[column_index],
                context=f"{path.name}, row {row_number}, {angle_deg:g}-degree bit",
            )
            for angle_deg, column_index in control_indices.items()
        }
        state_index = round(
            sum(
                controls[angle_deg] * angle_deg / BIT_ANGLES_DEG[0]
                for angle_deg in BIT_ANGLES_DEG
            )
        )
        values_by_frequency = {
            frequency_ghz: _parse_float(
                row[column_index],
                context=(
                    f"{path.name}, row {row_number}, "
                    f"{frequency_ghz:g} GHz"
                ),
            )
            for frequency_ghz, column_index in frequency_indices.items()
        }

        if state_index in states:
            raise ValueError(f"Duplicate state index {state_index} in {path}.")
        states[state_index] = CadenceState(
            state_index=state_index,
            controls=controls,
            values_by_frequency_ghz=values_by_frequency,
        )

    expected_states = set(range(64))
    if set(states) != expected_states:
        missing = sorted(expected_states - set(states))
        unexpected = sorted(set(states) - expected_states)
        raise ValueError(
            f"{path} does not contain exactly states 0-63. "
            f"Missing: {missing}; unexpected: {unexpected}."
        )

    return states


def load_processed_rows(data_dir: Path) -> list[dict[str, float | int]]:
    """Load and merge the three raw exports into a tidy 192-row dataset."""

    phase_states = read_cadence_export(data_dir / PHASE_FILE)
    insertion_states = read_cadence_export(data_dir / INSERTION_LOSS_FILE)
    return_states = read_cadence_export(data_dir / RETURN_LOSS_FILE)

    for state_index in range(64):
        expected_controls = phase_states[state_index].controls
        if insertion_states[state_index].controls != expected_controls:
            raise ValueError(
                f"Control mismatch in insertion-loss data for state {state_index}."
            )
        if return_states[state_index].controls != expected_controls:
            raise ValueError(
                f"Control mismatch in return-loss data for state {state_index}."
            )

    phase_reference = {
        frequency_ghz: phase_states[0].values_by_frequency_ghz[frequency_ghz]
        for frequency_ghz in (9.0, 10.0, 11.0)
    }

    processed_rows: list[dict[str, float | int]] = []
    for state_index in range(64):
        phase_state = phase_states[state_index]
        for frequency_ghz in (9.0, 10.0, 11.0):
            relative_phase = wrap_angle_deg(
                phase_state.values_by_frequency_ghz[frequency_ghz]
                - phase_reference[frequency_ghz]
            )
            phase_error = wrap_angle_deg(
                relative_phase - phase_state.ideal_phase_deg
            )
            processed_rows.append(
                {
                    "state_index": state_index,
                    "ideal_phase_deg": phase_state.ideal_phase_deg,
                    "control_5p625_deg": phase_state.controls[5.625],
                    "control_11p25_deg": phase_state.controls[11.25],
                    "control_22p5_deg": phase_state.controls[22.5],
                    "control_45_deg": phase_state.controls[45.0],
                    "control_90_deg": phase_state.controls[90.0],
                    "control_180_deg": phase_state.controls[180.0],
                    "frequency_ghz": frequency_ghz,
                    "s21_phase_deg": (
                        phase_state.values_by_frequency_ghz[frequency_ghz]
                    ),
                    "relative_phase_deg": relative_phase,
                    "phase_error_deg": phase_error,
                    "insertion_loss_db": -insertion_states[
                        state_index
                    ].values_by_frequency_ghz[frequency_ghz],
                    "return_loss_db": -return_states[
                        state_index
                    ].values_by_frequency_ghz[frequency_ghz],
                }
            )

    return processed_rows


def _root_mean_square(values: Sequence[float]) -> float:
    return math.sqrt(statistics.fmean(value * value for value in values))


def _metric_summary(
    rows: Sequence[Mapping[str, float | int]],
    *,
    scope: str,
    frequency_ghz: float | None,
    frequency_start_ghz: float,
    frequency_stop_ghz: float,
) -> dict[str, float | str | None]:
    phase_errors = [float(row["phase_error_deg"]) for row in rows]
    insertion_losses = [float(row["insertion_loss_db"]) for row in rows]
    return_losses = [float(row["return_loss_db"]) for row in rows]

    return {
        "scope": scope,
        "frequency_ghz": frequency_ghz,
        "frequency_start_ghz": frequency_start_ghz,
        "frequency_stop_ghz": frequency_stop_ghz,
        "phase_mean_error_deg": statistics.fmean(phase_errors),
        "phase_rms_offset_removed_deg": statistics.pstdev(phase_errors),
        "phase_rms_total_deg": _root_mean_square(phase_errors),
        "insertion_loss_mean_db": statistics.fmean(insertion_losses),
        "insertion_loss_rms_db": statistics.pstdev(insertion_losses),
        "insertion_loss_min_db": min(insertion_losses),
        "insertion_loss_max_db": max(insertion_losses),
        "return_loss_mean_db": statistics.fmean(return_losses),
        "return_loss_rms_db": statistics.pstdev(return_losses),
        "return_loss_min_db": min(return_losses),
        "return_loss_max_db": max(return_losses),
    }


def summarize_metrics(
    rows: Sequence[Mapping[str, float | int]],
) -> list[dict[str, float | str | None]]:
    """Compute per-frequency and aggregate metrics using population RMS."""

    summaries = []
    for frequency_ghz in (9.0, 10.0, 11.0):
        frequency_rows = [
            row
            for row in rows
            if math.isclose(
                float(row["frequency_ghz"]),
                frequency_ghz,
                abs_tol=1e-9,
            )
        ]
        if len(frequency_rows) != 64:
            raise ValueError(
                f"Expected 64 rows at {frequency_ghz:g} GHz; "
                f"found {len(frequency_rows)}."
            )
        summaries.append(
            _metric_summary(
                frequency_rows,
                scope="frequency",
                frequency_ghz=frequency_ghz,
                frequency_start_ghz=frequency_ghz,
                frequency_stop_ghz=frequency_ghz,
            )
        )

    if len(rows) != 192:
        raise ValueError(f"Expected 192 total state-frequency rows; found {len(rows)}.")
    summaries.append(
        _metric_summary(
            rows,
            scope="aggregate",
            frequency_ghz=None,
            frequency_start_ghz=9.0,
            frequency_stop_ghz=11.0,
        )
    )
    return summaries


def write_tidy_csv(
    rows: Sequence[Mapping[str, float | int]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_summary_files(
    summaries: Sequence[Mapping[str, float | str | None]],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fieldnames = list(summaries[0])

    with (output_dir / "phase_shifter_performance_metrics.csv").open(
        "w",
        encoding="utf-8",
        newline="",
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(summaries)

    with (output_dir / "phase_shifter_performance_metrics.json").open(
        "w",
        encoding="utf-8",
    ) as stream:
        json.dump(summaries, stream, indent=2, allow_nan=False)
        stream.write("\n")


def _rows_at_frequency(
    rows: Iterable[Mapping[str, float | int]],
    frequency_ghz: float,
) -> list[Mapping[str, float | int]]:
    return sorted(
        (
            row
            for row in rows
            if math.isclose(
                float(row["frequency_ghz"]),
                frequency_ghz,
                abs_tol=1e-9,
            )
        ),
        key=lambda row: int(row["state_index"]),
    )


def generate_plots(
    rows: Sequence[Mapping[str, float | int]],
    output_dir: Path,
) -> None:
    """Generate standalone figures and a publication-quality overview."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    colors = {9.0: "#1f77b4", 10.0: "#d62728", 11.0: "#2ca02c"}

    plot_definitions = (
        (
            "phase_error_deg",
            "Phase error (degrees)",
            "Phase Error Across 64 Control States",
            "phase_shifter_phase_error_by_state.png",
        ),
        (
            "insertion_loss_db",
            "Insertion loss (dB)",
            "Insertion Loss Across 64 Control States",
            "phase_shifter_insertion_loss_by_state.png",
        ),
        (
            "return_loss_db",
            "Return loss (dB)",
            "Input Return Loss Across 64 Control States",
            "phase_shifter_input_return_loss_by_state.png",
        ),
    )

    for field_name, y_label, title, filename in plot_definitions:
        figure, axis = plt.subplots(figsize=(8.0, 4.6), constrained_layout=True)
        for frequency_ghz in (9.0, 10.0, 11.0):
            frequency_rows = _rows_at_frequency(rows, frequency_ghz)
            axis.plot(
                [int(row["state_index"]) for row in frequency_rows],
                [float(row[field_name]) for row in frequency_rows],
                color=colors[frequency_ghz],
                linewidth=1.4,
                marker="o",
                markersize=2.5,
                label=f"{frequency_ghz:g} GHz",
            )

        axis.set_title(title)
        axis.set_xlabel("State index")
        axis.set_ylabel(y_label)
        axis.set_xlim(0, 63)
        axis.grid(True, color="#d9d9d9", linewidth=0.7, alpha=0.8)
        axis.legend(frameon=False, ncols=3)

        if field_name == "phase_error_deg":
            axis.axhline(0.0, color="#404040", linewidth=0.9)
        elif field_name == "return_loss_db":
            axis.axhline(
                10.0,
                color="#7f7f7f",
                linewidth=1.0,
                linestyle="--",
                label="10 dB reference",
            )
            axis.legend(frameon=False, ncols=2)

        figure.savefig(output_dir / filename, dpi=220)
        plt.close(figure)

    # A compact, publication-oriented overview with fixed point-size text.
    # Distinct line styles and markers preserve legibility in grayscale.
    figure, axes = plt.subplots(
        1,
        3,
        figsize=(7.16, 2.25),
        constrained_layout=True,
    )
    line_styles = {
        9.0: ("-", "o"),
        10.0: ("--", "s"),
        11.0: ("-.", "^"),
    }
    panel_definitions = (
        (
            "phase_error_deg",
            "Centered phase error (deg)",
            "(a) Phase accuracy",
        ),
        (
            "insertion_loss_db",
            "Insertion loss (dB)",
            "(b) Transmission loss",
        ),
        (
            "return_loss_db",
            "Input return loss (dB)",
            "(c) Input matching",
        ),
    )

    for axis, (field_name, y_label, title) in zip(
        axes,
        panel_definitions,
        strict=True,
    ):
        for frequency_ghz in (9.0, 10.0, 11.0):
            frequency_rows = _rows_at_frequency(rows, frequency_ghz)
            values = [float(row[field_name]) for row in frequency_rows]
            if field_name == "phase_error_deg":
                mean_error = statistics.fmean(values)
                values = [value - mean_error for value in values]

            line_style, marker = line_styles[frequency_ghz]
            axis.plot(
                [int(row["state_index"]) for row in frequency_rows],
                values,
                color=colors[frequency_ghz],
                linestyle=line_style,
                linewidth=0.9,
                marker=marker,
                markersize=1.7,
                markevery=4,
                label=f"{frequency_ghz:g} GHz",
            )

        axis.set_title(title, fontsize=8.0)
        axis.set_xlabel("State index", fontsize=7.2)
        axis.set_ylabel(y_label, fontsize=7.2)
        axis.set_xlim(0, 63)
        axis.tick_params(axis="both", labelsize=6.5, pad=1.5)
        axis.grid(True, color="#d9d9d9", linewidth=0.45, alpha=0.8)

        if field_name == "phase_error_deg":
            axis.axhline(0.0, color="#404040", linewidth=0.7)
            axis.legend(
                frameon=False,
                fontsize=6.2,
                ncols=1,
                handlelength=1.8,
            )
        elif field_name == "return_loss_db":
            axis.axhline(
                10.0,
                color="#505050",
                linewidth=0.7,
                linestyle=":",
            )

    figure.savefig(
        output_dir / "phase_shifter_performance_overview.png",
        dpi=300,
        facecolor="white",
    )
    plt.close(figure)


def print_summary(
    summaries: Sequence[Mapping[str, float | str | None]],
) -> None:
    header = (
        "Frequency | Phase offset | Phase RMS | Mean IL | IL RMS | "
        "Mean RL | Minimum RL"
    )
    print(header)
    print("-" * len(header))
    for summary in summaries:
        if summary["scope"] == "frequency":
            frequency = f"{float(summary['frequency_ghz']):g} GHz"
        else:
            frequency = (
                f"{float(summary['frequency_start_ghz']):g}-"
                f"{float(summary['frequency_stop_ghz']):g} GHz aggregate"
            )
        print(
            f"{frequency:>20} | "
            f"{float(summary['phase_mean_error_deg']):>+11.3f} deg | "
            f"{float(summary['phase_rms_offset_removed_deg']):>8.3f} deg | "
            f"{float(summary['insertion_loss_mean_db']):>7.3f} dB | "
            f"{float(summary['insertion_loss_rms_db']):>6.3f} dB | "
            f"{float(summary['return_loss_mean_db']):>7.3f} dB | "
            f"{float(summary['return_loss_min_db']):>10.3f} dB"
        )


def parse_arguments() -> argparse.Namespace:
    repository_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=repository_root / "data" / "raw" / "cadence-exports",
        help="Directory containing the three renamed raw Cadence CSV exports.",
    )
    parser.add_argument(
        "--processed-data",
        type=Path,
        default=(
            repository_root
            / "data"
            / "processed"
            / "phase_shifter_64_states.csv"
        ),
        help="Destination for the tidy state-frequency dataset.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repository_root / "results",
        help="Destination for summary tables and plots.",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip figure generation; only Python's standard library is then needed.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    processed_rows = load_processed_rows(args.data_dir)
    summaries = summarize_metrics(processed_rows)
    write_tidy_csv(processed_rows, args.processed_data)
    write_summary_files(summaries, args.output_dir)
    if not args.no_plots:
        generate_plots(processed_rows, args.output_dir)
    print_summary(summaries)


if __name__ == "__main__":
    main()
