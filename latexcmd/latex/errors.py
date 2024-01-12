"""# Detection and handling of errors during LaTeX parsing"""
from enum import Enum
# noinspection PyUnresolvedReferences
from typing import Union, Optional, Callable


class ErrorCodes(Enum):
    """Errors that can occur when parsing a LaTeX formula.
    The value is a substring, which is used to identify the error type from the log.

    Use `~.refine_text` to format the error text and extra info to be more adequate to the error type."""
    unknown = ""
    """An unidentifiable error, either due to unknown or due to undetectable error text."""
    undefined_control_sequence = "Undefined control sequence"
    undefined_symbol = "Invalid UTF-8 byte sequence"
    extra_bracket = "Extra }, or forgotten $"
    missing_bracket = "Missing } inserted"

    @property
    def refine_text(self) -> "_REFINER_SIG":
        """Formats the error text and extra info to be more adequate to the error type.
        Look into the corresponding `refine`-implementation decorated by `refiner_func(<ErrorCode>)` for details."""
        return REFINER_FUNCS[self]


_REFINER_SIG = Callable[[str, Optional[str]], tuple[str, Optional[str]]]
REFINER_FUNCS: dict[ErrorCodes, _REFINER_SIG] = dict()


def refiner_func(*keys: ErrorCodes):
    """Save the function as refiner for all error codes specified in `keys`."""

    def inner(func):
        for key in keys:
            if key in REFINER_FUNCS:
                raise AssertionError(f"{key} already exists in handler functions.")
            REFINER_FUNCS[key] = func
        return func

    return inner


@refiner_func(ErrorCodes.undefined_control_sequence)
def refine(error_text: str, added_info: Optional[str]):
    """Keeps the `error_text` and reduces `added_info` so it just shows the relevant control sequence."""
    if added_info is not None:
        added_info = added_info.split("\\")
        if len(added_info) > 1:
            # When the found sequence has a backslash, reinsert it to the text as it was removed by `split()`.
            added_info = "\\" + added_info[-1]
        else:
            # When the found sequence for some reason does not have a leading backslash,
            # do not insert a replacement one.
            added_info = added_info[0]
        added_info = "\"" + added_info.strip() + "\""
    return error_text, added_info


@refiner_func(ErrorCodes.extra_bracket)
def refine(error_text: str, added_info: Optional[str]):
    """Shrinks the error text as to only include the bracket-info but not the dollar-sign-info.
    This is because errors with dollar signs are not
    actually created by the user but the preset the user-written formula gets wrapped into.

    The added info gets reduced to only show the formula part, not the surrounding document markers.
    """
    error_text = error_text.split(",")[0] + "."
    added_info = added_info.split("$")[-1]
    added_info = "\"" + added_info.strip() + "\""
    return error_text, added_info


# noinspection PyUnusedLocal
@refiner_func(ErrorCodes.missing_bracket)
def refine(error_text: str, added_info: Optional[str]):
    """Changes the error text to only state the missing of the bracket.
    By default, it also states that the parser inserted the supposedly missing bracket, which is not the case here.

    Any added info gets removed as the suggestion by the parser is always the last bracket.
    """
    error_text = error_text.split("}")[0] + "}."
    return error_text, None


# noinspection PyUnusedLocal
@refiner_func(ErrorCodes.undefined_symbol, ErrorCodes.unknown)
def refine(error_text: str, added_info: Optional[str]):
    """Keeps the error text and removes any added info."""
    return error_text, None


for code in ErrorCodes:
    assert code in REFINER_FUNCS, f"There is no handler function for {code}"


class LatexError(Exception):
    """An error caused by the LaTeX-parser.
    Comes with a descriptive `~.text` and an identifying `~.code`.
    """
    def __init__(self, text: str, code: "ErrorCodes"):
        self.text = text
        self.code = code
