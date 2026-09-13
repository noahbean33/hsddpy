"""Crosstalk through a connector, as a function of its ground-pin pattern.

Source: GNDPINS.mcd, an experimental worksheet.

The question is the one every connector pinout argument turns on: how many
ground pins, and where? Signal current flowing down a pin has to come back
somewhere, and it comes back on whichever ground pins minimise the total
loop area. The return current spreads over several grounds, and the flux it
fails to cancel shows up as a voltage on every other pin.

The model solves for that return-current distribution exactly, for a given
pin field, then sums the coupled voltage on each signal pin.

  1. represent each pin position in the connector face as a complex number
  2. write the flux through each ground loop from one amp on each pin
  3. solve for the ground currents that null the flux in every ground loop,
     subject to all the current coming back
  4. add up what is left over on every victim pin

The original worksheet hard-codes one row of grounds and leaves scattering
them as an exercise ("change the equations to scatter the ground positions").
Here the pattern is an argument, so the comparison it was built for is one
call each.

Requires numpy: ``pip install hsdd[sim]``.

Caveats worth keeping in mind: pins are modelled as parallel straight wires
of finite length with no return path through a shell, the far-end and
near-end terminations are ignored, and the answer is a mutual-inductance
coupling only. It ranks pinouts against each other well; it is not a
substitute for a 3-D field solve of a specific connector.
"""

from __future__ import annotations

from dataclasses import dataclass

from .constants import INCH, U0_METERS
from .units import mil

__all__ = ["PinField", "CrosstalkResult", "connector_crosstalk"]


def _numpy():
    try:
        import numpy
    except ImportError:  # pragma: no cover - exercised only without numpy
        raise ImportError(
            "hsdd.connector needs numpy; install it with 'pip install hsdd[sim]'"
        )
    return numpy


@dataclass(frozen=True)
class PinField:
    """A connector pin pattern, parsed from rows of characters.

    ``G`` marks a ground pin, ``S`` a signal pin, and anything else (space,
    ``.``) an empty position. Row 0 is the top row as written.

    >>> from hsdd import PinField
    >>> field = PinField(["SSSS", "GGGG", "SSSS"])
    >>> field.n_ground, field.n_signal
    (4, 8)
    """

    pattern: "object"
    """The rows of characters, as given."""

    pitch: float = mil(50)
    """Centre-to-centre pin spacing, inches. 0.050 in. is the classic grid."""

    pin_length: float = mil(500)
    """Length of the pins through the connector, inches."""

    wire_radius: float = mil(10)
    """Pin radius, inches. Sets the near-field floor, so it barely matters."""

    def __post_init__(self):
        if not self.pattern:
            raise ValueError("pin pattern is empty")
        if self.pitch <= 0 or self.pin_length <= 0 or self.wire_radius <= 0:
            raise ValueError("pitch, pin length and wire radius must be positive")
        if not self.ground_positions:
            raise ValueError("pin pattern has no ground pins (mark them 'G')")
        if not self.signal_positions:
            raise ValueError("pin pattern has no signal pins (mark them 'S')")

    def _positions(self, marker):
        found = []
        for row, line in enumerate(self.pattern):
            for col, char in enumerate(line):
                if char.upper() == marker:
                    found.append(complex(col, row) * self.pitch)
        return found

    @property
    def ground_positions(self):
        """Ground pin positions as complex inches (real = column)."""
        return self._positions("G")

    @property
    def signal_positions(self):
        """Signal pin positions as complex inches."""
        return self._positions("S")

    @property
    def n_ground(self):
        return len(self.ground_positions)

    @property
    def n_signal(self):
        return len(self.signal_positions)

    @property
    def ground_fraction(self):
        """Grounds as a fraction of all populated pins."""
        return self.n_ground / float(self.n_ground + self.n_signal)

    def labels(self):
        """A ``(row, col)`` label for each signal pin, in solution order."""
        out = []
        for row, line in enumerate(self.pattern):
            for col, char in enumerate(line):
                if char.upper() == "S":
                    out.append((row, col))
        return out


def _flux_matrix(np, from_points, to_points, sources, radius_m, length_m):
    """Flux (Wb) in each loop from one amp at each source position.

    A loop is the area between the wires at ``from_points[i]`` and
    ``to_points[i]``. The path integral collapses to a log: deform the path
    to first circle the current source at constant radius (where the dot
    product is zero and nothing accumulates), then run radially out to the
    far wire (where it is unity and the 1/r integrand gives the log).
    """
    start = np.asarray(from_points)[:, None]
    end = np.asarray(to_points)[:, None]
    source = np.asarray(sources)[None, :]
    outer = np.maximum(np.abs(end - source), radius_m)
    inner = np.maximum(np.abs(start - source), radius_m)
    return U0_METERS / (2 * np.pi) * np.log(outer / inner) * length_m


@dataclass(frozen=True)
class CrosstalkResult:
    """What :func:`connector_crosstalk` worked out."""

    field: PinField
    crosstalk: "object"
    """Summed crosstalk voltage on each signal pin, volts (numpy array)."""

    coupling: "object"
    """Full victim-by-aggressor voltage matrix, volts (numpy array)."""

    ground_currents: "object"
    """Return current on each ground pin per aggressor, amps (numpy array).

    Column ``m`` is how one amp on signal ``m`` comes back. Every column sums
    to -1: all the current that leaves has to return.
    """

    di_dt: float
    """Aggressor current slew used, A/s."""

    @property
    def worst(self):
        """Largest total crosstalk on any one pin, volts."""
        return float(self.crosstalk.max())

    @property
    def mean(self):
        """Mean total crosstalk over the signal pins, volts."""
        return float(self.crosstalk.mean())

    @property
    def worst_pin(self):
        """``(row, col)`` of the worst-off signal pin."""
        import numpy as np

        return self.field.labels()[int(np.argmax(self.crosstalk))]

    def summary(self):
        row, col = self.worst_pin
        return "\n".join([
            "%d signal pins, %d grounds (%.0f%% ground)"
            % (self.field.n_signal, self.field.n_ground,
               100 * self.field.ground_fraction),
            "  aggressor slew  %8.3g A/s" % self.di_dt,
            "  worst crosstalk %8.1f mV  at pin row %d col %d"
            % (self.worst * 1e3, row, col),
            "  mean crosstalk  %8.1f mV" % (self.mean * 1e3),
        ])


def connector_crosstalk(pattern, pitch=mil(50), pin_length=mil(500),
                        wire_radius=mil(10), swing=4.0, impedance=50.0,
                        rise_time=1e-9, di_dt=None):
    """Sum the crosstalk on every signal pin of a connector pin field.

    ``pattern`` is a list of strings (``G`` ground, ``S`` signal, anything
    else empty) or a ready-made :class:`PinField`. Lengths are in inches.

    The aggressor slew defaults to a ``swing`` volt edge into ``impedance``
    ohms in ``rise_time`` seconds -- 4 V into 50 ohms in 1 ns, as the
    worksheet has it. Pass ``di_dt`` directly to override.

    Every signal pin is treated as an aggressor at once and the coupled
    voltages are summed in magnitude, so this is a worst case: all pins
    switching the same way at the same instant.

    Same eight grounds, two placements -- all in one row, or spread through
    the field:

    >>> from hsdd import connector_crosstalk
    >>> one_row   = ["SSSSSSSS", "GGGGGGGG", "SSSSSSSS"]
    >>> scattered = ["GSSGSSGS", "SGSSGSSG", "SSGSSGSS"]
    >>> round(connector_crosstalk(one_row).worst * 1e3)
    635
    >>> round(connector_crosstalk(scattered).worst * 1e3)
    542
    """
    np = _numpy()

    field = pattern if isinstance(pattern, PinField) else PinField(
        pattern=list(pattern), pitch=pitch, pin_length=pin_length,
        wire_radius=wire_radius,
    )

    if di_dt is None:
        if rise_time <= 0 or impedance <= 0:
            raise ValueError("rise time and impedance must be positive")
        di_dt = swing / impedance / rise_time

    # Work in metres: the flux integral is in SI.
    grounds = np.asarray(field.ground_positions) * INCH
    signals = np.asarray(field.signal_positions) * INCH
    radius_m = field.wire_radius * INCH
    length_m = field.pin_length * INCH

    n_gnd = len(grounds)
    n_sig = len(signals)
    if n_gnd < 2:
        raise ValueError("need at least two ground pins to form a return loop")

    # Ground loops run between consecutive grounds in the order they appear,
    # which gives n_gnd - 1 independent loops whatever the pattern.
    loop_start = grounds[:-1]
    loop_end = grounds[1:]

    # Flux in each ground loop from one amp on each signal, and on each ground.
    b_flux = np.zeros((n_gnd, n_sig))
    a_mat = np.zeros((n_gnd, n_gnd))
    b_flux[:-1, :] = _flux_matrix(np, loop_start, loop_end, signals, radius_m, length_m)
    a_mat[:-1, :] = _flux_matrix(np, loop_start, loop_end, grounds, radius_m, length_m)

    # The loops give one constraint too few: add "all the current comes back".
    a_mat[-1, :] = 1.0
    b_flux[-1, :] = 1.0

    ground_currents = -np.linalg.solve(a_mat, b_flux)

    # Victim voltage is measured between each signal pin and the first ground.
    reference = np.full(n_sig, grounds[0])
    from_signal = _flux_matrix(np, signals, reference, signals, radius_m, length_m)
    from_ground = _flux_matrix(np, signals, reference, grounds, radius_m, length_m)

    coupling = (from_signal + from_ground @ ground_currents) * di_dt
    np.fill_diagonal(coupling, 0.0)     # a pin does not talk to itself
    coupling = np.abs(coupling)

    return CrosstalkResult(
        field=field,
        crosstalk=coupling.sum(axis=1),   # sum over aggressors
        coupling=coupling,
        ground_currents=ground_currents,
        di_dt=di_dt,
    )
