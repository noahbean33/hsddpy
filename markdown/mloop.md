# MUTUAL INDUCTANCE OF TWO LOOPS

> Source: `MLOOP.pdf` — worksheet `MLOOP.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Formulas included in this spreadsheet

- Mutual inductance of two loops — `MLOOP()`

## Variables used

- `r` — Separation between loop centers (in.)
- `A1` — Surface area of loop 1 (in.2)
- `A2` — Surface area of loop 2 (in.2)

(We assume the loops are flat, and that their faces are oriented parallel to each other for maximum coupling)

The loops must be well separated for the MLOOP() approximation to work:

```text
r > sqrt(A1)
r > sqrt(A2)
```

and

Mutual inductance of two well-separated loops (nH):

```text
MLOOP(r, A1, A2) := 5.08*(A1*A2)/r**3
```
