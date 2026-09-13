# MUTUAL INDUCTANCE OF PARALLEL TRANSMISSION LINES

> Source: `MLINE.pdf` — worksheet `MLINE.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Formulas included in this spreadsheet

- Mutual inductance of two lines — `MLINE()`

## Variables used

- `s` — Separation between wire centers (in.)
- `h` — Height of wires above ground (in.)
- `x` — Length of parallel
- `span` — (in.)

(We assume that two identical transmission lines share a parallel run of length x, with a horizontal separation s.)

Let L equal the inductance (H) of the first transmission line of length x (use formula for round, microstrip, or stripline geometry as appropriate):

```text
MLINE(L, s, h) := L*(1/(1 + (s/h)**2))
```
