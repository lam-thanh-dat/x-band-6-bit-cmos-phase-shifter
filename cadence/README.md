# Cadence OpenAccess Design Source

## Included Source

Release v1.0.0 includes the original student-created Cadence OpenAccess
library at [`phase_shift/`](phase_shift). The library was restored byte-for-byte
from the submitted `phase_shift.zip` archive and independently matched against
the copy in the original full-flow package.

| Cadence cell | Schematic | Layout | Function |
| --- | :---: | :---: | --- |
| `bit5625` | Yes | No | 5.625-degree phase cell |
| `bit1125` | Yes | No | 11.25-degree phase cell |
| `bit225` | Yes | No | 22.5-degree phase cell |
| `bit45` | Yes | No | 45-degree phase cell |
| `bit90` | Yes | No | 90-degree phase cell |
| `bit180` | Yes | No | 180-degree phase cell |
| `nmos` | Yes | No | NMOS switch characterization |
| `phase_shift` | Yes | Yes | Cascaded 6-bit top-level design |

Cadence-managed files such as `sch.oa`, `layout.oa`, `data.dm`, `master.tag`,
and `.oalib` are intentionally retained. Empty constraint files are also
preserved because they are part of the original library structure.

## Required External Environment

The design references a TSMC 180 nm technology library named `tsmc18`. That
PDK, its models, process files, verification decks, and Cadence software are
not included. To open the design, users need:

- a legally licensed, compatible TSMC 180 nm PDK that resolves the `tsmc18`
  library references;
- Cadence Virtuoso with compatible OpenAccess support; and
- local site configuration required by the licensed PDK.

Binary metadata contains references to OpenAccess 22.50.034 and 22.50.036
components and `linux_rhel50_gcc48x_64`. These strings are compatibility clues,
not a confirmed Cadence Virtuoso application release.

## Setup

1. Extract or clone the repository without renaming files inside
   `cadence/phase_shift`.
2. Make the licensed `tsmc18` PDK available through the site's normal
   `cds.lib` or Library Path Editor configuration.
3. From the `cadence/` directory, copy `cds.lib.example` to a local working
   `cds.lib` and add the authorized PDK include path if your site requires it.
4. Start Virtuoso from that configured working directory.
5. Open library `phase_shift`, then cell `phase_shift`, view `schematic` or
   `layout`.

The supplied template defines only the student-created library. PDK setup is
site-specific and must be completed with instructions from the license
administrator.

## Integrity Check

From the repository root, run:

```bash
python scripts/verify_cadence_library.py
```

The checker confirms all expected cell views and verifies every design-library
file against [`SHA256SUMS`](SHA256SUMS).

## Important Handling Notes

- Do not rename cells or views with filesystem tools. Use Cadence-aware
  migration and then validate the complete hierarchy.
- Do not hand-edit `.oa` or `.dm` files.
- Before publishing changes, confirm that no PDK, model, rule-deck, netlist,
  simulation-result, lock, or session files were added.
- The library does not include ADE/Assembler/Maestro states or the original
  64-code sweep definition, so it is source-complete for the preserved views
  but not a turnkey simulation environment.

See
[`docs/x-band-phase-shifter-cadence-setup.md`](../docs/x-band-phase-shifter-cadence-setup.md)
for the detailed reproduction boundary.
