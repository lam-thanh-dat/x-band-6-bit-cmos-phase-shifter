#!/usr/bin/env python3
"""Validate the included Cadence OpenAccess design library and its checksums."""

from __future__ import annotations

import hashlib
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CADENCE_ROOT = REPOSITORY_ROOT / "cadence"
LIBRARY_ROOT = CADENCE_ROOT / "phase_shift"
MANIFEST_PATH = CADENCE_ROOT / "SHA256SUMS"

REQUIRED_VIEWS = {
    "phase_shift/bit5625/schematic/sch.oa",
    "phase_shift/bit1125/schematic/sch.oa",
    "phase_shift/bit225/schematic/sch.oa",
    "phase_shift/bit45/schematic/sch.oa",
    "phase_shift/bit90/schematic/sch.oa",
    "phase_shift/bit180/schematic/sch.oa",
    "phase_shift/nmos/schematic/sch.oa",
    "phase_shift/phase_shift/schematic/sch.oa",
    "phase_shift/phase_shift/layout/layout.oa",
}


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of *path* without altering its bytes."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(path: Path = MANIFEST_PATH) -> dict[str, str]:
    """Read a conventional SHA256SUMS file keyed by Cadence-relative path."""

    entries: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            digest, relative_path = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"Malformed manifest line {line_number}: {line!r}") from exc
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError(f"Invalid SHA-256 digest on line {line_number}")
        if relative_path in entries:
            raise ValueError(f"Duplicate manifest path: {relative_path}")
        entries[relative_path] = digest
    return entries


def verify_library() -> list[str]:
    """Return validation errors; an empty list means the library is intact."""

    errors: list[str] = []
    if not LIBRARY_ROOT.is_dir():
        return [f"Missing Cadence library directory: {LIBRARY_ROOT}"]
    if not MANIFEST_PATH.is_file():
        return [f"Missing checksum manifest: {MANIFEST_PATH}"]

    try:
        manifest = read_manifest()
    except ValueError as exc:
        return [str(exc)]

    actual_paths = {
        path.relative_to(CADENCE_ROOT).as_posix()
        for path in LIBRARY_ROOT.rglob("*")
        if path.is_file()
    }
    manifest_paths = set(manifest)

    for relative_path in sorted(REQUIRED_VIEWS - actual_paths):
        errors.append(f"Missing required cell view: {relative_path}")
    for relative_path in sorted(manifest_paths - actual_paths):
        errors.append(f"Manifest entry is missing from the library: {relative_path}")
    for relative_path in sorted(actual_paths - manifest_paths):
        errors.append(f"Untracked design-library file: {relative_path}")

    for relative_path in sorted(actual_paths & manifest_paths):
        actual_digest = sha256(CADENCE_ROOT / relative_path)
        if actual_digest != manifest[relative_path]:
            errors.append(
                f"Checksum mismatch for {relative_path}: "
                f"expected {manifest[relative_path]}, got {actual_digest}"
            )

    return errors


def main() -> int:
    errors = verify_library()
    if errors:
        print("Cadence library validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Cadence library validation passed: "
        f"{len(read_manifest())} files and {len(REQUIRED_VIEWS)} required views verified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
