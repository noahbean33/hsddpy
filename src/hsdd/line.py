"""The common interface every transmission-line geometry shares.

Each geometry in :mod:`hsdd.wires`, :mod:`hsdd.microstrip` and
:mod:`hsdd.stripline` is a frozen dataclass holding the cross-section, and
answers the same questions: what is the impedance, how fast does a signal
travel, how much L and C per inch, and -- the one that actually decides
layout -- how long can I run this before it has to be treated as a
transmission line?
"""

from __future__ import annotations

from .general import capacitance_per_inch, inductance_per_inch
from .units import to_mil, to_nh, to_pf, to_ps_per_inch

__all__ = ["TransmissionLine"]

#: A line shorter than (rise time / RISETIME_RULE) x velocity behaves as a
#: lumped element. Johnson & Graham use six: an unterminated line whose delay
#: is under a sixth of the rise time rings by less than a few percent.
RISETIME_RULE = 6.0


class TransmissionLine(object):
    """Base class for transmission-line geometries.

    Subclasses provide :attr:`z0` and :attr:`delay`; everything else is
    derived here. Subclasses whose worksheet gives an explicit inductance or
    capacitance formula override those properties so the library reproduces
    the book's numbers exactly rather than re-deriving them from Z0.
    """

    #: Short label used in :meth:`summary`.
    kind = "line"

    # --- subclasses must provide these ------------------------------------

    @property
    def z0(self):
        """Characteristic impedance, ohms."""
        raise NotImplementedError

    @property
    def delay(self):
        """Propagation delay, seconds per inch."""
        raise NotImplementedError

    # --- derived ----------------------------------------------------------

    @property
    def inductance_per_inch(self):
        """Series inductance, henries per inch."""
        return inductance_per_inch(self.z0, self.delay)

    @property
    def capacitance_per_inch(self):
        """Shunt capacitance, farads per inch."""
        return capacitance_per_inch(self.z0, self.delay)

    @property
    def velocity(self):
        """Propagation velocity, inches per second."""
        return 1.0 / self.delay

    def inductance(self, length):
        """Total series inductance (H) of a run of ``length`` inches."""
        return self.inductance_per_inch * length

    def capacitance(self, length):
        """Total shunt capacitance (F) of a run of ``length`` inches."""
        return self.capacitance_per_inch * length

    def delay_for(self, length):
        """One-way delay (s) of a run of ``length`` inches."""
        return self.delay * length

    # --- the layout questions --------------------------------------------

    def critical_length(self, rise_time, rule=RISETIME_RULE):
        """Longest run (in.) that still behaves as a lumped element.

        Johnson & Graham's rule of thumb: a point-to-point line needs to be
        treated as a transmission line -- and probably terminated -- once its
        one-way delay exceeds about a sixth of the driver's rise time. Below
        that, the reflections land inside the edge and the line is just a
        small lumped capacitance.

        ``rise_time`` is the 10-90% rise time in seconds.
        """
        if rise_time <= 0:
            raise ValueError("rise time must be positive")
        return rise_time / (rule * self.delay)

    def is_transmission_line(self, length, rise_time, rule=RISETIME_RULE):
        """True if a run of ``length`` inches must be treated as a line.

        The complement of :meth:`critical_length`.
        """
        return length > self.critical_length(rise_time, rule=rule)

    def reflection(self, z_other):
        """Reflection coefficient seen going from ``z_other`` into this line.

        Positive means the line looks like a higher impedance than what is
        driving it, so the edge steps up at the discontinuity.
        """
        return (self.z0 - z_other) / (self.z0 + z_other)

    # --- reporting --------------------------------------------------------

    def geometry(self):
        """The cross-section as an ordered list of (name, inches) pairs.

        Subclasses override to control what :meth:`summary` prints.
        """
        return []

    def summary(self):
        """A human-readable block of the numbers a designer wants."""
        dims = "  ".join(
            "%s=%.3gmil" % (name, to_mil(value)) for name, value in self.geometry()
        )
        er = getattr(self, "er", None)
        head = "%s  %s" % (self.kind, dims)
        if er is not None:
            head += "  er=%.3g" % er
        lines = [
            head,
            "  Z0       %8.2f ohm" % self.z0,
            "  delay    %8.2f ps/in   (%.3g in/ns)"
            % (to_ps_per_inch(self.delay), self.velocity * 1e-9),
            "  L        %8.3f nH/in" % to_nh(self.inductance_per_inch),
            "  C        %8.3f pF/in" % to_pf(self.capacitance_per_inch),
        ]
        return "\n".join(lines)
