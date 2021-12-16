"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

Fill in this file to complete the synthesis portion
of the assignment.
"""

from os import name
from typing import Mapping, List, Union, Set
from z3 import *
from lang.ast import *
import itertools


class ProductionRuleData:
    """
    Stores data of a ProductionRule in format that is easier for synthesizer to parse
    """
    def __init__(self, production_rule: ProductionRule) -> None:
        """
        Initializes new ProductionRuleData based on data from a given ProductionRule instance
        """
        # Redundant reference to the original ProductionRule, just in case its needed in future refactoring
        self.rule = production_rule
        # Identifer for the production rule
        self.symbol = production_rule.symbol
        # Contains grammar expression "Integer"
        self.grammar_int: bool = False
        # Contains grammar expression "Variable"
        self.grammar_var: bool = False
        # List of all VarExpr expressions
        self.vars: List[VarExpr] = list()
        # List of all constant expressions (IntConst or BoolConst)
        self.consts: List[Union[IntConst, BoolConst]] = list()
        # List of all BinaryExpression expressions
        self.binary_exprs: List[BinaryExpr] = list()
        # List of all UnaryExpresion expressions
        self.unary_exprs: List[UnaryExpr] = list()
        # List of all ITE expressions
        self.ite_exprs: List[Ite] = list()
        # History of past fillings for this hole.
        self.history: List[Expression] = list()

        for expr in production_rule.productions:
            self.add_expression(expr)
    
    def add_expression(self, expr: Expression) -> bool:
        """
        Analyze what type of Expression expr is, and add it to the class' correct collection.
        Return True if expression was successfully added to a collection, otherwise return False
        """
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
        elif isinstance(expr, (BoolConst, IntConst)):
            self.consts.append(expr.value)
        elif isinstance(expr, GrammarInteger):
            self.grammar_int = True
        elif isinstance(expr, GrammarVar):
            self.grammar_var = True
        else:
            return False
        
        return True


class HoleData:
    """
    Processes data of HoleDeclaration instance to make it easier for the synthesizer to parse
    """
    def __init__(self, hole: HoleDeclaration) -> None:
        """
        Initializes new HoleData based on data from a given HoleDeclaration instance
        """
        # Redundant reference to the hole itself
        self.hole: HoleDeclaration = hole
        # Mapping from each production rule's name, to a relevant instance of ProductionRuleData
        self.rules: Mapping[str, ProductionRuleData] = list()
        # The top-level rule. Hole fillings must match THIS rule
        self.top_level_rule: ProductionRuleData = None
        # Counter to track # of variables used so far for the top-level rule
        self.var_counter = 0
        # Counter to track # of constants used so far for the top-level rule
        self.const_counter

        for i, rule in enumerate(hole.grammar.rules):
            prod_data = ProductionRuleData(rule)
            self.rules[rule.symbol.name] = prod_data
            if i == 0:        
                self.top_level_rule = prod_data   


class Method1Helper:
    """
    Collection of methods and properties to help store state for synth_method_1
    """
    def __init__(self):
        self.hole_data: Mapping[str, HoleData] = dict()  # Mapping from hole to HoleData

    def hole_to_expression(self, hole: HoleDeclaration, vars_to_use: List[Variable], data: HoleData = None) -> Expression:

        # Initialize the return value
        return_expression: Expression = None

        # Fill in for empty hole data => not a recursive call
        if data is None:
            data = self.hole_data[hole.var.name]

        # Start with binary expressions and end with Integers
        if len(data.top_level_rule.binary_exprs) > 0:
            bin_expr = data.top_level_rule.binary_exprs[0]
            operator = bin_expr.operator
        
        # Return the expression to be put into hole_mappings[hole.var.name]
        return return_expression


class Method2Helper:
    """
    Collection of methods and properties to help store state for synth_method_2
    """
    def __init__(self):
        # List of dictionaries, containing the returned mappings in chronological order
        self.history: List[Mapping[str, Expression]] = list()
        # The number of calls to the method
        self.num_calls: int = 0
        # Mapping from hole to HoleData
        self.hole_data: Mapping[str, HoleData] = dict()

    def get_fixed_simple_expression_from_hole_data(self, hole_data: HoleData, vars_to_use: List[Variable]) -> Expression:
        """
        Return a simple expression from given HoleData instance.
        This method is *deterministic*, so calling it twice on the same data will return the same result.
        A simple expression is one of VarExpr, IntConst, or BoolConst 
        """
        if hole_data.top_level_rule.grammar_var and len(vars_to_use) > 0:
            return VarExpr(
                vars_to_use[hole_data.var_counter - 1], 
                vars_to_use[hole_data.var_counter - 1].name
            )
        elif len(hole_data.top_level_rule.consts) > 0:
            return hole_data.top_level_rule.consts[0]
        return None

    def hole_to_expression(self, hole: HoleDeclaration, vars_to_use: List[Variable], data: HoleData = None) -> Expression:
        try:
            if data is None:
                data = self.hole_data[hole.var.name]
        except KeyError as e:
            print(f"ERROR: Method2Helper.hole_data does not contain data for hole: {hole.var.name}")
            print(repr(e))
            return None

        return_expression: Expression = None
        # Step 1) Integers
        if data.top_level_rule.grammar_int:
            return_expression = IntConst(self.num_calls)

        # Step 2) Variables
        elif data.top_level_rule.grammar_var and data.var_counter < len(vars_to_use):
            return_expression = VarExpr(vars_to_use[data.var_counter], vars_to_use[data.var_counter].name)
            data.var_counter += 1
        
        # Step 3) Constants
        elif data.const_counter < len(data.top_level_rule.consts):
            return_expression = data.top_level_rule.consts[data.const_counter]
            data.const_counter += 1

        # Step 4) Expressions
        # We want to avoid unary expressions if possible, since uniary operators are their own inverse
        #   meaning if we recursively nest unary expressions, we end up with 
        #   symbolically unique but semantically identical expressions
        elif len(data.top_level_rule.binary_exprs) > 0:
            bin_expr = data.top_level_rule.binary_exprs[0]
            operator = bin_expr.operator

            if isinstance(bin_expr.left_operand, VarExpr):
                lhs_hole_data = self.hole_data[bin_expr.left_operand.var.name]
                # attempt to fix the LHS to a simple value
                lhs = self.get_fixed_simple_expression_from_hole_data(lhs_hole_data)

            # # fix the LHS to a simple value
            # if isinstance(bin_expr.left_operand, VarExpr):
            #     lhs_hole_data = self.hole_data[bin_expr.left_operand.var.name]
            #     lhs = self.get_fixed_simple_expression_from_hole_data(lhs_hole_data)
            # else:
            #     lhs = bin_expr.left_operand

            # # Recursively go thru the right hand side's history
            # if isinstance(bin_expr.right_operand, VarExpr):
            #     pass
            # else:
            #     rhs 
            
            return_expression = BinaryExpr(operator, lhs, rhs)

        data.top_level_rule.history.append(return_expression)
        return return_expression


class Method3Helper:
    """
    Collection of methods and properties to help store state for synth_method_3
    """
    def __init__(self) -> None:
        # Stores queued expressions for each hole.
        # Data is stored as a mapping from hole name to a dict
        # the dict then maps each production rule in the grammar to a list, which acts as that rule's queue
        self.queues: Mapping[str, Mapping[str, List[Expression]]] = dict()
        # Tracks number of times synth_method_3 has been called
        self.num_calls: int = 0
        # Stores HoleData for each hole
        self.hole_data: Mapping[str, HoleData] = dict()
        

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
        self.m1_helper = Method1Helper()
        self.m2_helper = Method2Helper()
        self.m3_helper = Method3Helper()
        self.method3_state = Method3Helper()
        # The synthesizer is initialized with the program ast it needs
        # to synthesize hole completions for.
        self.ast = ast

    def synth_method_1(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 1).

        **TODO: write a description of your approach in this method.**
        """
        # if self.m2_helper.num_calls == 0:
        #     # Initial setup
        #     for hole in self.ast.holes:
        #         self.m2_helper.hole_data[hole.var.name] = HoleData(hole)
        #         self.m2_helper.holes[hole.var.name] = hole

        hole_mappings = dict()
        for hole in self.ast.holes:
            hole_mappings[hole.var.name] = self.m1_helper.hole_to_expression(hole, self.ast.hole_can_use(hole.var.name))

        # self.m2_helper.history.append(hole_mappings)
        # self.m2_helper.num_calls += 1
        return hole_mappings

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
                self.m2_helper.holes[hole.var.name] = hole

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

        This method uses a queue to generate the expressions.
        Each hole has a set of queues, one for each production rule

        When we want to generate an expresion, first we check if the top-level rule contains "Integer"
        If so, then save time going thru the queues and just return an integer that increments every call
        Otherwise, go through the steps below

        STEP 1) If the queue is empty, return None

        STEP 2) Pop an expression from the queue. 
        If the expression is a Const or Var, and it has not been returned before, return it 
        """
        if self.m3_helper.num_calls == 0:
            # Initial Setup
            for hole in self.ast.holes:
                self.m3_helper.queues[hole.var.name] = dict()
                for rule in hole.grammar.rules:
                    self.m3_helper.queues[hole.var.name][rule.symbol.name] = list()
                    for expression in rule.productions:
                        if isinstance(expression, (BinaryExpr, UnaryExpr, Ite, BoolConst, IntConst, VarExpr)):
                            self.m3_helper.queues[hole.var.name][rule.symbol.name].append(expression)
                        elif isinstance(expression, GrammarVar):
                            self.m3_helper.queues[hole.var.name][rule.symbol.name].extend(self.ast.hole_can_use(hole.var.name))
            
            hole_mappings = dict()
            for hole in self.ast.holes:
                top_level_name = self.m3_helper.hole_data[hole.var.name].top_level_rule.symbol.name
                top_queue = self.m3_helper.queues[hole.var.name][top_level_name]

                return_expression = None 
                popped_queue = []
                num_to_pop = 1
                while len(top_queue) > 0 and num_to_pop > 0:
                    popped = top_queue.pop(0)
                    popped_queue.append(popped)
                    # if isinstance(popped, (BinaryExpr, UnaryExpr, Ite, BoolConst, IntConst, VarExpr)):
                        
                    if isinstance(return_expression, UnaryExpr):
                        pass
                        # num_to_pop += 1
                    elif isinstance(return_expression, BinaryExpr):
                        num_to_pop += 2
                    elif isinstance(return_expression, Ite):
                        num_to_pop += 3

                    num_to_pop -= 1
                # hole_mappings[hole.var.name] = return_expression
        return hole_mappings
