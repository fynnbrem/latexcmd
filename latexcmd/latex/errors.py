from enum import Enum
# noinspection PyUnresolvedReferences
from typing import Union, Optional


class ErrorCodes(Enum):
    """Errors that can occur when parsing a LaTeX formula.
    The value is a substring, which is used to identify the error type from the log.

    Use `~.handler` to handle the error text and added info extracted from the log.
    """
    unknown = ""
    undefined_control_sequence = "Undefined control sequence"
    undefined_symbol = "Invalid UTF-8 byte sequence"
    extra_bracket = "Extra }, or forgotten $"
    missing_bracket = "Missing } inserted"
    @property
    def handler(self):
        return HANDLER_FUNCS[self]

HANDLER_FUNCS = dict()


def handler_func(*keys: ErrorCodes):
    def inner(func):
        for key in keys:
            if key in HANDLER_FUNCS:
                raise AssertionError(f"{key} already exists in handler functions.")
            HANDLER_FUNCS[key] = func
        return func

    return inner


@handler_func(ErrorCodes.undefined_control_sequence)
def handle(error_text: str, added_info: Optional[str]):
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


@handler_func(ErrorCodes.extra_bracket)
def handle(error_text: str, added_info: Optional[str]):
    error_text = error_text.split(",")[0] + "."
    added_info = added_info.split("$")[-1]
    added_info = "\"" + added_info.strip() + "\""
    return error_text, added_info


@handler_func(ErrorCodes.missing_bracket)
def handle(error_text: str, added_info: Optional[str]):
    error_text = error_text.split("}")[0] + "}."
    return error_text, None


@handler_func(ErrorCodes.undefined_symbol, ErrorCodes.unknown)
def handle(error_text: str, added_info: Optional[str]):
    return error_text, None


for code in ErrorCodes:
    assert code in HANDLER_FUNCS, f"There is no handler function for {code}"
