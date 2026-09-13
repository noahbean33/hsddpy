# MICROSTRIP TRANSMISSION LINES

> Source: `MSTRIP.pdf` — worksheet `MSTRIP.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Formulas included in this spreadsheet

**Effective relative permittivity EEFF() (used internally)**

**Effective electrical trace width WE() (used internally)**

- Microstrip characteristic impedance — `ZMSTRIP()`
- Microstrip propagation delay — `PMSTRIP()`
- Microstrip trace inductance — `LMSTRIP()`
- Microstrip trace capacitance — `CMSTRIP()`

**(Watch out for Edward's error in**

**Equation 3.52b, where he omits a**

**ln() function.)**

This material is nicely summarized

in T. C. Edwards, "Foundations of

Microstrip Circuit Design," John

Wiley, New York, 1981, reprinted

1987.

## Variables used

- `h` — Trace height above ground (in.)
- `w` — Trace width (in.)
- `t` — Trace thickness (in.)
- `er` — Relative permittivity of material between trace and ground plane (dimensionless)
- `x` — Trace length (in.)

Effective relative permittivity as a function of microstrip trace geometry:

For skinny traces (w < h)

```text
E_skny(h, w, er) := (er + 1)/2 + ((er - 1)/2)*((1 + (12*h)/w)**(-.500) + .04*(1 - w/h)**2)
```

For wide traces (w > h)

```text
E_wide(h, w, er) := (er + 1)/2 + ((er - 1)/2)*(1 + (12*h)/w)**(-.500)
```

Composite formula picks skinny or wide model depending on w/h ratio:

```text
E_temp(h, w, er) := if(w > h, E_wide(h, w, er), E_skny(h, w, er))
```

Special adjustment to account for trace thickness:

```text
EEFF(h, w, t, er) := E_temp(h, w, er) - ((er - 1)*(t/h))/(4.6*sqrt(w/h))
```

When w/h is skinny, you get the average of the PCB permittivity, er, and the permittivity of air. When w/h is wide, (the trace is very close to the ground plane) you get er.

Effective trace width as a function of other parameters (in.):

For skinny traces (2πw < h)

```text
WE_skny(h, w, t) := w + (1.25*t)/π*(1 + ln((4*π*w)/t))
```

For wide traces (2πw > h)

```text
WE_wide(h, w, t) := w + (1.25*t)/π*(1 + ln((2*h)/t))
```

Composite formula picks skinny or wide model depending on w/h ratio:

```text
WE(h, w, t) := if(w > h/(2*π), WE_wide(h, w, t), WE_skny(h, w, t))
```

Characteristic impedance as a function of trace geometry (Ω):

Accuracy of better than 2 percent is obtained under the following conditions:

0 < t/h < 0.2 0.1 < w/h < 20 0 < er < 16

For skinny traces (w < h)

```text
ZMS_skny(h, w, t) := 60*ln((8*h)/WE(h, w, t) + WE(h, w, t)/(4*h))
```

For wide traces (w > h)

```text
ZMS_wide(h, w, t) := (120*π)/(WE(h, w, t)/h + 1.393 + .667*ln(WE(h, w, t)/h + 1.444))
```

Composite formula picks skinny or wide model depending on w/h ratio:

```text
ZMSTRIP(h, w, t, er) := if(w > h, ZMS_wide(h, w, t), ZMS_skny(h, w, t))/sqrt(EEFF(h, w, t, er))
```

Microstrip propagation delay (s/in.):

```text
PMSTRIP(h, w, t, er) := 84.72*10**(-12)*sqrt(EEFF(h, w, t, er))
```

Inductance of microstrip (H):

```text
LMSTRIP(h, w, t, x) := PMSTRIP(h, w, t, 1.)*ZMSTRIP(h, w, t, 1.)*x
```

(Use a dummy er value of 1. It doesn't matter for inductance calculations.)

Capacitance of microstrip (F):

```text
CMSTRIP(h, w, t, er, x) := PMSTRIP(h, w, t, er)/ZMSTRIP(h, w, t, er)*x
```

---

Example microstrip wire calculations

Height above ground (in.)

```text
H := .006
```

Width of trace (in.)

```text
W := .008
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
ZMSTRIP(H, W, T, er) = 56.44347575
```

Total inductance (H):

```text
LMSTRIP(H, W, T, X) = 9.340075734e-8
```

Same result in nH:

```text
LMSTRIP(H, W, T, X)*10**9 = 93.40075734
```

Inductance per in. (H):

```text
LMSTRIP(H, W, T, 1) = 8.49097794e-9
```

Total capacitance (F):

```text
CMSTRIP(H, W, T, er, X) = 2.931722762e-11
```

Same result in pF:

```text
CMSTRIP(H, W, T, er, X)*10**12 = 29.31722762
```

Capacitance per in. (F):

```text
CMSTRIP(H, W, T, er, 1) = 2.665202511e-12
```

Tolerance effects

```text
ZMSTRIP_TOL(h, dh, w, dw, t, er, der) := [[ZMSTRIP(h + dh, w - dw, t, er - der)], [ZMSTRIP(h, w, t, er)], [ZMSTRIP(h - dh, w + dw, t, er + der)]]
α := ZMSTRIP_TOL(.007, .002, .011, .002, .0022, 4.5, .1)
α = [[64.78678439], [51.37240818], [37.92666329]]
REFL(x, z) := [[(z - x[0])/(z + x[0])], [(z - x[1])/(z + x[1])], [(z - x[2])/(z + x[2])]]
REFL(α, 50) = [[-0.1288195716], [-0.01353828131], [0.1373114396]]
```
