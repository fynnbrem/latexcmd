import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
# noinspection PyUnresolvedReferences
from typing import Union, Optional

from latexcmd.latex.errors import ErrorCodes


class LatexError(Exception):
    def __init__(self, text: str, code: "ErrorCodes"):
        self.text = text
        self.code = code


def formula_to_dvi(formula):
    content = rf"""\documentclass{{standalone}}\begin{{document}}${formula}$\end{{document}}"""
    with tempfile.TemporaryDirectory() as temp:
        temp_dir = Path(temp)
        file_name = "formula.tex"

        temp_file = temp_dir / file_name
        with open(temp_file, "w") as stream:
            stream.write(content)

        code = subprocess.run(
            [
                "latex",
                temp_file,
                f"-output-directory={temp_dir.absolute()}",
                "-interaction=nonstopmode",
                "-halt-on-error"
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if code.returncode != 0:
            log = temp_file.with_suffix(".log")
            analyze_tex_error(log)


def analyze_tex_error(log: Path):
    with log.open() as stream:
        error_text = None
        added_info = None
        for line in stream.readlines():
            if line.startswith("!"):
                error_text = line.removeprefix("! ")
            if line.startswith("l.") and error_text is not None:
                added_info = re.sub(r"^l.\d+ ", "", line)
                break
        raise_tex_error(error_text, added_info)


def raise_tex_error(error_text: Optional[str], added_info: Optional[str]):
    logging.error("LaTeX parsing encountered an error: \"%s\": \"%s\"", error_text.strip(), added_info.strip())
    code = ErrorCodes.unknown
    if error_text is not None:
        codes: set[ErrorCodes] = set(ErrorCodes)
        codes.remove(ErrorCodes.unknown)

        for local_code in codes:
            if local_code.value in error_text:
                code = local_code
                error_text, added_info = local_code.handler(error_text, added_info)
                break
    if code == ErrorCodes.unknown:
        if error_text is None:
            error_text = "Unknown Error."
        else:
            added_info = "\"" + error_text.strip() + "\""
            error_text = "Unexpected Error."

    if added_info is None:
        raise LatexError(error_text, code)
    else:
        error_text = re.sub(".\s*$", ": ", error_text) + added_info
        raise LatexError(error_text, code)


if __name__ == '__main__':
    try:
        formula_to_dvi(r"E = \frac{1}{2} mv^2")
    except LatexError as err:
        print("Text:")
        print(err.text)
        print(err.code)
