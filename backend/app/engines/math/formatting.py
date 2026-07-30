"""Number and equation formatting helpers.

Coefficient arrays are converted into both a plain-text equation
(``y = 0.1052 + 1.9820x - 0.0125x^2``) and a LaTeX rendering for KaTeX.
"""

from __future__ import annotations


def fmt(value: float, precision: int = 4) -> str:
    """Format a float with fixed precision, trimming nothing.

    Switches to scientific notation for extreme magnitudes so the string
    stays readable (e.g. 1.2345e+10 instead of 12345000000.0000).
    """
    if value != 0.0 and (abs(value) >= 1e7 or abs(value) < 1e-4):
        return f"{value:.{precision}e}"
    return f"{value:.{precision}f}"


def latex_number(value: float, precision: int = 4) -> str:
    """Format a float for LaTeX output (scientific notation uses \\times 10^{})."""
    if value != 0.0 and (abs(value) >= 1e7 or abs(value) < 1e-4):
        mantissa, exponent = f"{value:.{precision}e}".split("e")
        return f"{mantissa} \\times 10^{{{int(exponent)}}}"
    return f"{value:.{precision}f}"


def build_polynomial_equation(
    coefficients: list[float], precision: int = 4
) -> tuple[str, str]:
    """Build plain and LaTeX equations for y = a0 + a1·x + ... + am·x^m.

    Args:
        coefficients: [a0, a1, ..., am].
        precision: Decimal places for the formatted coefficients.

    Returns:
        (plain, latex) equation strings.
    """
    plain_terms: list[str] = [fmt(coefficients[0], precision)]
    latex_terms: list[str] = [latex_number(coefficients[0], precision)]
    plain_signs: list[str] = []
    latex_signs: list[str] = []

    for k in range(1, len(coefficients)):
        c = coefficients[k]
        sign = "+" if c >= 0 else "-"
        plain_signs.append(sign)
        latex_signs.append(sign)
        power = "" if k == 1 else f"^{k}"
        superscript = "" if k == 1 else "²³⁴⁵⁶"[k - 2]
        plain_terms.append(f"{fmt(abs(c), precision)}x{superscript}")
        latex_terms.append(f"{latex_number(abs(c), precision)}x{power}")

    plain = plain_terms[0] + "".join(
        f" {s} {t}" for s, t in zip(plain_signs, plain_terms[1:])
    )
    latex = latex_terms[0] + "".join(
        f" {s} {t}" for s, t in zip(latex_signs, latex_terms[1:])
    )
    return f"y = {plain}", f"y = {latex}"


def build_exponential_equation(
    a: float, b: float, precision: int = 4
) -> tuple[str, str]:
    """Build plain and LaTeX equations for y = a·e^(bx)."""
    plain = f"y = {fmt(a, precision)}·e^({fmt(b, precision)}x)"
    latex = f"y = {latex_number(a, precision)}\\,e^{{{latex_number(b, precision)}x}}"
    return plain, latex
