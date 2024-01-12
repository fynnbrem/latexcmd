import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
# noinspection PyUnresolvedReferences
from typing import Union, Optional

from latexcmd.latex.errors import ErrorCodes, LatexError


def formula_to_dvi(formula: str, new_file: Path) -> None:
    """

    :param formula: The formula to be rendered.
    :param new_file: The file which to save the DVI into.
    """
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
            return

        shutil.copy(temp_file.with_suffix(".dvi"), new_file)



def analyze_tex_error(log: Path):
    """Analyzes the first occurred error during parsing by examining the log.
    Will always raise a `LatexError`, even if no specific could be found.

    Accordingly, this function should only be used if the return code of the latex-parser suggests an issue.

    :raises LatexError:
    """
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
    """Based on the description and additional info provided by skimming the log of the latex parser, raises an error with an adequate description.
    See `ErrorCodes` for details on distinctions.
    If no specific error could be determined from the arguments, an "Unknown Error"-error will be raised.

    :raises LatexError:
    """
    logging.error("LaTeX parsing encountered an error: \"%s\": \"%s\"", error_text.strip(), added_info.strip())
    code = ErrorCodes.unknown
    if error_text is not None:
        codes: set[ErrorCodes] = set(ErrorCodes)
        codes.remove(ErrorCodes.unknown)

        for local_code in codes:
            if local_code.value in error_text:
                code = local_code
                error_text, added_info = local_code.refine_text(error_text, added_info)
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
    formula_to_dvi(r"E = \frac{1}{2} mv^2", Path("hey.dvi"))

