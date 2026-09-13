# TRANSMISSION LINE MADE FROM TWISTED PAIR WIRE

> Source: `TWIST.pdf` — worksheet `TWIST.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Formulas included in this spreadsheet

- Twisted-pair characteristic impedance — `ZTWIST()`
- Twisted-pair propagation delay — `PTWIST()`
- Twisted-pair inductance — `LTWIST()`
- Twisted-pair capacitance — `CTWIST()`

## Variables used

- `d` — Diameter of wire (in.)
- `s` — Separation between
- `wires` — (in.)
- `x` — Length of wire (in.)
- `er` — Effective relative dielectric constant of medium between wires

Characteristic impedance of twisted pair (Ω):

```text
ZTWIST(d, s, er) := 120/sqrt(er)*ln((2*s)/d)
```

Propagation delay per in. twisted pair (s/in.):

```text
PTWIST(er) := 84.72*10**(-12)*sqrt(er)
```

Inductance of twisted pair (H):

```text
LTWIST(d, s, x) := x*10.16*10**(-9)*ln((2*s)/d)
```

Capacitance of twisted pair (F):

```text
CTWIST(d, s, er, x) := ((x*.7065*10**(-12))/ln((2*s)/d))*er
```

---

Example twisted-pair calculations

Diameter of AWG 24 wire (in.)

```text
D := .02
```

Length of wire (in.)

```text
X := 2.000
```

Separation between wire centers (in.)

```text
S := .038
```

Relative dielectric constant

```text
er := 2.5
```

Characteristic impedance (Ω):

```text
ZTWIST(D, S, er) = 101.3194572
```

Total inductance (H):

```text
LTWIST(D, S, X) = 2.712722168e-8
```

Same result in nH:

```text
LTWIST(D, S, X)*10**9 = 27.12722168
```

Inductance per in. (H):

```text
LTWIST(D, S, 1) = 1.356361084e-8
```

Total capacitance (F):

```text
CTWIST(D, S, er, X) = 2.646065301e-12
```

Same result in pF:

```text
CTWIST(D, S, er, X)*10**12 = 2.646065301
```

Capacitance per in. (F):

```text
CTWIST(D, S, er, 1) = 1.323032651e-12
```
