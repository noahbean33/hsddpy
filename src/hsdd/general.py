"""Conversions among the four numbers that describe any transmission line.

Given any two of impedance, delay, inductance per inch and capacitance per
inch, these give you the others. Source: GENERAL.mcd.
"""

from __future__ import annotations

from math import sqrt

from .constants import PDLY_LIGHT

__all__ = [
    "z0_from_lc", "delay_from_lc", "delay_from_er",
    "capacitance_per_inch", "inductance_per_inch", "er_from_delay",
]


def z0_from_lc(l_per_inch, c_per_inch):
    """Characteristic impedance (ohms) from L (H/in.) and C (F/in.)."""
    if c_per_inch <= 0:
        raise ValueError("capacitance per inch must be positive")
    return sqrt(l_per_inch / c_per_inch)


def delay_from_lc(l_per_inch, c_per_inch):
    """Propagation delay (s/in.) from L (H/in.) and C (F/in.)."""
    return sqrt(l_per_inch * c_per_inch)


def delay_from_er(eeff):
    """Propagation delay (s/in.) from effective relative permittivity.

    This is the 84.72 ps/in. of free space slowed by sqrt(eeff). It is the
    whole content of every ``P...()`` function in the book.
    """
    if eeff <= 0:
        raise ValueError("effective permittivity must be positive")
    return PDLY_LIGHT * sqrt(eeff)


def er_from_delay(delay):
    """Effective relative permittivity implied by a delay (s/in.).

    The inverse of :func:`delay_from_er`; useful for backing an effective
    permittivity out of a measured or datasheet delay.
    """
    return (delay / PDLY_LIGHT) ** 2


def capacitance_per_inch(z0, delay):
    """Capacitance per inch (F) from impedance (ohms) and delay (s/in.)."""
    if z0 <= 0:
        raise ValueError("impedance must be positive")
    return delay / z0


def inductance_per_inch(z0, delay):
    """Inductance per inch (H) from impedance (ohms) and delay (s/in.)."""
    return z0 * delay
