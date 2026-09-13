"""Microstrip transmission lines.

Transcribed from MSTRIP.mcd.

Formulas from I. J. Bahl and Ramesh Garg, "Simple and accurate formulas for
microstrip with finite strip thickness", Proc. IEEE 65, 1977, pp. 1611-1612;
summarized in T. C. Edwards, "Foundations of Microstrip Circuit Design",
John Wiley, 1981 (watch out for Edwards' error in Eq. 3.52b, where he omits
an ln()).

Variables
    h   trace height above ground (in.)
    w   trace width (in.)
    t   trace thickness (in.)
    er  relative permittivity between trace and ground plane
    x   trace length (in.)

Each quantity has a "skinny" and a "wide" model, with a composite function
that picks between them. Accuracy is better than 2% for
    0   < t/h < 0.2
    0.1 < w/h < 20
    0   < er  < 16
"""

from math import pi, sqrt, log


# --- effective relative permittivity --------------------------------------

def E_skny(h, w, er):
    """Effective permittivity, skinny-trace model (w < h)."""
    return (er + 1) / 2 + ((er - 1) / 2) * (
        (1 + 12 * h / w) ** -0.500 + 0.04 * (1 - w / h) ** 2
    )


def E_wide(h, w, er):
    """Effective permittivity, wide-trace model (w > h)."""
    return (er + 1) / 2 + ((er - 1) / 2) * (1 + 12 * h / w) ** -0.500


def E_temp(h, w, er):
    """Composite: picks the skinny or wide model on the w/h ratio.

    Skinny traces give roughly the average of the board permittivity and
    that of air; wide traces (trace close to the ground plane) give er.
    """
    return E_wide(h, w, er) if w > h else E_skny(h, w, er)


def EEFF(h, w, t, er):
    """Effective relative permittivity, adjusted for trace thickness."""
    return E_temp(h, w, er) - ((er - 1) * (t / h)) / (4.6 * sqrt(w / h))


# --- effective electrical trace width -------------------------------------

def WE_skny(h, w, t):
    """Effective trace width (in.), skinny-trace model (2*pi*w < h)."""
    return w + (1.25 * t) / pi * (1 + log(4 * pi * w / t))


def WE_wide(h, w, t):
    """Effective trace width (in.), wide-trace model (2*pi*w > h)."""
    return w + (1.25 * t) / pi * (1 + log(2 * h / t))


def WE(h, w, t):
    """Composite effective trace width (in.)."""
    return WE_wide(h, w, t) if w > h / (2 * pi) else WE_skny(h, w, t)


# --- impedance, delay, inductance, capacitance ----------------------------

def ZMS_skny(h, w, t):
    """Impedance (ohms) before the permittivity divide, skinny model."""
    we = WE(h, w, t)
    return 60 * log(8 * h / we + we / (4 * h))


def ZMS_wide(h, w, t):
    """Impedance (ohms) before the permittivity divide, wide model."""
    we = WE(h, w, t)
    return (120 * pi) / (we / h + 1.393 + 0.667 * log(we / h + 1.444))


def ZMSTRIP(h, w, t, er):
    """Characteristic impedance (ohms) of microstrip."""
    z = ZMS_wide(h, w, t) if w > h else ZMS_skny(h, w, t)
    return z / sqrt(EEFF(h, w, t, er))


def PMSTRIP(h, w, t, er):
    """Propagation delay (s/in.) of microstrip."""
    return 84.72e-12 * sqrt(EEFF(h, w, t, er))


def LMSTRIP(h, w, t, x):
    """Inductance (H) of a microstrip of length x (in.).

    Uses a dummy er of 1: permittivity does not affect inductance.
    """
    return PMSTRIP(h, w, t, 1.0) * ZMSTRIP(h, w, t, 1.0) * x


def CMSTRIP(h, w, t, er, x):
    """Capacitance (F) of a microstrip of length x (in.)."""
    return PMSTRIP(h, w, t, er) / ZMSTRIP(h, w, t, er) * x


# --- tolerance analysis ---------------------------------------------------

def ZMSTRIP_TOL(h, dh, w, dw, t, er, der):
    """Impedance at the two tolerance corners and at nominal.

    Returns [high, nominal, low]. The high corner stacks the height, width
    and permittivity errors that all push impedance up; the low corner
    stacks the ones that push it down.
    """
    return [
        ZMSTRIP(h + dh, w - dw, t, er - der),
        ZMSTRIP(h, w, t, er),
        ZMSTRIP(h - dh, w + dw, t, er + der),
    ]


def REFL(x, z):
    """Reflection coefficient of each impedance in x against a source z."""
    return [(z - xi) / (z + xi) for xi in x]
