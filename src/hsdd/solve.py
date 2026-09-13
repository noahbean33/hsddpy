"""Root finding and tolerance analysis.

The worksheets all run forwards: geometry in, impedance out. A designer
almost always has the opposite problem -- the stackup is fixed by the
fabricator and the target impedance by the standard, and the question is how
wide to draw the trace. :func:`solve_monotone` does that inversion, and the
geometry classes wrap it in ``for_impedance()`` constructors.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["solve_monotone", "ImpedanceRange"]


def solve_monotone(func, target, lo, hi, tol=1e-12, max_iter=200):
    """Solve ``func(x) == target`` for x in [lo, hi] by bisection.

    ``func`` must be continuous and monotone over the bracket -- increasing
    or decreasing, it works out which. Returns x. Raises :class:`ValueError`
    if the target is not bracketed, with the range that *is* reachable, which
    is usually the more useful message ("you cannot get 50 ohms out of this
    stackup at any width").
    """
    if lo >= hi:
        raise ValueError("bracket is empty: lo=%g hi=%g" % (lo, hi))

    f_lo = func(lo)
    f_hi = func(hi)
    low_value, high_value = min(f_lo, f_hi), max(f_lo, f_hi)
    if not (low_value <= target <= high_value):
        raise ValueError(
            "target %g is out of reach: the search range gives %g to %g"
            % (target, low_value, high_value)
        )

    rising = f_hi > f_lo
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        value = func(mid)
        if abs(value - target) <= tol * max(1.0, abs(target)):
            return mid
        if (value < target) == rising:
            lo = mid
        else:
            hi = mid
        if hi - lo <= tol * max(1.0, abs(mid)):
            break
    return 0.5 * (lo + hi)


@dataclass(frozen=True)
class ImpedanceRange:
    """What a stackup's tolerances do to characteristic impedance.

    ``low`` and ``high`` are the corners, ``nominal`` the centre. Produced by
    the ``tolerance()`` method on the microstrip and stripline classes.
    """

    low: float
    nominal: float
    high: float

    @property
    def spread(self):
        """Full corner-to-corner spread, ohms."""
        return self.high - self.low

    @property
    def percent(self):
        """Worst-case deviation from nominal, percent.

        This is the number to compare against the +/-10% (or tighter) that a
        controlled-impedance spec will ask the fabricator to hold.
        """
        worst = max(abs(self.high - self.nominal), abs(self.nominal - self.low))
        return 100.0 * worst / self.nominal

    def reflection(self, z_source):
        """Reflection coefficient at each corner against a source impedance.

        Returns ``(low, nominal, high)`` in the same order as the fields, so
        the signs run the other way: the low-impedance corner reflects
        positive against a higher source.
        """
        return tuple(
            (z_source - z) / (z_source + z) for z in (self.low, self.nominal, self.high)
        )

    def worst_reflection(self, z_source):
        """Largest reflection magnitude over the corners, as a fraction.

        Multiply by the driver's swing to get the size of the step the
        receiver sees off the discontinuity.
        """
        return max(abs(r) for r in self.reflection(z_source))

    def summary(self, z_source=None):
        lines = [
            "Z0  %.2f ohm nominal, %.2f to %.2f (+/-%.1f%%)"
            % (self.nominal, self.low, self.high, self.percent)
        ]
        if z_source is not None:
            low, nom, high = self.reflection(z_source)
            lines.append(
                "reflection vs %.4g ohm:  %+.3f nominal, worst %+.3f"
                % (z_source, nom, max((low, high), key=abs))
            )
        return "\n".join(lines)
