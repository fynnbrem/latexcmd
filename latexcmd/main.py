# noinspection PyUnresolvedReferences
from typing import Union, Optional
import subprocess

def create_latex_file(formula, filename="formula.tex"):
    content = rf"""\documentclass{{standalone}}\begin{{document}}${formula}$\end{{document}}"""
    with open(filename, "w") as file:
        file.write(content)


def compile_latex_to_dvi(latex_file):
    """Errors to handle:
    - Undefined Control Sequence
    - Unknown character (e.g. "ä")
    - Mismatched arguments
    - Missing }
    - Extra }
    """
    code = subprocess.run(["latex", latex_file, "-interaction=nonstopmode", "-halt-on-error"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("#" * 60)
    print(code.returncode)
    print("#" * 60)


def convert_dvi_to_svg(dvi_file, svg_file="output.svg"):
    code = subprocess.run(["dvisvgm", dvi_file, "-n", "-e", "-o", svg_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(code.returncode)

formula = r"\frac{E}{Y} = mc^{3^{2^\frac{2}{1}}}"  # Replace this with your LaTeX formula
latex_file = "formula.tex"
dvi_file = latex_file.replace(".tex", ".dvi")
svg_file = "formula.svg"

create_latex_file(formula, latex_file)
compile_latex_to_dvi(latex_file)
convert_dvi_to_svg(dvi_file, svg_file)

