# TRANSMISSION LINE MADE FROM ROUND WIRE (WIRE-WRAP)

> Source: `ROUND.pdf` — worksheet `ROUND.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Formulas included in this spreadsheet

- Round wire characteristic impedance — `ZROUND()`
- Round wire propagation delay — `PROUND()`
- Round wire inductance — `LROUND()`
- Round wire capacitance — `CROUND()`

## Variables used

- `d` — Diameter of wire (in.)
- `h` — Height of wire above ground (in.)
- `x` — Length of wire (in.)

(We assume the wire is suspended in air, for which the relative dielectric constant is 1.00.)

Characteristic impedance of round wire above ground plane (Ω):

```text
ZROUND(d, h) := 60*ln((4*h)/d)
```

Propagation delay per in. of round wire above ground plane (s/in):

```text
PROUND(d, h) := 84.72*10**(-12)
```

(assume air dielectric)

Inductance of round wire above ground plane (H):

```text
LROUND(d, h, x) := x*5.08*10**(-9)*ln((4*h)/d)
```

Capacitance of round wire above ground plane (F):

```text
CROUND(d, h, x) := ((x*1.413*10**(-12))/ln((4*h)/d))
```

---

Example round wire calculations

Diameter of AWG 30 wire (in.)

```text
D := .01
```

Length of wire (in.)

```text
X := 2.000
```

Height above ground (in.)

```text
H := .100
```

Characteristic impedance (Ω):

```text
ZROUND(D, H) = 221.3327672
```

Total inductance (H):

```text
LROUND(D, H, X) = 3.747901525e-8
```

Same result in nH:

```text
LROUND(D, H, X)*10**9 = 37.47901525
```

Inductance per in. (H):

```text
LROUND(D, H, 1) = 1.873950763e-8
```

Total capacitance (F):

```text
CROUND(D, H, X) = 7.660862967e-13
```

Same result in units pF:

```text
CROUND(D, H, X)*10**12 = 0.7660862967
```

Capacitance per in. (F):

```text
CROUND(D, H, 1) = 3.830431484e-13
```
