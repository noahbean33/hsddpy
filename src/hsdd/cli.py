"""Command line front end: ``hsdd microstrip --height 6mil --width 8mil ...``

Every dimension accepts a unit suffix -- ``6mil``, ``0.15mm``, ``1oz``,
``350ps``, ``2.5GHz``. A bare number means the base unit (inches, seconds,
hertz, ohms).
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .microstrip import Microstrip
from .signal import check_termination, knee_frequency
from .stripline import OffsetStripline, Stripline
from .units import (
    mil,
    parse_length,
    parse_resistance,
    parse_time,
    to_mil,
    to_mhz,
    to_ps_per_inch,
)
from .wires import Coax, RoundWire, TwistedPair


def _length(text):
    try:
        return parse_length(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc))


def _time(text):
    try:
        return parse_time(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc))


def _ohms(text):
    try:
        return parse_resistance(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc))


def _add_common(parser):
    """Options every transmission-line subcommand shares."""
    parser.add_argument("--length", type=_length,
                        help="run length, for total L, C and flight time")
    parser.add_argument("--rise-time", type=_time,
                        help="driver 10-90%% rise time, e.g. 350ps")
    parser.add_argument("--driver", type=_ohms, default=30,
                        help="driver output impedance, ohms (default 30)")


def _report(line, args):
    """Print the standard block for any geometry, plus optional extras."""
    print(line.summary())

    if args.length:
        print("  over %.4g in.:  %.2f nH  %.2f pF  %.0f ps flight time"
              % (args.length,
                 line.inductance(args.length) * 1e9,
                 line.capacitance(args.length) * 1e12,
                 line.delay_for(args.length) * 1e12))

    problems = getattr(line, "check_accuracy", lambda: [])()
    for problem in problems:
        print("  ! %s" % problem)

    if args.rise_time:
        print()
        print("  knee frequency  %8.0f MHz" % to_mhz(knee_frequency(args.rise_time)))
        if args.length:
            check = check_termination(line, args.length, args.rise_time, args.driver)
            for row in check.summary().splitlines():
                print("  " + row)
        else:
            print("  lumped up to    %8.2f in.  (give --length for a verdict)"
                  % line.critical_length(args.rise_time))


def _report_tolerance(span, driver):
    print()
    for row in span.summary(driver).splitlines():
        print("  " + row)


def cmd_microstrip(args):
    if args.z0 is not None:
        line = Microstrip.for_impedance(
            args.z0, height=args.height, thickness=args.thickness, er=args.er
        )
        print("solved width: %.3f mil  (%.4f in.)"
              % (to_mil(line.width), line.width))
    else:
        if args.width is None:
            raise SystemExit("give --width, or --z0 to solve for it")
        line = Microstrip(height=args.height, width=args.width,
                          thickness=args.thickness, er=args.er)
    _report(line, args)
    if args.tol_height or args.tol_width or args.tol_er:
        _report_tolerance(
            line.tolerance(height=args.tol_height, width=args.tol_width,
                           er=args.tol_er),
            args.driver,
        )
    return 0


def cmd_stripline(args):
    if args.z0 is not None:
        line = Stripline.for_impedance(
            args.z0, separation=args.separation, thickness=args.thickness,
            er=args.er,
        )
        print("solved width: %.3f mil  (%.4f in.)"
              % (to_mil(line.width), line.width))
    else:
        if args.width is None:
            raise SystemExit("give --width, or --z0 to solve for it")
        line = Stripline(separation=args.separation, width=args.width,
                         thickness=args.thickness, er=args.er)
    _report(line, args)
    if args.tol_separation or args.tol_width or args.tol_er:
        _report_tolerance(
            line.tolerance(separation=args.tol_separation, width=args.tol_width,
                           er=args.tol_er),
            args.driver,
        )
    return 0


def cmd_offset(args):
    if args.z0 is not None:
        line = OffsetStripline.for_impedance(
            args.z0, height_below=args.height_below,
            height_above=args.height_above, thickness=args.thickness, er=args.er,
        )
        print("solved width: %.3f mil  (%.4f in.)"
              % (to_mil(line.width), line.width))
    else:
        if args.width is None:
            raise SystemExit("give --width, or --z0 to solve for it")
        line = OffsetStripline(
            height_below=args.height_below, height_above=args.height_above,
            width=args.width, thickness=args.thickness, er=args.er,
        )
    _report(line, args)
    return 0


def cmd_round(args):
    _report(RoundWire(diameter=args.diameter, height=args.height), args)
    return 0


def cmd_coax(args):
    _report(Coax(inner_diameter=args.inner, shield_diameter=args.shield,
                 er=args.er), args)
    return 0


def cmd_twist(args):
    _report(TwistedPair(diameter=args.diameter, spacing=args.spacing,
                        er=args.er), args)
    return 0


def cmd_edge(args):
    """What a rise time implies, independent of any particular geometry."""
    rise_time = args.rise_time
    print("rise time      %8.0f ps" % (rise_time * 1e12))
    print("knee frequency %8.0f MHz" % to_mhz(knee_frequency(rise_time)))
    print()
    print("longest unterminated run, by medium:")
    media = [
        ("microstrip, FR-4 outer layer", Microstrip(
            height=mil(6), width=mil(8), thickness=mil(1.37), er=4.5)),
        ("stripline, FR-4 inner layer", Stripline(
            separation=mil(20), width=mil(6), thickness=mil(1.37), er=4.5)),
        ("wire in air", RoundWire(diameter=mil(10), height=mil(100))),
    ]
    for label, line in media:
        print("  %-30s %6.2f in.  (%3.0f ps/in.)"
              % (label, line.critical_length(rise_time),
                 to_ps_per_inch(line.delay)))
    return 0


def cmd_sim(args):
    from .sim import step_response

    response = step_response(
        delay=args.delay, rise_time=args.rise_time, z0=args.z0,
        source_impedance=args.driver, load_capacitance=args.load,
    )
    print(response.summary())
    if args.plot:
        _ascii_plot(response)
    return 0


def _ascii_plot(response, width=64, height=16):
    """A rough terminal plot, for when you just want the shape."""
    voltage = response.voltage
    lo, hi = float(voltage.min()), float(voltage.max())
    span = (hi - lo) or 1.0
    step = max(1, len(voltage) // width)
    columns = voltage[::step][:width]
    print()
    for row in range(height, -1, -1):
        level = lo + span * row / height
        line = "".join(
            "*" if abs(v - level) <= span / (2 * height) else " " for v in columns
        )
        print("  %6.3f |%s" % (level, line))
    print("         +" + "-" * len(columns))
    print("          0%s%.1f ns"
          % (" " * max(0, len(columns) - 8), response.time[-1] * 1e9))


def cmd_crosstalk(args):
    from .connector import connector_crosstalk

    if args.pattern_file:
        with open(args.pattern_file) as handle:
            rows = [line.rstrip("\n") for line in handle if line.strip()]
    else:
        rows = args.row
    if not rows:
        raise SystemExit("give --row (repeatable) or --pattern-file")

    result = connector_crosstalk(
        rows, pitch=args.pitch, pin_length=args.pin_length,
        swing=args.swing, impedance=args.impedance, rise_time=args.rise_time,
    )
    print(result.summary())
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="hsdd",
        description="Transmission line and signal integrity calculations "
                    "for high-speed digital design.",
        epilog="Dimensions take unit suffixes: 6mil, 0.15mm, 1oz, 350ps, 2.5GHz.",
    )
    parser.add_argument("--version", action="version",
                        version="hsdd %s" % __version__)
    subparsers = parser.add_subparsers(dest="command")

    ms = subparsers.add_parser("microstrip", help="surface trace over one plane")
    ms.add_argument("--height", type=_length, required=True,
                    help="dielectric height under the trace, e.g. 6mil")
    ms.add_argument("--width", type=_length, help="trace width")
    ms.add_argument("--thickness", type=_length, default=mil(1.37),
                    help="copper thickness (default 1oz)")
    ms.add_argument("--er", type=float, default=4.5,
                    help="dielectric constant (default 4.5, FR-4)")
    ms.add_argument("--z0", type=float, help="solve for the width that hits this")
    ms.add_argument("--tol-height", type=_length, default=0.0)
    ms.add_argument("--tol-width", type=_length, default=0.0)
    ms.add_argument("--tol-er", type=float, default=0.0)
    _add_common(ms)
    ms.set_defaults(func=cmd_microstrip)

    sl = subparsers.add_parser("stripline", help="buried trace, centred")
    sl.add_argument("--separation", type=_length, required=True,
                    help="plane-to-plane spacing b, e.g. 20mil")
    sl.add_argument("--width", type=_length, help="trace width")
    sl.add_argument("--thickness", type=_length, default=mil(1.37),
                    help="copper thickness (default 1oz)")
    sl.add_argument("--er", type=float, default=4.5)
    sl.add_argument("--z0", type=float, help="solve for the width that hits this")
    sl.add_argument("--tol-separation", type=_length, default=0.0)
    sl.add_argument("--tol-width", type=_length, default=0.0)
    sl.add_argument("--tol-er", type=float, default=0.0)
    _add_common(sl)
    sl.set_defaults(func=cmd_stripline)

    off = subparsers.add_parser("offset-stripline", help="buried trace, off centre")
    off.add_argument("--height-below", type=_length, required=True)
    off.add_argument("--height-above", type=_length, required=True)
    off.add_argument("--width", type=_length)
    off.add_argument("--thickness", type=_length, default=mil(1.37))
    off.add_argument("--er", type=float, default=4.5)
    off.add_argument("--z0", type=float, help="solve for the width that hits this")
    _add_common(off)
    off.set_defaults(func=cmd_offset)

    rd = subparsers.add_parser("round", help="round wire over a ground plane")
    rd.add_argument("--diameter", type=_length, required=True)
    rd.add_argument("--height", type=_length, required=True)
    _add_common(rd)
    rd.set_defaults(func=cmd_round)

    cx = subparsers.add_parser("coax", help="coaxial cable")
    cx.add_argument("--inner", type=_length, required=True)
    cx.add_argument("--shield", type=_length, required=True)
    cx.add_argument("--er", type=float, default=2.2)
    _add_common(cx)
    cx.set_defaults(func=cmd_coax)

    tw = subparsers.add_parser("twist", help="twisted pair")
    tw.add_argument("--diameter", type=_length, required=True)
    tw.add_argument("--spacing", type=_length, required=True)
    tw.add_argument("--er", type=float, default=2.5)
    _add_common(tw)
    tw.set_defaults(func=cmd_twist)

    edge = subparsers.add_parser(
        "edge", help="what a rise time implies: knee frequency, critical lengths")
    edge.add_argument("--rise-time", type=_time, required=True)
    edge.set_defaults(func=cmd_edge)

    sim = subparsers.add_parser("sim", help="step response of a loaded line")
    sim.add_argument("--delay", type=_time, required=True,
                     help="one-way line delay, e.g. 500ps")
    sim.add_argument("--rise-time", type=_time, required=True)
    sim.add_argument("--z0", type=float, default=65.0)
    sim.add_argument("--driver", type=_ohms, default=30,
                     help="driver output impedance (ECL 10, TTL/CMOS 30)")
    sim.add_argument("--load", type=float, default=0.0,
                     help="far-end capacitance in farads, e.g. 20e-12")
    sim.add_argument("--plot", action="store_true", help="rough terminal plot")
    sim.set_defaults(func=cmd_sim)

    xt = subparsers.add_parser(
        "crosstalk", help="connector crosstalk from a G/S pin pattern")
    xt.add_argument("--row", action="append", default=[],
                    help="one row of the pin field, e.g. SSGSSG (repeatable)")
    xt.add_argument("--pattern-file", help="file of G/S rows, one per line")
    xt.add_argument("--pitch", type=_length, default=mil(50))
    xt.add_argument("--pin-length", type=_length, default=mil(500))
    xt.add_argument("--swing", type=float, default=4.0, help="driver swing, volts")
    xt.add_argument("--impedance", type=float, default=50.0)
    xt.add_argument("--rise-time", type=_time, default=1e-9)
    xt.set_defaults(func=cmd_crosstalk)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 1
    try:
        return args.func(args)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
