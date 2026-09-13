# This is an experimental spreadsheet used to gauge the impact of various patterns of ground/power pins in a high-speed digital connector. See MSWORD 6.0 file gndpins.doc .

> Source: `GNDPINS.pdf` — worksheet `GNDPINS.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

Gndpins.mcd -- crosstalk in connectors

Magnetic field intensity at a point x, given current flow of 1 amp in a wire located at position p. All positions in a 2-dimensional plane. Positions on the plane are represented by complex quantities (this results in more convenient notation than if I had used little 2-element vectors to represent each quantity).

Magnetic permeability of free space

```text
μ0 := 4*π*10**(-7)
```

Wire radius (m)

```text
R := 0.01*.0254
B(x, p) := if(abs(x - p) > R, μ0/(2*π*abs(x - p)), 0)
```

Length of connector pins

Wire length (m)

```text
L := 0.5*.0254
```

Elemental flux induced at point v, located on flux integration path between points X and Y, due to durrent flow of 1 amp at position p.

Dot product operator applied to our complex position variables

```text
dot(a, b) := Re(a*conj(b))
dφ(v, x, y, p) := B(v, p)*dot((y - x), (p - v))/(abs(y - x)*abs(p - v))
```

Integral of flux between wires located at points X and Y, due to flow of 1 amp at position p

```text
φ(x, y, p) := INTEGRAL(lambda v: dφ(v, x, y, p)*L; x, y)
```

Where the integration variable, v, traces a path from x to y

Change the flux integration path to first circumscrbe a circle of constant radius about the current source, starting at point x andending at a location nearest to point y. Now complete the integral, moving radially out towards point y. On the circumscribed path, the dot product is always zero, so we get no result. On the radial path, the dot product is always unity. Furthermore, along the radial path the integrand is a function of 1/R, which integrates to log(R).

```text
φ(x, y, p) := μ0/(2*π)*ln(if(abs(y - p) > R, abs(y - p), R)/if(abs(x - p) > R, abs(x - p), R))*L
```

Define wire positions. M and N need not necessarily be equal.

Standard pin spacing (m)

```text
D := 0.05*0.0254
N := 50
n := 0, 1 .. N - 1
```

Ground wires, row 1

```text
g[n] := n + 1j
```

Where the position "g" has an imaginary "j" (vertical) component and a real (horizontal) component.

Signal wires, row 2

```text
p1[n] := n + 2j
```

This arrangement has all the grounds on row 1. Change the equations to scatter the ground positions.

row 3

```text
p2[n] := n + 3j
```

row 0

```text
p3[n] := n + 0j
M := N*3
m := 0, 1 .. M - 1
append(a, b) := transpose(augment(transpose(a), transpose(b)))
p := append(p1, append(p2, p3))
fixpos(x) := D*(Re(x) + 1j*mod(Im(x), 4))
p := vectorize(fixpos(p))
g := vectorize(fixpos(g))
```

Matrix showing flux induced in various ground loops, due to flow of 1 amp in wire located at position p

```text
nLessOne := 0, 1 .. N - 2
B[nLessOne, m] := φ(g[nLessOne], g[nLessOne + 1], p[m])
```

Matrix relating flux in each ground loop to flow of current in other ground wires.

```text
A[nLessOne, n] := φ(g[nLessOne], g[nLessOne + 1], g[n])
```

Column <m> of matrix B shows how signal currents affect the flux in each ground loop. The matrix A shows how ground currents affect the flux in each ground loop. For each possible signal current (that is, for each column of B), the pattern of ground currents must be such that the total flux through each ground loop is zero. Arranging the ground current solutions as columns of a matrix G, we get:

```text
A*G[:, m] + B[:, m] := 0
```

- OR -

```text
A*G + B := 0
```

The above constraints are insufficient to completely solve our problem. The matrix A is of size (N-1)xN, because while there are N ground currents, there are only (N-1) ground current loop constraints. We need an Nth constraint to solve the problem. The last constraint is found by forcing the sum of all ground currents to equal the signal current (that is, all curent going out must find a way back along the grounds). We will add an Nth row to matrices A and B to effect this constraint.

Bottom row of matrix represents our last constraint, which says that the sum of all currents has to equal zero.

```text
A[N - 1, n] := 1
```

Sum of ground currents and source current equals zero

```text
B[N - 1, m] := 1
```

Solve for vectors of ground currents. Each column represents ground excitation by a different agressor source.

```text
G := -(A**(-1)*B)
```

Plot out calculated versus ideal distribution

```text
nPlusOne := 0, 1 .. N
Gd := G
Gd[N, m] := 0
g[N] := 0
```

*Plot*

Compute crosstalk voltage received between wires positioned at any points x and y in space, as a result of current flowing on wire m, with consideration given to currents induced on all ground wires.

Aggressor current dI/dt on each signal

```text
dIdt[m] := 4/50*1/10**(-9)
```

Note: these could be different for different net classes

```text
voltage(x, y, m) := (φ(x, y, p[m]) + SUM(lambda n: (φ(x, y, g[n])*G[n, m])))*dIdt[m]
```

Matrix of output crosstalk voltages, as a function of signal currents

```text
k := 0, 1 .. M - 1
V[k, m] := voltage(p[k], g[0], m)
```

Vectorize the above equation

How signal currents affect other signal voltages

```text
C[k, m] := φ(p[k], g[0], p[m])
```

How ground currents affect signal voltages

```text
D[k, n] := φ(p[k], g[0], g[n])
V := C + D*G
```

Scale by dIdt on each signal wire

```text
V[k, m] := V[k, m]*dIdt[m]
```

Zero out self-crosstalk terms

```text
V[m, m] := 0
```

Evaluate worst case crosstalk on a line-by-line basis

```text
V[k, m] := abs(V[k, m])
V := transpose(V)
XTLK[m] := sum(V[:, m])
WRITEPRN("straight.prn") := XTLK
```

I have pre-computed and stored the two configurations documented in gndpins.doc.

```text
WRITEPRN("scatter.prn") := XTLK
XSTRAIGHT := READPRN("straight.prn")
```

The graph below displays these two pre-computed solutions.

```text
XSCATTER := READPRN("scatter.prn")
```

*Plot*
