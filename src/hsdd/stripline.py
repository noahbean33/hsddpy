"""Stripline: a buried trace between two reference planes.

Source: SLINE.mcd (file SLINE2.xmcd).

Formulas from Seymour Cohn, "Problems in Strip Transmission Lines", MTT-3
No. 2, March 1955, summarized in Harlan Howe, "Stripline Circuit Design",
Artech House, 1974. The skinny-trace shape factor carries a correction
credited in the worksheet to Robert Canright of Richardson, TX.

Accuracy is better than 1.3% for ``t/b < 0.25`` and ``t/w < 0.11``, with
``er`` unrestricted.

Unlike microstrip, all of the field is inside the board, so the effective
permittivity is just ``er`` and the delay does not depend on trace geometry
at all -- only on the laminate.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import log, pi, sqrt

from .constants import PDLY_LIGHT
from .line import TransmissionLine
from .solve import ImpedanceRange, solve_monotone

__all__ = ["Stripline", "OffsetStripline"]


# --- the raw formulas, kept close to the worksheet ------------------------

def _k1(w, t):
    """Skinny-trace shape factor (the Canright-corrected form)."""
    return (w / 2) * (
        1 + t / (pi * w) * (1 + log(4 * pi * w / t)) + 0.255 * (t / w) ** 2
    )


def _k2(b, t):
    """Wide-trace shape factor."""
    u = 1 - t / b
    return 2 / u * log(1 / u + 1) - (1 / u - 1) * log(1 / u ** 2 - 1)


def _z_skinny(b, w, t, er):
    return 60 / sqrt(er) * log(4 * b / (pi * _k1(w, t)))


def _z_wide(b, w, t, er):
    return 94.15 / (w / b / (1 - t / b) + _k2(b, t) / pi) * 1 / sqrt(er)


def _z_centered(b, w, t, er):
    if w > 0.35 * b:
        return _z_wide(b, w, t, er)
    return _z_skinny(b, w, t, er)


# --- centred stripline ----------------------------------------------------

@dataclass(frozen=True)
class Stripline(TransmissionLine):
    """A trace centred between two reference planes.

    ``separation``  plane-to-plane spacing b (= h1 + h2 + t)
    ``width``       drawn trace width
    ``thickness``   copper thickness
    ``er``          relative permittivity of the laminate

    >>> from hsdd import Stripline, mil, oz
    >>> sl = Stripline(separation=mil(20), width=mil(6), thickness=oz(1), er=4.5)
    >>> round(sl.z0, 2)
    51.44
    """

    separation: float
    width: float
    thickness: float
    er: float = 4.5

    kind = "Stripline"

    def __post_init__(self):
        if self.separation <= 0:
            raise ValueError("plane separation must be positive")
        if self.width <= 0:
            raise ValueError("trace width must be positive")
        if self.thickness <= 0:
            raise ValueError("copper thickness must be positive")
        if self.er < 1:
            raise ValueError("relative permittivity must be at least 1")
        if self.thickness >= self.separation:
            raise ValueError(
                "copper thickness (%g in.) must be less than the plane "
                "separation (%g in.)" % (self.thickness, self.separation)
            )

    @property
    def z0(self):
        return _z_centered(self.separation, self.width, self.thickness, self.er)

    @property
    def delay(self):
        """Propagation delay (s/in.). Buried, so the wave sees only ``er``."""
        return PDLY_LIGHT * sqrt(self.er)

    @property
    def eeff(self):
        """Effective permittivity -- for stripline, just ``er``."""
        return float(self.er)

    def geometry(self):
        return [("b", self.separation), ("w", self.width), ("t", self.thickness)]

    # --- inverse and tolerance -------------------------------------------

    @classmethod
    def for_impedance(cls, z0, separation, thickness, er=4.5, min_width=None,
                      max_width=None):
        """The trace width that hits a target impedance, as a Stripline.

        >>> from hsdd import Stripline, mil, oz, to_mil
        >>> sl = Stripline.for_impedance(50, separation=mil(20), thickness=oz(1))
        >>> round(to_mil(sl.width), 2)
        6.41
        """
        lo = min_width if min_width is not None else max(thickness * 1.01,
                                                         separation * 0.02)
        hi = max_width if max_width is not None else separation * 10.0

        def z_of(w):
            return cls(separation=separation, width=w, thickness=thickness, er=er).z0

        width = solve_monotone(z_of, z0, lo, hi)
        return cls(separation=separation, width=width, thickness=thickness, er=er)

    def with_width(self, width):
        """A copy of this cross-section with a different trace width."""
        return replace(self, width=width)

    def tolerance(self, separation=0.0, width=0.0, er=0.0):
        """Impedance corners for +/- tolerances on the stackup.

        Pass the half-width of each tolerance band. Wider plane separation,
        narrower trace and lower permittivity all push impedance up, so they
        stack into the high corner.
        """
        high = replace(
            self, separation=self.separation + separation,
            width=self.width - width, er=self.er - er,
        )
        low = replace(
            self, separation=self.separation - separation,
            width=self.width + width, er=self.er + er,
        )
        return ImpedanceRange(low=low.z0, nominal=self.z0, high=high.z0)

    def check_accuracy(self):
        """Warnings about being outside the 1.3% accuracy band of the model."""
        problems = []
        t_b = self.thickness / self.separation
        t_w = self.thickness / self.width
        if t_b > 0.25:
            problems.append("t/b = %.3g is above 0.25" % t_b)
        if t_w > 0.11:
            problems.append("t/w = %.3g is above 0.11" % t_w)
        return problems


# --- offset (asymmetric) stripline ----------------------------------------

@dataclass(frozen=True)
class OffsetStripline(TransmissionLine):
    """A buried trace that is not centred between its two planes.

    Rarely are the two dielectric heights equal in practice; the common case
    is a trace offset to one side of the cavity. The model treats the two
    halves as two centred striplines in parallel.

    ``height_below``  dielectric between the trace and the lower plane (h1)
    ``height_above``  dielectric between the trace and the upper plane (h2)

    No accuracy is guaranteed for this one -- the worksheet says so plainly.

    >>> from hsdd import OffsetStripline, mil
    >>> sl = OffsetStripline(height_below=mil(7), height_above=mil(32),
    ...                      width=mil(8), thickness=mil(1.5), er=4.5)
    >>> round(sl.z0, 2)
    51.73
    """

    height_below: float
    height_above: float
    width: float
    thickness: float
    er: float = 4.5

    kind = "OffsetStripline"

    def __post_init__(self):
        if self.height_below <= 0 or self.height_above <= 0:
            raise ValueError("dielectric heights must be positive")
        if self.width <= 0:
            raise ValueError("trace width must be positive")
        if self.thickness <= 0:
            raise ValueError("copper thickness must be positive")
        if self.er < 1:
            raise ValueError("relative permittivity must be at least 1")

    @property
    def separation(self):
        """Total plane-to-plane spacing, b = h1 + h2 + t."""
        return self.height_below + self.height_above + self.thickness

    @property
    def z0(self):
        w, t, er = self.width, self.thickness, self.er
        za = _z_centered(2 * self.height_below + t, w, t, er)
        zb = _z_centered(2 * self.height_above + t, w, t, er)
        return (2 * za * zb) / (za + zb)

    @property
    def delay(self):
        """Same as centred stripline: the wave sees only ``er``."""
        return PDLY_LIGHT * sqrt(self.er)

    @property
    def eeff(self):
        return float(self.er)

    def geometry(self):
        return [
            ("h1", self.height_below),
            ("h2", self.height_above),
            ("w", self.width),
            ("t", self.thickness),
        ]

    @classmethod
    def for_impedance(cls, z0, height_below, height_above, thickness, er=4.5,
                      min_width=None, max_width=None):
        """The trace width that hits a target impedance, as an OffsetStripline."""
        span = min(height_below, height_above)
        lo = min_width if min_width is not None else max(thickness * 1.01, span * 0.02)
        hi = max_width if max_width is not None else span * 20.0

        def z_of(w):
            return cls(
                height_below=height_below, height_above=height_above,
                width=w, thickness=thickness, er=er,
            ).z0

        width = solve_monotone(z_of, z0, lo, hi)
        return cls(
            height_below=height_below, height_above=height_above,
            width=width, thickness=thickness, er=er,
        )

    def with_width(self, width):
        """A copy of this cross-section with a different trace width."""
        return replace(self, width=width)

    def tolerance(self, height_below=0.0, height_above=0.0, width=0.0, er=0.0):
        """Impedance corners for +/- tolerances on the stackup.

        >>> from hsdd import OffsetStripline, mil
        >>> sl = OffsetStripline(height_below=mil(7), height_above=mil(32),
        ...                      width=mil(8), thickness=mil(1.5), er=4.5)
        >>> rng = sl.tolerance(height_below=mil(2), height_above=mil(2),
        ...                    width=mil(2), er=0.1)
        >>> round(rng.high, 2), round(rng.nominal, 2), round(rng.low, 2)
        (64.06, 51.73, 39.23)
        """
        high = replace(
            self,
            height_below=self.height_below + height_below,
            height_above=self.height_above + height_above,
            width=self.width - width,
            er=self.er - er,
        )
        low = replace(
            self,
            height_below=self.height_below - height_below,
            height_above=self.height_above - height_above,
            width=self.width + width,
            er=self.er + er,
        )
        return ImpedanceRange(low=low.z0, nominal=self.z0, high=high.z0)

    def check_accuracy(self):
        """Warnings about the cross-section, plus the standing caveat."""
        problems = ["offset stripline is an approximation with no accuracy bound"]
        t_w = self.thickness / self.width
        if t_w > 0.11:
            problems.append("t/w = %.3g is above 0.11" % t_w)
        return problems
