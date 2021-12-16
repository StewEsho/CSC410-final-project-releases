"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

Fill in this file to complete the verification portion
of the assignment.
"""

from z3 import *
from lang.ast import *
from typing import Union


class AstToZ3:
    def __init__(self) -> None:
        self.pythonize_map = {
            '=': '==',
            '&&': 'and',
            '||': 'or',
            '!': 'not'
        }

    def pythonize(self, operator: str) -> str:
        """
        Convert some operators into python syntax
        """
        if operator in self.pythonize_map:
            return self.pythonize_map[operator]
        return operator

    def convert(self, formula: Expression) -> Union[ExprRef, bool, int]:
        """
        Converts the format of an AST expression
        from lang.ast.Expression
        to z3.ExprRef.

        This allows z3 to attempt to solve the expression,
        and thus verify the expression.
        """
        result = None

        # Case 1 : formula is a binary expression
        if isinstance(formula, BinaryExpr):
            operator = self.pythonize(str(formula.operator))
            lhs = self.convert(formula.left_operand)
            rhs = self.convert(formula.right_operand)
            op_to_func = {
                "and": And,
                "or": Or
            }

            if operator in op_to_func:
                result = op_to_func[operator](lhs, rhs)
            else:
                result = eval(f"lhs {operator} rhs")

        # Case 2 : formula is a unary expression.
        elif isinstance(formula, UnaryExpr):
            operand = self.convert(formula.operand)

            if formula.operator == UnaryOperator.NOT:
                result = Not(operand)
            elif formula.operator == UnaryOperator.ABS:
                result = If(operand < 0, -operand, operand)
            elif formula.operator == UnaryOperator.NEG:
                result = -operand
            else:
                result = None

        # Case 3 : formula is a if-then-else expression (a ternary expression).
        elif isinstance(formula, Ite):
            cond = self.convert(formula.cond)
            true_branch = self.convert(formula.true_br)
            false_branch = self.convert(formula.false_br)

            result = If(cond, true_branch, false_branch)

        # Case 4: formula is a variable
        elif isinstance(formula, VarExpr):
            if formula.var.type == PaddleType.INT:
                result = Int(formula.var.name)
            elif formula.var.type == PaddleType.BOOL:
                result = Bool(formula.var.name)
            else:
                None

        # Case 5 : formula is a constant
        elif isinstance(formula, (BoolConst, IntConst)):
            result = formula.value

        # Case 6 : formula is GrammarInteger or GramamrVar: this should
        # never happen during evaluation!
        elif isinstance(formula, (GrammarInteger, GrammarVar)):
            raise TypeError(
                "GrammarInteger and GrammarVar should not appear in\
                    expressions that are evaluated.")

        # Case 7 should never be reached.
        elif isinstance(formula, Expression):
            raise TypeError(
                "Argument is an Expression of unknown type!\n\
                    Maybe you forgot to implement a case in \
                        verifier.expression_to_z3")

        return result


def is_valid(formula: Expression) -> bool:
    """
    Returns true if the formula is valid.
    """
    z3_converter = AstToZ3()
    z3_formula = z3_converter.convert(formula)
    s = Solver()
    # To solve for validity instead of satisfiability,
    # we negate the formula and check if its unsatisfiable
    s.add(Not(z3_formula))
    return s.check() == unsat
