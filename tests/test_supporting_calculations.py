"""Tests for analytical phase-cell values and historical NMOS calculations."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.analyze_nmos_switch import load_characterization_summary
from scripts.calculate_phase_cell_starting_values import (
    calculate_starting_values,
)
from scripts.verify_raw_data_checksums import verify_manifest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class PhaseCellCalculationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = calculate_starting_values()
        cls.values = {
            (float(row["phase_increment_deg"]), str(row["parameter"])): float(
                row["value_si"]
            )
            for row in cls.rows
        }

    def test_small_bit_starting_values(self) -> None:
        self.assertAlmostEqual(
            self.values[(5.625, "L1")] * 1e12,
            78.18781,
            places=5,
        )
        self.assertAlmostEqual(
            self.values[(22.5, "C2")] * 1e15,
            121.81192,
            places=5,
        )

    def test_bridged_t_and_180_degree_values(self) -> None:
        self.assertAlmostEqual(
            self.values[(45.0, "L2")] * 1e12,
            960.58506,
            places=5,
        )
        self.assertAlmostEqual(
            self.values[(90.0, "Coff2_ideal")] * 1e15,
            318.31,
            places=2,
        )
        self.assertAlmostEqual(
            self.values[(180.0, "L_low_pass_1")] * 1e9,
            0.7958,
            places=4,
        )


class HistoricalNmosCalculationTests(unittest.TestCase):
    def test_center_frequency_values(self) -> None:
        input_path = (
            REPOSITORY_ROOT
            / "data"
            / "reference"
            / "historical_nmos_characterization.csv"
        )
        rows = load_characterization_summary(input_path)
        center = next(row for row in rows if row["frequency_ghz"] == 10.0)
        self.assertAlmostEqual(center["ron_ohm"], 3.32681, places=5)
        self.assertAlmostEqual(center["coff_ff"], 57.8003, places=4)
        self.assertAlmostEqual(
            center["off_state_reactance_ohm"],
            275.3531,
            places=4,
        )


class RawDataChecksumTests(unittest.TestCase):
    def test_raw_exports_match_manifest(self) -> None:
        manifest = REPOSITORY_ROOT / "data" / "raw" / "SHA256SUMS"
        self.assertEqual(verify_manifest(manifest), 3)


if __name__ == "__main__":
    unittest.main()
