"""DC resistance of copper wires, traces and planes, and gauge conversions.

Source: RESIST.mcd.

The wire and trace formulas assume current is spread uniformly through the
conductor, so resistance is proportional to length. That holds beautifully
for anything long and skinny. It does not hold for a plane, where current
spreads out between the two contact points -- so :func:`plane_resistance`
goes as the *log* of separation, with contact diameter setting the scale.

These are DC numbers. At the frequencies that make a digital edge, skin
effect confines current to the surface and the real resistance is higher;
treat these as the floor.
"""

from __future__ import annotations

from math import log, log10, pi

from .constants import (
    COPPER_RESISTIVITY,
    COPPER_TEMPCO,
    OZ_COPPER_INCHES,
    ROOM_TEMP_C,
)

__all__ = [
    "awg_to_diameter", "diameter_to_awg",
    "oz_to_thickness", "thickness_to_oz",
    "wire_resistance", "awg_wire_resistance",
    "trace_resistance", "trace_resistance_oz",
    "plane_resistance", "plane_resistance_oz",
    "temperature_factor",
]


def temperature_factor(temp_c):
    """Resistance multiplier at ``temp_c`` relative to 20 C.

    Copper rises about 0.39% per degree, so over a 0-70 C operating range a
    wire resistance varies by 28% -- worth remembering before designing a
    voltage drop budget against a room-temperature number.

    >>> from hsdd import temperature_factor
    >>> round(temperature_factor(70), 4)
    1.195
    """
    return 1 + (temp_c - ROOM_TEMP_C) * COPPER_TEMPCO


# --- gauge and plating weight conversions ---------------------------------

def awg_to_diameter(awg):
    """Wire diameter (in.) from American Wire Gauge.

    >>> from hsdd import awg_to_diameter, to_mil
    >>> round(to_mil(awg_to_diameter(30)), 2)
    10.0
    """
    return 10 ** (-((awg + 10) / 20))


def diameter_to_awg(diameter):
    """American Wire Gauge from wire diameter (in.).

    >>> from hsdd import diameter_to_awg
    >>> round(diameter_to_awg(0.010), 2)
    30.0
    """
    if diameter <= 0:
        raise ValueError("wire diameter must be positive")
    return -10 - 20 * log10(diameter)


def oz_to_thickness(cpw):
    """Copper thickness (in.) from plating weight (oz/ft^2). 1 oz = 1.37 mil."""
    return OZ_COPPER_INCHES * cpw


def thickness_to_oz(thickness):
    """Copper plating weight (oz/ft^2) from thickness (in.)."""
    return thickness / OZ_COPPER_INCHES


# --- round wires ----------------------------------------------------------

def wire_resistance(diameter, length, temp_c=ROOM_TEMP_C):
    """DC resistance (ohms) of a round copper wire.

    ``diameter`` and ``length`` in inches, temperature in degrees C.

    >>> from hsdd import wire_resistance, awg_to_diameter
    >>> round(wire_resistance(awg_to_diameter(24), 12.0), 4)   # 1 ft of AWG 24
    0.026
    """
    if diameter <= 0:
        raise ValueError("wire diameter must be positive")
    return (4 * COPPER_RESISTIVITY * length) / (pi * diameter ** 2) * temperature_factor(temp_c)


def awg_wire_resistance(awg, length, temp_c=ROOM_TEMP_C):
    """DC resistance (ohms) of a round wire given by gauge, not diameter."""
    return wire_resistance(awg_to_diameter(awg), length, temp_c)


# --- circuit traces -------------------------------------------------------

def trace_resistance(width, thickness, length, temp_c=ROOM_TEMP_C):
    """DC resistance (ohms) of a PCB trace.

    All dimensions in inches.

    >>> from hsdd import trace_resistance, mil, oz
    >>> round(trace_resistance(mil(8), oz(1), 10.0), 3)
    0.619
    """
    if width <= 0 or thickness <= 0:
        raise ValueError("trace width and thickness must be positive")
    return (length * COPPER_RESISTIVITY) / (width * thickness) * temperature_factor(temp_c)


def trace_resistance_oz(width, cpw, length, temp_c=ROOM_TEMP_C):
    """Trace resistance (ohms) with thickness given as plating weight."""
    return trace_resistance(width, oz_to_thickness(cpw), length, temp_c)


# --- power and ground planes ---------------------------------------------

def plane_resistance(contact1, contact2, thickness, separation,
                     temp_c=ROOM_TEMP_C):
    """DC resistance (ohms) between two contact points on a plane.

    ``contact1`` and ``contact2`` are the diameters of the two contacts (a
    via, a pad), ``thickness`` the plane copper, ``separation`` the distance
    between the contacts -- all in inches.

    Current in a plane is not uniform: it spreads out from the contact and
    re-converges, so resistance goes as the log of separation and the contact
    diameter sets the scale. Doubling the distance between two vias barely
    changes anything; halving the via diameter matters more.

    This assumes contacts well inside the plane. Near an edge the resistance
    can be twice this, and near a corner higher still.

    >>> from hsdd import plane_resistance, mil, oz
    >>> round(plane_resistance(mil(25), mil(25), oz(1), 4.0) * 1000, 3)  # milliohms
    0.91
    """
    if thickness <= 0:
        raise ValueError("plane thickness must be positive")
    if contact1 <= 0 or contact2 <= 0:
        raise ValueError("contact diameters must be positive")
    if separation <= max(contact1, contact2) / 2:
        raise ValueError("contacts must be separated by more than a contact radius")
    return (
        COPPER_RESISTIVITY / (2 * pi * thickness)
        * (log(2 * separation / contact1) + log(2 * separation / contact2))
        * temperature_factor(temp_c)
    )


def plane_resistance_oz(contact1, contact2, cpw, separation,
                        temp_c=ROOM_TEMP_C):
    """Plane resistance (ohms) with thickness given as plating weight."""
    return plane_resistance(contact1, contact2, oz_to_thickness(cpw), separation, temp_c)
