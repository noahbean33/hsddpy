"""Transmission lines made of wire: round wire over ground, coax, twisted pair.

Source: ROUND.mcd, COAX.mcd, TWIST.mcd.

All three worksheets have the same shape -- impedance, delay, inductance,
capacitance -- so all three are the same class shape here.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log, sqrt

from .constants import PDLY_LIGHT
from .line import TransmissionLine

__all__ = ["RoundWire", "Coax", "TwistedPair"]


def _check_er(er):
    if er < 1:
        raise ValueError("relative permittivity must be at least 1, got %r" % (er,))


@dataclass(frozen=True)
class RoundWire(TransmissionLine):
    """Round wire suspended above a ground plane -- wire-wrap, flying leads.

    ``diameter`` and ``height`` (of the wire centre above the plane) are in
    inches. The wire is assumed to be in air, so the delay is just the speed
    of light and there is no ``er`` to set.

    >>> from hsdd import RoundWire, mil
    >>> w = RoundWire(diameter=mil(10), height=mil(100))   # AWG 30, 0.1 in. up
    >>> round(w.z0, 1)
    221.3
    """

    diameter: float
    height: float

    kind = "RoundWire"

    def __post_init__(self):
        if self.diameter <= 0:
            raise ValueError("wire diameter must be positive")
        if self.height <= self.diameter / 2:
            raise ValueError(
                "wire centre height (%g in.) must clear the plane by more than "
                "the wire radius (%g in.)" % (self.height, self.diameter / 2)
            )

    @property
    def _shape(self):
        return log(4 * self.height / self.diameter)

    @property
    def z0(self):
        return 60 * self._shape

    @property
    def delay(self):
        """Propagation delay (s/in.). Air dielectric, so this is a constant."""
        return PDLY_LIGHT

    @property
    def inductance_per_inch(self):
        return 5.08e-9 * self._shape

    @property
    def capacitance_per_inch(self):
        return 1.413e-12 / self._shape

    def geometry(self):
        return [("d", self.diameter), ("h", self.height)]


@dataclass(frozen=True)
class Coax(TransmissionLine):
    """Coaxial cable.

    ``inner_diameter`` is the centre conductor, ``shield_diameter`` the
    inside diameter of the shield, both in inches. ``er`` is the relative
    dielectric constant of the material between them (2.2 for solid PTFE,
    2.3 for polyethylene, 1.4-1.6 for foamed dielectrics).

    >>> from hsdd import Coax, mil
    >>> c = Coax(inner_diameter=mil(10), shield_diameter=mil(100), er=2.2)
    >>> round(c.z0, 1)
    93.1
    """

    inner_diameter: float
    shield_diameter: float
    er: float = 1.0

    kind = "Coax"

    def __post_init__(self):
        if self.inner_diameter <= 0:
            raise ValueError("inner conductor diameter must be positive")
        if self.shield_diameter <= self.inner_diameter:
            raise ValueError("shield diameter must exceed the inner diameter")
        _check_er(self.er)

    @property
    def _shape(self):
        return log(self.shield_diameter / self.inner_diameter)

    @property
    def z0(self):
        return 60 / sqrt(self.er) * self._shape

    @property
    def delay(self):
        return PDLY_LIGHT * sqrt(self.er)

    @property
    def inductance_per_inch(self):
        return 5.08e-9 * self._shape

    @property
    def capacitance_per_inch(self):
        return (1.41e-12 / self._shape) * self.er

    def geometry(self):
        return [("d1", self.inner_diameter), ("d2", self.shield_diameter)]


@dataclass(frozen=True)
class TwistedPair(TransmissionLine):
    """Twisted pair.

    ``diameter`` is the wire diameter and ``spacing`` the separation between
    wire centres, both in inches. ``er`` is the effective relative dielectric
    constant of the medium between the wires -- lower than the insulation's
    own permittivity, because much of the field is in air.

    Same formula shape as coax, but with 2s/d in place of d2/d1 and twice
    the inductance coefficient, because both wires carry field.

    >>> from hsdd import TwistedPair, mil
    >>> tp = TwistedPair(diameter=mil(20), spacing=mil(38), er=2.5)
    >>> round(tp.z0, 1)
    101.3
    """

    diameter: float
    spacing: float
    er: float = 1.0

    kind = "TwistedPair"

    def __post_init__(self):
        if self.diameter <= 0:
            raise ValueError("wire diameter must be positive")
        if self.spacing < self.diameter:
            raise ValueError(
                "centre-to-centre spacing (%g in.) cannot be less than the wire "
                "diameter (%g in.)" % (self.spacing, self.diameter)
            )
        _check_er(self.er)

    @property
    def _shape(self):
        return log(2 * self.spacing / self.diameter)

    @property
    def z0(self):
        return 120 / sqrt(self.er) * self._shape

    @property
    def delay(self):
        return PDLY_LIGHT * sqrt(self.er)

    @property
    def inductance_per_inch(self):
        return 10.16e-9 * self._shape

    @property
    def capacitance_per_inch(self):
        return (0.7065e-12 / self._shape) * self.er

    def geometry(self):
        return [("d", self.diameter), ("s", self.spacing)]
