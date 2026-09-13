# STRIPLINE TRANSMISSION LINES

> Source: `SLINE2.pdf` — worksheet `SLINE2.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Formulas included in this spreadsheet

- Stripline characteristic impedance — `ZSTRIP()`
- Offset stripline characteristic impedance — `ZOFFSET()`
- Stripline propagation delay — `PSTRIP()`
- Stripline trace inductance — `LSTRIP()`
- Offset stripline inductance — `LOSTRIP()`
- Stripline trace capacitance — `CSTRIP()`
- Offset stripline capacitance — `COSTRIP()`

This material is summarized in

Harlan Howe, Stripline Circuit

Design, Artech House, Norwood, MA,

1974.

## Variables used

- `h1` — Trace height above lower ground plane (in.)
- `h2` — Trace headroom below upper ground plane (in.)
- `b` — Separation between ground planes, b = h1 + h2 + t (in.)
- `w` — Trace width (in.)
- `t` — Trace thickness (in.)
- `er` — Trace thickness (in.)
- `x` — Trace length (in.)

Stripline characteristic impedance (Ω:)

Accuracy of better than 1.3% is obtained under the following conditions:

t/b < 0.25 t/w < 0.11 er unrestricted

NOTE: formula ZSTR_K1() corrected per instructions from Robert Canright of Richardson, TX. Thanks, Robert.

For skinny traces (w/b < 0.35)

```text
ZSTR_K1(w, t) := (w/2)*(1 + t/(π*w)*(1 + ln((4*π*w)/t)) + 0.255*(t/w)**2)
ZSTR_skny(b, w, t, er) := 60/sqrt(er)*ln((4*b)/(π*ZSTR_K1(w, t)))
```

For wide traces (w/b > 0.35)

```text
ZSTR_K2(b, t) := (2/(1 - t/b)*ln(1/(1 - t/b) + 1) - (1/(1 - t/b) - 1)*ln(1/(1 - t/b)**2 - 1))
ZSTR_wide(b, w, t, er) := 94.15/(w/b/(1 - t/b) + ZSTR_K2(b, t)/π)*1/sqrt(er)
```

Composite formula picks skinny or wide model depending on w/b ratio:

```text
ZSTRIP(b, w, t, er) := if(w > .35*b, ZSTR_wide(b, w, t, er), ZSTR_skny(b, w, t, er))
```

Rarely are the two parameters h1 and h2 equal in practice. The more common case is an assymetric stripline having the conducting trace offset to one side.

Offset, or asymmetric, stripline characteristic impedance (Ω)

(no accuracy guaranteed):

```text
ZOFFSET(h1, h2, w, t, er) := (2*ZSTRIP(2*h1 + t, w, t, er)*ZSTRIP(2*h2 + t, w, t, er))/(ZSTRIP(2*h1 + t, w, t, er) + ZSTRIP(2*h2 + t, w, t, er))
```

Propagation delay of stripline (s/in.):

```text
PSTRIP(er) := 84.72*10**(-12)*sqrt(er)
```

(same formula for centered or offset stripline)

Inductance of stripline (H):

```text
LSTRIP(b, w, t, x) := PSTRIP(1.)*ZSTRIP(b, w, t, 1.)*x
```

In the equation above, we can assume a relative permittivity of 1.; it doesn't affect the answer.

Inductance of offset stripline (H):

```text
LOSTRIP(h1, h2, w, t, x) := PSTRIP(1.)*ZOFFSET(h1, h2, w, t, 1.)*x
```

Capacitance of stripline (F):

```text
CSTRIP(b, w, t, er, x) := PSTRIP(er)/ZSTRIP(b, w, t, er)*x
```

In the equations above and below, we must use the relative permittivity.

Capacitance of offset stripline (F):

```text
COSTRIP(h1, h2, w, t, er, x) := PSTRIP(er)/ZOFFSET(h1, h2, w, t, er)*x
```

---

Example stripline calculations

Ground plane separation (in.)

```text
B := .020
```

Width of trace (in.)

```text
W := .006
```

Thickness of trace (in.)

```text
T := .00137
```

(1-oz copper plating weight)

Length of wire (in.)

```text
X := 11.000
```

Relative electric permeability (affects capacitance, but not inductance)

```text
er := 4.5
```

Impedance (Ω):

```text
ZSTRIP(B, W, T, er) = 51.4370796
```

Total inductance (H):

```text
LSTRIP(B, W, T, X) = 1.016860066e-7
```

Same result in nH:

```text
LSTRIP(B, W, T, X)*10**9 = 101.6860066
```

Inductance per in. (H):

```text
LSTRIP(B, W, T, 1) = 9.244182419e-9
```

Total capacitance (F):

```text
CSTRIP(B, W, T, er, X) = 3.843338055e-11
```

Same result in pF:

```text
CSTRIP(B, W, T, er, X)*10**12 = 38.43338055
```

Capacitance per in. (F):

```text
CSTRIP(B, W, T, er, 1) = 3.493943687e-12
```

Tolerance effects

```text
ZOFF_TOL(h1, dh1, h2, dh2, w, dw, t, er, der) := [[ZOFFSET(h1 + dh1, h2 + dh2, w - dw, t, er - der)], [ZOFFSET(h1, h2, w, t, er)], [ZOFFSET(h1 - dh1, h2 - dh2, w + dw, t, er + der)]]
α := ZOFF_TOL(.007, .002, .032, .002, .008, .002, .0015, 4.5, .1)
α = [[64.05664731], [51.72631593], [39.22802945]]
REFL(x, z) := [[(z - x[0])/(z + x[0])], [(z - x[1])/(z + x[1])], [(z - x[2])/(z + x[2])]]
REFL(α, 50) = [[-0.1232426837], [-0.01697020001], [0.1207240663]]
```
