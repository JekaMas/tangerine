"""Parse restricted metric arithmetic. Do not evaluate untrusted source code."""
import ast
from fractions import Fraction

def from_stat(v):
    return Fraction(v['numerator'],v['denominator']) if isinstance(v,dict) else Fraction(v)

def evaluate(expression: str, stats: dict):
    def visit(node):
        if isinstance(node,ast.Expression):return visit(node.body)
        if isinstance(node,ast.Name):return from_stat(stats[node.id])
        if isinstance(node,ast.Constant) and type(node.value) is int:return Fraction(node.value)
        if isinstance(node,ast.BinOp):
            left,right=visit(node.left),visit(node.right)
            if isinstance(node.op,ast.Add):return left+right
            if isinstance(node.op,ast.Sub):return left-right
            if isinstance(node.op,ast.Mult):return left*right
            if isinstance(node.op,ast.Div):return left/right
        raise ValueError('unsupported formula operation')
    try:return visit(ast.parse(expression,mode='eval'))
    except ZeroDivisionError:return None

def percent(numerator: int, denominator: int) -> str:
    if type(numerator) is not int or type(denominator) is not int or not 0<=numerator<=denominator or denominator<=0:
        raise ValueError('expected nonnegative ratio')
    tenths=(2000*numerator+denominator)//(2*denominator)
    return f'{tenths//10}.{tenths%10}%'
