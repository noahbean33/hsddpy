# CAPACITANCE OF TWO PARALLEL PLATES

> Source: `CAPAC.pdf` — worksheet `CAPAC.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Formulas included in this spreadsheet

- Capacitance of two plates — `CPLATE()`

**Impedance magnitude of capacitor at**

- one frequency — `XCF()`

**Impedance magnitude of capacitor as**

- seen by rising edge — `XCR()`

## Variables used

- `w` — Width of plate overlap (in.)
- `x` — Length of plate overlap (in.)
- `h` — Height of one plate above the other (in.)
- `er` — Relative dielectric constant of material between plates

Capacitance of two plates (F):

```text
CPLATE(w, x, h, er) := 2.249*10**(-13)*(er*x*w)/h
```

A power and ground plane separated by 0.010 in. of FR-4 dielectric (er = 4.5) share a capacitance of 100 pF/in. 2

Halving the separation doubles the capacitance.

Impedance magnitude of capacitor at frequency f ( Ω ):

- `c` — Capacitance (F)
- `f` — Frequency (Hz)

```text
XCF(c, f) := 1/(2*π*f*c)
```

The impedance, at 100 MHz, of a 100-pF capacitor is 16 Ω .

```text
XCF(100*10**(-12), 10**8) = 15.91549431
```

Impedance magnitude of capacitor as seen by rising edge (Ω ):

- `c` — Capacitance (F)

tr 10-90% rise time (s)

```text
XCR(c, tr) := tr/(π*c)
```

The impedance, as seen by a 5-ns rising edge of a 100-pF capacitor is 16 Ω .

```text
XCR(100*10**(-12), 5*10**(-9)) = 15.91549431
```
