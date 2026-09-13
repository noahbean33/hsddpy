"""Mutual inductance: parallel lines, and two separated loops.

Source: MLINE.mcd, MLOOP.mcd.

Both formulas answer the same design question from different directions --
how much of what happens on one conductor shows up on another.

Note one deliberate difference from the worksheet: ``MLOOP()`` in Mathcad
returns nanohenries, the only formula in the whole set that does not return
base units. :func:`loop_mutual_inductance` here returns henries like
everything else. The nH-returning original is still available as
``hsdd.mathcad.MLOOP``.
"""

from __future__ import annotations

from math import sqrt

__all__ = [
    "coupling_ratio",
    "parallel_line_mutual_inductance",
    "loop_mutual_inductance",
    "loops_are_well_separated",
]


def coupling_ratio(spacing, height):
    """Fraction of a line inductance that couples to a parallel neighbour.

    ``spacing`` is the centre-to-centre separation and ``height`` the height
    above the reference plane, both in inches.

    The shape is the whole lesson: coupling falls off as ``(s/h)**2``, so it
    is the ratio of separation to *plane distance* that matters, not the
    separation on its own. Halving the dielectric height under a pair of
    traces quarters the crosstalk between them without moving either trace.

    >>> from hsdd import coupling_ratio
    >>> round(coupling_ratio(0.020, 0.010), 3)   # 2h separation
    0.2
    >>> round(coupling_ratio(0.020, 0.005), 3)   # same traces, thinner core
    0.059
    """
    if height <= 0:
        raise ValueError("height above the plane must be positive")
    return 1.0 / (1.0 + (spacing / height) ** 2)


def parallel_line_mutual_inductance(self_inductance, spacing, height):
    """Mutual inductance (H) between two parallel lines over a plane.

    ``self_inductance`` is the inductance of one line over the shared
    parallel run -- get it from the matching geometry class, for example
    ``Microstrip(...).inductance(length)``. Both lines are assumed identical
    and to share a run of that length with centre separation ``spacing``.

    >>> from hsdd import Microstrip, mil, parallel_line_mutual_inductance, to_nh
    >>> ms = Microstrip(height=mil(6), width=mil(8), thickness=mil(1.37))
    >>> l = ms.inductance(2.0)
    >>> round(to_nh(parallel_line_mutual_inductance(l, mil(20), mil(6))), 2)
    1.4
    """
    return self_inductance * coupling_ratio(spacing, height)


def loop_mutual_inductance(separation, area1, area2):
    """Mutual inductance (H) between two well-separated flat loops.

    ``separation`` is the centre-to-centre distance in inches and the areas
    are in square inches. The loops are assumed flat with faces parallel --
    the orientation for maximum coupling, so this is a worst case.

    Falls off as the cube of separation, which is why moving a noisy loop
    twice as far away buys a factor of eight.

    Valid only when the loops are well separated; check with
    :func:`loops_are_well_separated` first.

    >>> from hsdd import loop_mutual_inductance, to_nh
    >>> round(to_nh(loop_mutual_inductance(4.0, 1.0, 1.0)), 4)
    0.0794
    """
    if separation <= 0:
        raise ValueError("loop separation must be positive")
    return 5.08e-9 * (area1 * area2) / separation ** 3


def loops_are_well_separated(separation, area1, area2):
    """True when the :func:`loop_mutual_inductance` approximation holds.

    The derivation treats each loop as a point dipole, which needs the
    separation to exceed the size of either loop.
    """
    return separation > sqrt(area1) and separation > sqrt(area2)
