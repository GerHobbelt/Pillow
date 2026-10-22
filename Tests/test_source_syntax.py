# Every PIL module must compile on the running interpreter. Run on Python 2.7,
# this catches Python 3-only syntax (f-strings, keyword-only arguments, ...)
# in a module that no other test imports.

import io
import os

import pytest

import PIL

PIL_DIR = os.path.dirname(PIL.__file__)
MODULES = sorted(f for f in os.listdir(PIL_DIR) if f.endswith(".py"))


@pytest.mark.parametrize("module", MODULES)
def test_module_compiles(module):
    path = os.path.join(PIL_DIR, module)
    with io.open(path, "rb") as fp:
        source = fp.read()
    compile(source, path, "exec")
