"""hsdd -- transmission lines and signal integrity for high-speed digital design.

A Python library built from the Mathcad worksheets that ship with
*High-Speed Digital Design: A Handbook of Black Magic* (Howard Johnson and
Martin Graham), checked against the worked examples stored in those sheets.

Units in, units out: **inches, seconds, ohms, henries, farads**. Nobody draws
a board in inches, so convert at the call site with the helpers::

    from hsdd import Microstrip, mil, oz, ns

    trace = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    trace.z0                      # 56.4 ohms
    trace.critical_length(ns(1))  # 1.1 in. before it needs terminating

    Microstrip.for_impedance(50, height=mil(6), thickness=oz(1))

The original worksheet function names are all available under
:mod:`hsdd.mathcad` for cross-checking against the book.
"""

from .constants import (
    C_INCHES,
    COPPER_RESISTIVITY,
    COPPER_TEMPCO,
    E0_INCHES,
    INCH,
    L_COEFF,
    OZ_COPPER_INCHES,
    PDLY_LIGHT,
    PDLY_LIGHT_PS_PER_IN,
    ROOM_TEMP_C,
    U0_INCHES,
)
from .general import (
    capacitance_per_inch,
    delay_from_er,
    delay_from_lc,
    er_from_delay,
    inductance_per_inch,
    z0_from_lc,
)
from .line import RISETIME_RULE, TransmissionLine
from .lumped import (
    capacitive_reactance,
    capacitive_reactance_to_edge,
    circular_loop_inductance,
    inductive_reactance,
    inductive_reactance_to_edge,
    plane_capacitance_per_square_inch,
    plate_capacitance,
    rectangular_loop_inductance,
)
from .microstrip import Microstrip
from .mutual import (
    coupling_ratio,
    loop_mutual_inductance,
    loops_are_well_separated,
    parallel_line_mutual_inductance,
)
from .resistance import (
    awg_to_diameter,
    awg_wire_resistance,
    diameter_to_awg,
    oz_to_thickness,
    plane_resistance,
    plane_resistance_oz,
    temperature_factor,
    thickness_to_oz,
    trace_resistance,
    trace_resistance_oz,
    wire_resistance,
)
from .signal import (
    TerminationCheck,
    check_termination,
    critical_length,
    knee_frequency,
    reflection_coefficient,
    rise_time_for_knee,
    series_terminator,
)
from .solve import ImpedanceRange, solve_monotone
from .stripline import OffsetStripline, Stripline
from .units import (
    cm,
    farad,
    ghz,
    henry,
    hz,
    inch,
    khz,
    meter,
    mhz,
    micron,
    mil,
    mm,
    ms,
    nf,
    nh,
    ns,
    oz,
    parse_capacitance,
    parse_frequency,
    parse_inductance,
    parse_length,
    parse_resistance,
    parse_time,
    pf,
    ph,
    ps,
    second,
    to_ghz,
    to_inch,
    to_inches_per_ns,
    to_meter,
    to_mhz,
    to_mil,
    to_mm,
    to_nf,
    to_nh,
    to_ns,
    to_ns_per_meter,
    to_oz,
    to_pf,
    to_ph,
    to_ps,
    to_ps_per_inch,
    uf,
    us,
)
from .wires import Coax, RoundWire, TwistedPair

__version__ = "0.1.0"


def __getattr__(name):
    """Expose the numpy-backed simulators lazily.

    ``hsdd.step_response`` and ``hsdd.connector_crosstalk`` work if numpy is
    installed, and raise a clear ImportError naming the extra if it is not --
    without making numpy a hard dependency of ``import hsdd``.
    """
    sim_names = {
        "StepResponse", "step_response", "frequency_response", "simulate_line",
    }
    connector_names = {"PinField", "CrosstalkResult", "connector_crosstalk"}
    if name in sim_names:
        from . import sim

        return getattr(sim, name)
    if name in connector_names:
        from . import connector

        return getattr(connector, name)
    raise AttributeError("module %r has no attribute %r" % (__name__, name))


__all__ = [
    "__version__",
    # geometries
    "TransmissionLine", "RoundWire", "Coax", "TwistedPair",
    "Microstrip", "Stripline", "OffsetStripline",
    # general relations
    "z0_from_lc", "delay_from_lc", "delay_from_er", "er_from_delay",
    "capacitance_per_inch", "inductance_per_inch",
    # signal integrity
    "knee_frequency", "rise_time_for_knee", "reflection_coefficient",
    "series_terminator", "critical_length", "check_termination",
    "TerminationCheck", "RISETIME_RULE",
    # lumped elements
    "plate_capacitance", "plane_capacitance_per_square_inch",
    "capacitive_reactance", "capacitive_reactance_to_edge",
    "circular_loop_inductance", "rectangular_loop_inductance",
    "inductive_reactance", "inductive_reactance_to_edge",
    # coupling
    "coupling_ratio", "parallel_line_mutual_inductance",
    "loop_mutual_inductance", "loops_are_well_separated",
    # resistance
    "awg_to_diameter", "diameter_to_awg", "oz_to_thickness", "thickness_to_oz",
    "wire_resistance", "awg_wire_resistance", "trace_resistance",
    "trace_resistance_oz", "plane_resistance", "plane_resistance_oz",
    "temperature_factor",
    # solving
    "solve_monotone", "ImpedanceRange",
    # simulation (lazy, needs numpy)
    "step_response", "frequency_response", "simulate_line", "StepResponse",
    "connector_crosstalk", "PinField", "CrosstalkResult",
    # constants
    "INCH", "E0_INCHES", "U0_INCHES", "C_INCHES", "L_COEFF", "PDLY_LIGHT",
    "PDLY_LIGHT_PS_PER_IN", "COPPER_RESISTIVITY", "COPPER_TEMPCO",
    "ROOM_TEMP_C", "OZ_COPPER_INCHES",
    # units
    "inch", "mil", "mm", "cm", "meter", "micron", "oz",
    "to_inch", "to_mil", "to_mm", "to_meter", "to_oz",
    "second", "ms", "us", "ns", "ps", "to_ns", "to_ps",
    "hz", "khz", "mhz", "ghz", "to_mhz", "to_ghz",
    "henry", "nh", "ph", "to_nh", "to_ph",
    "farad", "uf", "nf", "pf", "to_pf", "to_nf",
    "to_ps_per_inch", "to_ns_per_meter", "to_inches_per_ns",
    "parse_length", "parse_time", "parse_frequency",
    "parse_capacitance", "parse_inductance", "parse_resistance",
]
