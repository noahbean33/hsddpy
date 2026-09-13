"""A worked design pass, start to finish.

Run it::

    python examples/design_walkthrough.py

The question: a 100 MHz clock with a 500 ps edge has to get from an FPGA to
three loads across a 6-layer FR-4 board. What trace width, how long can the
run be, does it need terminating, and what does the fab tolerance do to it?
"""

from hsdd import (
    Microstrip,
    Stripline,
    check_termination,
    coupling_ratio,
    knee_frequency,
    mil,
    ns,
    oz,
    plane_capacitance_per_square_inch,
    ps,
    series_terminator,
    simulate_line,
    to_mhz,
    to_mil,
    to_pf,
    to_ps_per_inch,
    trace_resistance,
)

RISE_TIME = ps(500)
DRIVER_Z = 30.0          # a typical CMOS output
TARGET_Z0 = 50.0
RUN_LENGTH = 6.0         # inches


def rule(title):
    print()
    print(title)
    print("-" * len(title))


print("Clock: 100 MHz, %g ps edge, %g ohm driver" % (RISE_TIME * 1e12, DRIVER_Z))

rule("1. What bandwidth are we actually designing for?")
print("knee frequency         %6.0f MHz" % to_mhz(knee_frequency(RISE_TIME)))
print("The clock rate does not enter into it. The edge does.")

rule("2. Pick a trace width for 50 ohms on the outer layer")
outer = Microstrip.for_impedance(
    TARGET_Z0, height=mil(4), thickness=oz(1), er=4.2
)
print(outer.summary())
print("  width needed         %6.2f mil" % to_mil(outer.width))
for note in outer.check_accuracy():
    print("  ! %s" % note)

rule("3. And on an inner layer, for comparison")
inner = Stripline.for_impedance(
    TARGET_Z0, separation=mil(16), thickness=oz(1), er=4.2
)
print(inner.summary())
print("  width needed         %6.2f mil" % to_mil(inner.width))
print("  inner is %.0f ps/in. slower -- all of its field is in the laminate"
      % (to_ps_per_inch(inner.delay) - to_ps_per_inch(outer.delay)))

rule("4. Does a 6 in. run need terminating?")
verdict = check_termination(outer, RUN_LENGTH, RISE_TIME, DRIVER_Z)
print(verdict.summary())
print()
print("series terminator      %6.0f ohm at the driver pin"
      % series_terminator(outer.z0, DRIVER_Z))

rule("5. What it looks like unterminated")
response = simulate_line(outer, length=RUN_LENGTH, rise_time=RISE_TIME,
                         source_impedance=DRIVER_Z)
print(response.summary())
print()
matched = simulate_line(outer, length=RUN_LENGTH, rise_time=RISE_TIME,
                        source_impedance=outer.z0)
print("with the series terminator fitted: %.1f%% overshoot" % matched.overshoot)

rule("6. What the fab tolerance does to the impedance")
span = outer.tolerance(height=mil(0.5), width=mil(0.5), er=0.2)
print(span.summary(z_source=TARGET_Z0))
print("A +/-10%% controlled impedance spec %s this stackup."
      % ("covers" if span.percent <= 10 else "does NOT cover"))

rule("7. Crosstalk to the neighbouring trace")
for spacing_mils in (8, 12, 20):
    print("  %2d mil pitch:  %4.1f%% of the aggressor inductance couples"
          % (spacing_mils, 100 * coupling_ratio(mil(spacing_mils), outer.height)))
print("Coupling goes as (s/h)^2, so the thin 4 mil core is doing most of the")
print("work here -- more than any realistic amount of extra spacing would.")

rule("8. The things that are easy to forget")
print("DC drop over the run   %6.1f mohm"
      % (1e3 * trace_resistance(outer.width, oz(1), RUN_LENGTH)))
print("plane pair, 4 mil FR-4 %6.0f pF per square inch"
      % to_pf(plane_capacitance_per_square_inch(mil(4), 4.2)))
print("flight time            %6.0f ps over %g in."
      % (outer.delay_for(RUN_LENGTH) * 1e12, RUN_LENGTH))
print()
print("For reference, a 1 ns edge would allow a %.1f in. run unterminated;"
      % outer.critical_length(ns(1)))
print("the 500 ps edge allows %.1f in." % outer.critical_length(RISE_TIME))
