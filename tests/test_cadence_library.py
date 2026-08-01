"""Regression tests for the preserved Cadence OpenAccess source library."""

import unittest

from scripts.verify_cadence_library import REQUIRED_VIEWS, read_manifest, verify_library


class CadenceLibraryTests(unittest.TestCase):
    def test_library_matches_integrity_manifest(self) -> None:
        self.assertEqual(verify_library(), [])

    def test_required_views_are_manifested(self) -> None:
        manifest_paths = set(read_manifest())
        self.assertTrue(REQUIRED_VIEWS.issubset(manifest_paths))


if __name__ == "__main__":
    unittest.main()
