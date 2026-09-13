# PHYSICAL CONSTANTS USED IN TRANSMISSION LINE WORK

> Source: `CONSTANT.pdf` — worksheet `CONSTANT.xmcd` — original `constant.mcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

Electric permittivity of free space (metric)

```text
E0_meters := 8.854*10**(-12)
```

F/m

Recalculate in in.

```text
E0_inches := E0_meters*.0254
E0_inches = 2.248916e-13
```

Display calculated value

Magnetic permeability of free space (metric)

```text
U0_meters := 4*π*10**(-7)
```

H/m

Recalculate in in.

```text
U0_inches := U0_meters*.0254
U0_inches = 3.191858136e-8
```

Display calculated value

We often need this number

```text
U0_inches/(2*π) = 5.08E-09
```

Speed of light (metric)

```text
C_meters := 2.998*10**8
```

m/s

```text
C_inches := C_meters/.0254
```

Recalculated in in.

```text
C_inches = 1.180314961e10
```

Display calculated value

```text
10**12/C_inches = 84.72314877
```

Propagation delay at light speed (ps/in.)
