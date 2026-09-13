"""Transmission lines made of wire: round wire over ground, coax, twisted pair.

Transcribed from ROUND.mcd, COAX.mcd and TWIST.mcd.

All three sheets have the same four-function shape:
    Z...()  characteristic impedance (ohms)
    P...()  propagation delay (s/in.)
    L...()  total inductance (H) over a length x
    C...()  total capacitance (F) over a length x
"""

from math import sqrt, log


# --- ROUND.mcd: round wire above a ground plane (wire-wrap) ---------------
# The wire is assumed suspended in air, so er = 1.00 and the delay is just
# the speed of light.

def ZROUND(d, h):
    """Characteristic impedance (ohms) of round wire above a ground plane.

    d   diameter of the wire (in.)
    h   height of the wire above ground (in.)
    """
    return 60 * log(4 * h / d)


def PROUND(d, h):
    """Propagation delay (s/in.). Air dielectric, so this is a constant."""
    return 84.72e-12


def LROUND(d, h, x):
    """Inductance (H) of a round wire of length x (in.) above ground."""
    return x * 5.08e-9 * log(4 * h / d)


def CROUND(d, h, x):
    """Capacitance (F) of a round wire of length x (in.) above ground."""
    return x * 1.413e-12 / log(4 * h / d)


# --- COAX.mcd: coaxial cable ----------------------------------------------

def ZCOAX(d1, d2, er):
    """Characteristic impedance (ohms) of coaxial cable.

    d1  diameter of the inner wire (in.)
    d2  inside diameter of the outer shield (in.)
    er  relative dielectric constant surrounding the inner wire
    """
    return 60 / sqrt(er) * log(d2 / d1)


def PCOAX(er):
    """Propagation delay (s/in.) of coaxial cable."""
    return 84.72e-12 * sqrt(er)


def LCOAX(d1, d2, x):
    """Inductance (H) of a coaxial cable of length x (in.)."""
    return x * 5.08e-9 * log(d2 / d1)


def CCOAX(d1, d2, er, x):
    """Capacitance (F) of a coaxial cable of length x (in.)."""
    return (x * 1.41e-12 / log(d2 / d1)) * er


# --- TWIST.mcd: twisted pair ----------------------------------------------
# Same forms as coax, but with 2s/d instead of d2/d1 and twice the
# inductance coefficient, because both wires carry the field.

def ZTWIST(d, s, er):
    """Characteristic impedance (ohms) of twisted pair.

    d   diameter of the wire (in.)
    s   separation between wire centers (in.)
    er  effective relative dielectric constant of the medium between wires
    """
    return 120 / sqrt(er) * log(2 * s / d)


def PTWIST(er):
    """Propagation delay (s/in.) of twisted pair."""
    return 84.72e-12 * sqrt(er)


def LTWIST(d, s, x):
    """Inductance (H) of a twisted pair of length x (in.)."""
    return x * 10.16e-9 * log(2 * s / d)


def CTWIST(d, s, er, x):
    """Capacitance (F) of a twisted pair of length x (in.)."""
    return (x * 0.7065e-12 / log(2 * s / d)) * er
