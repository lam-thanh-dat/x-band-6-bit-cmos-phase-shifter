# Historical NMOS Characterization Samples

`historical_nmos_characterization.csv` contains three values of on-state
`real(Z11)` and off-state `imag(Y11)` transcribed from the original academic
report at 9, 10, and 11 GHz.

These values are included for calculation traceability only. They are not
native Cadence exports, and they do not make the original device simulation
reproducible. The original ADE/Spectre state, netlist, PDK revision, process
corner, temperature, and raw sweep data are unavailable.

Run `python scripts/analyze_nmos_switch.py` to calculate the equivalent
on-state resistance, off-state capacitance, and off-state reactance reported
in `data/processed/nmos_switch_characterization.csv`.
