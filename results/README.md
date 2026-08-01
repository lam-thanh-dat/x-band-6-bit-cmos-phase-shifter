# Generated Results

The files in this directory are generated from the raw Cadence exports by:

```bash
python scripts/analyze_phase_shifter.py
```

- `phase_shifter_performance_metrics.csv`: machine-readable statistics
- `phase_shifter_performance_metrics.json`: equivalent structured output
- `phase_shifter_phase_error_by_state.png`: phase error for all states
- `phase_shifter_insertion_loss_by_state.png`: insertion loss for all states
- `phase_shifter_input_return_loss_by_state.png`: input return loss for all
  states
- `phase_shifter_performance_overview.png`: compact three-panel performance
  overview for publication
- `phase_cell_starting_values.csv`: first-order component values regenerated
  from the documented 10-GHz, 50-ohm analytical equations

Population RMS definitions are documented in
[`docs/x-band-phase-shifter-analysis-methodology.md`](../docs/x-band-phase-shifter-analysis-methodology.md).

The metrics schema uses:

- `scope=frequency` with a numeric `frequency_ghz`;
- `scope=aggregate` with `frequency_ghz` empty/null and numeric
  `frequency_start_ghz` and `frequency_stop_ghz`.

This avoids mixing numeric frequencies and descriptive text in one field.
