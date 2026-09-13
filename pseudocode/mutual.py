"""Mutual inductance: parallel transmission lines, and two separated loops.

Transcribed from MLINE.mcd and MLOOP.mcd.
"""


def MLINE(L, s, h):
    """Mutual inductance of two parallel lines above a ground plane.

    L   inductance (H) of the first line over its parallel run of length x
        (compute it with the round-wire, microstrip or stripline formula,
        whichever matches the geometry)
    s   separation between wire centers (in.)
    h   height of the wires above ground (in.)

    Two identical lines are assumed to share a parallel run of length x with
    horizontal separation s. Note the shape: coupling falls off with (s/h)^2,
    so halving the height above ground quarters the crosstalk.
    """
    return L * (1 / (1 + (s / h) ** 2))


def MLOOP(r, A1, A2):
    """Mutual inductance (nH) of two well-separated flat loops.

    r    separation between loop centers (in.)
    A1   surface area of loop 1 (in.^2)
    A2   surface area of loop 2 (in.^2)

    The loops are assumed flat, with faces parallel to each other for
    maximum coupling. Note this returns nH, not H -- it is the one formula
    in the set that does not return base units.

    Valid only when the loops are well separated:
        r > sqrt(A1)  and  r > sqrt(A2)
    Use mloop_is_valid() to check before trusting the answer.
    """
    return 5.08 * (A1 * A2) / r ** 3


def mloop_is_valid(r, A1, A2):
    """True when r is large enough for the MLOOP() approximation to hold."""
    return r > A1 ** 0.5 and r > A2 ** 0.5
