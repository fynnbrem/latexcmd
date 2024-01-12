import subprocess
# noinspection PyUnresolvedReferences
from typing import Union, Optional


def is_installed(cmd: str) -> bool:
    """Check if the `command` is installed."""
    try:
        subprocess.run([cmd, "--version"], stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        return False
    else:
        return True


def is_latex_installed() -> bool:
    """Check if LaTeX is installed for command line usage."""
    return is_installed("latex")


def is_dvisvgm_installed():
    """Check if dvisvgm is installed for command line usage."""
    return is_installed("dvisvgm")

def enquote(text: str, /):
    return f"\"{text}\""


if __name__ == '__main__':
    print(f"LaTeX is installed: {is_latex_installed()}")
    print(f"dvisvgm is installed: {is_dvisvgm_installed()}")
