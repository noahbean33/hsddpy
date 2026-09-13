"""Microstrip: a trace on an outer layer, over one ground plane.

Source: MSTRIP.mcd.

Formulas from I. J. Bahl and Ramesh Garg, "Simple and accurate formulas for
microstrip with finite strip thickness", Proc. IEEE 65, 1977, pp. 1611-1612,
summarized in T. C. Edwards, "Foundations of Microstrip Circuit Design",
John Wiley, 1981. (Watch out for the error in Edwards Eq. 3.52b, where he
omits an ln().)

Each quantity has a skinny-trace and a wide-trace model with a changeover at
w = h. Accuracy is better than 2% over::

    0   < t/h < 0.2
    0.1 < w/h < 20
    0   < er  < 16

:meth:`Microstrip.check_accuracy` will tell you when you have wandered out.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import log, pi, sqrt

from .constants import PDLY_LIGHT
from .line import TransmissionLine
from .solve import ImpedanceRange, solve_monotone

__all__ = ["Microstrip", "effective_permittivity", "effective_width"]


# --- the raw formulas, kept close to the worksheet ------------------------

def _e_skinny(h, w, er):
    """Effective permittivity, skinny-trace model (w < h)."""
    return (er + 1) / 2 + ((er - 1) / 2) * (
        (1 + 12 * h / w) ** -0.500 + 0.04 * (1 - w / h) ** 2
    )


def _e_wide(h, w, er):
    """Effective permittivity, wide-trace model (w > h)."""
    return (er + 1) / 2 + ((er - 1) / 2) * (1 + 12 * h / w) ** -0.500


def effective_permittivity(h, w, t, er):
    """Effective relative permittivity of a microstrip cross-section.

    A microstrip field is partly in the board and partly in the air above it,
    so the signal sees something between ``er`` and 1. A skinny trace (little
    of its field trapped under it) approaches the average of the two; a wide
    trace close to the plane approaches ``er``. The trace thickness term
    pulls the result back down slightly.
    """
    base = _e_wide(h, w, er) if w > h else _e_skinny(h, w, er)
    return base - ((er - 1) * (t / h)) / (4.6 * sqrt(w / h))


def effective_width(h, w, t):
    """Effective electrical trace width (in.).

    A trace of finite thickness behaves as though it were wider than it is
    drawn, because the sidewalls hold charge too.
    """
    if w > h / (2 * pi):
        return w + (1.25 * t) / pi * (1 + log(2 * h / t))
    return w + (1.25 * t) / pi * (1 + log(4 * pi * w / t))


def _z_skinny(h, w, t):
    we = effective_width(h, w, t)
    return 60 * log(8 * h / we + we / (4 * h))


def _z_wide(h, w, t):
    we = effective_width(h, w, t)
    return (120 * pi) / (we / h + 1.393 + 0.667 * log(we / h + 1.444))


# --- the geometry ---------------------------------------------------------

@dataclass(frozen=True)
class Microstrip(TransmissionLine):
    """A surface trace over a single reference plane.

    All dimensions in inches; use :func:`hsdd.mil` and :func:`hsdd.oz`.

    ``height``     dielectric thickness between trace and plane
    ``width``      drawn trace width
    ``thickness``  copper thickness (``oz(1)`` is 1.37 mil)
    ``er``         relative permittivity of the dielectric (4.5 for FR-4)

    >>> from hsdd import Microstrip, mil, oz
    >>> ms = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    >>> round(ms.z0, 2)
    56.44
    """

    height: float
    width: float
    thickness: float
    er: float = 4.5

    kind = "Microstrip"

    def __post_init__(self):
        if self.height <= 0:
            raise ValueError("dielectric height must be positive")
        if self.width <= 0:
            raise ValueError("trace width must be positive")
        if self.thickness <= 0:
            raise ValueError("copper thickness must be positive")
        if self.er < 1:
            raise ValueError("relative permittivity must be at least 1")
        if self.thickness >= self.height:
            raise ValueError(
                "copper thickness (%g in.) must be less than the dielectric "
                "height (%g in.)" % (self.thickness, self.height)
            )

    # --- the numbers ------------------------------------------------------

    @property
    def eeff(self):
        """Effective relative permittivity seen by the propagating wave."""
        return effective_permittivity(self.height, self.width, self.thickness, self.er)

    @property
    def effective_width(self):
        """Electrical trace width (in.), wider than drawn by the copper."""
        return effective_width(self.height, self.width, self.thickness)

    @property
    def z0(self):
        h, w, t = self.height, self.width, self.thickness
        z = _z_wide(h, w, t) if w > h else _z_skinny(h, w, t)
        return z / sqrt(self.eeff)

    @property
    def delay(self):
        return PDLY_LIGHT * sqrt(self.eeff)

    def geometry(self):
        return [("h", self.height), ("w", self.width), ("t", self.thickness)]

    # --- inverse and tolerance -------------------------------------------

    @classmethod
    def for_impedance(cls, z0, height, thickness, er=4.5, min_width=None,
                      max_width=None):
        """The trace width that hits a target impedance, as a Microstrip.

        The stackup (``height``, ``thickness``, ``er``) is what the
        fabricator gives you; this solves for the one dimension you control.

        >>> from hsdd import Microstrip, mil, oz, to_mil
        >>> ms = Microstrip.for_impedance(50, height=mil(6), thickness=oz(1))
        >>> round(to_mil(ms.width), 2)
        10.15
        >>> round(ms.z0, 6)
        50.0

        Raises :class:`ValueError` if no width in the search range reaches
        the target -- widen it with ``min_width``/``max_width``, or accept
        that the stackup cannot do it.
        """
        lo = min_width if min_width is not None else max(thickness * 1.01, height * 0.05)
        hi = max_width if max_width is not None else height * 25.0

        def z_of(w):
            return cls(height=height, width=w, thickness=thickness, er=er).z0

        width = solve_monotone(z_of, z0, lo, hi)
        return cls(height=height, width=width, thickness=thickness, er=er)

    def with_width(self, width):
        """A copy of this cross-section with a different trace width."""
        return replace(self, width=width)

    def tolerance(self, height=0.0, width=0.0, er=0.0):
        """Impedance corners for +/- tolerances on the stackup.

        Pass the *half-width* of each tolerance band (``height=mil(1)`` means
        the dielectric is held to +/-1 mil). The corners stack the errors that
        push the same way: a thicker dielectric with a narrower trace in a
        lower-permittivity laminate gives the high corner.

        >>> from hsdd import Microstrip, mil
        >>> ms = Microstrip(height=mil(7), width=mil(11), thickness=mil(2.2), er=4.5)
        >>> rng = ms.tolerance(height=mil(2), width=mil(2), er=0.1)
        >>> round(rng.high, 2), round(rng.nominal, 2), round(rng.low, 2)
        (64.79, 51.37, 37.93)
        """
        high = replace(
            self, height=self.height + height, width=self.width - width,
            er=self.er - er,
        )
        low = replace(
            self, height=self.height - height, width=self.width + width,
            er=self.er + er,
        )
        return ImpedanceRange(low=low.z0, nominal=self.z0, high=high.z0)

    # --- model validity ---------------------------------------------------

    def check_accuracy(self):
        """Warnings about being outside the 2% accuracy band of the model.

        Returns a list of strings, empty when the cross-section is inside
        ``0 < t/h < 0.2``, ``0.1 < w/h < 20`` and ``er < 16``. The formulas
        still return a number outside those bounds; it is just less trusted.
        """
        problems = []
        t_h = self.thickness / self.height
        w_h = self.width / self.height
        if t_h > 0.2:
            problems.append("t/h = %.3g is above 0.2" % t_h)
        if not (0.1 < w_h < 20):
            problems.append("w/h = %.3g is outside 0.1 to 20" % w_h)
        if self.er > 16:
            problems.append("er = %.3g is above 16" % self.er)
        return problems
