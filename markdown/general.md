# GENERAL RELATIONS AMONG TRANSMISSION LINE PARAMETERS

> Source: `GENERAL.pdf` — worksheet `GENERAL.xmcd` — original `general.mcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Conversion formulas included in this spreadsheet

- Inductance and capacitance to impedance — `Z0()`
- Inductance and capacitance to propagation delay — `PDLY1()`
- Effective permittivity to propagation delay — `PDLY2()`
- Impedance and propagation delay to capacitance — `CPI()`
- Impedance and propagation delay to inductance — `LPI()`

## Variables used

- `lpi` — Inductance per inch (H)
- `cpi` — Capacitance per inch (F)
- `pdly` — Propagation delay (s/in.)
- `z0` — Line impedance (Ω)
- `eeff` — Effective relative permittivity

Given inductance per inch and capacitance per inch, find the characteristic impedance in ohms:

```text
Z0(lpi, cpi) := sqrt(lpi/cpi)
```

Given inductance per inch and capacitance per inch, find the propagation delay per inch:

```text
PDLY1(lpi, cpi) := sqrt(lpi*cpi)
```

Given the effective electric permittivity of the surrounding medium, find the propagation delay per inch:

```text
PDLY2(eeff) := 84.72*10**(-12)*sqrt(eeff)
```

Given impedance and propagation delay, find the capacitance per inch:

```text
CPI(zo, pdly) := pdly/zo
```

Given impedance and propagation delay, find the inductance per inch:

```text
LPI(zo, pdly) := zo*pdly
```
