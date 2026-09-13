# INDUCTANCE OF CIRCULAR LOOP

> Source: `CIRCULAR.pdf` — worksheet `CIRCULAR.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Formulas included in this spreadsheet

- Inductance of circular wire loop — `LCIRC()`

**Impedance magnitude of inductor at**

- one frequency — `XLF()`

**Impedance magnitude of inductor as**

- seen by rising edge — `XLR()`

## Variables used

- `d` — Diameter of wire (in.)
- `x` — Diameter of wire loop (in.)

Inductance of wire loop (H):

```text
LCIRC(d, x) := 1.56*10**(-8)*x*(ln((8*x)/d) - 2)
```

A loop of 24-gauge wire the size of the loop between your thumb and forefinger has about 100 nH of inductance.

```text
LCIRC(.01, 1.3) = 1.003246731e-7
```

Changing the wire diameter from AWG 24 to AWG 14 makes little difference. The log function is rather insensitive to wire size.

```text
LCIRC(.1, 1.3) = 5.362824743e-8
```

Impedance magnitude of inductor at frequency f (Ω):

- `l` — Inductance (H)
- `f` — Frequency (Hz)

```text
XLF(l, f) := 2*π*f*l
```

The impedance, at 100 MHz, of a 100-nH inductor is 62 Ω.

```text
XLF(100*10**(-9), 10**8) = 62.83185307
```

Impedance magnitude of inductor as seen by rising edge (Ω):

- `l` — Inductance (H)

tr 10-90% rise time (s)

```text
XLT(l, tr) := (π*l)/tr
```

The impedance, as seen by a 5-ns rising edge, of a 100-nH inductor is 62 Ω.

```text
XLT(100*10**(-9), 5*10**(-9)) = 62.83185307
```
