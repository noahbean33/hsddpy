"""Stripline transmission lines, centered and offset.

Transcribed from SLINE.mcd (file SLINE2.xmcd).

Formulas from Seymour Cohn, "Problems in Strip Transmission Lines", MTT-3
No. 2, March 1955; summarized in Harlan Howe, "Stripline Circuit Design",
Artech House, 1974.

The worksheet notes that ZSTR_K1() was corrected per instructions from
Robert Canright of Richardson, TX.

Variables
    h1  trace height above the lower ground plane (in.)
    h2  trace headroom below the upper ground plane (in.)
    b   separation between ground planes, b = h1 + h2 + t (in.)
    w   trace width (in.)
    t   trace thickness (in.)
    er  relative permittivity
    x   trace length (in.)

Accuracy is better than 1.3% for t/b < 0.25 and t/w < 0.11, with er
unrestricted.
"""

from math import pi, sqrt, log


# --- centered stripline ---------------------------------------------------

def ZSTR_K1(w, t):
    """Skinny-trace shape factor."""
    return (w / 2) * (
        1 + t / (pi * w) * (1 + log(4 * pi * w / t)) + 0.255 * (t / w) ** 2
    )


def ZSTR_skny(b, w, t, er):
    """Impedance (ohms), skinny-trace model (w/b < 0.35)."""
    return 60 / sqrt(er) * log(4 * b / (pi * ZSTR_K1(w, t)))


def ZSTR_K2(b, t):
    """Wide-trace shape factor."""
    u = 1 - t / b
    return 2 / u * log(1 / u + 1) - (1 / u - 1) * log(1 / u ** 2 - 1)


def ZSTR_wide(b, w, t, er):
    """Impedance (ohms), wide-trace model (w/b > 0.35)."""
    return 94.15 / (w / b / (1 - t / b) + ZSTR_K2(b, t) / pi) * 1 / sqrt(er)


def ZSTRIP(b, w, t, er):
    """Characteristic impedance (ohms) of centered stripline."""
    if w > 0.35 * b:
        return ZSTR_wide(b, w, t, er)
    return ZSTR_skny(b, w, t, er)


# --- offset (asymmetric) stripline ----------------------------------------

def ZOFFSET(h1, h2, w, t, er):
    """Characteristic impedance (ohms) of offset stripline.

    Rarely are h1 and h2 equal in practice; the common case is a trace
    offset to one side. This models the two halves as two centered
    striplines in parallel. No accuracy is guaranteed for this one.
    """
    za = ZSTRIP(2 * h1 + t, w, t, er)
    zb = ZSTRIP(2 * h2 + t, w, t, er)
    return (2 * za * zb) / (za + zb)


# --- delay, inductance, capacitance ---------------------------------------

def PSTRIP(er):
    """Propagation delay (s/in.). Same for centered or offset stripline."""
    return 84.72e-12 * sqrt(er)


def LSTRIP(b, w, t, x):
    """Inductance (H) of a centered stripline of length x (in.).

    A relative permittivity of 1 is assumed; it does not affect the answer.
    """
    return PSTRIP(1.0) * ZSTRIP(b, w, t, 1.0) * x


def LOSTRIP(h1, h2, w, t, x):
    """Inductance (H) of an offset stripline of length x (in.)."""
    return PSTRIP(1.0) * ZOFFSET(h1, h2, w, t, 1.0) * x


def CSTRIP(b, w, t, er, x):
    """Capacitance (F) of a centered stripline of length x (in.).

    Here the real relative permittivity must be used.
    """
    return PSTRIP(er) / ZSTRIP(b, w, t, er) * x


def COSTRIP(h1, h2, w, t, er, x):
    """Capacitance (F) of an offset stripline of length x (in.)."""
    return PSTRIP(er) / ZOFFSET(h1, h2, w, t, er) * x


# --- tolerance analysis ---------------------------------------------------

def ZOFF_TOL(h1, dh1, h2, dh2, w, dw, t, er, der):
    """Offset-stripline impedance at the tolerance corners and nominal.

    Returns [high, nominal, low].
    """
    return [
        ZOFFSET(h1 + dh1, h2 + dh2, w - dw, t, er - der),
        ZOFFSET(h1, h2, w, t, er),
        ZOFFSET(h1 - dh1, h2 - dh2, w + dw, t, er + der),
    ]


def REFL(x, z):
    """Reflection coefficient of each impedance in x against a source z."""
    return [(z - xi) / (z + xi) for xi in x]
