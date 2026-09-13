"""Physical constants, in the units the HSDD worksheets use.

Everything in this library is in ENGLISH units -- inches, seconds, ohms,
henries, farads -- because that is what the source worksheets use and what
the bare coefficients in the formulas (5.08, 10.16, 84.72, 2.249) are scaled
for. Use :mod:`hsdd.units` to get in and out of mils, millimetres, ounces of
copper and so on.

Source: CONSTANT.mcd.
"""

from math import pi

__all__ = [
    "INCH",
    "E0_METERS", "U0_METERS", "C_METERS",
    "E0_INCHES", "U0_INCHES", "C_INCHES",
    "L_COEFF", "C_COEFF",
    "PDLY_LIGHT", "PDLY_LIGHT_PS_PER_IN",
    "COPPER_RESISTIVITY", "COPPER_TEMPCO", "ROOM_TEMP_C", "OZ_COPPER_INCHES",
]

INCH = 0.0254
"""Metres per inch."""

# --- free space, metric ---------------------------------------------------

E0_METERS = 8.854e-12
"""Electric permittivity of free space, F/m."""

U0_METERS = 4 * pi * 1e-7
"""Magnetic permeability of free space, H/m."""

C_METERS = 2.998e8
"""Speed of light, m/s."""

# --- the same constants, per inch -----------------------------------------

E0_INCHES = E0_METERS * INCH
"""Electric permittivity of free space, 2.249e-13 F/in."""

U0_INCHES = U0_METERS * INCH
"""Magnetic permeability of free space, 3.192e-8 H/in."""

C_INCHES = C_METERS / INCH
"""Speed of light, 1.180e10 in./s."""

L_COEFF = U0_INCHES / (2 * pi)
"""5.08e-9 H/in.

This turns up in every inductance formula in the book, which is why 5.08 and
its multiples (10.16 = 2 x 5.08) appear as bare literals in the worksheets.
"""

C_COEFF = 2 * pi * E0_INCHES
"""1.413e-12 F/in., the capacitance counterpart of :data:`L_COEFF`."""

PDLY_LIGHT = 84.72e-12
"""Propagation delay at the speed of light, s/in., as written in the sheets.

Every propagation-delay formula in the book is this number times sqrt(er).
"""

PDLY_LIGHT_PS_PER_IN = 1e12 / C_INCHES
"""The same delay in ps/in., computed rather than rounded: 84.7231."""

# --- copper ---------------------------------------------------------------

COPPER_RESISTIVITY = 6.787e-7
"""Bulk resistivity of copper, ohm-in.

Slightly higher than pure copper (6.58e-7) because of the annealing process
used in making wire and the chemical imperfections in practical copper.
"""

COPPER_TEMPCO = 0.0039
"""Thermal coefficient of resistance, per degree C.

A wire of resistance R at room temperature is R*(1 + COPPER_TEMPCO) one
degree hotter. Over 0-70 C, copper resistance varies by 28%.
"""

ROOM_TEMP_C = 20.0
"""Room temperature, degrees C, as the worksheets define it."""

OZ_COPPER_INCHES = 0.00137
"""Thickness of one ounce of copper plating, inches."""
