"""Step-response simulator for a lossless line with an arbitrary load.

Source: SHORTLIN.mcd (H. Johnson, 5/29/95).

This is the worksheet that makes the case for the whole risetime/delay rule:
drive an unterminated line with edges of 0, 2, 3, 4, 5 and 6 times the line
delay and watch the ringing disappear. What matters is the *ratio* -- scale
delay and rise time together and the waveform does not change.

The method is frequency-domain. Build the response of the line-plus-load
over a grid of frequencies, multiply by the spectrum of a driving step with
a shaped edge, and inverse-FFT back to a waveform. The line itself is
modelled as pure delay: lossless and distortionless. Real FR-4 above a
gigahertz is neither, so treat the ringing amplitudes as an upper bound and
the edge degradation as optimistic.

Requires numpy: ``pip install hsdd[sim]``.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["StepResponse", "step_response", "frequency_response", "simulate_line"]


def _numpy():
    try:
        import numpy
    except ImportError:  # pragma: no cover - exercised only without numpy
        raise ImportError(
            "hsdd.sim needs numpy; install it with 'pip install hsdd[sim]'"
        )
    return numpy


def _grid(np, record, dt):
    """FFT indices, frequency points and complex frequency.

    The driving waveform is a rectangular pulse N/2 samples long, so only the
    first half of the transform is usable -- and the trailing falling edge
    has to stay outside the part we keep, or it drags the settled value down.
    Callers pass ``record`` already padded for that.
    """
    if dt <= 0:
        raise ValueError("sample interval must be positive")
    if record <= 0:
        raise ValueError("record length must be positive")
    needed = 2 * record / dt
    logn = np.ceil(np.log(needed) / np.log(2))
    n = int(np.floor(2 ** logn + 0.5))
    k = np.arange(0, n // 2 + 1)
    f = (1.0 / dt) * k / n
    return n, k, f, 2j * np.pi * f


def _drive_spectrum(np, n, k, s, dt):
    """Spectrum of a rectangular pulse n/2 samples long, unit amplitude."""
    denominator = np.where(k == 0, 1, 1 - np.exp(-s * dt))
    return np.where(
        k == 0, n / 2, (1 - np.exp(-s * n / 2 * dt)) / denominator
    ) * dt


def _edge_spectrum(np, s, rise_time, dt, shape):
    """Edge-shaping filter applied to the ideal step."""
    if rise_time == 0:
        return np.ones_like(s)
    if shape == "gaussian":
        # 10-90% rise time is 2.56 sigma for a Gaussian edge. The guard
        # matches the worksheet: past |s*r| = 10 the term has decayed into
        # nothing anyway, and zeroing it keeps the exponent finite.
        within = np.abs(s * rise_time) < 10
        safe = np.where(within, s, 0)
        envelope = np.where(within, np.exp((safe ** 2 * (rise_time / 2.56) ** 2) / 2), 0)
        return envelope * np.exp(-s * rise_time / 2)
    if shape == "linear":
        # 0-100% ramp: a boxcar of width rise_time, normalized.
        denominator = np.where(s == 0, 1, 1 - np.exp(-s * dt))
        return np.where(
            s == 0, 1,
            (1 - np.exp(-s * rise_time)) / denominator * dt / rise_time,
        )
    raise ValueError("edge shape must be 'gaussian' or 'linear', got %r" % (shape,))


def _system_response(np, s, delay, z0, source_impedance, load_resistance,
                     load_capacitance):
    """Frequency response from driver output to the far end of the line."""
    zl = load_resistance / (1 + s * load_resistance * load_capacitance)
    h = np.exp(-s * delay)                       # lossless delay
    accept = z0 / (source_impedance + z0)        # what gets launched
    near_end = 1 - 2 * accept                    # (ZS - Z0) / (ZS + Z0)
    transmit = 2 * zl / (zl + z0)                # far-end transmission
    far_end = transmit - 1                       # far-end reflection
    # Forward path over the sum of all round trips.
    return accept * h * transmit / (1 - far_end * h * near_end * h)


@dataclass(frozen=True)
class StepResponse:
    """A simulated waveform at the far end of a line, plus its metrics.

    ``voltage`` is normalized so that an ideal, perfectly matched step
    settles at 1.0 -- multiply by the driver swing for volts.
    """

    time: "object"
    """Sample times, seconds (a numpy array)."""

    voltage: "object"
    """Far-end voltage, normalized to a unit driver step (a numpy array)."""

    delay: float
    """One-way line delay used, seconds."""

    rise_time: float
    """Driver 10-90% rise time used, seconds."""

    z0: float
    source_impedance: float
    load_resistance: float
    load_capacitance: float

    @property
    def final_value(self):
        """Settled value, taken from the last tenth of the record."""
        tail = self.voltage[-max(1, len(self.voltage) // 10):]
        return float(tail.mean())

    @property
    def peak(self):
        """Highest voltage reached."""
        return float(self.voltage.max())

    @property
    def overshoot(self):
        """Overshoot past the settled value, percent.

        This is the number the risetime/delay rule is about. Keep the rise
        time above six times the line delay and it stays in single digits.
        """
        final = self.final_value
        return 100.0 * (self.peak - final) / final

    @property
    def undershoot(self):
        """Deepest dip below the settled value after the first peak, percent.

        The ring-back that causes double-clocking on an edge-triggered input.
        """
        import numpy as np

        final = self.final_value
        peak_index = int(np.argmax(self.voltage))
        after = self.voltage[peak_index:]
        if len(after) == 0:
            return 0.0
        return 100.0 * (final - float(after.min())) / final

    def settling_time(self, tolerance=0.05):
        """Time (s) until the waveform stays inside ``tolerance`` of final.

        Measured from t=0, so it includes the flight time down the line.
        Returns the end of the record if it never settles that tightly.
        """
        import numpy as np

        final = self.final_value
        outside = np.abs(self.voltage - final) > tolerance * abs(final)
        if not outside.any():
            return 0.0
        return float(self.time[int(np.where(outside)[0][-1])])

    def summary(self):
        return "\n".join([
            "step response  Z0=%.4g  ZS=%.4g  delay=%.3g ps  tr=%.3g ps"
            % (self.z0, self.source_impedance, self.delay * 1e12,
               self.rise_time * 1e12),
            "  tr/delay ratio  %8.2f" % (
                self.rise_time / self.delay if self.delay else float("inf")),
            "  peak            %8.3f  (%.1f%% overshoot)"
            % (self.peak, self.overshoot),
            "  ring-back       %8.1f%%" % self.undershoot,
            "  settles (5%%)    %8.1f ps" % (self.settling_time() * 1e12),
        ])


def step_response(delay, rise_time, z0=65.0, source_impedance=30.0,
                  load_resistance=10e3, load_capacitance=0.0,
                  duration=None, dt=None, edge="gaussian"):
    """Simulate the far end of a line driven by a step.

    ``delay``             one-way line delay, seconds
    ``rise_time``         driver 10-90% rise time, seconds (0 for an ideal step)
    ``z0``                line impedance, ohms
    ``source_impedance``  driver output impedance (ECL ~10, TTL/CMOS ~30)
    ``load_resistance``   far-end resistance (10k stands in for "open")
    ``load_capacitance``  far-end capacitance, farads
    ``duration``          record length, seconds (default 20 line delays)
    ``dt``                sample interval (default delay/50)
    ``edge``              ``"gaussian"`` or ``"linear"``

    >>> from hsdd import step_response, ns
    >>> fast = step_response(delay=ns(1), rise_time=ns(2))
    >>> slow = step_response(delay=ns(1), rise_time=ns(6))
    >>> fast.overshoot > 20 and slow.overshoot < 5
    True
    """
    np = _numpy()
    if delay <= 0:
        raise ValueError("line delay must be positive")
    if rise_time < 0:
        raise ValueError("rise time cannot be negative")
    if load_resistance <= 0:
        raise ValueError("load resistance must be positive")

    if duration is None:
        duration = 20 * delay
    if dt is None:
        dt = delay / 50.0

    # Pad the transform so the trailing edge of the drive pulse, smeared out
    # by the edge filter and the round trips, lands outside the kept record.
    record = duration + 5 * rise_time + 10 * delay
    n, k, _f, s = _grid(np, record, dt)
    spectrum = (
        _drive_spectrum(np, n, k, s, dt)
        * _edge_spectrum(np, s, rise_time, dt, edge)
        * _system_response(np, s, delay, z0, source_impedance,
                           load_resistance, load_capacitance)
    )
    waveform = np.fft.irfft(spectrum, n=n) / dt

    keep = min(n // 2, int(round(duration / dt)))
    return StepResponse(
        time=np.arange(keep) * dt,
        voltage=waveform[:keep],
        delay=delay,
        rise_time=rise_time,
        z0=z0,
        source_impedance=source_impedance,
        load_resistance=load_resistance,
        load_capacitance=load_capacitance,
    )


def frequency_response(delay, z0=65.0, source_impedance=30.0,
                       load_resistance=10e3, load_capacitance=0.0,
                       duration=None, dt=None):
    """Frequency response of the same line, as ``(frequencies, response)``.

    ``frequencies`` in hertz and ``response`` complex. The capacitive load
    shows up here as the rolloff that eats the edge in the time domain.
    """
    np = _numpy()
    if duration is None:
        duration = 20 * delay
    if dt is None:
        dt = delay / 50.0
    _n, _k, f, s = _grid(np, duration + 10 * delay, dt)
    response = _system_response(
        np, s, delay, z0, source_impedance, load_resistance, load_capacitance
    )
    return f, response


def simulate_line(line, length, rise_time, source_impedance=30.0,
                  load_resistance=10e3, load_capacitance=0.0, **kwargs):
    """Run :func:`step_response` on a geometry from this library.

    Takes the impedance and delay straight off a :class:`hsdd.Microstrip`,
    :class:`hsdd.Stripline` or any other geometry class.

    >>> from hsdd import Microstrip, mil, oz, ns, simulate_line
    >>> ms = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    >>> response = simulate_line(ms, length=6.0, rise_time=ns(1))
    >>> response.overshoot > 10
    True
    """
    return step_response(
        delay=line.delay_for(length),
        rise_time=rise_time,
        z0=line.z0,
        source_impedance=source_impedance,
        load_resistance=load_resistance,
        load_capacitance=load_capacitance,
        **kwargs
    )
