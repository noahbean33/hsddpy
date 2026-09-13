"""Unit conversion for a library whose internals are inches and seconds.

The formulas in this library take inches, seconds, ohms, henries and farads,
because that is what the coefficients in the source worksheets are scaled
for. Nobody draws a board in inches, so convert at the call site::

    from hsdd import Microstrip, mil, oz
    Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)

The helpers come in pairs: ``mil(6)`` goes in, ``to_mil(x)`` comes back out.
"""

from __future__ import annotations

import re

from .constants import INCH, OZ_COPPER_INCHES

__all__ = [
    "inch", "mil", "mm", "cm", "meter", "micron",
    "to_inch", "to_mil", "to_mm", "to_meter",
    "oz", "to_oz",
    "second", "ms", "us", "ns", "ps", "to_ns", "to_ps",
    "hz", "khz", "mhz", "ghz", "to_mhz", "to_ghz",
    "henry", "nh", "ph", "to_nh", "to_ph",
    "farad", "uf", "nf", "pf", "to_pf", "to_nf",
    "to_ps_per_inch", "to_ns_per_meter", "to_inches_per_ns",
    "parse_length", "parse_time", "parse_frequency",
    "parse_capacitance", "parse_inductance", "parse_resistance",
]


# --- length ---------------------------------------------------------------

def inch(value):
    """Inches to inches. Here so call sites can be explicit about units."""
    return value


def mil(value):
    """Mils (thousandths of an inch) to inches."""
    return value * 1e-3


def mm(value):
    """Millimetres to inches."""
    return value / (INCH * 1000.0)


def cm(value):
    """Centimetres to inches."""
    return value / (INCH * 100.0)


def meter(value):
    """Metres to inches."""
    return value / INCH


def micron(value):
    """Micrometres to inches."""
    return value / (INCH * 1e6)


def to_inch(inches):
    return inches


def to_mil(inches):
    """Inches to mils."""
    return inches * 1e3


def to_mm(inches):
    """Inches to millimetres."""
    return inches * INCH * 1000.0


def to_meter(inches):
    """Inches to metres."""
    return inches * INCH


# --- copper thickness -----------------------------------------------------

def oz(value):
    """Copper plating weight (oz/ft^2) to thickness in inches.

    1 oz copper is 0.00137 in. -- about 1.4 mil.
    """
    return value * OZ_COPPER_INCHES


def to_oz(inches):
    """Copper thickness in inches to plating weight (oz/ft^2)."""
    return inches / OZ_COPPER_INCHES


# --- time -----------------------------------------------------------------

def second(value):
    return value


def ms(value):
    return value * 1e-3


def us(value):
    return value * 1e-6


def ns(value):
    """Nanoseconds to seconds."""
    return value * 1e-9


def ps(value):
    """Picoseconds to seconds."""
    return value * 1e-12


def to_ns(seconds):
    return seconds * 1e9


def to_ps(seconds):
    return seconds * 1e12


# --- frequency ------------------------------------------------------------

def hz(value):
    return value


def khz(value):
    return value * 1e3


def mhz(value):
    """Megahertz to hertz."""
    return value * 1e6


def ghz(value):
    """Gigahertz to hertz."""
    return value * 1e9


def to_mhz(hertz):
    return hertz / 1e6


def to_ghz(hertz):
    return hertz / 1e9


# --- inductance and capacitance ------------------------------------------

def henry(value):
    return value


def nh(value):
    """Nanohenries to henries."""
    return value * 1e-9


def ph(value):
    """Picohenries to henries."""
    return value * 1e-12


def to_nh(henries):
    return henries * 1e9


def to_ph(henries):
    return henries * 1e12


def farad(value):
    return value


def uf(value):
    return value * 1e-6


def nf(value):
    return value * 1e-9


def pf(value):
    """Picofarads to farads."""
    return value * 1e-12


def to_pf(farads):
    return farads * 1e12


def to_nf(farads):
    return farads * 1e9


# --- propagation delay ----------------------------------------------------

def to_ps_per_inch(seconds_per_inch):
    """Delay in s/in. to the ps/in. that datasheets quote."""
    return seconds_per_inch * 1e12


def to_ns_per_meter(seconds_per_inch):
    """Delay in s/in. to ns/m."""
    return seconds_per_inch / INCH * 1e9


def to_inches_per_ns(seconds_per_inch):
    """Delay in s/in. to propagation velocity in in./ns."""
    return 1e-9 / seconds_per_inch


# --- string parsing (used by the CLI, handy in notebooks) ----------------

_NUMBER = re.compile(r"^\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)\s*([a-zA-Z/^2%]*)\s*$")

_LENGTH_UNITS = {
    "": inch, "in": inch, "inch": inch, "inches": inch, '"': inch,
    "mil": mil, "mils": mil, "th": mil, "thou": mil,
    "mm": mm, "cm": cm, "m": meter, "um": micron, "micron": micron,
    "oz": oz,
}

_TIME_UNITS = {
    "": second, "s": second, "sec": second,
    "ms": ms, "us": us, "ns": ns, "ps": ps,
}

_FREQ_UNITS = {
    "": hz, "hz": hz, "khz": khz, "mhz": mhz, "ghz": ghz,
}

_CAP_UNITS = {
    "": farad, "f": farad, "uf": uf, "nf": nf, "pf": pf,
}

_IND_UNITS = {
    "": henry, "h": henry, "nh": nh, "ph": ph,
    "uh": lambda v: v * 1e-6,
}

_RES_UNITS = {
    "": lambda v: v, "ohm": lambda v: v, "ohms": lambda v: v, "r": lambda v: v,
    "k": lambda v: v * 1e3, "kohm": lambda v: v * 1e3,
    "meg": lambda v: v * 1e6, "megohm": lambda v: v * 1e6,
}


def _parse(text, table, what):
    if isinstance(text, (int, float)):
        return float(text)
    match = _NUMBER.match(str(text))
    if not match:
        raise ValueError("cannot parse %s value %r" % (what, text))
    number, unit = match.group(1), match.group(2).lower()
    if unit not in table:
        raise ValueError(
            "unknown %s unit %r in %r (known: %s)"
            % (what, unit, text, ", ".join(sorted(u for u in table if u)))
        )
    return float(table[unit](float(number)))


def parse_length(text):
    """Parse ``"6mil"``, ``"0.15mm"``, ``"1oz"`` or ``"0.006"`` to inches.

    A bare number is taken as inches.
    """
    return _parse(text, _LENGTH_UNITS, "length")


def parse_time(text):
    """Parse ``"350ps"``, ``"1ns"`` or ``"1e-9"`` to seconds."""
    return _parse(text, _TIME_UNITS, "time")


def parse_frequency(text):
    """Parse ``"100MHz"``, ``"2.5GHz"`` or ``"1e8"`` to hertz."""
    return _parse(text, _FREQ_UNITS, "frequency")


def parse_capacitance(text):
    """Parse ``"10pF"`` or ``"1e-11"`` to farads."""
    return _parse(text, _CAP_UNITS, "capacitance")


def parse_inductance(text):
    """Parse ``"100nH"`` or ``"1e-7"`` to henries."""
    return _parse(text, _IND_UNITS, "inductance")


def parse_resistance(text):
    """Parse ``"50"``, ``"50ohm"`` or ``"10k"`` to ohms."""
    return _parse(text, _RES_UNITS, "resistance")
