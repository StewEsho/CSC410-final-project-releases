from lang.ast import BinaryExpr, BinaryOperator, PaddleType, VarExpr, Variable
import unittest
from verification.verifier import *
from z3 import *

class TestStudent(unittest.TestCase):

    def test_sanity_student(self):
        self.assertTrue(True)

    ###############################
    ## Q2) Symbolic Evaluation
    ###############################

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
        self.assertEquals(ast_to_z3.convert(IntConst(5)), 5)
    
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
