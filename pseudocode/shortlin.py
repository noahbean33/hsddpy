"""Transmission line simulator -- unterminated lines, risetime vs. delay.

Transcribed from SHORTLIN.mcd (H. Johnson, 5/29/95).

PSEUDOCODE. Unlike the closed-form sheets in this directory, this one is a
frequency-domain simulation: it builds the system response over a grid of
frequency points, multiplies by the spectrum of a driving step, and inverse
FFTs back to a waveform. It is written against numpy but has not been run.

Order of operations:
  1. establish indices for the FFT
  2. generate the frequency response of the unterminated line
  3. convert to a time-domain waveform and display

Mathcad notes carried over:
  * Mathcad's vectorize operator (an arrow over an expression) forces
    element-by-element evaluation; numpy does that by default, so the
    mpy()/div() helpers below exist only to keep the transcription honest.
  * Mathcad indexes s[k] over the half-spectrum, k = 0 .. N/2.
"""

import numpy as np

# --- 1. indices for FFT operations ---------------------------------------

DT = 1e-10                      # sampling resolution, seconds
FSAMPLE = 1 / DT
TLEN = 100e-9                   # desired trace length, seconds

LOGN = np.ceil(np.log(TLEN / DT) / np.log(2))   # next biggest power of two
N = int(np.floor(2 ** LOGN + 0.5))

j = np.arange(0, N)             # index to time points
k = np.arange(0, N // 2 + 1)    # index to frequency points

f = FSAMPLE * k / N             # list of frequency points
s = 2j * np.pi * f              # complex frequency


def mpy(A, B):
    """Mathcad vectorized multiply."""
    return A * B


def div(A, B):
    """Mathcad vectorized divide."""
    return A / B


# --- 2. frequency response of the unterminated line ----------------------

ZS = 30         # source impedance (ohms): ECL = 10, TTL/CMOS = 30
RL = 10000      # load resistance (ohms)
ZC = 65         # transmission line impedance (ohms)


def ZL(cl):
    """Load impedance: RL in parallel with load capacitance cl."""
    return div(RL, 1 + s * RL * cl)


def D(t):
    """Delay operator; t is the delay in seconds."""
    return np.exp(-s * t)


def H(t):
    """Transmission line response -- delay only, no distortion assumed."""
    return D(t)


A = div(ZC, ZS + ZC)        # acceptance function
R1 = 1 - 2 * A              # near-end reflection, = (ZS-ZC)/(ZS+ZC)


def T(cl):
    """Transmission function at the far end."""
    return div(2 * ZL(cl), ZL(cl) + ZC)


def R2(cl):
    """Far-end reflection."""
    return T(cl) - 1


def S3(t, cl):
    """System response: forward path over the multiple-reflection sum."""
    return div(
        mpy(A, mpy(H(t), T(cl))),
        1 - mpy(mpy(R2(cl), H(t)), mpy(R1, H(t))),
    )


# Driving waveform: a rectangular waveform N/2 points long.
# np.where evaluates both branches eagerly, so the false branch is fed a
# safe stand-in denominator at k == 0 (where it is 0/0) purely to keep numpy
# from warning about a value that gets discarded anyway.
_denom = np.where(k == 0, 1, 1 - np.exp(-s * DT))
S1 = np.where(
    k == 0,
    N / 2,
    (1 - np.exp(-s * N / 2 * DT)) / _denom,
) * (1 / FSAMPLE)


def linear(mu, r):
    """Linear rise/fall slopes; 0-100% risetime = r."""
    denom = np.where(mu == 0, 1, 1 - np.exp(-mu * DT))
    return np.where(mu == 0, 1,
                    (1 - np.exp(-mu * r)) / denom * DT / r)


def gaussian(mu, r):
    """Gaussian rise/fall slopes; 10-90% risetime = r."""
    safe = np.where(np.abs(mu * r) < 10, mu, 0)
    return np.where(np.abs(mu * r) < 10,
                    np.exp((safe ** 2 * (r / 2.56) ** 2) / 2),
                    0) * np.exp(-mu * r / 2)


def S2(r):
    """Edge shaping. Swap in linear() here to use linear slopes instead."""
    return gaussian(s, r)


# --- 3. convert to the time domain ---------------------------------------

def _ifft(spectrum):
    """Mathcad's IFFT over a half-spectrum of N/2+1 points."""
    return np.fft.irfft(spectrum, n=N)


SYS1 = _ifft(S1) * FSAMPLE / N
"""Ideal driving waveform."""


def SYS2(r):
    """Driving waveform with rise/fall slopes."""
    return _ifft(mpy(S1, S2(r))) * FSAMPLE / N


def SYS3(d, r, cl):
    """Response of the driven trace.

    d   transmission line delay (s)
    r   risetime (s)
    cl  load capacitance (F)
    """
    return _ifft(mpy(mpy(S1, S2(r)), S3(d, cl))) * FSAMPLE / N


# --- worked cases from the worksheet -------------------------------------

if __name__ == '__main__':
    # It's the risetime/delay ratio that counts: scale both together.
    delay = 1e-9
    risetime = 2 * delay
    CL = 0

    X1 = SYS3(delay, risetime, CL)
    X2 = SYS3(delay * 2, risetime * 2, CL)
    X3 = SYS3(delay * 3, risetime * 3, CL)

    # Risetime swept from 0 to 6 times the line delay.
    X0 = SYS3(delay, 0, CL)
    sweep = [SYS3(delay, delay * i, CL) for i in range(1, 7)]

    # Effect of termination capacitance on a 1/2 ns line.
    delay = 0.5e-9
    risetime = 6 * delay
    NOLOAD, TEN_PF, TWENTY_PF = 0, 10e-12, 20e-12

    Y1 = S3(delay, NOLOAD)      # frequency response
    Y2 = S3(delay, TEN_PF)
    Y3 = S3(delay, TWENTY_PF)

    # The knee frequency of the driving waveform is 160 MHz
    # (3 ns rise/fall time).
