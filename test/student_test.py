from lang.ast import BinaryExpr, BinaryOperator, PaddleType, VarExpr, Variable
import unittest
from verification.verifier import *
from z3 import *
from pathlib import Path
from lang.paddle import parse
from lang.symb_eval import EvaluationUndefinedHoleError, Evaluator

class TestStudent(unittest.TestCase):

    def test_sanity_student(self):
        self.assertTrue(True)

    ###############################
    ## Q2) Symbolic Evaluation
    ###############################

    def test_basic_example(self):
        """
        A basic example that tests two variables.
        """
        filename = '%s/test/paddle_test_files/basic_example.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        # Evaluating this program with no hole definitions should raise an EvaluationUndefinedHoleError
        with self.assertRaises(EvaluationUndefinedHoleError):
            empty.evaluate(prog)
        # Definitions
        self.assertEqual(len(prog.inputs), 2,
                    msg="In %s, we expected exactly 2 inputs." % filename)
        x = VarExpr(prog.inputs[0])
        y = VarExpr(prog.inputs[1])
        e1 = BinaryExpr(BinaryOperator.EQUALS, x, y)
        e2 = Ite(e1, x, y)
        defined = Evaluator({"h": e2})
        prog_res = defined.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.AND)
        # there is only two variables in prog_res
        self.assertEqual(len(prog_res.uses()), 2)

    def test_three_variables(self):
        """
        Same as test_basic_example but with three variables.
        """
        filename = '%s/test/paddle_test_files/three_variables.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)
        
        prog: Program = parse(filename)
        empty = Evaluator({})
        # Evaluating this program with no hole definitions should raise an EvaluationUndefinedHoleError
        with self.assertRaises(EvaluationUndefinedHoleError):
            empty.evaluate(prog)
        # Definitions
        self.assertEqual(len(prog.inputs), 3,
            msg="In %s, we expected exactly 3 inputs." % filename)
        x = VarExpr(prog.inputs[0])
        y = VarExpr(prog.inputs[1])
        z = VarExpr(prog.inputs[2])

        e1 = BinaryExpr(BinaryOperator.EQUALS, x, y)
        e2 = Ite(e1, x, z)
        defined = Evaluator({"h": e2})
        prog_res = defined.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.AND)
        # there is only two variables in prog_res
        self.assertEqual(len(prog_res.uses()), 3)
        
    def test_div_to_add_true(self):
        """
        Division test that asserts that a quotient is true.
        """
        filename = '%s/test/paddle_test_files/div_to_add_true.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.EQUALS)
        # there is only one variable in prog_res
        self.assertEqual(len(prog_res.uses()), 1)
        # Evaluate the expression
        lhs = empty.evaluate_expr({"x": IntConst(0)}, prog_res.left_operand)
        rhs = empty.evaluate_expr({"x": IntConst(0)}, prog_res.right_operand)
        # These expressions can be evaluated in Python directly
        self.assertTrue(eval(str(lhs)) == eval(str(rhs)))

    def test_div_to_add_false(self):
        """
        Division test that asserts that a quotient is false.
        """
        filename = '%s/test/paddle_test_files/div_to_add_false.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.EQUALS)
        # there is only one variable in prog_res
        self.assertEqual(len(prog_res.uses()), 1)
        # Evaluate the expression
        lhs = empty.evaluate_expr({"x": IntConst(1)}, prog_res.left_operand)
        rhs = empty.evaluate_expr({"x": IntConst(1)}, prog_res.right_operand)
        # These expressions can be evaluated in Python directly
        # They should be different (5 != 4)
        self.assertFalse(eval(str(lhs)) == eval(str(rhs)))


    ###############################
    ## Q3) Verifying Programs
    ###############################

    def test_ast_to_z3_variable(self):
        """
        Assert that AstToZ3.convert properly converts an AST VarExpr to z3 format
        """
        ast_to_z3 = AstToZ3()

        expr = VarExpr(Variable('x', PaddleType.INT))
        expected = Int('x')
        actual = ast_to_z3.convert(expr)
        self.assertIsInstance(actual, z3.z3.ArithRef)
        self.assertTrue(expected.eq(actual))

    def test_ast_to_z3_binary_expression_arith_ref(self):
        """
        Assert that AstToZ3.convert properly converts an AST BinaryExpr between two INT variables to z3 format
        """
        ast_to_z3 = AstToZ3()

        LHS = VarExpr(Variable('x', PaddleType.INT))
        RHS = VarExpr(Variable('y', PaddleType.INT))
        expr = BinaryExpr(BinaryOperator.PLUS, LHS, RHS)

        expected = Int('x') + Int('y')
        actual = ast_to_z3.convert(expr)
        self.assertIsInstance(actual, z3.z3.ArithRef)
        self.assertTrue(expected.eq(actual))
    
    def test_ast_to_z3_binary_expression_bool_ref(self):
        """
        Assert that AstToZ3.convert properly converts an AST BinaryExpr between two BOOL variables to z3 format
        """
        ast_to_z3 = AstToZ3()

        LHS = VarExpr(Variable('x', PaddleType.BOOL))
        RHS = VarExpr(Variable('y', PaddleType.BOOL))
        expr = BinaryExpr(BinaryOperator.AND, LHS, RHS)

        expected = And(Bool('x'), Bool('y'))
        actual = ast_to_z3.convert(expr)
        self.assertIsInstance(actual, z3.z3.BoolRef)
        self.assertTrue(expected.eq(actual))
    
    def test_ast_to_z3_binary_expression_arith_to_bool(self):
        """
        Assert that AstToZ3.convert properly converts an AST BinaryExpr between two INT variables 
        *With a comparison operator* to z3 *BoolRef* format
        """
        ast_to_z3 = AstToZ3()

        LHS = VarExpr(Variable('x', PaddleType.INT))
        RHS = VarExpr(Variable('y', PaddleType.INT))
        expr = BinaryExpr(BinaryOperator.GREATER, LHS, RHS)

        expected = Int('x') > Int('y')
        actual = ast_to_z3.convert(expr)
        self.assertIsInstance(actual, z3.z3.BoolRef)
        self.assertTrue(expected.eq(actual))

    def test_ast_to_z3_unary_arith_ref(self):
        """
        Assert that AstToZ3.convert properly converts an AST UnaryExpr to z3 format ArithRef
        """
        ast_to_z3 = AstToZ3()

        var =  VarExpr(Variable('x', PaddleType.INT))
        expr = UnaryExpr(UnaryOperator.NEG, var)
        
        expected = -Int('x')
        actual = ast_to_z3.convert(expr)
        self.assertIsInstance(actual, z3.z3.ArithRef)
        self.assertTrue(expected.eq(actual))
    
    def test_ast_to_z3_unary_bool_ref(self):
        """
        Assert that AstToZ3.convert properly converts an AST UnaryExpr to z3 format BoolRef
        """
        ast_to_z3 = AstToZ3()

        var =  VarExpr(Variable('x', PaddleType.BOOL))
        expr = UnaryExpr(UnaryOperator.NOT, var)
        
        expected = Not(Bool('x'))
        actual = ast_to_z3.convert(expr)
        self.assertIsInstance(actual, z3.z3.BoolRef)
        self.assertTrue(expected.eq(actual))
    
    def test_ast_to_z3_if_then_else(self):
        """
        Assert that AstToZ3.convert properly converts an AST ITE to z3 format If BoolRef
        """
        ast_to_z3 = AstToZ3()

        cond = VarExpr(Variable('x', PaddleType.BOOL))
        true_branch = VarExpr(Variable('y', PaddleType.BOOL))
        false_branch = VarExpr(Variable('z', PaddleType.BOOL))
        expr = Ite(cond, true_branch, false_branch)

        expected = If(Bool('x'), Bool('y'), Bool('z'))
        actual = ast_to_z3.convert(expr)
        self.assertIsInstance(actual, z3.z3.BoolRef)
        self.assertTrue(expected.eq(actual))
    
    def test_ast_to_z3_constant(self):
        """
        Assert that AstToZ3.convert returns the raw value of any constants
        """
        ast_to_z3 = AstToZ3()

        self.assertTrue(ast_to_z3.convert(BoolConst(True)))
        self.assertFalse(ast_to_z3.convert(BoolConst(False)))
        self.assertEqual(ast_to_z3.convert(IntConst(5)), 5)
    
    def test_ast_to_z3_exception(self):
        """
        Assert that AstToZ3.convert raises an TypeError when encountering a Grammar or unknown expression
        """
        ast_to_z3 = AstToZ3()

        with self.assertRaises(TypeError):
            ast_to_z3.convert(GrammarVar())

        with self.assertRaises(TypeError):
            ast_to_z3.convert(GrammarInteger())
            
        with self.assertRaises(TypeError):
            ast_to_z3.convert(Expression())

    ###############################
    ## Q4) Enumerating Programs
    ###############################
