"""The library as a designer uses it: units, solvers, tolerances, validation."""

import math

import pytest

import hsdd
from hsdd import (
    Coax,
    Microstrip,
    OffsetStripline,
    RoundWire,
    Stripline,
    TwistedPair,
    mil,
    ns,
    oz,
    ps,
    to_mil,
)

GEOMETRIES = [
    RoundWire(diameter=mil(10), height=mil(100)),
    Coax(inner_diameter=mil(10), shield_diameter=mil(100), er=2.2),
    TwistedPair(diameter=mil(20), spacing=mil(38), er=2.5),
    Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5),
    Stripline(separation=mil(20), width=mil(6), thickness=oz(1), er=4.5),
    OffsetStripline(height_below=mil(7), height_above=mil(32), width=mil(8),
                    thickness=oz(1), er=4.5),
]


# --- units ----------------------------------------------------------------

def test_unit_helpers_round_trip():
    assert hsdd.to_mil(hsdd.mil(6)) == pytest.approx(6)
    assert hsdd.to_mm(hsdd.mm(1.5)) == pytest.approx(1.5)
    assert hsdd.to_oz(hsdd.oz(2)) == pytest.approx(2)
    assert hsdd.to_ps(hsdd.ps(350)) == pytest.approx(350)
    assert hsdd.to_pf(hsdd.pf(10)) == pytest.approx(10)


def test_one_oz_copper_is_1_37_mil():
    assert to_mil(oz(1)) == pytest.approx(1.37)


@pytest.mark.parametrize("text, want", [
    ("6mil", 0.006), ("6 mil", 0.006), ("0.006", 0.006), ("0.006in", 0.006),
    ("1oz", 0.00137), ("2.54mm", 0.1), ("1e-3", 0.001),
])
def test_parse_length(text, want):
    assert hsdd.parse_length(text) == pytest.approx(want)


@pytest.mark.parametrize("text, want", [
    ("350ps", 350e-12), ("1ns", 1e-9), ("1e-9", 1e-9),
])
def test_parse_time(text, want):
    assert hsdd.parse_time(text) == pytest.approx(want)


def test_parse_rejects_unknown_units():
    with pytest.raises(ValueError) as info:
        hsdd.parse_length("6furlongs")
    assert "unknown" in str(info.value)


def test_parse_rejects_nonsense():
    with pytest.raises(ValueError):
        hsdd.parse_time("soon")


# --- the shared line interface -------------------------------------------

@pytest.mark.parametrize("line", GEOMETRIES, ids=lambda g: g.kind)
def test_every_geometry_is_self_consistent(line):
    """Z0, delay, L and C must agree with each other to within the rounding
    in the worksheet coefficients."""
    assert line.z0 > 0
    assert line.delay > 0
    derived_z0 = math.sqrt(line.inductance_per_inch / line.capacitance_per_inch)
    derived_delay = math.sqrt(line.inductance_per_inch * line.capacitance_per_inch)
    assert derived_z0 == pytest.approx(line.z0, rel=0.01)
    assert derived_delay == pytest.approx(line.delay, rel=0.01)


@pytest.mark.parametrize("line", GEOMETRIES, ids=lambda g: g.kind)
def test_totals_scale_with_length(line):
    assert line.inductance(4.0) == pytest.approx(4 * line.inductance(1.0))
    assert line.capacitance(4.0) == pytest.approx(4 * line.capacitance(1.0))
    assert line.delay_for(4.0) == pytest.approx(4 * line.delay)


@pytest.mark.parametrize("line", GEOMETRIES, ids=lambda g: g.kind)
def test_summary_mentions_the_kind(line):
    assert line.kind in line.summary()


def test_nothing_travels_faster_than_light():
    for line in GEOMETRIES:
        assert line.delay >= hsdd.PDLY_LIGHT * (1 - 1e-12)


def test_critical_length_halves_when_the_edge_halves():
    line = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    assert line.critical_length(ns(1)) == pytest.approx(
        2 * line.critical_length(ps(500))
    )


def test_is_transmission_line_agrees_with_critical_length():
    line = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    limit = line.critical_length(ns(1))
    assert line.is_transmission_line(limit * 1.01, ns(1))
    assert not line.is_transmission_line(limit * 0.99, ns(1))


# --- solving for width ----------------------------------------------------

@pytest.mark.parametrize("target", [40, 50, 60, 75, 90])
def test_microstrip_solver_hits_the_target(target):
    line = Microstrip.for_impedance(target, height=mil(6), thickness=oz(1), er=4.5)
    assert line.z0 == pytest.approx(target, rel=1e-9)


@pytest.mark.parametrize("target", [40, 50, 60, 75])
def test_stripline_solver_hits_the_target(target):
    line = Stripline.for_impedance(target, separation=mil(20), thickness=oz(1),
                                   er=4.5)
    assert line.z0 == pytest.approx(target, rel=1e-9)


def test_offset_stripline_solver_hits_the_target():
    line = OffsetStripline.for_impedance(
        50, height_below=mil(7), height_above=mil(32), thickness=oz(1), er=4.5
    )
    assert line.z0 == pytest.approx(50, rel=1e-9)


def test_solver_reports_an_unreachable_target():
    with pytest.raises(ValueError) as info:
        Microstrip.for_impedance(500, height=mil(6), thickness=oz(1), er=4.5)
    assert "out of reach" in str(info.value)


def test_wider_traces_have_lower_impedance():
    base = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    assert base.with_width(mil(16)).z0 < base.z0
    assert base.with_width(mil(4)).z0 > base.z0


def test_solve_monotone_handles_a_rising_function():
    assert hsdd.solve_monotone(lambda x: x ** 2, 4.0, 0.0, 10.0) == pytest.approx(2.0)


# --- tolerance ------------------------------------------------------------

def test_tolerance_corners_bracket_nominal():
    line = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    span = line.tolerance(height=mil(1), width=mil(1), er=0.2)
    assert span.low < span.nominal < span.high
    assert span.spread == pytest.approx(span.high - span.low)
    assert span.percent > 0


def test_zero_tolerance_collapses_to_nominal():
    line = Stripline(separation=mil(20), width=mil(6), thickness=oz(1), er=4.5)
    span = line.tolerance()
    assert span.low == span.nominal == span.high
    assert span.percent == 0


def test_reflection_is_zero_at_a_perfect_match():
    line = Microstrip.for_impedance(50, height=mil(6), thickness=oz(1))
    assert line.reflection(50) == pytest.approx(0, abs=1e-9)


def test_worst_reflection_picks_the_bigger_corner():
    line = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    span = line.tolerance(height=mil(1), width=mil(1), er=0.2)
    assert span.worst_reflection(50) == max(abs(r) for r in span.reflection(50))


# --- validation -----------------------------------------------------------

@pytest.mark.parametrize("build", [
    lambda: Microstrip(height=0, width=mil(8), thickness=oz(1)),
    lambda: Microstrip(height=mil(6), width=-1, thickness=oz(1)),
    lambda: Microstrip(height=mil(1), width=mil(8), thickness=oz(1)),  # t > h
    lambda: Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=0.5),
    lambda: Stripline(separation=mil(1), width=mil(6), thickness=oz(1)),
    lambda: RoundWire(diameter=mil(10), height=mil(2)),   # wire in the plane
    lambda: Coax(inner_diameter=mil(100), shield_diameter=mil(10)),
    lambda: TwistedPair(diameter=mil(20), spacing=mil(5)),
    lambda: OffsetStripline(height_below=0, height_above=mil(10),
                            width=mil(8), thickness=oz(1)),
])
def test_impossible_geometry_is_rejected(build):
    with pytest.raises(ValueError):
        build()


def test_accuracy_warnings_fire_outside_the_published_band():
    fine = Microstrip(height=mil(20), width=mil(20), thickness=mil(1.37), er=4.5)
    assert fine.check_accuracy() == []

    thick = Microstrip(height=mil(4), width=mil(8), thickness=mil(2.8), er=4.5)
    assert any("t/h" in note for note in thick.check_accuracy())

    exotic = Microstrip(height=mil(20), width=mil(20), thickness=mil(1.37), er=20)
    assert any("er" in note for note in exotic.check_accuracy())


def test_stripline_accuracy_warnings():
    thick = Stripline(separation=mil(8), width=mil(6), thickness=mil(2.8), er=4.5)
    notes = thick.check_accuracy()
    assert any("t/b" in note for note in notes)
    assert any("t/w" in note for note in notes)


def test_offset_stripline_always_warns_it_is_an_approximation():
    line = OffsetStripline(height_below=mil(7), height_above=mil(32),
                           width=mil(8), thickness=oz(1))
    assert any("approximation" in note for note in line.check_accuracy())


# --- physical sanity ------------------------------------------------------

def test_stripline_is_slower_than_microstrip_on_the_same_laminate():
    """Stripline buries the whole field in the laminate; microstrip keeps
    some of it in air, so microstrip is faster."""
    ms = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    sl = Stripline(separation=mil(20), width=mil(6), thickness=oz(1), er=4.5)
    assert sl.delay > ms.delay


def test_microstrip_effective_permittivity_sits_between_air_and_laminate():
    line = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    assert 1.0 < line.eeff < 4.5


def test_effective_width_exceeds_drawn_width():
    line = Microstrip(height=mil(6), width=mil(8), thickness=oz(1), er=4.5)
    assert line.effective_width > line.width


def test_centred_offset_stripline_matches_the_centred_model():
    """An offset stripline with equal heights is a centred stripline."""
    t = oz(1)
    h = mil(9)
    offset = OffsetStripline(height_below=h, height_above=h, width=mil(6),
                             thickness=t, er=4.5)
    centred = Stripline(separation=2 * h + t, width=mil(6), thickness=t, er=4.5)
    assert offset.z0 == pytest.approx(centred.z0)


def test_coupling_falls_off_as_the_square_of_separation_over_height():
    assert hsdd.coupling_ratio(0.02, 0.01) == pytest.approx(1 / 5)
    assert hsdd.coupling_ratio(0.04, 0.01) == pytest.approx(1 / 17)


def test_loop_separation_check():
    assert hsdd.loops_are_well_separated(4.0, 1.0, 1.0)
    assert not hsdd.loops_are_well_separated(0.5, 1.0, 1.0)
