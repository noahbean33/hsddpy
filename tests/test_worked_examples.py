"""Every result Mathcad stored in the worksheets, replayed against hsdd.

These are not made-up expected values: each one was computed by Mathcad 13.1
and saved in the worksheet file. They are the reason to trust the library.

The checks run through :mod:`hsdd.mathcad`, which is a thin layer over the
real API, so a failure here is a failure in the formulas underneath.
"""

import pytest

from hsdd import mathcad as mc

TOL = 1e-9


def close(got, want, tol=TOL):
    return abs(got - want) <= tol * (abs(want) if want else 1)


# --- CONSTANT.mcd ---------------------------------------------------------

@pytest.mark.parametrize("name, want", [
    ("E0_INCHES", 2.2489159999999998e-13),
    ("U0_INCHES", 3.19185813604723e-08),
    ("C_INCHES", 11803149606.299213),
    ("PDLY_LIGHT_PS_PER_IN", 84.723148765843888),
])
def test_constants(name, want):
    import hsdd

    assert close(getattr(hsdd, name), want)


def test_inductance_coefficient_is_the_5_08_everywhere():
    import hsdd

    assert close(hsdd.L_COEFF, 5.08e-9, 1e-3)


# --- GENERAL.mcd ----------------------------------------------------------

def test_general_relations_round_trip():
    lpi, cpi = 8.49e-9, 2.67e-12
    z0 = mc.Z0(lpi, cpi)
    pdly = mc.PDLY1(lpi, cpi)
    assert close(mc.LPI(z0, pdly), lpi, 1e-12)
    assert close(mc.CPI(z0, pdly), cpi, 1e-12)


def test_delay_of_light():
    assert close(mc.PDLY2(1.0), 84.72e-12)


# --- ROUND.mcd ------------------------------------------------------------

ROUND_D, ROUND_X, ROUND_H = .01, 2.000, .100


@pytest.mark.parametrize("expr, want", [
    (lambda: mc.ZROUND(ROUND_D, ROUND_H), 221.33276724683617),
    (lambda: mc.LROUND(ROUND_D, ROUND_H, ROUND_X), 3.7479015253797596e-08),
    (lambda: mc.LROUND(ROUND_D, ROUND_H, ROUND_X) * 1e9, 37.4790152537976),
    (lambda: mc.LROUND(ROUND_D, ROUND_H, 1), 1.8739507626898798e-08),
    (lambda: mc.CROUND(ROUND_D, ROUND_H, ROUND_X), 7.6608629670681425e-13),
    (lambda: mc.CROUND(ROUND_D, ROUND_H, ROUND_X) * 1e12, 0.76608629670681427),
    (lambda: mc.CROUND(ROUND_D, ROUND_H, 1), 3.8304314835340713e-13),
])
def test_round_wire(expr, want):
    assert close(expr(), want)


# --- COAX.mcd -------------------------------------------------------------

COAX_D1, COAX_D2, COAX_X, COAX_ER = .01, .1, 20.000, 2.2


@pytest.mark.parametrize("expr, want", [
    (lambda: mc.ZCOAX(COAX_D1, COAX_D2, COAX_ER), 93.144153180389836),
    (lambda: mc.LCOAX(COAX_D1, COAX_D2, COAX_X), 2.3394264544819505e-07),
    (lambda: mc.LCOAX(COAX_D1, COAX_D2, COAX_X) * 1e9, 233.94264544819504),
    (lambda: mc.LCOAX(COAX_D1, COAX_D2, 1), 1.1697132272409754e-08),
    (lambda: mc.CCOAX(COAX_D1, COAX_D2, COAX_ER, COAX_X), 2.6943629657277744e-11),
    (lambda: mc.CCOAX(COAX_D1, COAX_D2, COAX_ER, COAX_X) * 1e12, 26.943629657277743),
    (lambda: mc.CCOAX(COAX_D1, COAX_D2, COAX_ER, 1), 1.3471814828638871e-12),
])
def test_coax(expr, want):
    assert close(expr(), want)


# --- TWIST.mcd ------------------------------------------------------------

TW_D, TW_X, TW_S, TW_ER = .02, 2.000, .038, 2.5


@pytest.mark.parametrize("expr, want", [
    (lambda: mc.ZTWIST(TW_D, TW_S, TW_ER), 101.31945719108722),
    (lambda: mc.LTWIST(TW_D, TW_S, TW_X), 2.7127221676001153e-08),
    (lambda: mc.LTWIST(TW_D, TW_S, TW_X) * 1e9, 27.127221676001152),
    (lambda: mc.LTWIST(TW_D, TW_S, 1), 1.3563610838000576e-08),
    (lambda: mc.CTWIST(TW_D, TW_S, TW_ER, TW_X), 2.6460653013906885e-12),
    (lambda: mc.CTWIST(TW_D, TW_S, TW_ER, 1), 1.3230326506953442e-12),
])
def test_twisted_pair(expr, want):
    assert close(expr(), want)


# --- MSTRIP.mcd -----------------------------------------------------------

MS_H, MS_W, MS_T, MS_X, MS_ER = .006, .008, .00137, 11.000, 4.5


@pytest.mark.parametrize("expr, want", [
    (lambda: mc.ZMSTRIP(MS_H, MS_W, MS_T, MS_ER), 56.4434757473894),
    (lambda: mc.LMSTRIP(MS_H, MS_W, MS_T, MS_X), 9.3400757344533228e-08),
    (lambda: mc.LMSTRIP(MS_H, MS_W, MS_T, MS_X) * 1e9, 93.400757344533233),
    (lambda: mc.LMSTRIP(MS_H, MS_W, MS_T, 1), 8.4909779404121116e-09),
    (lambda: mc.CMSTRIP(MS_H, MS_W, MS_T, MS_ER, MS_X), 2.9317227617246377e-11),
    (lambda: mc.CMSTRIP(MS_H, MS_W, MS_T, MS_ER, 1), 2.6652025106587616e-12),
])
def test_microstrip(expr, want):
    assert close(expr(), want)


MSTRIP_TOL_WANT = [64.786784392070174, 51.372408178485863, 37.926663287015465]
MSTRIP_REFL_WANT = [-0.12881957161169236, -0.013538281305002351, 0.13731143957520631]


@pytest.mark.parametrize("index", range(3))
def test_microstrip_tolerance(index):
    got = mc.ZMSTRIP_TOL(.007, .002, .011, .002, .0022, 4.5, .1)
    assert close(got[index], MSTRIP_TOL_WANT[index])


@pytest.mark.parametrize("index", range(3))
def test_microstrip_reflection(index):
    corners = mc.ZMSTRIP_TOL(.007, .002, .011, .002, .0022, 4.5, .1)
    assert close(mc.REFL(corners, 50)[index], MSTRIP_REFL_WANT[index])


# --- SLINE.mcd ------------------------------------------------------------

SL_B, SL_W, SL_T, SL_X, SL_ER = .020, .006, .00137, 11.000, 4.5


@pytest.mark.parametrize("expr, want", [
    (lambda: mc.ZSTRIP(SL_B, SL_W, SL_T, SL_ER), 51.437079595177309),
    (lambda: mc.LSTRIP(SL_B, SL_W, SL_T, SL_X), 1.0168600660829638e-07),
    (lambda: mc.LSTRIP(SL_B, SL_W, SL_T, SL_X) * 1e9, 101.68600660829638),
    (lambda: mc.LSTRIP(SL_B, SL_W, SL_T, 1), 9.2441824189360338e-09),
    (lambda: mc.CSTRIP(SL_B, SL_W, SL_T, SL_ER, SL_X), 3.8433380552099893e-11),
    (lambda: mc.CSTRIP(SL_B, SL_W, SL_T, SL_ER, 1), 3.4939436865545359e-12),
])
def test_stripline(expr, want):
    assert close(expr(), want)


OFFSET_TOL_WANT = [64.056647305279526, 51.726315927621933, 39.2280294542347]
OFFSET_REFL_WANT = [-0.1232426836785414, -0.016970200010488958, 0.12072406632369118]


@pytest.mark.parametrize("index", range(3))
def test_offset_stripline_tolerance(index):
    got = mc.ZOFF_TOL(.007, .002, .032, .002, .008, .002, .0015, 4.5, .1)
    assert close(got[index], OFFSET_TOL_WANT[index])


@pytest.mark.parametrize("index", range(3))
def test_offset_stripline_reflection(index):
    corners = mc.ZOFF_TOL(.007, .002, .032, .002, .008, .002, .0015, 4.5, .1)
    assert close(mc.REFL(corners, 50)[index], OFFSET_REFL_WANT[index])


# --- CAPAC.mcd, CIRCULAR.mcd ---------------------------------------------

@pytest.mark.parametrize("expr, want", [
    (lambda: mc.XCF(100e-12, 1e8), 15.915494309189537),
    (lambda: mc.XCR(100e-12, 5e-9), 15.915494309189533),
    (lambda: mc.LCIRC(.01, 1.3), 1.0032467312050629e-07),
    (lambda: mc.LCIRC(.1, 1.3), 5.3628247434587034e-08),
    (lambda: mc.XLF(100e-9, 1e8), 62.831853071795862),
    (lambda: mc.XLT(100e-9, 5e-9), 62.831853071795862),
])
def test_lumped(expr, want):
    assert close(expr(), want)


def test_plane_pair_is_100_pf_per_square_inch():
    """The worksheet claim: 0.010 in. of FR-4 gives 100 pF/in^2."""
    assert mc.CPLATE(1.0, 1.0, 0.010, 4.5) == pytest.approx(101.2e-12, rel=0.02)


# --- RESIST.mcd (round-trip; the sheet stores no results) ----------------

@pytest.mark.parametrize("expr, want", [
    (lambda: mc.DIAMETER(30), 0.01),
    (lambda: mc.AWG(.01), 30.0),
    (lambda: mc.AWG(mc.DIAMETER(24)), 24.0),
    (lambda: mc.THICKNESS(1), 0.00137),
    (lambda: mc.CPW(.00137), 1.0),
])
def test_resistance_conversions(expr, want):
    assert close(expr(), want, 1e-12)


def test_resistance_temperature_coefficient():
    """The sheet says copper varies 28% over 0-70 C.

    Measured against the room-temperature value the sheet references
    everything to, which is where the 28% comes from: 70 * 0.0039.
    """
    room = mc.RROUND(.01, 1.0, 20)
    cold = mc.RROUND(.01, 1.0, 0)
    hot = mc.RROUND(.01, 1.0, 70)
    assert (hot - cold) / room == pytest.approx(0.28, abs=0.01)


def test_room_temperature_shortcuts_match():
    assert mc.RROUND_RT(.01, 10) == mc.RROUND(.01, 10, 20)
    assert mc.RTRACE_RT(.008, .00137, 10) == mc.RTRACE(.008, .00137, 10, 20)


# --- MLOOP keeps its odd units in the compatibility layer ----------------

def test_mloop_returns_nanohenries_but_the_modern_name_returns_henries():
    from hsdd import loop_mutual_inductance

    assert mc.MLOOP(4.0, 1.0, 1.0) == pytest.approx(
        loop_mutual_inductance(4.0, 1.0, 1.0) * 1e9
    )
