"""Regression tests for the reproducible 64-state analysis."""

from __future__ import annotations

import csv
import math
import tempfile
import unittest
from pathlib import Path

from scripts.analyze_phase_shifter import (
    _parse_float,
    load_processed_rows,
    read_cadence_export,
    summarize_metrics,
    wrap_angle_deg,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = REPOSITORY_ROOT / "data" / "raw" / "cadence-exports"


class AngleWrappingTests(unittest.TestCase):
    def test_wraps_to_expected_interval(self) -> None:
        test_cases = {
            -540.0: -180.0,
            -181.0: 179.0,
            -180.0: -180.0,
            0.0: 0.0,
            179.0: 179.0,
            180.0: -180.0,
            540.0: -180.0,
        }
        for input_angle, expected in test_cases.items():
            with self.subTest(input_angle=input_angle):
                self.assertTrue(
                    math.isclose(
                        wrap_angle_deg(input_angle),
                        expected,
                        abs_tol=1e-12,
                    )
                )


class InputValidationTests(unittest.TestCase):
    def test_rejects_non_finite_numeric_values(self) -> None:
        for value in ("NaN", "inf", "-inf"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ValueError,
                    "Non-finite numeric value",
                ):
                    _parse_float(value, context="unit test")

    def test_rejects_duplicate_frequency_columns(self) -> None:
        source = DATA_DIRECTORY / "phase_shifter_s21_phase_deg.csv"
        with source.open("r", encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.reader(stream))

        frequency_columns = []
        for index, value in enumerate(rows[1]):
            try:
                float(value)
            except ValueError:
                continue
            frequency_columns.append(index)
        self.assertGreaterEqual(len(frequency_columns), 2)
        rows[1][frequency_columns[1]] = rows[1][frequency_columns[0]]

        with tempfile.TemporaryDirectory() as temporary_directory:
            duplicate_path = Path(temporary_directory) / "duplicate.csv"
            with duplicate_path.open(
                "w",
                encoding="utf-8",
                newline="",
            ) as stream:
                csv.writer(stream).writerows(rows)

            with self.assertRaisesRegex(ValueError, "Duplicate frequency"):
                read_cadence_export(duplicate_path)


class DatasetRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = load_processed_rows(DATA_DIRECTORY)
        cls.summaries = summarize_metrics(cls.rows)

    def test_contains_all_state_frequency_pairs(self) -> None:
        self.assertEqual(len(self.rows), 192)
        self.assertEqual(
            {int(row["state_index"]) for row in self.rows},
            set(range(64)),
        )
        self.assertEqual(
            {float(row["frequency_ghz"]) for row in self.rows},
            {9.0, 10.0, 11.0},
        )

    def test_center_frequency_metrics_match_raw_exports(self) -> None:
        center = next(
            summary
            for summary in self.summaries
            if summary["scope"] == "frequency"
            and summary["frequency_ghz"] == 10.0
        )
        self.assertAlmostEqual(
            float(center["phase_rms_offset_removed_deg"]),
            2.276,
            places=3,
        )
        self.assertAlmostEqual(
            float(center["insertion_loss_mean_db"]),
            15.722,
            places=3,
        )
        self.assertAlmostEqual(
            float(center["return_loss_mean_db"]),
            9.462,
            places=3,
        )

    def test_aggregate_metrics_match_independent_recalculation(self) -> None:
        aggregate = next(
            summary
            for summary in self.summaries
            if summary["scope"] == "aggregate"
        )
        self.assertIsNone(aggregate["frequency_ghz"])
        self.assertEqual(aggregate["frequency_start_ghz"], 9.0)
        self.assertEqual(aggregate["frequency_stop_ghz"], 11.0)
        self.assertAlmostEqual(
            float(aggregate["phase_rms_offset_removed_deg"]),
            3.671,
            places=3,
        )
        self.assertAlmostEqual(
            float(aggregate["insertion_loss_rms_db"]),
            1.729,
            places=3,
        )
        self.assertAlmostEqual(
            float(aggregate["return_loss_min_db"]),
            5.482,
            places=3,
        )


if __name__ == "__main__":
    unittest.main()
