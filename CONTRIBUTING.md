# Contributing

External contributions are not currently accepted. This document describes
the internal development and validation process used to preserve numerical
traceability to the native Cadence exports.

1. Create a focused branch.
2. Do not commit PDK, model, rule-deck, license, or NDA-controlled files.
3. Keep documentation, filenames, comments, and commit messages in English.
4. Regenerate the processed data and result figures.
5. Run:

   ```bash
   python scripts/verify_cadence_library.py
   python scripts/verify_raw_data_checksums.py
   python -m compileall -q scripts tests
   python -m unittest discover -s tests -v
   python scripts/analyze_phase_shifter.py
   ```

6. Describe any change to metric definitions or source data in the pull
   request.

Do not silently modify raw simulation exports. Add a new source file and
document its origin when simulation data change.

## Naming Conventions

- Keep standard repository filenames unchanged: `README.md`, `LICENSE`,
  `CITATION.cff`, `CHANGELOG.md`, and `requirements.txt`.
- Use lowercase kebab-case for project documentation and workflow files.
- Use lowercase snake_case for Python modules, datasets, and generated figures.
- Keep the tracked `cadence/phase_shift` OpenAccess files binary-exact unless a
  design change is made in a compatible Cadence environment and documented.
- Never add PDK, model, rule-deck, Cadence installation, license, NDA-controlled,
  simulation-result, or session material.
