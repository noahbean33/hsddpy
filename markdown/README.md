# HSDD Mathcad worksheets, as Markdown

Markdown conversions of the PDF worksheets in this directory — the Mathcad
13.1 companion files to *High-Speed Digital Design: A Handbook of Black
Magic* (Howard Johnson & Martin Graham).

Math is rendered as infix expressions in code blocks, close enough to Python
to paste and adapt. Runnable Python versions are in
[`../pseudocode/`](../pseudocode).

## Transmission line geometries

| Document | Covers |
| --- | --- |
| [general.md](general.md) | Converting among Z0, delay, L and C |
| [round.md](round.md) | Round wire over a ground plane (wire-wrap) |
| [coax.md](coax.md) | Coaxial cable |
| [twist.md](twist.md) | Twisted pair |
| [mstrip.md](mstrip.md) | Microstrip |
| [sline2.md](sline2.md) | Stripline, centered and offset |

## Lumped elements and coupling

| Document | Covers |
| --- | --- |
| [capac.md](capac.md) | Parallel-plate capacitance; impedance to a rising edge |
| [circular.md](circular.md) | Inductance of a circular loop |
| [rectangl.md](rectangl.md) | Inductance of a rectangular loop |
| [mline.md](mline.md) | Mutual inductance of parallel lines |
| [mloop.md](mloop.md) | Mutual inductance of two loops |

## Resistance, constants and simulations

| Document | Covers |
| --- | --- |
| [constant.md](constant.md) | Physical constants in inch units |
| [resist.md](resist.md) | DC resistance of wires, traces and planes |
| [shortlin-v2001.md](shortlin-v2001.md) | Transmission line simulator |
| [shortlin-examples.md](shortlin-examples.md) | Slide deck of simulator results |
| [gndpins.md](gndpins.md) | Connector crosstalk vs. ground-pin pattern |
| [hsdd-greeting.md](hsdd-greeting.md) | Howard Johnson's cover letter |

## How these were made

The PDFs are Mathcad printouts, and `pdftotext` drops the radical signs and
superscripts from them — `Z0 := sqrt(lpi/cpi)` comes out as `Z0 := lpi/cpi`,
which is wrong in a way that is hard to spot. The formulas here were instead
read from the `.xmcd` sources next to each PDF, which are Mathcad XML and
hold the real expression trees. The PDF text was used for layout and prose.

`hsdd-greeting.md` and `shortlin-examples.md` have no `.xmcd` counterpart and
come from the PDF text directly.
