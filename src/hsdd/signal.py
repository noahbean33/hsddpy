"""Rules of thumb that turn the geometry formulas into layout decisions.

The worksheets compute cross-sections. These are the handful of relations
that tell you what to *do* with the answer: how much bandwidth an edge
actually contains, how long a stub can be before it rings, and what resistor
to put in series with the driver.

Everything here is first-order and deliberately so. Johnson and Graham argue
the case throughout *High-Speed Digital Design*: a two-significant-figure
answer you can get at your desk beats a four-figure one you have to wait for.
"""

from __future__ import annotations

from dataclasses import dataclass

from .line import RISETIME_RULE

__all__ = [
    "knee_frequency", "rise_time_for_knee",
    "reflection_coefficient", "series_terminator",
    "critical_length", "TerminationCheck", "check_termination",
    "RISETIME_RULE",
]


def knee_frequency(rise_time):
    """Highest frequency that matters in a digital edge, hertz.

    ``F_knee = 0.5 / rise_time``, with ``rise_time`` the 10-90% time in
    seconds. Above the knee a step contains little energy; below it the
    spectrum follows the step. Any circuit that behaves properly up to the
    knee passes the edge more or less intact.

    Note what this does *not* depend on: the clock rate. A 10 MHz clock with
    a 500 ps edge is a 1 GHz design problem.

    >>> from hsdd import knee_frequency, ns, to_mhz
    >>> round(to_mhz(knee_frequency(ns(1))))
    500
    """
    if rise_time <= 0:
        raise ValueError("rise time must be positive")
    return 0.5 / rise_time


def rise_time_for_knee(f_knee):
    """The 10-90% rise time (s) whose knee frequency is ``f_knee`` (Hz).

    The inverse of :func:`knee_frequency`; use it to turn a component
    bandwidth into the fastest edge that component can carry.
    """
    if f_knee <= 0:
        raise ValueError("knee frequency must be positive")
    return 0.5 / f_knee


def reflection_coefficient(z_line, z_source):
    """Fraction of an incident step reflected at an impedance step.

    Going from ``z_source`` into ``z_line``. Positive means the line looks
    higher than what drives it and the voltage steps up at the junction.
    Multiply by the driver swing for the size of the step.

    >>> from hsdd import reflection_coefficient
    >>> round(reflection_coefficient(65, 50), 3)
    0.13
    """
    if z_line + z_source == 0:
        raise ValueError("impedances cannot sum to zero")
    return (z_line - z_source) / (z_line + z_source)


def series_terminator(z0, driver_impedance):
    """Series resistor (ohms) that source-terminates a line.

    A series terminator works by making the driver output impedance add up
    to the line impedance, so the reflection that comes back from the far end
    is absorbed rather than re-reflected. The resistor goes right at the
    driver pin -- any line between the driver and the resistor is unmatched.

    Returns 0 if the driver already matches or exceeds the line impedance,
    in which case a series resistor makes things worse, not better.

    >>> from hsdd import series_terminator
    >>> series_terminator(65, 30)
    35
    """
    return max(z0 - driver_impedance, 0)


def critical_length(rise_time, delay_per_inch, rule=RISETIME_RULE):
    """Longest run (in.) that still behaves as a lumped element.

    The free-function form of :meth:`hsdd.TransmissionLine.critical_length`,
    for when you have a delay from a datasheet rather than a geometry.

    >>> from hsdd import critical_length, ns, ps
    >>> round(critical_length(ns(1), ps(180)), 2)    # 1 ns edge on FR-4 outer
    0.93
    """
    if rise_time <= 0:
        raise ValueError("rise time must be positive")
    if delay_per_inch <= 0:
        raise ValueError("delay per inch must be positive")
    return rise_time / (rule * delay_per_inch)


@dataclass(frozen=True)
class TerminationCheck:
    """The verdict from :func:`check_termination`."""

    length: float
    """Run length considered, inches."""

    critical_length: float
    """Longest run that would still be lumped, inches."""

    flight_time: float
    """One-way delay of the run, seconds."""

    rise_time: float
    """Driver 10-90% rise time, seconds."""

    reflection: float
    """Reflection coefficient the line presents to the driver."""

    @property
    def needs_termination(self):
        """True when the run is long enough to ring without a terminator."""
        return self.length > self.critical_length

    @property
    def margin(self):
        """How much of the critical length the run uses, as a ratio.

        Under 1.0 is lumped, over 1.0 wants terminating. Around 1.0 is the
        uncomfortable middle where it depends on how much overshoot the
        receiver tolerates.
        """
        return self.length / self.critical_length

    def summary(self):
        verdict = (
            "TERMINATE: %.3g in. run exceeds the %.3g in. lumped limit"
            % (self.length, self.critical_length)
            if self.needs_termination
            else "lumped: %.3g in. run is inside the %.3g in. limit"
            % (self.length, self.critical_length)
        )
        return "\n".join([
            verdict,
            "  flight time   %8.1f ps  (rise time %.1f ps)"
            % (self.flight_time * 1e12, self.rise_time * 1e12),
            "  length/limit  %8.2f" % self.margin,
            "  reflection    %+8.3f at the driver" % self.reflection,
        ])


def check_termination(line, length, rise_time, driver_impedance,
                      rule=RISETIME_RULE):
    """Decide whether a run needs terminating, and say why.

    ``line`` is any geometry object (:class:`hsdd.Microstrip` and friends),
    ``length`` the run in inches, ``rise_time`` the driver 10-90% edge in
    seconds, ``driver_impedance`` its output impedance in ohms.

    >>> from hsdd import Microstrip, mil, oz, ns, check_termination
    >>> ms = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    >>> check = check_termination(ms, length=6.0, rise_time=ns(1),
    ...                           driver_impedance=30)
    >>> check.needs_termination
    True
    >>> round(check.critical_length, 2)
    1.11
    """
    return TerminationCheck(
        length=length,
        critical_length=line.critical_length(rise_time, rule=rule),
        flight_time=line.delay_for(length),
        rise_time=rise_time,
        reflection=line.reflection(driver_impedance),
    )
