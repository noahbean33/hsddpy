"""The command line front end."""

import pytest

from hsdd.cli import main


def run(capsys, *argv):
    code = main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_microstrip_reports_the_worked_example(capsys):
    code, out, _err = run(
        capsys, "microstrip", "--height", "6mil", "--width", "8mil",
        "--thickness", "1oz", "--er", "4.5",
    )
    assert code == 0
    assert "56.44" in out


def test_units_are_interchangeable(capsys):
    _code, metric, _err = run(
        capsys, "microstrip", "--height", "0.1524mm", "--width", "0.2032mm",
        "--thickness", "1oz",
    )
    _code, imperial, _err = run(
        capsys, "microstrip", "--height", "6mil", "--width", "8mil",
        "--thickness", "1oz",
    )
    assert metric == imperial


def test_solving_for_width(capsys):
    code, out, _err = run(
        capsys, "microstrip", "--height", "6mil", "--thickness", "1oz", "--z0", "50",
    )
    assert code == 0
    assert "solved width" in out
    assert "50.00 ohm" in out


def test_width_is_required_without_a_target(capsys):
    with pytest.raises(SystemExit):
        main(["microstrip", "--height", "6mil"])


def test_tolerance_block(capsys):
    code, out, _err = run(
        capsys, "microstrip", "--height", "6mil", "--width", "8mil",
        "--tol-height", "1mil", "--tol-er", "0.2",
    )
    assert code == 0
    assert "nominal" in out


def test_termination_check_appears_with_a_rise_time(capsys):
    code, out, _err = run(
        capsys, "microstrip", "--height", "6mil", "--width", "8mil",
        "--length", "6", "--rise-time", "1ns",
    )
    assert code == 0
    assert "knee frequency" in out
    assert "TERMINATE" in out


def test_stripline(capsys):
    code, out, _err = run(
        capsys, "stripline", "--separation", "20mil", "--width", "6mil",
        "--thickness", "1oz", "--er", "4.5",
    )
    assert code == 0
    assert "51.44" in out


def test_offset_stripline(capsys):
    code, out, _err = run(
        capsys, "offset-stripline", "--height-below", "7mil",
        "--height-above", "32mil", "--width", "8mil", "--thickness", "1.5mil",
    )
    assert code == 0
    assert "51.73" in out


@pytest.mark.parametrize("argv, expected", [
    (["round", "--diameter", "10mil", "--height", "100mil"], "221.33"),
    (["coax", "--inner", "10mil", "--shield", "100mil", "--er", "2.2"], "93.14"),
    (["twist", "--diameter", "20mil", "--spacing", "38mil", "--er", "2.5"], "101.32"),
])
def test_wire_geometries(capsys, argv, expected):
    code, out, _err = run(capsys, *argv)
    assert code == 0
    assert expected in out


def test_edge_command(capsys):
    code, out, _err = run(capsys, "edge", "--rise-time", "350ps")
    assert code == 0
    assert "1429 MHz" in out
    assert "microstrip" in out


def test_sim_command(capsys):
    pytest.importorskip("numpy")
    code, out, _err = run(
        capsys, "sim", "--delay", "500ps", "--rise-time", "1ns", "--plot",
    )
    assert code == 0
    assert "overshoot" in out


def test_crosstalk_command(capsys):
    pytest.importorskip("numpy")
    code, out, _err = run(
        capsys, "crosstalk", "--row", "SSSSSSSS", "--row", "GGGGGGGG",
        "--row", "SSSSSSSS",
    )
    assert code == 0
    assert "worst crosstalk" in out


def test_crosstalk_from_a_file(capsys, tmp_path):
    pytest.importorskip("numpy")
    path = tmp_path / "pins.txt"
    path.write_text("SSSSSSSS\nGGGGGGGG\nSSSSSSSS\n")
    code, out, _err = run(capsys, "crosstalk", "--pattern-file", str(path))
    assert code == 0
    assert "8 grounds" in out


def test_crosstalk_needs_a_pattern():
    pytest.importorskip("numpy")
    with pytest.raises(SystemExit):
        main(["crosstalk"])


def test_bad_units_are_reported(capsys):
    with pytest.raises(SystemExit):
        main(["microstrip", "--height", "6furlongs", "--width", "8mil"])


def test_impossible_geometry_exits_with_an_error(capsys):
    code, _out, err = run(
        capsys, "microstrip", "--height", "1mil", "--width", "8mil",
        "--thickness", "1oz",
    )
    assert code == 2
    assert "error:" in err


def test_no_command_prints_help(capsys):
    code, out, _err = run(capsys)
    assert code == 1
    assert "usage:" in out
