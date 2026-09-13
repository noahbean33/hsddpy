"""DC resistance of copper wires, traces and planes.

Transcribed from RESIST.mcd.

Variables
    x      length of wire (in.), or separation between contact points
    d      diameter of wire (in.), or diameter of a contact point
    awg    American wire gauge
    temp   temperature (degrees C)
    w      width of a PCB trace (in.)
    t      thickness of a PCB trace or plane (in.)
    cpw    thickness in units of copper plating weight (oz/ft^2)
"""

from math import pi, log, log10


# --- material constants ---------------------------------------------------

RHO = 6.787e-7
"""Bulk resistivity of copper, ohm-in.

Slightly different from the bulk resistivity of pure copper (6.58e-7) owing
to the annealing process used in making wire, and to chemical imperfections
in the copper used for practical wires.

In practice the two wires of a twisted pair may be matched as well as 10%,
but almost never as well as 1%.
"""

DRHO = 0.0039
"""Thermal coefficient of resistance, per degree C.

If a copper wire is R at room temperature, at 1 degree C higher it is
R*(1 + DRHO). Over 0-70 C the resistance of copper wire varies by 28%.
"""

ROOM_TEMP = 20  # degrees C


def _temp_factor(temp):
    """Resistance multiplier for a temperature other than room temperature."""
    return 1 + (temp - ROOM_TEMP) * DRHO


# --- wire gauge conversions -----------------------------------------------

def DIAMETER(awg):
    """Wire diameter (in.) from American Wire Gauge."""
    return 10 ** (-((awg + 10) / 20))


def AWG(d):
    """American Wire Gauge from wire diameter (in.). log() here is base 10."""
    return -10 - 20 * log10(d)


# --- plating weight conversions -------------------------------------------

def CPW(t):
    """Copper plating weight (oz) from trace thickness (in.)."""
    return t / 0.00137


def THICKNESS(cpw):
    """Trace thickness (in.) from copper plating weight (oz).

    1 oz copper is 0.00137 in.
    """
    return 0.00137 * cpw


# --- round wires ----------------------------------------------------------

def RROUND(d, x, temp):
    """DC resistance (ohms) of a round wire."""
    return (4 * RHO * x) / (pi * d ** 2) * _temp_factor(temp)


def RROUND_AWG(awg, x, temp):
    """DC resistance (ohms) of a round wire given by gauge instead of diameter."""
    return RROUND(DIAMETER(awg), x, temp)


def RROUND_RT(d, x):
    """DC resistance (ohms) of a round wire at room temperature."""
    return RROUND(d, x, ROOM_TEMP)


# --- circuit traces -------------------------------------------------------

def RTRACE(w, t, x, temp):
    """DC resistance (ohms) of a printed circuit board trace."""
    return (x * RHO) / (w * t) * _temp_factor(temp)


def RTRACE_CPW(w, cpw, x, temp):
    """DC resistance (ohms) of a trace given by plating weight, not thickness."""
    return RTRACE(w, THICKNESS(cpw), x, temp)


def RTRACE_RT(w, t, x):
    """DC resistance (ohms) of a circuit trace at room temperature."""
    return RTRACE(w, t, x, ROOM_TEMP)


# --- power and ground planes ----------------------------------------------

def RPLANE(d1, d2, t, x, temp):
    """DC resistance (ohms) between two contact points on a plane.

    d1, d2  diameters of the two contact points (in.)
    t       thickness of the plane (in.)
    x       separation between contact points (in.)

    For long skinny traces and wires the formulas above work extremely well,
    because they assume current is uniformly distributed and so resistance
    is proportional to length. Current circulating in a large plane is NOT
    uniform, so resistance between two points is not proportional to their
    separation -- it goes as the log of it, and the contact diameter sets
    the scale.

    If the contact points lie near an edge of the plane the resistance
    between them may go up by a factor of 2, and near corners even higher.
    """
    return (RHO / (2 * pi * t)
            * (log(2 * x / d1) + log(2 * x / d2))
            * _temp_factor(temp))


def RPLANE_CPW(d1, d2, cpw, x, temp):
    """Plane resistance (ohms) given by plating weight instead of thickness."""
    return RPLANE(d1, d2, THICKNESS(cpw), x, temp)
