"""Rules of thumb, the simulator, and the connector crosstalk model."""

import pytest

import hsdd
from hsdd import Microstrip, mil, ns, oz, pf, ps

np = pytest.importorskip("numpy")


# --- knee frequency and terminations --------------------------------------

def test_knee_frequency_is_half_over_rise_time():
    assert hsdd.knee_frequency(ns(1)) == pytest.approx(500e6)
    assert hsdd.knee_frequency(ps(100)) == pytest.approx(5e9)


def test_knee_frequency_round_trips():
    assert hsdd.rise_time_for_knee(hsdd.knee_frequency(ps(350))) == pytest.approx(ps(350))


def test_knee_frequency_does_not_care_about_clock_rate():
    """The whole point: a slow clock with a fast edge is still a fast design."""
    assert hsdd.knee_frequency(ps(500)) == pytest.approx(1e9)


@pytest.mark.parametrize("rise_time", [0, -1e-9])
def test_knee_frequency_rejects_impossible_edges(rise_time):
    with pytest.raises(ValueError):
        hsdd.knee_frequency(rise_time)


def test_series_terminator_completes_the_driver_impedance():
    assert hsdd.series_terminator(65, 30) == 35
    assert hsdd.series_terminator(50, 20) == 30


def test_series_terminator_refuses_to_go_negative():
    """A driver already stronger than the line cannot be series-terminated."""
    assert hsdd.series_terminator(50, 75) == 0


def test_reflection_coefficient_signs():
    assert hsdd.reflection_coefficient(65, 50) > 0     # step up into a higher line
    assert hsdd.reflection_coefficient(40, 50) < 0     # step down
    assert hsdd.reflection_coefficient(50, 50) == 0


def test_critical_length_free_function_matches_the_method():
    line = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    assert hsdd.critical_length(ns(1), line.delay) == pytest.approx(
        line.critical_length(ns(1))
    )


def test_check_termination_verdict():
    line = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    short = hsdd.check_termination(line, 0.5, ns(1), 30)
    long = hsdd.check_termination(line, 6.0, ns(1), 30)
    assert not short.needs_termination
    assert long.needs_termination
    assert short.margin < 1 < long.margin
    assert "TERMINATE" in long.summary()
    assert "lumped" in short.summary()


# --- the step response simulator -----------------------------------------

def test_unterminated_line_settles_at_the_dc_divider():
    """RL = 10k against a 30 ohm driver settles just under 1.0."""
    response = hsdd.step_response(delay=ns(1), rise_time=0, z0=65,
                                  source_impedance=30, load_resistance=10e3)
    assert response.final_value == pytest.approx(10e3 / (10e3 + 30), rel=1e-3)


def test_first_step_is_the_source_divider_doubled_at_the_open_end():
    """Launch ZC/(ZS+ZC), double it at the open far end."""
    z0, zs = 65.0, 30.0
    response = hsdd.step_response(delay=ns(1), rise_time=0, z0=z0,
                                  source_impedance=zs)
    expected = 2 * z0 / (zs + z0)
    first_plateau = response.voltage[
        int(1.5e-9 / (response.time[1] - response.time[0]))
    ]
    assert first_plateau == pytest.approx(expected, rel=0.01)


def test_overshoot_falls_as_the_edge_slows():
    """The worksheet's whole argument, as a monotone sequence."""
    overshoots = [
        hsdd.step_response(delay=ns(1), rise_time=ns(1) * ratio).overshoot
        for ratio in (0, 2, 3, 4)
    ]
    assert overshoots == sorted(overshoots, reverse=True)
    assert overshoots[0] > 30      # ideal edge rings badly
    assert overshoots[-1] < 5      # four times the delay is nearly clean


def test_six_times_the_delay_is_effectively_clean():
    """Which is where the rule of six in critical_length() comes from."""
    response = hsdd.step_response(delay=ns(1), rise_time=ns(6))
    assert response.overshoot < 2


def test_only_the_ratio_matters():
    """Scale delay and rise time together and the waveform is unchanged."""
    a = hsdd.step_response(delay=ns(1), rise_time=ns(2))
    b = hsdd.step_response(delay=ns(2), rise_time=ns(4))
    c = hsdd.step_response(delay=ns(3), rise_time=ns(6))
    assert a.overshoot == pytest.approx(b.overshoot, abs=0.5)
    assert a.overshoot == pytest.approx(c.overshoot, abs=0.5)


def test_capacitive_load_slows_the_edge_and_adds_overshoot():
    clean = hsdd.step_response(delay=ps(500), rise_time=ns(3))
    loaded = hsdd.step_response(delay=ps(500), rise_time=ns(3),
                                load_capacitance=pf(20))
    assert loaded.overshoot > clean.overshoot
    assert loaded.settling_time() > clean.settling_time()


def test_matched_source_does_not_ring():
    """Series-terminate the driver to the line and the ringing goes away."""
    response = hsdd.step_response(delay=ns(1), rise_time=0, z0=65,
                                  source_impedance=65)
    assert response.overshoot < 1


def test_linear_and_gaussian_edges_broadly_agree():
    gaussian = hsdd.step_response(delay=ns(1), rise_time=ns(3), edge="gaussian")
    linear = hsdd.step_response(delay=ns(1), rise_time=ns(3), edge="linear")
    assert linear.final_value == pytest.approx(gaussian.final_value, rel=0.01)


def test_unknown_edge_shape_is_rejected():
    with pytest.raises(ValueError):
        hsdd.step_response(delay=ns(1), rise_time=ns(1), edge="triangular")


@pytest.mark.parametrize("kwargs", [
    {"delay": 0, "rise_time": ns(1)},
    {"delay": ns(1), "rise_time": -1},
    {"delay": ns(1), "rise_time": ns(1), "load_resistance": 0},
])
def test_simulator_rejects_impossible_inputs(kwargs):
    with pytest.raises(ValueError):
        hsdd.step_response(**kwargs)


def test_simulate_line_takes_its_numbers_from_the_geometry():
    line = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    response = hsdd.simulate_line(line, length=6.0, rise_time=ns(1))
    assert response.z0 == pytest.approx(line.z0)
    assert response.delay == pytest.approx(line.delay_for(6.0))


def test_frequency_response_starts_at_dc_and_rolls_off_with_load():
    freq, bare = hsdd.frequency_response(delay=ps(500), load_capacitance=0)
    _freq, loaded = hsdd.frequency_response(delay=ps(500), load_capacitance=pf(20))
    assert freq[0] == 0
    assert abs(bare[0]) == pytest.approx(10e3 / (10e3 + 30), rel=1e-3)
    high = len(freq) // 4
    assert abs(loaded[high]) < abs(bare[high])


# --- connector crosstalk --------------------------------------------------

ONE_ROW = ["SSSSSSSS", "GGGGGGGG", "SSSSSSSS"]
SCATTERED = ["GSSGSSGS", "SGSSGSSG", "SSGSSGSS"]


def test_pin_field_counts():
    field = hsdd.PinField(ONE_ROW)
    assert (field.n_ground, field.n_signal) == (8, 16)
    assert field.ground_fraction == pytest.approx(8 / 24)


def test_pin_field_rejects_patterns_it_cannot_solve():
    with pytest.raises(ValueError):
        hsdd.PinField(["SSSS", "SSSS"])          # no grounds
    with pytest.raises(ValueError):
        hsdd.PinField(["GGGG"])                  # no signals
    with pytest.raises(ValueError):
        hsdd.PinField([])


def test_one_ground_pin_cannot_form_a_loop():
    with pytest.raises(ValueError):
        hsdd.connector_crosstalk(["SSSS", "GSSS"])


def test_every_amp_that_leaves_comes_back_on_the_grounds():
    """The physical constraint the last row of the linear system imposes.

    It holds whatever the pin pattern, so it is the check that the system
    was assembled correctly.
    """
    for pattern in (ONE_ROW, SCATTERED):
        result = hsdd.connector_crosstalk(pattern)
        assert np.allclose(result.ground_currents.sum(axis=0), -1.0)


def test_scattering_the_grounds_beats_lining_them_up():
    """The conclusion the worksheet was built to reach, with the ground
    count held equal so it is the placement doing the work."""
    lined_up = hsdd.connector_crosstalk(ONE_ROW)
    scattered = hsdd.connector_crosstalk(SCATTERED)
    assert lined_up.field.n_ground == scattered.field.n_ground
    assert scattered.worst < lined_up.worst
    assert scattered.mean < lined_up.mean


def test_more_grounds_beats_fewer():
    sparse = hsdd.connector_crosstalk(["SSSSSSSS", "GSSSSSSG", "SSSSSSSS"])
    dense = hsdd.connector_crosstalk(["SSSSSSSS", "GGGGGGGG", "SSSSSSSS"])
    assert dense.worst < sparse.worst


def test_crosstalk_scales_with_slew_rate():
    slow = hsdd.connector_crosstalk(ONE_ROW, rise_time=ns(2))
    fast = hsdd.connector_crosstalk(ONE_ROW, rise_time=ns(1))
    assert fast.worst == pytest.approx(2 * slow.worst)


def test_a_pin_does_not_talk_to_itself():
    result = hsdd.connector_crosstalk(ONE_ROW)
    assert np.allclose(np.diag(result.coupling), 0)


def test_crosstalk_result_reports_a_real_pin():
    result = hsdd.connector_crosstalk(ONE_ROW)
    assert result.worst_pin in result.field.labels()
    assert "worst crosstalk" in result.summary()


def test_explicit_slew_overrides_the_swing_calculation():
    result = hsdd.connector_crosstalk(ONE_ROW, di_dt=1e8)
    assert result.di_dt == 1e8
