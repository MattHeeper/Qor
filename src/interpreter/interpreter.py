"""
QOR Language Interpreter v1.0
------------------------------
This module implements the execution engine for the QOR language.
It traverses the Abstract Syntax Tree (AST) and executes the program.

Features:
- Variable storage (symbol table)
- Expression evaluation
- Arithmetic operations (+, -, *, /)
- Print statements
- Runtime error handling

Author: QOR Development Team
License: MIT
Version: 1.0.0
"""

from typing import Any, Dict, List
import sys


class RuntimeError(Exception):
    """Custom exception for runtime errors in QOR programs."""
    pass


class Interpreter:
    """
    Execution engine for the QOR programming language.
    
    The interpreter walks through the AST and executes each node,
    maintaining a symbol table for variable storage.
    
    Attributes:
        variables (Dict[str, Any]): Symbol table storing variable values
        output (List[str]): Captured output for testing
    """
    
    def __init__(self):
        """Initialize interpreter with empty symbol table."""
        self.variables: Dict[str, Any] = {}
        self.output: List[str] = []
    
    def visit(self, node) -> Any:
        """
        Dispatch method to visit appropriate node type.
        
        Args:
            node: AST node to visit
            
        Returns:
            Any: Result of visiting the node
        """
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        """Fallback for unhandled node types."""
        raise RuntimeError(f"No visit method for {type(node).__name__}")
    
    def visit_NumberNode(self, node) -> float:
        """
        Visit a number literal node.
        
        Args:
            node: NumberNode
            
        Returns:
            float: Numeric value
        """
        return node.value
    
    def visit_StringNode(self, node) -> str:
        """
        Visit a string literal node.
        
        Args:
            node: StringNode
            
        Returns:
            str: String value
        """
        return node.value
    
    def visit_VariableNode(self, node) -> Any:
        """
        Visit a variable reference node.
        
        Args:
            node: VariableNode
            
        Returns:
            Any: Value stored in variable
            
        Raises:
            RuntimeError: If variable is not defined
        """
        if node.name not in self.variables:
            raise RuntimeError(f"Undefined variable: '{node.name}'")
        
        return self.variables[node.name]
    
    def visit_BinaryOpNode(self, node) -> float:
        """
        Visit a binary operation node.
        
        Args:
            node: BinaryOpNode
            
        Returns:
            float: Result of operation
            
        Raises:
            RuntimeError: For division by zero or unknown operators
        """
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if node.operator == '+':
            return left + right
        elif node.operator == '-':
            return left - right
        elif node.operator == '*':
            return left * right
        elif node.operator == '/':
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        else:
            raise RuntimeError(f"Unknown operator: {node.operator}")
    
    def visit_AssignmentNode(self, node) -> None:
        """
        Visit an assignment node.
        
        Args:
            node: AssignmentNode
        """
        value = self.visit(node.value)
        self.variables[node.variable] = value
    
    def visit_PrintNode(self, node) -> None:
        """
        Visit a print statement node.
        
        Args:
            node: PrintNode
        """
        value = self.visit(node.expression)
        output = str(value)
        
        # Store for testing
        self.output.append(output)
        
        # Print to console
        print(output)
    
    def interpret(self, ast: List) -> None:
        """
        Execute a list of AST nodes.
        
        Args:
            ast (List): List of statement nodes to execute
        """
        for node in ast:
            self.visit(node)


# Integration module to connect Lexer -> Parser -> Interpreter
class QOR:
    """
    Main QOR language interface.
    
    Combines lexer, parser, and interpreter for easy execution.
    """
    
    def __init__(self):
        """Initialize QOR runtime."""
        self.interpreter = Interpreter()
    
    def run(self, code: str) -> None:
        """
        Execute QOR source code.
        
        Args:
            code (str): QOR source code to execute
        """
        # Import lexer and parser
        # Note: In real usage, these would be proper imports
        from lexer import Lexer
        from parser import Parser
        
        # Lexical analysis
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        # Syntax analysis
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Execution
        self.interpreter.interpret(ast)
    
    def get_variable(self, name: str) -> Any:
        """Get value of a variable."""
        return self.interpreter.variables.get(name)
    
    def get_output(self) -> List[str]:
        """Get captured output."""
        return self.interpreter.output


# Testing
if __name__ == "__main__":
    print("=" * 60)
    print("QOR INTERPRETER v1.0 - TEST SUITE")
    print("=" * 60)
    
    # We'll test with manually created AST nodes
    # Import AST node classes
    from parser import (
        NumberNode, StringNode, VariableNode,
        BinaryOpNode, AssignmentNode, PrintNode
    )
    
    interpreter = Interpreter()
    
    # Test 1: Simple number
    print("\n[Test 1] Evaluate Number")
    print("-" * 60)
    node1 = NumberNode('42')
    result1 = interpreter.visit(node1)
    print(f"42 => {result1}")
    
    # Test 2: Variable assignment
    print("\n[Test 2] Variable Assignment")
    print("-" * 60)
    assign_node = AssignmentNode('x', NumberNode('10'))
    interpreter.visit(assign_node)
    print(f"x = 10")
    print(f"Variables: {interpreter.variables}")
    
    # Test 3: Arithmetic
    print("\n[Test 3] Arithmetic Operations")
    print("-" * 60)
    # x = 10 + 5
    expr = BinaryOpNode(NumberNode('10'), '+', NumberNode('5'))
    result3 = interpreter.visit(expr)
    print(f"10 + 5 => {result3}")
    
    # Test 4: Variable reference
    print("\n[Test 4] Variable Reference")
    print("-" * 60)
    # y = x + 3 (where x = 10)
    var_ref = VariableNode('x')
    expr4 = BinaryOpNode(var_ref, '+', NumberNode('3'))
    assign4 = AssignmentNode('y', expr4)
    interpreter.visit(assign4)
    print(f"y = x + 3 => y = {interpreter.variables['y']}")
    print(f"Variables: {interpreter.variables}")
    
    # Test 5: Print statement
    print("\n[Test 5] Print Statement")
    print("-" * 60)
    print_node = PrintNode(StringNode('"Hello, QOR!"'))
    print("Executing: print(\"Hello, QOR!\")")
    interpreter.visit(print_node)
    
    # Test 6: Complex expression with operator precedence
    print("\n[Test 6] Operator Precedence")
    print("-" * 60)
    # result = 10 + 5 * 2 (should be 20, not 30)
    mul_expr = BinaryOpNode(NumberNode('5'), '*', NumberNode('2'))
    add_expr = BinaryOpNode(NumberNode('10'), '+', mul_expr)
    assign6 = AssignmentNode('result', add_expr)
    interpreter.visit(assign6)
    print(f"result = 10 + 5 * 2")
    print(f"result = {interpreter.variables['result']} (expected: 20)")
    
    # Test 7: Division by zero (error handling)
    print("\n[Test 7] Error Handling - Division by Zero")
    print("-" * 60)
    try:
        div_expr = BinaryOpNode(NumberNode('10'), '/', NumberNode('0'))
        interpreter.visit(div_expr)
    except RuntimeError as e:
        print(f"✅ Caught error: {e}")
    
    # Test 8: Undefined variable (error handling)
    print("\n[Test 8] Error Handling - Undefined Variable")
    print("-" * 60)
    try:
        undefined_var = VariableNode('undefined')
        interpreter.visit(undefined_var)
    except RuntimeError as e:
        print(f"✅ Caught error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All interpreter tests completed!")
    print("=" * 60)
    print(f"\nFinal symbol table: {interpreter.variables}")
    print(f"Captured output: {interpreter.output}")