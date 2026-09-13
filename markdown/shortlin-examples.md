# Short Transmission Line Examples

> Source: `SHORTLIN EXAMPLES.pdf` (exported from `SHORTLIN.PPT`) — copyright 1994.
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

A nine-slide deck of step-response plots produced by the `SHORTLIN` worksheet
(see [shortlin-v2001.md](shortlin-v2001.md)). The substance of each slide is
the waveform plot; only the captions and parameter sets are reproduced here.

## Slide 1 — Setup

Lossless, distortionless transmission line driven by a unit step.

- Source impedance: ECL = 10 Ω, TTL/CMOS = 30 Ω
- Load impedance: `RL` = 10 kΩ, `CL` = zero or 20 pF
- IDEAL risetime = 6 × (line delay)

## Slide 2 — It's the Risetime/Delay Ratio that Counts

Set nominal transmission line delay and risetime, then scale both together to
see what happens:

```text
delay    := 10**(-9)
risetime := 2*delay

X1 := SYS3(delay,   risetime)
X2 := SYS3(delay*2, risetime*2)
X3 := SYS3(delay*3, risetime*3)
```

Parameters: `ZS` = 10 Ω, `RL` = 1×10⁴ Ω, `ZC` = 65 Ω, `CL` = 0.

*Plot: response versus time, 0 to 2×10⁻⁸ s.*

## Slide 3 — ECL, unterminated line response

Risetime set to 0, 2 and 3 times transmission line delay.

Parameters: `ZS` = 10 Ω, `RL` = 1×10⁴ Ω, `ZC` = 65 Ω, `CL` = 0.

*Plot: time in units of line delay, 0 to 20.*

## Slide 4 — ECL, unterminated line response

Risetime set to 4, 5 and 6 times transmission line delay.

Parameters: `ZS` = 10 Ω, `RL` = 1×10⁴ Ω, `ZC` = 65 Ω, `CL` = 0.

*Plot: time in units of line delay, 0 to 20.*

## Slide 5 — ECL, unterminated line response (blowup)

Risetime set to 4, 5 and 6 times transmission line delay.
BLOWUP of vertical axis.

Parameters: `ZS` = 10 Ω, `RL` = 1×10⁴ Ω, `ZC` = 65 Ω, `CL` = 0.

*Plot: time in units of line delay, 0 to 20.*

## Slide 6 — TTL/CMOS, unterminated line response

Risetime set to 0, 2 and 3 times transmission line delay.

Parameters: `ZS` = 30 Ω, `RL` = 1×10⁴ Ω, `ZC` = 65 Ω, `CL` = 0.

*Plot: time in units of line delay, 0 to 20.*

## Slide 7 — TTL/CMOS, unterminated line response

Risetime set to 4, 5 and 6 times transmission line delay.

Parameters: `ZS` = 30 Ω, `RL` = 1×10⁴ Ω, `ZC` = 65 Ω, `CL` = 0.

*Plot: time in units of line delay, 0 to 20.*

## Slide 8 — TTL/CMOS, unterminated line response (blowup)

Risetime set to 4, 5 and 6 times transmission line delay.
BLOWUP of vertical axis.

Parameters: `ZS` = 30 Ω, `RL` = 1×10⁴ Ω, `ZC` = 65 Ω, `CL` = 0.

*Plot: time in units of line delay, 0 to 20.*

## Slide 9 — TTL/CMOS with capacitive load (20 pF)

Unterminated line response, risetime set to 4, 5 and 6 times transmission
line delay. BLOWUP of vertical axis.

Parameters: `ZS` = 30 Ω, `RL` = 1×10⁴ Ω, `ZC` = 65 Ω, `CL` = 2×10⁻¹¹ F.

*Plot: time in units of line delay, 0 to 20.*
