"""Lumped capacitors and inductors, and what they look like to a rising edge.

Transcribed from CAPAC.mcd, CIRCULAR.mcd and RECTANGL.mcd.

All dimensions in inches. The XCR()/XLT() pair is the point of these sheets:
a rising edge does not see the impedance at one frequency, it sees the
impedance at the knee frequency, and these give you that directly.
"""

from math import pi, log


# --- CAPAC.mcd: capacitance of two parallel plates ------------------------

def CPLATE(w, x, h, er):
    """Capacitance (F) of two parallel plates.

    w   width of plate overlap (in.)
    x   length of plate overlap (in.)
    h   height of one plate above the other (in.)
    er  relative dielectric constant between the plates

    A power and ground plane 0.010 in. apart in FR-4 (er = 4.5) give
    100 pF/in.^2. Halving the separation doubles the capacitance.
    """
    return 2.249e-13 * (er * x * w) / h


def XCF(c, f):
    """Impedance magnitude (ohms) of capacitance c (F) at frequency f (Hz)."""
    return 1 / (2 * pi * f * c)


def XCR(c, tr):
    """Impedance magnitude (ohms) of capacitance c (F) seen by a rising edge.

    tr is the 10-90% rise time (s).
    """
    return tr / (pi * c)


# --- CIRCULAR.mcd: inductance of a circular loop --------------------------

def LCIRC(d, x):
    """Inductance (H) of a circular wire loop.

    d   diameter of the wire (in.)
    x   diameter of the loop (in.)

    A loop of 24-gauge wire the size of the loop between your thumb and
    forefinger has about 100 nH. The log makes it very insensitive to wire
    size: going from AWG 24 to AWG 14 barely changes the answer.
    """
    return 1.56e-8 * x * (log(8 * x / d) - 2)


# --- RECTANGL.mcd: inductance of a rectangular loop -----------------------

def LRECT(d, x, y):
    """Inductance (H) of a rectangular wire loop.

    d   diameter of the wire (in.)
    x   length of the loop (in.)
    y   breadth of the loop (in.)

    A loop of 24-gauge wire enclosing 1 in.^2 has about 100 nH. If the loop
    is made of different-sized conductors, use the diameter of the smallest.
    """
    return 10.16e-9 * (x * log(2 * y / d) + y * log(2 * x / d))


# --- shared by both inductance sheets -------------------------------------

def XLF(l, f):
    """Impedance magnitude (ohms) of inductance l (H) at frequency f (Hz)."""
    return 2 * pi * f * l


def XLT(l, tr):
    """Impedance magnitude (ohms) of inductance l (H) seen by a rising edge.

    tr is the 10-90% rise time (s). The worksheet index calls this XLR();
    the definition is named XLT(). Same function.
    """
    return pi * l / tr
