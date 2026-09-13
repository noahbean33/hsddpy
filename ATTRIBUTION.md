# Attribution and provenance

## Where the formulas come from

The formulas implemented in `src/hsdd/` were transcribed from the Mathcad
13.1 worksheets distributed as companion files to:

> Howard Johnson and Martin Graham, *High-Speed Digital Design: A Handbook of
> Black Magic*, Prentice Hall, 1993.

The worksheets themselves carry a cover letter from Dr. Howard Johnson
(Signal Consulting, Inc., www.sigcon.com) dated 3 January 2008, reproduced in
[`markdown/hsdd-greeting.md`](markdown/hsdd-greeting.md).

The worksheets in turn cite their own sources, which are carried through into
the module docstrings:

- **Microstrip** — I. J. Bahl and Ramesh Garg, "Simple and accurate formulas
  for microstrip with finite strip thickness", *Proc. IEEE* 65, 1977,
  pp. 1611–1612; summarized in T. C. Edwards, *Foundations of Microstrip
  Circuit Design*, John Wiley, 1981 (reprinted 1987). The worksheet warns of
  an error in Edwards Eq. 3.52b, where an `ln()` is omitted.
- **Stripline** — Seymour Cohn, "Problems in Strip Transmission Lines",
  *MTT-3* No. 2, March 1955; summarized in Harlan Howe, *Stripline Circuit
  Design*, Artech House, Norwood MA, 1974.
- **Stripline correction** — the skinny-trace shape factor `ZSTR_K1()`
  carries a correction credited in the worksheet to Robert Canright of
  Richardson, TX.

## How the transcription was done

The PDFs in this repository are Mathcad printouts. `pdftotext` silently drops
radical signs and superscripts from them, so `Z0 := sqrt(lpi/cpi)` comes out
as `Z0 := lpi/cpi` — wrong in a way that is very difficult to spot by eye.
The formulas were instead read from the rendered pages and transcribed by
hand into [`markdown/`](markdown), then into Python.

The check on that work is that every closed-form worksheet stored its own
worked examples, with results Mathcad had computed and saved into the file.
All 60 of those stored results are asserted in
[`tests/test_worked_examples.py`](tests/test_worked_examples.py) and
reproduce to within 1e-9 relative error. That covers the branch selection
between the skinny and wide models in microstrip and stripline, and the
tolerance and reflection-coefficient vectors.

The two simulation worksheets (SHORTLIN, GNDPINS) store no numeric results —
they drive plots — so they are verified against physical invariants instead:
an unterminated line must settle at its DC divider ratio and launch
`2*Z0/(ZS+Z0)` off the open far end; every amp leaving a connector signal pin
must return on the ground pins, whatever the pin pattern.

## Licensing

The formulas here are standard published engineering results, most of them
traceable to the primary literature cited above and predating the book. The
particular *selection*, arrangement and worked examples are Johnson and
Graham's, and the worksheets are distributed as companion material to a
copyrighted book.

No license has been chosen for this repository. Before publishing this
package — to PyPI or anywhere else — decide on one, and consider contacting
Signal Consulting about the derivation from their companion worksheets. The
prose, comments and code here are original; the formulas are not.

## What is original to this library

- The class-based API, unit handling, and the inverse (`for_impedance`) and
  tolerance-corner solvers, none of which are in the worksheets.
- The signal-integrity helpers in `hsdd/signal.py`. Knee frequency
  (`F_knee = 0.5/Tr`) and the rule that a line under a sixth of the rise time
  behaves as a lumped element are both from the book's prose rather than from
  the worksheets.
- Re-casting the connector crosstalk worksheet to take an arbitrary pin
  pattern. The original hard-codes a single ground row and leaves scattering
  the grounds as an exercise for the reader.
- All tests, documentation and the command-line tool.
