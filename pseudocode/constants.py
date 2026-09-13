"""Physical constants used in transmission line work.

Transcribed from CONSTANT.mcd.

Everything in these worksheets is in ENGLISH units: inches, seconds, ohms,
henries, farads. The metric constants are kept only to show where the
inch-based ones come from.
"""

from math import pi

# --- free space, metric ---------------------------------------------------

E0_METERS = 8.854e-12          # electric permittivity of free space, F/m
U0_METERS = 4 * pi * 1e-7      # magnetic permeability of free space, H/m
C_METERS = 2.998e8             # speed of light, m/s

# --- the same constants, per inch ----------------------------------------

INCH = 0.0254                  # meters per inch

E0_INCHES = E0_METERS * INCH   # 2.249e-13 F/in.
U0_INCHES = U0_METERS * INCH   # 3.192e-8  H/in.
C_INCHES = C_METERS / INCH     # 1.180e10  in./s

# U0_INCHES / (2*pi) = 5.08e-9 turns up in every inductance formula in the
# book, which is why 5.08 and its multiples (10.16 = 2 x 5.08) appear as
# bare literals throughout these worksheets.
L_COEFF = U0_INCHES / (2 * pi)          # 5.08e-9 H/in.

# Propagation delay at the speed of light, in ps/in. Every propagation-delay
# formula in the book is this number times sqrt(er).
PDLY_LIGHT_PS_PER_IN = 1e12 / C_INCHES  # 84.72 ps/in.
PDLY_LIGHT = 84.72e-12                  # s/in., as written in the worksheets


if __name__ == "__main__":
    print("E0_INCHES            = %.4g F/in."  % E0_INCHES)
    print("U0_INCHES            = %.4g H/in."  % U0_INCHES)
    print("U0_INCHES/(2*pi)     = %.4g H/in."  % L_COEFF)
    print("C_INCHES             = %.4g in./s"  % C_INCHES)
    print("PDLY at light speed  = %.5g ps/in." % PDLY_LIGHT_PS_PER_IN)
