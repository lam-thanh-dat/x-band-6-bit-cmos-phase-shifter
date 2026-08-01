# Known Limitations and Uncertainties

## Confirmed Technical Limitations

- The insertion loss is high: the aggregate mean is 15.69 dB.
- The insertion-loss variation across states is also high: 1.73 dB RMS in the
  aggregate dataset.
- The aggregate mean input return loss is 9.49 dB, and the worst simulated
  value is 5.48 dB.
- The results contain only three frequency samples for the 64-state statistical
  evaluation.

## Information Not Confirmed by the Submitted Files

- exact Cadence Virtuoso and simulator versions;
- exact TSMC 180 nm PDK revision and process option;
- simulation temperature, process corner, and supply-tolerance sweeps;
- whether the 64-state CSV exports are schematic, extracted, or
  electromagnetic post-layout results;
- inductor quality-factor assumptions and passive-model revisions;
- chip area, power consumption, and measured hardware performance;
- DRC, LVS, and post-layout extraction status; and
- Monte Carlo mismatch and process-variation results.

These items should be supplied before describing the project as tapeout-ready
or experimentally validated.

## Reproducibility Boundary

Fully reproducible from this repository:

- byte-level integrity checks for the included student-created OpenAccess
  library;
- processing of the three 64-state Cadence S-parameter exports;
- processed datasets, performance metrics, and four figures;
- equivalent NMOS calculations from three values transcribed from the
  historical report; and
- first-order phase-cell starting values from the documented analytical
  equations.

Available for inspection with a compatible, authorized Cadence/PDK setup:

- schematics for the six phase cells, NMOS cell, and top-level design; and
- the top-level `phase_shift` layout.

Not reproducible from this repository alone:

- the original NMOS characterization simulation;
- the original 64-state Cadence simulations;
- exact final tuned values and optimization history;
- the ADE/Assembler/Maestro state and code-sweep definition; and
- verified extraction, DRC, LVS, and electromagnetic results.

## Interpretation Boundary

The repository documents a circuit-simulation study and preserved design
source. It does not claim fabricated-chip measurements, tapeout readiness, or
commercial-level performance.
