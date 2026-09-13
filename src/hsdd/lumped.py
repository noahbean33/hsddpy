"""Lumped capacitors and inductors, and what they look like to a rising edge.

Source: CAPAC.mcd, CIRCULAR.mcd, RECTANGL.mcd.

The point of these sheets is the pair :func:`capacitive_reactance_to_edge`
and :func:`inductive_reactance_to_edge`. A digital edge does not care about
the impedance of a part at one sine-wave frequency; it cares about the
impedance at its own knee frequency, and these give you that in one step.
"""

from __future__ import annotations

from math import log, pi

__all__ = [
    "plate_capacitance", "plane_capacitance_per_square_inch",
    "capacitive_reactance", "capacitive_reactance_to_edge",
    "inductive_reactance", "inductive_reactance_to_edge",
    "circular_loop_inductance", "rectangular_loop_inductance",
]


# --- capacitance ----------------------------------------------------------

def plate_capacitance(width, length, height, er):
    """Capacitance (F) of two overlapping parallel plates.

    ``width`` and ``length`` describe the overlap, ``height`` the separation,
    all in inches. This is the power/ground plane pair of a PCB.

    A plane pair 0.010 in. apart in FR-4 (er = 4.5) gives 100 pF per square
    inch. Halving the separation doubles it -- which is the whole argument
    for thin power-plane dielectrics.

    >>> from hsdd import plate_capacitance, to_pf
    >>> round(to_pf(plate_capacitance(1.0, 1.0, 0.010, 4.5)), 1)
    101.2
    """
    if height <= 0:
        raise ValueError("plate separation must be positive")
    return 2.249e-13 * (er * length * width) / height


def plane_capacitance_per_square_inch(height, er):
    """Interplane capacitance (F per square inch) of a plane pair.

    The same formula as :func:`plate_capacitance` over unit area, which is
    how plane capacitance is usually quoted.
    """
    return plate_capacitance(1.0, 1.0, height, er)


def capacitive_reactance(c, f):
    """Impedance magnitude (ohms) of capacitance ``c`` (F) at ``f`` (Hz).

    >>> from hsdd import capacitive_reactance, pf, mhz
    >>> round(capacitive_reactance(pf(100), mhz(100)), 1)
    15.9
    """
    if f <= 0:
        raise ValueError("frequency must be positive")
    if c <= 0:
        raise ValueError("capacitance must be positive")
    return 1 / (2 * pi * f * c)


def capacitive_reactance_to_edge(c, rise_time):
    """Impedance (ohms) of capacitance ``c`` (F) as a rising edge sees it.

    ``rise_time`` is the 10-90% rise time in seconds. This is the reactance
    at the knee frequency, and it is the number that decides whether a
    bypass capacitor or a stub is doing anything at digital speeds.

    A 100 pF capacitor looks like 16 ohms to a 5 ns edge -- the same 16 ohms
    it presents to a 100 MHz sine wave, which is the point.

    >>> from hsdd import capacitive_reactance_to_edge, pf, ns
    >>> round(capacitive_reactance_to_edge(pf(100), ns(5)), 1)
    15.9
    """
    if rise_time <= 0:
        raise ValueError("rise time must be positive")
    if c <= 0:
        raise ValueError("capacitance must be positive")
    return rise_time / (pi * c)


# --- inductance -----------------------------------------------------------

def circular_loop_inductance(wire_diameter, loop_diameter):
    """Inductance (H) of a circular loop of wire.

    Both dimensions in inches. A loop of 24-gauge wire the size of the circle
    between your thumb and forefinger is about 100 nH. The log makes it very
    insensitive to wire size: going from AWG 24 to AWG 14 -- ten times the
    copper -- only halves it.

    >>> from hsdd import circular_loop_inductance, to_nh
    >>> round(to_nh(circular_loop_inductance(0.01, 1.3)), 1)
    100.3
    """
    if wire_diameter <= 0 or loop_diameter <= 0:
        raise ValueError("wire and loop diameters must be positive")
    if loop_diameter <= wire_diameter:
        raise ValueError("loop diameter must exceed wire diameter")
    return 1.56e-8 * loop_diameter * (log(8 * loop_diameter / wire_diameter) - 2)


def rectangular_loop_inductance(wire_diameter, length, breadth):
    """Inductance (H) of a rectangular loop of wire.

    All dimensions in inches. A 1 in. square loop of 24-gauge wire is about
    100 nH. If the loop is made of different-sized conductors, use the
    diameter of the smallest -- it dominates.

    >>> from hsdd import rectangular_loop_inductance, to_nh
    >>> round(to_nh(rectangular_loop_inductance(0.02, 1.0, 1.0)), 1)
    93.6
    """
    if wire_diameter <= 0:
        raise ValueError("wire diameter must be positive")
    if length <= wire_diameter or breadth <= wire_diameter:
        raise ValueError("loop sides must exceed the wire diameter")
    return 10.16e-9 * (
        length * log(2 * breadth / wire_diameter)
        + breadth * log(2 * length / wire_diameter)
    )


def inductive_reactance(l, f):
    """Impedance magnitude (ohms) of inductance ``l`` (H) at ``f`` (Hz).

    >>> from hsdd import inductive_reactance, nh, mhz
    >>> round(inductive_reactance(nh(100), mhz(100)), 1)
    62.8
    """
    if f <= 0:
        raise ValueError("frequency must be positive")
    return 2 * pi * f * l


def inductive_reactance_to_edge(l, rise_time):
    """Impedance (ohms) of inductance ``l`` (H) as a rising edge sees it.

    ``rise_time`` is the 10-90% rise time in seconds. A 100 nH loop -- a
    finger-sized loop of wire, or a sloppy ground return -- looks like 63
    ohms to a 5 ns edge. That is why lead inductance, not capacitor value,
    limits bypassing.

    >>> from hsdd import inductive_reactance_to_edge, nh, ns
    >>> round(inductive_reactance_to_edge(nh(100), ns(5)), 1)
    62.8
    """
    if rise_time <= 0:
        raise ValueError("rise time must be positive")
    return pi * l / rise_time
