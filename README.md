# hsdd

Transmission-line, crosstalk and signal-integrity calculations for high-speed
digital design, as a Python library and a command-line tool.

The formulas come from the Mathcad worksheets that ship with *High-Speed
Digital Design: A Handbook of Black Magic* (Howard Johnson and Martin
Graham). Every closed-form sheet in that set stored its own worked examples,
and all 60 of those stored results are replayed by the test suite — so the
numbers this library returns are the numbers Mathcad returned, to within
1e-9.

What the library adds on top of the transcription is the part a designer
actually needs: **the inverse problem** (what width gives me 50 Ω?),
**tolerance corners**, **unit handling**, and the **rules of thumb** that turn
an impedance into a layout decision.

```python
from hsdd import Microstrip, mil, oz, ns

trace = Microstrip.for_impedance(50, height=mil(6), thickness=oz(1), er=4.5)
trace.width                      # 0.0102 in. -- 10.15 mil
trace.z0                         # 50.0 ohms
trace.critical_length(ns(1))     # 1.09 in. before it needs terminating
trace.tolerance(height=mil(1), width=mil(1), er=0.2).percent   # 17.0% swing
```

## Install

```bash
pip install -e .
```

Python 3.8 or newer, no required dependencies. The two simulators need numpy:

```bash
pip install -e ".[sim]"
```

## Units

Everything inside the library is **inches, seconds, ohms, henries, farads**,
because that is what the coefficients in the source formulas are scaled for.
Nobody draws a board in inches, so convert at the call site:

```python
from hsdd import mil, mm, oz, ns, ps, pf, to_mil, to_ps_per_inch

mil(6)            # 0.006 in.
mm(0.15)          # 0.0059 in.
oz(1)             # 0.00137 in. -- one ounce of copper
to_mil(0.0102)    # 10.2
```

Every `x()` has a matching `to_x()`. The command-line tool takes the same
units as suffixes: `--height 6mil`, `--thickness 1oz`, `--rise-time 350ps`.

## What is in it

### Transmission-line geometries

Each is a frozen dataclass holding a cross-section, and each answers the same
questions — `z0`, `delay`, `inductance_per_inch`, `capacitance_per_inch`,
`inductance(length)`, `capacitance(length)`, `critical_length(rise_time)`.

| Class | Cross-section | Source sheet |
| --- | --- | --- |
| `RoundWire` | wire above a plane (wire-wrap, flying leads) | ROUND |
| `Coax` | coaxial cable | COAX |
| `TwistedPair` | twisted pair | TWIST |
| `Microstrip` | surface trace over one plane | MSTRIP |
| `Stripline` | buried trace, centred | SLINE2 |
| `OffsetStripline` | buried trace, off centre | SLINE2 |

```python
>>> from hsdd import Stripline, mil, oz
>>> print(Stripline(separation=mil(20), width=mil(6), thickness=oz(1), er=4.5).summary())
Stripline  b=20mil  w=6mil  t=1.37mil  er=4.5
  Z0          51.44 ohm
  delay      179.72 ps/in   (5.56 in/ns)
  L           9.244 nH/in
  C           3.494 pF/in
```

The microstrip and stripline classes carry the published accuracy bands, and
`check_accuracy()` tells you when a cross-section has wandered outside them
instead of silently returning a worse number.

### Solving backwards, and tolerance

```python
Microstrip.for_impedance(50, height=mil(6), thickness=oz(1), er=4.5)
Stripline.for_impedance(50, separation=mil(20), thickness=oz(1), er=4.5)
```

If a target is unreachable the error says what range *is* reachable, which is
usually the more useful answer.

```python
>>> span = trace.tolerance(height=mil(0.5), width=mil(0.5), er=0.2)
>>> print(span.summary(z_source=50))
Z0  50.00 ohm nominal, 45.40 to 54.76 (+/-9.5%)
reflection vs 50 ohm:  -0.000 nominal, worst +0.048
```

### Signal integrity

| Function | Answers |
| --- | --- |
| `knee_frequency(rise_time)` | how much bandwidth the edge really contains |
| `critical_length(...)` | how long a run can be before it is a transmission line |
| `check_termination(...)` | terminate this run or not, and why |
| `series_terminator(z0, driver)` | what resistor to fit at the driver pin |
| `reflection_coefficient(...)` | size of the step off a discontinuity |
| `coupling_ratio(spacing, height)` | how much couples to the next trace over |

### Lumped elements and copper

Plate and plane capacitance, loop inductance (circular and rectangular), and
the pair that makes the rest of it useful — the impedance a capacitor or an
inductor presents *to an edge*, not to a sine wave:

```python
>>> from hsdd import capacitive_reactance_to_edge, inductive_reactance_to_edge, pf, nh, ns
>>> round(capacitive_reactance_to_edge(pf(100), ns(5)), 1)    # 100 pF to a 5 ns edge
15.9
>>> round(inductive_reactance_to_edge(nh(100), ns(5)), 1)     # 100 nH of lead inductance
62.8
```

Plus DC resistance of wires, traces and planes, with AWG and copper-plating-
weight conversions and a temperature coefficient.

### Simulators (need numpy)

`step_response()` reproduces the SHORTLIN worksheet: drive a line through a
source impedance into a resistive-capacitive load and get the waveform back,
with overshoot, ring-back and settling time computed for you.

```python
>>> from hsdd import step_response, ns
>>> for ratio in (0, 2, 4, 6):
...     r = step_response(delay=ns(1), rise_time=ns(1) * ratio)
...     print("tr = %d x delay:  %5.1f%% overshoot" % (ratio, r.overshoot))
tr = 0 x delay:   36.4% overshoot
tr = 2 x delay:   20.6% overshoot
tr = 4 x delay:    0.8% overshoot
tr = 6 x delay:    0.0% overshoot
```

That table is where the factor of six in `critical_length()` comes from.

`connector_crosstalk()` reproduces the GNDPINS worksheet, which solves for
how return current distributes itself over a connector's ground pins and sums
the crosstalk left over. The original hard-codes one ground row and leaves
scattering them as an exercise; here the pin pattern is the argument:

```python
>>> from hsdd import connector_crosstalk
>>> one_row   = ["SSSSSSSS", "GGGGGGGG", "SSSSSSSS"]
>>> scattered = ["GSSGSSGS", "SGSSGSSG", "SSGSSGSS"]   # same eight grounds
>>> round(connector_crosstalk(one_row).worst * 1e3)
635
>>> round(connector_crosstalk(scattered).worst * 1e3)
542
```

## Command line

```bash
hsdd microstrip --height 6mil --width 8mil --thickness 1oz --er 4.5
hsdd microstrip --height 6mil --thickness 1oz --z0 50        # solve for width
hsdd stripline --separation 20mil --width 6mil --tol-separation 1mil --tol-er 0.2
hsdd edge --rise-time 350ps                                  # what that edge implies
hsdd sim --delay 500ps --rise-time 1ns --plot
hsdd crosstalk --row SSSSSSSS --row GGGGGGGG --row SSSSSSSS
```

```
$ hsdd edge --rise-time 350ps
rise time           350 ps
knee frequency     1429 MHz

longest unterminated run, by medium:
  microstrip, FR-4 outer layer     0.39 in.  (150 ps/in.)
  stripline, FR-4 inner layer      0.32 in.  (180 ps/in.)
  wire in air                      0.69 in.  ( 85 ps/in.)
```

Run `examples/design_walkthrough.py` for a full design pass — width, length,
termination, tolerance, crosstalk and DC drop on one clock net.

## Checking against the book

`hsdd.mathcad` carries every worksheet function under its original name, with
the original argument order and return units, for transliterating a sheet
line by line:

```python
>>> from hsdd.mathcad import ZMSTRIP
>>> round(ZMSTRIP(.006, .008, .00137, 4.5), 6)
56.443476
```

Use it to check the library against the book. Use the rest of the library for
new work — those signatures carry the quirks of a 1990s Mathcad sheet,
including `MLOOP()`, which returns nanohenries while everything around it
returns base units.

## Tests

```bash
pip install -e ".[test]"
python -m pytest
```

203 tests: the 60 stored Mathcad results, the physical invariants the
simulators must satisfy (every amp that leaves a connector pin comes back on
the grounds; an unterminated line settles at its DC divider), input
validation, the CLI, and every example in every docstring.

## Accuracy, and what this is not

These are closed-form approximations, and the library reports their published
bounds rather than hiding them:

- **Microstrip** — better than 2% for `0 < t/h < 0.2`, `0.1 < w/h < 20`,
  `er < 16`. Note that 1 oz copper on a 4 mil core is already outside it.
- **Stripline** — better than 1.3% for `t/b < 0.25`, `t/w < 0.11`.
- **Offset stripline** — an approximation with no accuracy bound; the
  worksheet says so plainly.
- **Resistance** — DC only. Skin effect makes the real number higher at any
  frequency a digital edge cares about.
- **`step_response()`** — lossless and distortionless line. Real FR-4 above a
  gigahertz is neither, so ringing amplitudes are an upper bound and edge
  degradation is optimistic.
- **`connector_crosstalk()`** — mutual inductance between parallel straight
  pins, no shell return, no terminations. It ranks pinouts against each
  other; it does not replace a 3-D field solve.

None of this is a substitute for a field solver on a specific stackup. It is
for the part of the job that comes first: deciding what to ask the field
solver, and noticing at your desk that a number is wrong by a factor of two.

## Source material

The original worksheets, their PDF printouts, and Markdown transcriptions of
each one are in [`markdown/`](markdown). The formulas here were read out of
those; `pdftotext` silently drops radical signs and superscripts from Mathcad
printouts, so `sqrt(lpi/cpi)` comes out as `lpi/cpi` — wrong in a way that is
very hard to spot. See [ATTRIBUTION.md](ATTRIBUTION.md).
