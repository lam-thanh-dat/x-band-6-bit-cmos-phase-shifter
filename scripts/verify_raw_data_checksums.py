#!/usr/bin/env python3
"""Verify SHA-256 checksums for the preserved native Cadence CSV exports."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def verify_manifest(manifest_path: Path) -> int:
    """Verify every file listed in a conventional SHA256SUMS manifest."""

    verified = 0
    for line_number, raw_line in enumerate(
        manifest_path.read_text(encoding="ascii").splitlines(),
        start=1,
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            expected_hash, relative_name = line.split(maxsplit=1)
        except ValueError as exc:
            raise ValueError(
                f"Malformed checksum line {line_number} in {manifest_path}."
            ) from exc
        relative_name = relative_name.lstrip("*")
        relative_path = Path(relative_name)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(
                f"Unsafe checksum path {relative_name!r} in {manifest_path}."
            )
        if not SHA256_PATTERN.fullmatch(expected_hash):
            raise ValueError(
                f"Invalid SHA-256 value on line {line_number} in {manifest_path}."
            )

        file_path = manifest_path.parent / relative_path
        if not file_path.is_file():
            raise FileNotFoundError(f"Checksum target not found: {file_path}")
        actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(
                f"Checksum mismatch for {relative_name}: "
                f"expected {expected_hash}, found {actual_hash}."
            )
        verified += 1

    if verified == 0:
        raise ValueError(f"No checksum entries found in {manifest_path}.")
    return verified


def parse_arguments() -> argparse.Namespace:
    repository_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=repository_root / "data" / "raw" / "SHA256SUMS",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    verified = verify_manifest(args.manifest)
    print(f"Verified {verified} raw-data files against {args.manifest}.")


if __name__ == "__main__":
    main()
