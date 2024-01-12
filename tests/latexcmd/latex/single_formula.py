from pathlib import Path
# noinspection PyUnresolvedReferences
from typing import Union, Optional

from latexcmd.latex.errors import ErrorCodes
from latexcmd.latex.single_formula import analyze_tex_error, LatexError


def test_analyze_tex_error():
    def run(log: Path, expected: ErrorCodes):
        try:
            analyze_tex_error(log)
        except LatexError as err:
            assert err.code == expected, f"Incorrect error code evaluated from {log.name}"
        else:
            raise AssertionError(f"No `LatexError` was raised for {log.name}")
    for code in ErrorCodes:
        file = Path(__file__).parent / "data" / (code.name + ".log")
        run(file, code)
