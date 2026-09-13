# INDUCTANCE OF RECTANGULAR LOOPS

> Source: `RECTANGL.pdf` — worksheet `RECTANGL.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Formulas included in this spreadsheet

- Inductance of rectangular wire loop — `LRECT()`

**Impedance magnitude of inductor at**

- one frequency — `XLF()`

**Impedance magnitude of inductor to**

- rising edge — `XLR()`

## Variables used

- `d` — Diameter of wire (in.)
- `x` — Length of wire loop (in.)
- `y` — Breadth of wire loop (in.)

Inductance of wire loop (H):

```text
LRECT(d, x, y) := 10.16*10**(-9)*(x*ln((2*y)/d) + y*ln((2*x)/d))
```

A loop of 24-gauge wire 1 in.2 has about 100 nH of inductance.

Changing the wire diameter from AWG 30 to AWG 10 makes little difference. The log function is very insensitive to wire size.

If your loop consists of different-sized conductors, use the diameter of the smallest one.

Impedance magnitude of inductor at frequency f (Ω):

- `l` — Inductance (H)
- `f` — Frequency (Hz)

```text
XLF(l, f) := 2*π*f*l
```

The impedance, at 100 MHz, of a 100-nH inductor is 62 Ω.

Impedance magnitude of inductor as seen by rising edge (Ω):

- `l` — Inductance (H)

tr 10-90% rise time (s)

```text
XLT(l, tr) := (π*l)/tr
```

The impedance, as seen by a 5-ns rising edge, of a 100-nH inductor is 62 Ω.
