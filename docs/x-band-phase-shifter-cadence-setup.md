# Cadence Design Setup and Reproduction Boundary

## Release Status

Release v1.0.0 includes the original student-created `phase_shift` Cadence
OpenAccess library. The preserved source provides schematic views for all six
binary-weighted phase cells, the NMOS characterization cell, the complete
6-bit top-level schematic, and the top-level layout.

The repository does not include the TSMC 180 nm PDK, device models, process
files, Calibre rule decks, Cadence software, ADE/Assembler/Maestro state,
simulation netlists, process corners, or the original 64-code sweep setup.

## Included Cell Views

| Cell | Included views |
| --- | --- |
| `bit5625` | schematic, constraint metadata |
| `bit1125` | schematic, constraint metadata |
| `bit225` | schematic, constraint metadata |
| `bit45` | schematic, constraint metadata |
| `bit90` | schematic, constraint metadata |
| `bit180` | schematic, constraint metadata |
| `nmos` | schematic |
| `phase_shift` | schematic, layout |

The abbreviated names `bit5625`, `bit1125`, and `bit225` denote 5.625, 11.25,
and 22.5 degrees. These identifiers are embedded in the OpenAccess hierarchy
and should not be changed with ordinary filesystem tools.

## Requirements

Opening the source requires:

- Cadence Virtuoso with compatible OpenAccess support;
- a legally licensed TSMC 180 nm PDK resolving the original `tsmc18` library
  references; and
- any local site configuration required by that PDK.

Exact Virtuoso, simulator, and PDK revisions were not recorded. Binary OA
metadata references OpenAccess 22.50.034 and 22.50.036 components and
`linux_rhel50_gcc48x_64`; these are observations, not a confirmed application
version or compatibility guarantee.

## Suggested Setup Procedure

1. Clone or extract the repository on the Linux host used for Virtuoso.
2. Confirm with the license administrator that the local TSMC 180 nm PDK may be
   used for this project.
3. Make the PDK's `tsmc18` library visible through the site's normal `cds.lib`
   configuration or Library Path Editor.
4. Use `cadence/cds.lib.example` as a starting point for the student-created
   library definition.
5. Start Virtuoso from the configured working directory and open library
   `phase_shift`.
6. Inspect the top-level `phase_shift/schematic` hierarchy before attempting
   any migration or simulation.
7. Rebuild the required analyses and the 64-state S-parameter sweep because the
   original ADE state and sweep definition are unavailable.

## What Can Be Reproduced

Fully reproducible without Cadence:

- integrity verification of the included OpenAccess source files;
- processing of the three preserved 64-state Cadence S-parameter exports;
- processed datasets, performance metrics, and result figures;
- equivalent NMOS calculations from values transcribed from the historical
  report; and
- first-order phase-cell starting values from the documented equations.

Available for inspection with an authorized Cadence/PDK environment:

- all preserved schematic views;
- the top-level phase-shifter layout; and
- the original library hierarchy and Cadence-managed metadata.

Not directly reproducible from the repository alone:

- the original NMOS characterization simulation;
- the original 64-state simulation run;
- exact process, voltage, temperature, model, and extraction conditions;
- DRC, LVS, parasitic extraction, or electromagnetic verification; and
- final optimization history.

## Redistribution Boundary

The repository contains only the student-created `phase_shift` library. Do not
add or redistribute the TSMC PDK, models, support files, rule decks, Cadence
software components, or any other license-controlled material without explicit
authorization from the relevant rights holder or license administrator.
