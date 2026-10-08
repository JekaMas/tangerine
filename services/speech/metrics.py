"""Exact registry arithmetic, not claim interpretation or a complete scorer.

Only already validated counters may be supplied by a future domain owner. Missing
taxonomy, claim/mapping schemas and counting decisions cannot be invented here.
"""
import ast
from fractions import Fraction
from pathlib import Path
import re


def load_core_registry(path: Path) -> dict[str, str]:
    """Read the retained simple ID/formula fields, not arbitrary YAML syntax."""
    source = path.read_text(encoding="utf-8")
    block = source.split("metrics:\n", 1)[1].split("auxiliary_metrics:\n", 1)[0]
    result = {}
    for match in re.finditer(r"^- id: (\S+)\n(.*?)(?=^- id: |\Z)", block, re.M | re.S):
        formula = re.search(r"^  formula: (.+)$", match.group(2), re.M)
        if formula is None or match.group(1) in result:
            raise ValueError("invalid core metric registry")
        result[match.group(1)] = formula.group(1)
    if len(result) != 27:
        raise ValueError("the retained registry must contain 27 core metrics")
    return result


def _arithmetic(node, counters):
    if isinstance(node, ast.Name):
        value = counters[node.id]
        if isinstance(value, bool) or not isinstance(value, (int, Fraction)) or value < 0:
            raise ValueError("counters must be nonnegative exact numbers")
        return Fraction(value)
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return Fraction(node.value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        left, right = _arithmetic(node.left, counters), _arithmetic(node.right, counters)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        return left * right
    raise ValueError("unsupported registry arithmetic")


def ratio(numerator, denominator, zero_reason):
    if any(isinstance(value, bool) or not isinstance(value, (int, Fraction))
           for value in (numerator, denominator)):
        raise ValueError("ratio counters must be exact numbers")
    if zero_reason not in {"no_opportunities", "no_assertions"}:
        raise ValueError("explicit zero-denominator reason required")
    if numerator < 0 or denominator < 0 or numerator > denominator:
        raise ValueError("ratio counters are inconsistent")
    result = {"numerator": str(numerator), "denominator": str(denominator)}
    if denominator == 0:
        return {**result, "value": None, "status": "not_applicable", "reason": zero_reason, "percent": None}
    value = Fraction(numerator) / denominator
    scaled = value * 1000
    tenths = (2 * scaled.numerator + scaled.denominator) // (2 * scaled.denominator)
    return {**result, "value": str(value), "status": "available", "reason": None, "percent": f"{tenths // 10}.{tenths % 10}"}


def evaluate(formula, counters, *, zero_reason):
    node = ast.parse(formula, mode="eval").body
    if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
        raise ValueError("metric must be a ratio")
    numerator = _arithmetic(node.left, counters)
    denominator = _arithmetic(node.right, counters)
    return ratio(numerator, denominator, zero_reason)


def evaluate_all(registry, counters, *, zero_reasons, unresolved=False):
    if unresolved:
        return {"status": "needs_review", "metrics": None}
    return {"status": "arithmetic_only", "metrics": {
        metric: evaluate(formula, counters, zero_reason=zero_reasons[metric])
        for metric, formula in registry.items()
    }}
