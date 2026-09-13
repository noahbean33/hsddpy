"""The worksheet function names, verbatim, for cross-checking against the book.

Every function here has the name, the argument order and the return units of
the Mathcad original, so a worksheet can be transliterated line for line and
the answers compared. They are thin wrappers over the rest of the library.

    >>> from hsdd.mathcad import ZMSTRIP
    >>> round(ZMSTRIP(.006, .008, .00137, 4.5), 6)
    56.443476

Use this module when checking the library against a worksheet. Use the rest
of the library for new work -- these signatures carry the quirks of a 1990s
Mathcad sheet, including one function (``MLOOP``) that returns nanohenries
while everything around it returns base units, and a pair of functions whose
first argument does nothing.
"""

from __future__ import annotations

from math import sqrt

from . import lumped, microstrip, resistance, stripline, wires
from .constants import PDLY_LIGHT
from .general import (
    capacitance_per_inch as _cpi,
    delay_from_er as _pdly2,
    delay_from_lc as _pdly1,
    inductance_per_inch as _lpi,
    z0_from_lc as _z0,
)

__all__ = [
    # GENERAL
    "Z0", "PDLY1", "PDLY2", "CPI", "LPI",
    # ROUND
    "ZROUND", "PROUND", "LROUND", "CROUND",
    # COAX
    "ZCOAX", "PCOAX", "LCOAX", "CCOAX",
    # TWIST
    "ZTWIST", "PTWIST", "LTWIST", "CTWIST",
    # MSTRIP
    "EEFF", "WE", "ZMSTRIP", "PMSTRIP", "LMSTRIP", "CMSTRIP", "ZMSTRIP_TOL",
    # SLINE
    "ZSTRIP", "ZOFFSET", "PSTRIP", "LSTRIP", "LOSTRIP", "CSTRIP", "COSTRIP",
    "ZOFF_TOL",
    # CAPAC / CIRCULAR / RECTANGL
    "CPLATE", "XCF", "XCR", "LCIRC", "LRECT", "XLF", "XLT",
    # MLINE / MLOOP
    "MLINE", "MLOOP",
    # RESIST
    "DIAMETER", "AWG", "CPW", "THICKNESS",
    "RROUND", "RROUND_AWG", "RROUND_RT",
    "RTRACE", "RTRACE_CPW", "RTRACE_RT",
    "RPLANE", "RPLANE_CPW",
    # shared
    "REFL",
]


# --- GENERAL.mcd ----------------------------------------------------------

def Z0(lpi, cpi):
    """Characteristic impedance (ohms) from L and C per inch."""
    return _z0(lpi, cpi)


def PDLY1(lpi, cpi):
    """Propagation delay (s/in.) from L and C per inch."""
    return _pdly1(lpi, cpi)


def PDLY2(eeff):
    """Propagation delay (s/in.) from effective relative permittivity."""
    return _pdly2(eeff)


def CPI(zo, pdly):
    """Capacitance per inch (F) from impedance and delay."""
    return _cpi(zo, pdly)


def LPI(zo, pdly):
    """Inductance per inch (H) from impedance and delay."""
    return _lpi(zo, pdly)


# --- ROUND.mcd ------------------------------------------------------------

def ZROUND(d, h):
    """Characteristic impedance (ohms) of round wire above a ground plane."""
    return wires.RoundWire(diameter=d, height=h).z0


def PROUND(d, h):
    """Propagation delay (s/in.). Air dielectric, so d and h do nothing."""
    return PDLY_LIGHT


def LROUND(d, h, x):
    """Inductance (H) of round wire of length x above a ground plane."""
    return wires.RoundWire(diameter=d, height=h).inductance(x)


def CROUND(d, h, x):
    """Capacitance (F) of round wire of length x above a ground plane."""
    return wires.RoundWire(diameter=d, height=h).capacitance(x)


# --- COAX.mcd -------------------------------------------------------------

def ZCOAX(d1, d2, er):
    """Characteristic impedance (ohms) of coaxial cable."""
    return wires.Coax(inner_diameter=d1, shield_diameter=d2, er=er).z0


def PCOAX(er):
    """Propagation delay (s/in.) of coaxial cable."""
    return PDLY_LIGHT * sqrt(er)


def LCOAX(d1, d2, x):
    """Inductance (H) of coaxial cable of length x."""
    return wires.Coax(inner_diameter=d1, shield_diameter=d2).inductance(x)


def CCOAX(d1, d2, er, x):
    """Capacitance (F) of coaxial cable of length x."""
    return wires.Coax(inner_diameter=d1, shield_diameter=d2, er=er).capacitance(x)


# --- TWIST.mcd ------------------------------------------------------------

def ZTWIST(d, s, er):
    """Characteristic impedance (ohms) of twisted pair."""
    return wires.TwistedPair(diameter=d, spacing=s, er=er).z0


def PTWIST(er):
    """Propagation delay (s/in.) of twisted pair."""
    return PDLY_LIGHT * sqrt(er)


def LTWIST(d, s, x):
    """Inductance (H) of twisted pair of length x."""
    return wires.TwistedPair(diameter=d, spacing=s).inductance(x)


def CTWIST(d, s, er, x):
    """Capacitance (F) of twisted pair of length x."""
    return wires.TwistedPair(diameter=d, spacing=s, er=er).capacitance(x)


# --- MSTRIP.mcd -----------------------------------------------------------

def EEFF(h, w, t, er):
    """Effective relative permittivity of microstrip."""
    return microstrip.effective_permittivity(h, w, t, er)


def WE(h, w, t):
    """Effective electrical trace width (in.) of microstrip."""
    return microstrip.effective_width(h, w, t)


def ZMSTRIP(h, w, t, er):
    """Characteristic impedance (ohms) of microstrip."""
    return microstrip.Microstrip(height=h, width=w, thickness=t, er=er).z0


def PMSTRIP(h, w, t, er):
    """Propagation delay (s/in.) of microstrip."""
    return microstrip.Microstrip(height=h, width=w, thickness=t, er=er).delay


def LMSTRIP(h, w, t, x):
    """Inductance (H) of microstrip of length x. Permittivity does not matter."""
    return microstrip.Microstrip(height=h, width=w, thickness=t, er=1.0).inductance(x)


def CMSTRIP(h, w, t, er, x):
    """Capacitance (F) of microstrip of length x."""
    return microstrip.Microstrip(height=h, width=w, thickness=t, er=er).capacitance(x)


def ZMSTRIP_TOL(h, dh, w, dw, t, er, der):
    """Microstrip impedance at [high corner, nominal, low corner]."""
    line = microstrip.Microstrip(height=h, width=w, thickness=t, er=er)
    span = line.tolerance(height=dh, width=dw, er=der)
    return [span.high, span.nominal, span.low]


# --- SLINE.mcd ------------------------------------------------------------

def ZSTRIP(b, w, t, er):
    """Characteristic impedance (ohms) of centred stripline."""
    return stripline.Stripline(separation=b, width=w, thickness=t, er=er).z0


def ZOFFSET(h1, h2, w, t, er):
    """Characteristic impedance (ohms) of offset stripline."""
    return stripline.OffsetStripline(
        height_below=h1, height_above=h2, width=w, thickness=t, er=er
    ).z0


def PSTRIP(er):
    """Propagation delay (s/in.) of stripline, centred or offset."""
    return PDLY_LIGHT * sqrt(er)


def LSTRIP(b, w, t, x):
    """Inductance (H) of centred stripline of length x."""
    return stripline.Stripline(separation=b, width=w, thickness=t, er=1.0).inductance(x)


def LOSTRIP(h1, h2, w, t, x):
    """Inductance (H) of offset stripline of length x."""
    return stripline.OffsetStripline(
        height_below=h1, height_above=h2, width=w, thickness=t, er=1.0
    ).inductance(x)


def CSTRIP(b, w, t, er, x):
    """Capacitance (F) of centred stripline of length x."""
    return stripline.Stripline(separation=b, width=w, thickness=t, er=er).capacitance(x)


def COSTRIP(h1, h2, w, t, er, x):
    """Capacitance (F) of offset stripline of length x."""
    return stripline.OffsetStripline(
        height_below=h1, height_above=h2, width=w, thickness=t, er=er
    ).capacitance(x)


def ZOFF_TOL(h1, dh1, h2, dh2, w, dw, t, er, der):
    """Offset stripline impedance at [high corner, nominal, low corner]."""
    line = stripline.OffsetStripline(
        height_below=h1, height_above=h2, width=w, thickness=t, er=er
    )
    span = line.tolerance(
        height_below=dh1, height_above=dh2, width=dw, er=der
    )
    return [span.high, span.nominal, span.low]


# --- CAPAC.mcd, CIRCULAR.mcd, RECTANGL.mcd --------------------------------

def CPLATE(w, x, h, er):
    """Capacitance (F) of two parallel plates."""
    return lumped.plate_capacitance(w, x, h, er)


def XCF(c, f):
    """Impedance magnitude (ohms) of a capacitor at one frequency."""
    return lumped.capacitive_reactance(c, f)


def XCR(c, tr):
    """Impedance magnitude (ohms) of a capacitor seen by a rising edge."""
    return lumped.capacitive_reactance_to_edge(c, tr)


def LCIRC(d, x):
    """Inductance (H) of a circular wire loop."""
    return lumped.circular_loop_inductance(d, x)


def LRECT(d, x, y):
    """Inductance (H) of a rectangular wire loop."""
    return lumped.rectangular_loop_inductance(d, x, y)


def XLF(l, f):
    """Impedance magnitude (ohms) of an inductor at one frequency."""
    return lumped.inductive_reactance(l, f)


def XLT(l, tr):
    """Impedance magnitude (ohms) of an inductor seen by a rising edge.

    CIRCULAR.mcd lists this as ``XLR()`` in its index but defines it as
    ``XLT()``. The defined name wins.
    """
    return lumped.inductive_reactance_to_edge(l, tr)


# --- MLINE.mcd, MLOOP.mcd -------------------------------------------------

def MLINE(L, s, h):
    """Mutual inductance (H) of two parallel lines above a ground plane."""
    return L * (1 / (1 + (s / h) ** 2))


def MLOOP(r, A1, A2):
    """Mutual inductance of two well-separated loops, in NANOHENRIES.

    The units really are nH here, unlike everything else in the worksheets.
    :func:`hsdd.loop_mutual_inductance` is the same formula in henries.
    """
    return 5.08 * (A1 * A2) / r ** 3


# --- RESIST.mcd -----------------------------------------------------------

def DIAMETER(awg):
    """Wire diameter (in.) from American Wire Gauge."""
    return resistance.awg_to_diameter(awg)


def AWG(d):
    """American Wire Gauge from wire diameter (in.)."""
    return resistance.diameter_to_awg(d)


def CPW(t):
    """Copper plating weight (oz) from trace thickness (in.)."""
    return resistance.thickness_to_oz(t)


def THICKNESS(cpw):
    """Trace thickness (in.) from copper plating weight (oz)."""
    return resistance.oz_to_thickness(cpw)


def RROUND(d, x, temp):
    """DC resistance (ohms) of a round wire."""
    return resistance.wire_resistance(d, x, temp)


def RROUND_AWG(awg, x, temp):
    """DC resistance (ohms) of a round wire given by gauge."""
    return resistance.awg_wire_resistance(awg, x, temp)


def RROUND_RT(d, x):
    """DC resistance (ohms) of a round wire at room temperature."""
    return resistance.wire_resistance(d, x)


def RTRACE(w, t, x, temp):
    """DC resistance (ohms) of a circuit trace."""
    return resistance.trace_resistance(w, t, x, temp)


def RTRACE_CPW(w, cpw, x, temp):
    """DC resistance (ohms) of a trace given by plating weight."""
    return resistance.trace_resistance_oz(w, cpw, x, temp)


def RTRACE_RT(w, t, x):
    """DC resistance (ohms) of a circuit trace at room temperature."""
    return resistance.trace_resistance(w, t, x)


def RPLANE(d1, d2, t, x, temp):
    """DC resistance (ohms) between two contact points on a plane."""
    return resistance.plane_resistance(d1, d2, t, x, temp)


def RPLANE_CPW(d1, d2, cpw, x, temp):
    """Plane resistance (ohms) given by plating weight."""
    return resistance.plane_resistance_oz(d1, d2, cpw, x, temp)


# --- shared between the two tolerance sheets ------------------------------

def REFL(x, z):
    """Reflection coefficient of each impedance in x against a source z."""
    return [(z - xi) / (z + xi) for xi in x]
