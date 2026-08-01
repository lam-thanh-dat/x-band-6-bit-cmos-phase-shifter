# Analysis Methodology

## Simulated States

The six binary-weighted cells correspond to nominal phase increments of:

```text
5.625, 11.25, 22.5, 45, 90, and 180 degrees
```

The state index is the binary-weighted sum normalized by the 5.625-degree
least significant bit. This maps the 64 control combinations to state indices
0 through 63 and ideal phase values from 0 to 354.375 degrees.

## Phase Error

For state `i` and frequency `f`, the relative simulated phase is referenced to
state 0:

```text
relative_phase(i, f) = wrap(phase(i, f) - phase(0, f))
```

The phase error is:

```text
error(i, f) = wrap(relative_phase(i, f) - ideal_phase(i))
```

Here, `wrap` maps an angle to the interval [-180, 180) degrees. The common phase
offset is the population mean of the 64 errors. The offset-removed phase RMS is
the population standard deviation:

```text
phase_rms(f) = sqrt(mean((error(i, f) - mean_error(f))^2))
```

The analysis also reports total RMS without offset removal:

```text
total_phase_rms(f) = sqrt(mean(error(i, f)^2))
```

## Insertion Loss

Insertion loss is derived directly from the simulated transmission magnitude:

```text
insertion_loss(i, f) = -S21_dB(i, f)
```

The reported insertion-loss RMS is the population standard deviation across
the 64 states at each frequency.

## Return Loss

Input return loss is calculated as:

```text
return_loss(i, f) = -S11_dB(i, f)
```

The workflow reports the mean, population RMS, minimum, and maximum across the
64 states.

## Aggregate Values

The aggregate metrics flatten the 64 states at 9, 10, and 11 GHz into 192
state-frequency observations. No interpolation is applied between the three
frequencies.

Metric records use an explicit `scope` field. Per-frequency records contain a
numeric `frequency_ghz`; the aggregate record uses a null/empty
`frequency_ghz` and numeric `frequency_start_ghz` and
`frequency_stop_ghz` bounds. This avoids mixed numeric and text values in one
column.

## Input Validation

The analysis rejects:

- missing or duplicate state codes;
- missing or duplicate 9, 10, or 11 GHz columns;
- inconsistent controls across the three exports;
- control voltages other than 0 or 1.8 V;
- non-finite values such as `NaN`, positive infinity, and negative infinity.

JSON output is written with non-standard `NaN` values disabled.

The implementation is available in
[`scripts/analyze_phase_shifter.py`](../scripts/analyze_phase_shifter.py).
