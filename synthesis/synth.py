"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

Fill in this file to complete the synthesis portion
of the assignment.
"""

from types import CodeType
from typing import Mapping, List, Union, Set
from z3 import *
from lang.ast import *
import itertools

class HoleData:
    """
    Processes data of HoleDeclaration instance to make it easier for the synthesizer to parse
    """

    def __init__(self, hole: HoleDeclaration) -> None:
        self.hole: HoleDeclaration = hole

        self.var_counter: int = 0
        self.const_counter: int = 0
        # number of steps the method was called before reaching step 4 (method 2 use only)
        self.pre_step_4_steps: int = 0

        self.vars: List[VarExpr] = list()
        self.consts: List[Union[int, bool]] = list()
        self.binary_exprs: List[BinaryExpr] = list()
        self.unary_exprs: List[UnaryExpr] = list()
        self.ite_exprs: List[Ite] = list()
        self.rules: Mapping[str, ProductionRule] = list()
        self.grammar_int: bool = False
        self.grammar_var: bool = False
        self.sub_hole_data: Mapping[str, HoleData]

        for rule in hole.grammar.rules:
            self.rules[rule.symbol.name] = (rule)
            for expr in rule.productions:
                self.add_expression(expr)

    def add_expression(self, expr: Expression) -> bool:
        if isinstance(expr, BinaryExpr):
            self.binary_exprs.append(expr)
        elif isinstance(expr, UnaryExpr):
            self.unary_exprs.append(expr)
        elif isinstance(expr, Ite):
            self.ite_exprs.append(expr)
        elif isinstance(expr, VarExpr):
            if expr not in self.vars:
                self.vars.append(expr)
                return True
        elif isinstance(expr, (BoolConst, IntConst)) and expr.value not in self.consts:
            self.consts.append(expr.value)
        elif isinstance(expr, GrammarInteger):
            self.grammar_int = True
        elif isinstance(expr, GrammarVar):
            self.grammar_var = True
        else:
            return False
        
        return True


class Method2Helper:
    def __init__(self):
        self.history: List[Mapping[str, Expression]] = list() # List of dictionaries, containing the returned mappings in chronological order
        self.num_calls: int = 0 # The number of calls to the method
        self.hole_data: Mapping[str, HoleData] = dict() # Mapping from hole to HoleData

    def hole_to_expression(self, hole: HoleDeclaration, vars_to_use: List[Variable]) -> Expression:
        try:
            data = self.hole_data[hole.var.name]
        except KeyError as e:
            print(f"ERROR: Method2Helper.hole_data does not contain data for hole: {hole.var.name}")
            print(repr(e))
            return None

        # Step 1) Integers
        if data.grammar_int:
            return IntConst(self.num_calls)

        # Step 2) Variables
        if data.grammar_var and data.var_counter < len(vars_to_use):
            data.var_counter += 1
            return vars_to_use[data.var_counter - 1]
        
        # Step 3) Constants
        if data.const_counter < len(data.consts):
            data.const_counter += 1
            if type(data.consts[data.const_counter - 1]) is bool:
                return BoolConst(data.consts[data.const_counter - 1])
            else: # is int
                return IntConst(data.consts[data.const_counter - 1])

        # Step 4) Expressions
        # We want to avoid unary expressions if possible, since uniary operators are their own inverse
        if len(data.binary_exprs) > 0:
            # return BinaryExpr()

        # TODO: add in logic for Unary Expression, Binary Expression, ITE expression
        
        return None

class Synthesizer():
    """
    This class is has three methods `synth_method_1`, `synth_method_2` or
    `synth_method_3` for generating expression for a program's holes.

    You may also choose to add data attributes and methods to this class
    to enable instances of `Synthesizer` to remember information about
    previous runs.

    Calling `synth_method_1`, `synth_method_2` or `synth_method_3` should
    produce a new set of hole completions at each call for a given
    `Synthesizer` instance.
    For example, suppose the program p contains one hole `h1` with the
    grammar `[ G : int -> G + G | 0 | 1 ]`. Then, the following sequence
    is a possible execution:
    ```
    > s = Synthesizer(p)
    > s.synth_method_1()
    { "h1" : 0 }
    > s.synth_method_1()
    { "h1" : 1 }
    > s.synth_method_1()
    { "h1" : 0 + 1 }
    ...
    ```
    Each call produces a hole completion. The returned object should
    be a mapping from the hole id (its name) to the expression of the
    hole.
    Each `synth_method_..` should implement a different enumeration
    strategy (e.g. depth first, breadth first, constants-first,
    variables-first...).

    **Don't forget that we expect your third method to be the best on
    average!**

    *Hint*: the method `hole_can_use` in the `Program` class returns the
    set of variables that a given hole can use in its completions.
    e.g. `prog.hole_can_use("h1")` returns the variables that "h1" can use.
    """

    def __init__(self, ast: Program):
        """
        Initialize the Synthesizer.
        The Synthesizer can have a state or other data attributes and
        methods to remember which programs have been synthesized before.
        """
        self.method1_state = None
        self.m2_helper = Method2Helper()
        self.method3_state = None
        # The synthesizer is initialized with the program ast it needs
        # to synthesize hole completions for.
        self.ast = ast

    # TODO: implement something that allows you to remember which
    # programs have already been generated.

    def synth_method_1(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 1).

        **TODO: write a description of your approach in this method.**
        """
        # TODO : complete this method
        raise Exception("Synth.Synthesizer.synth_method_1 is not implemented.")

    def synth_method_2(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 2).

        This is an Raw-Value Priority enumeration method.
        The goal is to try to fill the hole with computationally easy fillings first,
        and only fill it with complex expressions as a last resort.
        
        For each hole, go thru each of the following steps. 
        At each step, we check if any rule in the hole satisfies the current step.
        If so, return that as the assignment.
        Otherwise, go to the next step
        STEP 1) Integers
            |-> If a hole contains "Integer", simply return a integer. Otherwise, go to Step 2
            |-> Increment this integer after every call, producing *infinite* hole fillings.
        STEP 2) Variables
            |-> If a hole contains "Variable", return the input variables in order.
            |-> Once all variables are exhausted, go to Step 3
        STEP 3) Constants
            |-> If a hole contains any constant values (0, 1, etc.), return these constants in order.
            |-> Once all constants are exhausted, go to Step 4
        Step 4) Expressions
            |-> As a last resort, the hole will have to return an expression.
            |-> To do this, recursively use synth_method_2 to fill each hole in the expression grammar, 
            |   then return the final grammar.
            |-> Use the following steps to fill in the hole:
            |   |-> Step 4.a) Add  
        Step 5) None
            |-> If there are no more unique possibilities, then return None
        ===== EXAMPLE =====
        hole h : int [G : int -> Integer];
        >> 0
        >> 1
        >> 2
        >> 3
        . . .
        ==================================
        input x : int;
        hole h : int [ G : int -> G + G | Var | 0 | 1 ];
        >> 0
        >> 1
        >> x
        >> 0 + 0
        >> 0 + 1
        >> 0 + x
        >> 0 + (0 + 0)
        >> 0 + (0 + 1)
        . . .

        hole h : int [
            G : int -> G + G | G % H | H * G | H | Var;
            H : int -> Integer
        ];
        >> 0
        >> 1
        >> 2
        >> 3
        . . .
        """
        if self.m2_helper.num_calls == 0:
            # Initial setup
            for hole in self.ast.holes:
                self.m2_helper.hole_data[hole.var.name] = HoleData(hole)

        hole_mappings = dict()
        for hole in self.ast.holes:
            hole_mappings[hole.var.name] = self.m2_helper.hole_to_expression(hole, self.ast.hole_can_use(hole.var.name))


        self.m2_helper.history.append(hole_mappings)
        self.m2_helper.num_calls += 1
        return hole_mappings
    
    def synth_method_3(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 3).

        **TODO: write a description of your approach in this method.**
        """
        # TODO : complete this method
        raise Exception("Synth.synth_method_3 is not implemented.")
