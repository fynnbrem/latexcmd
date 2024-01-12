from dataclasses import dataclass, field
# noinspection PyUnresolvedReferences
from typing import Union, Optional, Any

from latexcmd.latex.errors import ErrorCodes
from latexcmd.utils import enquote


@dataclass(kw_only=True)
class Fixture():
    i: Any
    """The input."""
    e: Any
    """The expected output."""
    c: Optional[str] = field(default=None)
    """Comment."""


def test_undefined_control_sequence():
    error_text = ""
    added_info_fixtures = [
        Fixture(i=r"...lass{standalone}\begin{document}$E = \frac", e=enquote(r"\frac")),
        Fixture(i=r"\frac", e=enquote(r"\frac"), c="No leading symbols."),
        Fixture(i="frac", e=enquote("frac"), c="No backslash.")
    ]

    handler = ErrorCodes.undefined_control_sequence.refine_text

    def run(fix: Fixture):
        _, added_info = handler(error_text, fix.i)
        assert added_info == fix.e

    for fixture in added_info_fixtures:
        run(fixture)

