# DC RESISTANCE OF COPPER WIRES AND TRACES

> Source: `RESIST.pdf` — worksheet `RESIST.xmcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

## Conversion formulas included in this spreadsheet

- Diameter to AWG — `AWG()`
- AWG to diameter — `DIAMETER()`
- Thickness to copper plating weight — `CPW()`
- Copper plating weight to thickness — `THICKNESS()`

## Resistance formulas included in this spreadsheet

**DC resistance of round wires**

- From diameter — `RROUND()`
- From AWG wire size — `RROUND_AWG()`
- At room temperature only — `RROUND_RT()`

**DC resistance of printed circuit board traces**

- From trace thickness and width — `RTRACE()`
- Using copper plating weight — `RTRACE_CPW()`
- At room temperature only — `RTRACE_RT()`

**DC resistance of power or ground planes**

- Using thickness and via diameter — `RPLANE()`
- Using copper plating weight — `RPLANE_CPW()`

## Variables used

```text
ρ := 6.787*10**(-7)
```

- `ρ` — Bulk resistivity of copper

ohm-in.

This coefficient is slightly different from the bulk resistivity of pure copper (6.58E-07) owing to the annealing process used in making wire, and chemical imperfections in the copper used for making practical wires.

In practice, the resistance of two wires making up a twisted pair may often be matched as well as 10%, but almost never as well as 1%.

δ ρ Thermal coefficient of resistance

```text
δρ := .0039
```

per deg. C

If the resistance of a copper wire is R at room temperature, then at a temperature 1oC higher it will be R(1 + δ ρ). This coefficient applies to standard annealed copper wires. The coefficient for pure copper in its bulk state varies slightly.

Over a temperature range 0-70oC the resistance of copper wires varies 28%.

- `x` — Length of wire (in.) (or separation between contact points on ground plane)
- `d` — Diameter of wire (in.) (or diameter of contact point on ground plane)
- `AWG` — American wire gauge (English units)
- `temp` — Temperature (oC)
- `w` — Width of printed circuit board trace (in.)
- `t` — Thickness of printed circuit board trace (in.)
- `cpw` — Thickness of printed circuit board traces, in units of copper plating weight (oz/ft2)

```text
DIAMETER(awg) := 10**(-((awg + 10)/20))
```

Conversions between American Wire Gauge (AWG) and diameter (in.):

```text
AWG(d) := -10 - 20*log(d)
```

General formula for resistance of a round wire (Ω):

```text
RROUND(d, x, temp) := (4*ρ*x)/(π*d**2)*(1 + (temp - 20)*δρ)
```

Resistance of a round wire specified by AWG size instead of diameter (Ω):

```text
RROUND_AWG(awg, x, temp) := RROUND(DIAMETER(awg), x, temp)
```

Resistance of a round wire at room temperature (Ω):

```text
RROUND_RT(d, x) := RROUND(d, x, 20)
```

Conversion between thickness, t (in.) and copper plating weight, cpw (oz):

```text
CPW(t) := t/.00137
THICKNESS(cpw) := .00137*cpw
```

Resistance of a circuit trace (Ω):

```text
RTRACE(w, t, x, temp) := (x*ρ)/(w*t)*(1 + (temp - 20)*δρ)
```

Resistance of a trace specified by plating weight instead of thickness (Ω):

```text
RTRACE_CPW(w, cpw, x, temp) := RTRACE(w, THICKNESS(cpw), x, temp)
```

Resistance of a circuit trace at room temperature (Ω):

```text
RTRACE_RT(w, t, x) := RTRACE(w, t, x, 20)
```

Resistance of a power or ground plane (Ω):

When using long, skinny traces or wires, the approximations above work extremely well. Each formula assumes a uniform distribution of current throughout the conducting body, for which resistance is directly proportional to length.

Currents circulating in a large ground or power plane are not uniform. Consequently, the resistance measured between two points on a ground or power plane is not directly proportional to the separation between measurement points.

The following equation models the resistance between two contact points on a ground plane. This model assumes each contact point touches the ground plane over some finite area. The approximate diameter of the contact point determines the overall resistance.

If the contact points lie near any edge of the plane, the resistance between them may go up by a factor of 2. The resistance near corners may rise even higher.

- `d1` — Diameter of 1st contact point (in.)
- `d2` — Diameter of 2nd contact point (in.)
- `t` — Thickness of plane (in.)
- `cpw` — Thickness of plane, copper plating weight (oz)
- `x` — Separation between contact points (in.)
- `temp` — Temperature (oC)

Resistance of a power or ground plane (Ω):

```text
RPLANE(d1, d2, t, x, temp) := ρ/(2*π*t)*(ln((2*x)/d1) + ln((2*x)/d2))*(1 + (temp - 20)*δρ)
```

Resistance of a power or ground plane specified by plating weight instead of thickness (Ω):

```text
RPLANE_CPW(d1, d2, cpw, x, temp) := RPLANE(d1, d2, THICKNESS(cpw), x, temp)
```
