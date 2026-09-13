"""Run the examples embedded in the docstrings.

Every worked example in the documentation is executable, so the docs cannot
drift away from the code without the suite noticing.
"""

import doctest
import importlib

import pytest

MODULES = [
    "hsdd.connector",
    "hsdd.general",
    "hsdd.line",
    "hsdd.lumped",
    "hsdd.mathcad",
    "hsdd.microstrip",
    "hsdd.mutual",
    "hsdd.resistance",
    "hsdd.signal",
    "hsdd.sim",
    "hsdd.solve",
    "hsdd.stripline",
    "hsdd.units",
    "hsdd.wires",
]

NEEDS_NUMPY = {"hsdd.connector", "hsdd.sim"}


@pytest.mark.parametrize("name", MODULES)
def test_docstring_examples(name):
    if name in NEEDS_NUMPY:
        pytest.importorskip("numpy")
    module = importlib.import_module(name)
    results = doctest.testmod(module, verbose=False)
    assert results.failed == 0, "%d doctest failures in %s" % (results.failed, name)
