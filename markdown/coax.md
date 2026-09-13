# COAXIAL TRANSMISSION LINE

> Source: `COAX.pdf` — worksheet `COAX.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Formulas included in this spreadsheet

- Coaxial cable characteristic impedance — `ZCOAX()`
- Coaxial cable propagation delay — `PCOAX()`
- Coaxial cable inductance — `LCOAX()`
- Coaxial cable capacitance — `CCOAX()`

## Variables used

- `d1` — Diameter of inner wire (in)
- `d2` — Diameter of outer shield (in)
- `x` — Length of cable (in)
- `er` — Relative dielectric constant of material surrounding the inner wire

Characteristic impedance of coaxial cable (Ω):

```text
ZCOAX(d1, d2, er) := 60/sqrt(er)*ln(d2/d1)
```

Propagation delay per in. for coaxial cable (s/in.):

```text
PCOAX(er) := 84.72*10**(-12)*sqrt(er)
```

Inductance of coaxial cable (H):

```text
LCOAX(d1, d2, x) := x*5.08*10**(-9)*ln(d2/d1)
```

Capacitance of coaxial cable (F):

```text
CCOAX(d1, d2, er, x) := ((x*1.41*10**(-12))/ln(d2/d1))*er
```

---

Example coaxial cable calculations

Diameter of AWG 30 inner wire (in.)

```text
D1 := .01
```

Inside diameter of shield (in.)

```text
D2 := .1
```

Length of cable (in.)

```text
X := 20.000
```

Relative dielectric constant

```text
er := 2.2
```

Characteristic impedance (Ω):

```text
ZCOAX(D1, D2, er) = 93.14415318
```

Total inductance (H):

```text
LCOAX(D1, D2, X) = 2.339426454e-7
```

Same result in nH:

```text
LCOAX(D1, D2, X)*10**9 = 233.9426454
```

Inductance per in. (H):

```text
LCOAX(D1, D2, 1) = 1.169713227e-8
```

Total capacitance (F):

```text
CCOAX(D1, D2, er, X) = 2.694362966e-11
```

Same result in pF:

```text
CCOAX(D1, D2, er, X)*10**12 = 26.94362966
```

Capacitance per in. (F):

```text
CCOAX(D1, D2, er, 1) = 1.347181483e-12
```
