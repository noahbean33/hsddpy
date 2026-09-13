"""Crosstalk in a high-speed connector, as a function of ground-pin pattern.

Transcribed from GNDPINS.mcd (an experimental worksheet; see gndpins.doc).

PSEUDOCODE. This is a simulation, not a closed-form sheet: it solves a
linear system for the ground-return currents and then sums the resulting
crosstalk. Written against numpy but not run.

The trick that makes the worksheet readable: positions in the 2-D connector
face are represented as COMPLEX numbers rather than 2-element vectors, so
the real part is horizontal and the imaginary part is vertical.

Two names are reused in the original with different meanings. They are
disambiguated here:
    Mathcad B(x, p)  -> field_B()        magnetic field intensity
    Mathcad B matrix -> B_flux           flux from signal currents
    Mathcad D        -> PITCH            pin spacing
    Mathcad D matrix -> D_gnd            flux from ground currents

Everything is in METERS in this worksheet, not inches.
"""

import numpy as np

MU0 = 4 * np.pi * 1e-7          # magnetic permeability of free space
R_WIRE = 0.01 * 0.0254          # wire radius (m)
L_PIN = 0.5 * 0.0254            # connector pin length (m)
PITCH = 0.05 * 0.0254           # standard pin spacing (m)


def field_B(x, p):
    """Magnetic field intensity at point x from 1 A flowing in a wire at p.

    Zero inside the wire itself.
    """
    r = np.abs(x - p)
    return np.where(r > R_WIRE, MU0 / (2 * np.pi * r), 0)


def dot(a, b):
    """Dot product of two positions held as complex numbers."""
    return np.real(a * np.conj(b))


def d_phi(v, x, y, p):
    """Elemental flux at point v on the integration path from x to y.

    Due to 1 A flowing at position p.
    """
    return field_B(v, p) * dot(y - x, p - v) / (np.abs(y - x) * np.abs(p - v))


def phi(x, y, p):
    """Flux threading the loop between wires at x and y, from 1 A at p.

    The direct form is the path integral of d_phi from x to y. The worksheet
    replaces it with a closed form by deforming the path: first circumscribe
    a circle of constant radius about the current source (the dot product is
    zero all along it, so it contributes nothing), then run radially out
    toward y (where the dot product is unity and the integrand goes as 1/r,
    which integrates to a log).
    """
    outer = np.where(np.abs(y - p) > R_WIRE, np.abs(y - p), R_WIRE)
    inner = np.where(np.abs(x - p) > R_WIRE, np.abs(x - p), R_WIRE)
    return MU0 / (2 * np.pi) * np.log(outer / inner) * L_PIN


# --- wire positions -------------------------------------------------------
# M and N need not be equal. Row number is the imaginary part.

N = 50                              # ground wires
n = np.arange(0, N)

g = n + 1j                          # ground wires, row 1
p1 = n + 2j                         # signal wires, row 2
p2 = n + 3j                         # row 3
p3 = n + 0j                         # row 0

M = N * 3                           # signal wires
m = np.arange(0, M)

p = np.concatenate([p1, p2, p3])


def fixpos(x):
    """Scale to real pin spacing and wrap rows modulo 4."""
    return PITCH * (np.real(x) + 1j * np.mod(np.imag(x), 4))


p = fixpos(p)
g = fixpos(g)

# As written, all the grounds sit on row 1. Change the assignments above to
# scatter the ground positions -- that is the whole point of the study.

# --- solve for ground-return currents -------------------------------------
# There are N ground currents but only N-1 ground loops, so the system needs
# one more constraint: all current going out must return along the grounds.

nLessOne = np.arange(0, N - 1)

# Flux induced in each ground loop by 1 A in each signal wire.
B_flux = np.zeros((N, M))
for i in nLessOne:
    B_flux[i, :] = phi(g[i], g[i + 1], p)

# Flux induced in each ground loop by 1 A in each ground wire.
A_mat = np.zeros((N, N))
for i in nLessOne:
    A_mat[i, :] = phi(g[i], g[i + 1], g)

# Last row: the sum of all ground currents equals the signal current.
A_mat[N - 1, :] = 1
B_flux[N - 1, :] = 1

# Column m of B is how signal m disturbs each ground loop; A is how ground
# currents disturb them. For each signal, the ground currents must cancel
# the flux in every ground loop:  A*G + B = 0.
G = -np.linalg.solve(A_mat, B_flux)

# --- crosstalk voltages ---------------------------------------------------

dIdt = np.full(M, 4 / 50 * 1 / 1e-9)
"""Aggressor dI/dt on each signal wire. Could differ per net class."""


def voltage(x, y, mi):
    """Crosstalk voltage between points x and y from current on wire mi.

    Accounts for the currents induced on all ground wires.
    """
    direct = phi(x, y, p[mi])
    via_grounds = sum(phi(x, y, g[ni]) * G[ni, mi] for ni in range(N))
    return (direct + via_grounds) * dIdt[mi]


# The same thing, vectorized: C is how signal currents reach the victim,
# D_gnd is how ground currents reach it.
C = np.zeros((M, M))
D_gnd = np.zeros((M, N))
for kk in range(M):
    C[kk, :] = phi(p[kk], g[0], p)
    D_gnd[kk, :] = phi(p[kk], g[0], g)

V = C + D_gnd @ G
V = V * dIdt[np.newaxis, :]     # scale by dI/dt on each aggressor
np.fill_diagonal(V, 0)          # zero out self-crosstalk
V = np.abs(V)
V = V.T

XTLK = V.sum(axis=0)
"""Worst-case crosstalk on each line, summed over all aggressors."""


if __name__ == '__main__':
    # Sanity check: row N-1 of A*G = -B forces every column of G to sum to
    # exactly -1 (all current leaving on a signal wire must return along the
    # grounds). This is a hard constraint of the solve, independent of wire
    # geometry, so it is a good check that the linear system was assembled
    # correctly.
    col_sums = G.sum(axis=0)
    assert np.allclose(col_sums, -1.0), "ground currents do not balance the signal current"
    print("ground-current balance OK: every column of G sums to -1")
    print("XTLK range: %.4g to %.4g" % (XTLK.min(), XTLK.max()))

    # The worksheet pre-computed and stored two configurations, documented
    # in gndpins.doc, and plots them against each other:
    #   straight.prn  all grounds on one row (the layout wired up above)
    #   scatter.prn   ground positions scattered through the field -- left
    #                 as an exercise in the original ("change the equations
    #                 to scatter the ground positions"); no scattered layout
    #                 is transcribed here, so only the straight case is
    #                 written out.
    np.savetxt('straight.prn', XTLK)
    XSTRAIGHT = np.loadtxt('straight.prn')
