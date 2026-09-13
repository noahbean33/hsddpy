"""General relations among transmission line parameters.

Transcribed from GENERAL.mcd.

Variables
    lpi   inductance per inch (H)
    cpi   capacitance per inch (F)
    pdly  propagation delay (s/in.)
    z0    line impedance (ohms)
    eeff  effective relative permittivity
"""

from math import sqrt


def Z0(lpi, cpi):
    """Characteristic impedance (ohms) from L and C per inch."""
    return sqrt(lpi / cpi)


def PDLY1(lpi, cpi):
    """Propagation delay (s/in.) from L and C per inch."""
    return sqrt(lpi * cpi)


def PDLY2(eeff):
    """Propagation delay (s/in.) from effective relative permittivity."""
    return 84.72e-12 * sqrt(eeff)


def CPI(zo, pdly):
    """Capacitance per inch (F) from impedance and propagation delay."""
    return pdly / zo


def LPI(zo, pdly):
    """Inductance per inch (H) from impedance and propagation delay."""
    return zo * pdly
