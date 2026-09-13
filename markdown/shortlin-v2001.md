# Transmission Line Simulator

*H. Johnson, 5/29/95*

> Source: `SHORTLIN.PPT / SHORTLIN EXAMPLES.pdf` — worksheet `SHORTLIN V2001.xmcd` — original `shortlin.mcd`  
> From the Mathcad 13.1 companion files to *High-Speed Digital Design:
> A Handbook of Black Magic* (Howard Johnson & Martin Graham).

Investigation of untermiated lines showing effects of rise time and line length. Order of operations: Establish indices for FFT operations, generate frequency response of unterminated line, convert to time domain waveform and display.

Establish indices for FFT operations

Sampling resolution, in seconds

```text
ΔT := 10**(-10)
fsample := 1/ΔT
```

Desired trace length, in seconds

```text
Tlen := 100*10**(-9)
logN := ceil(log(Tlen/ΔT)/log(2))
```

Pick next biggest power of two trace length

```text
N := floor(2**logN + 0.5)
```

Index to time points

```text
j := 0, 1 .. N - 1
```

Index to frequency points

```text
k := 0, 1 .. N/2
f[k] := fsample*k/N
```

List of frequency points

```text
s := 2j*π*f
```

Dummy vector used to vectorize some scaler functions

```text
Vdummy[k] := 1
mpy(A, B) := vectorize((A*B))
div(A, B) := vectorize(A/B)
```

Vector operations

Source impedance

```text
ZS := 30
RL := 10000
```

Load impedance

```text
ZL(cl) := div(RL, 1 + s*RL*cl)
```

cl = load capacitance

Transmission line impedance

```text
ZC := 65
```

Delay function, argument t is delay in seconds

```text
D(t) := vectorize(exp(-s*t))
```

Generate frequency response of unterminated line

Transmission line response (delay only, assume no distortion)

```text
H(t) := D(t)
```

Acceptance function

```text
A := div(ZC, ZS + ZC)
```

Near-end reflection

```text
R1 := 1 - 2*A
```

Transmission function at far end

```text
T(cl) := div(2*ZL(cl), ZL(cl) + ZC)
```

Far-end reflection

```text
R2(cl) := T(cl) - 1
```

System response

```text
S3(t, cl) := div(mpy(A, mpy(H(t), T(cl))), 1 - mpy(mpy(R2(cl), H(t)), mpy(R1, H(t))))
S1[k] := if(k == 0, N/2, (1 - e**(-s[k]*N/2*ΔT))/(1 - e**(-s[k]*ΔT)))*1/fsample
```

Driving waveform (a rectangular waveform, N/2 points in length)

```text
linear(μ, r) := if(μ == 0, 1, (1 - e**(-μ*r))/(1 - e**(-μ*ΔT))*ΔT/r)
```

Linear rise/fall slopes; 0-100% risetime = r

```text
gaussian(μ, r) := if(abs(μ*r) < 10, e**((μ**2*(r/2.56)**2)/2), 0)*e**(-μ*r/2)
```

Gaussian rise/fall slopes, 10-90% risetime = r

Use linear or gaussian slope

```text
S2(r) := vectorize(gaussian(s, r))
```

Convert to time domain and display

Ideal driving waveform

```text
SYS1 := IFFT(S1)*fsample/N
```

Driving waveform with rise/fall slopes

```text
SYS2(r) := IFFT(mpy(S1, S2(r)))*fsample/N
```

Response of driven trace

```text
SYS3(d, r, cl) := IFFT(mpy(mpy(S1, S2(r)), S3(d, cl)))*fsample/N
```

Set nominal transmission line delay and risetime

```text
delay := 10**(-9)
RL = 10000
ZS = 30
risetime := 2*delay
ZC = 65
CL := 0
```

Scale both delay and risetime to see what happens

```text
X1 := SYS3(delay, risetime, CL)
X2 := SYS3(delay*2, risetime*2, CL)
X3 := SYS3(delay*3, risetime*3, CL)
```

*Plot*

Sample some test functions

```text
X0 := SYS3(delay, 0, CL)
X01 := SYS3(delay, delay, CL)
X02 := SYS3(delay, delay*2, CL)
X03 := SYS3(delay, delay*3, CL)
X04 := SYS3(delay, delay*4, CL)
X05 := SYS3(delay, delay*5, CL)
X06 := SYS3(delay, delay*6, CL)
RL = 10000
```

Unterminated line response Risetime set to 0, 2 and 3 times transmission line delay

```text
ZS = 30
ZC = 65
CL = 0
```

*Plot*

```text
ZS = 30
RL = 10000
```

Unterminated line response Risetime set to 4, 5 and 6 times transmission line delay

```text
ZC = 65
CL = 0
```

*Plot*

Unterminated line response Risetime set to 4, 5 and 6 times transmission line delay BLOWUP of vertical axis

```text
ZS = 30
RL = 10000
ZC = 65
CL = 0
```

*Plot*

Investigate effect of termination capacitance

Set nominal transmission line delay and risetime

```text
delay := .5*10**(-9)
RL = 10000
ZS = 30
risetime := 6*delay
ZC = 65
NOLOAD := 0
TEN_PF := 10*10**(-12)
TWENTY_PF := 20*10**(-12)
```

Adjust load capacitance and produce step response for each c ase

```text
X1 := SYS3(delay, risetime, NOLOAD)
X2 := SYS3(delay, risetime, TEN_PF)
X3 := SYS3(delay, risetime, TWENTY_PF)
```

Step response of 1/2 ns line with 0, 10 and 20 pF load BLOWUP of vertical axis

*Plot*

Record frequency response for each value of load capacitance

```text
Y1 := S3(delay, NOLOAD)
Y2 := S3(delay, TEN_PF)
Y3 := S3(delay, TWENTY_PF)
```

Frequency response of 1/2 ns line with 0, 10 and 20 pF load

*Plot*

Hz ->

Knee frequency of driving waveform is 160 MHz (3-ns rise/fall time)
