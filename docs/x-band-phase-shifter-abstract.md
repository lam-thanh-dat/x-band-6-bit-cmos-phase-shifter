# Technical Abstract

## Title

**Design and Simulation of a 6-Bit X-Band CMOS Phase Shifter in a 180-nm
CMOS Process**

## Abstract

**Abstract—** This work presents the design and simulation of a 6-bit digital
phase shifter for X-band operation using a TSMC 180 nm CMOS design environment.
Six binary-weighted cells of 5.625, 11.25, 22.5, 45, 90, and 180 degrees are
cascaded to provide 64 phase states. High-pass/low-pass and switched-network
topologies are designed around 10 GHz and adjusted using historically reported
switch parasitics, including an on-state resistance of approximately 3.33 ohms
and an off-state capacitance of approximately 57.8 fF. These quantities are
recalculated from three samples transcribed from the original report; the
native NMOS export is unavailable. Preserved S-parameter exports are evaluated
for all states at 9, 10, and 11 GHz. Across the resulting 192
state-frequency points, the root-mean-square (RMS) phase error after
common-offset removal is 3.67 degrees; at 10 GHz, it is 2.28 degrees. The
aggregate mean insertion loss is 15.69 dB with 1.73 dB RMS variation. The mean
input return loss is 9.49 dB, and the worst-case value is 5.48 dB. The results
demonstrate useful phase accuracy but also reveal significant loss and
impedance-matching limitations. Further improvement should focus on switch
sizing, passive-element quality factor, local matching networks, stage
ordering, and electromagnetic post-layout verification.

**Index Terms—** CMOS phase shifter, digital phase shifter, X-band,
S-parameters, phased array, 180 nm CMOS.

## Scope Note

The reported aggregate statistics use three discrete frequency samples
(9, 10, and 11 GHz). They should not be interpreted as a dense or continuous
frequency sweep over the complete X-band. Release v1.0.0 includes the preserved
Cadence OpenAccess schematic source and top-level layout. It reproduces the
data analysis, but not the original Cadence simulation because the licensed
PDK and original ADE state, models, corners, and sweep configuration are not
included.
