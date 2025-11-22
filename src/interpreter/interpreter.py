"""
QOR Language Interpreter v2.5
------------------------------
This module implements the execution engine for the QOR language.
It traverses the Abstract Syntax Tree (AST) and executes the program.

Version 2.5 adds support for:
- Built-in mathematical functions (sqrt, sin, cos, etc.)
- Mathematical constants (pi, e)
- User-defined functions
- If/elif/else statements
- For and while loops
- Comparison and logical operators
- Return statements with proper control flow

Author: QOR Development Team
License: MIT
Version: 2.5.0
"""

from typing import Any, Dict, List
import sys
import math


class ReturnValue(Exception):
    """Exception used to implement return statements."""
    def __init__(self, value):
        self.value = value


class RuntimeError(Exception):
    """Custom exception for runtime errors in QOR programs."""
    pass


class Function:
    """Represents a user-defined function."""
    def __init__(self, name: str, params: List[str], body: List, closure: Dict):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure  # Save enclosing scope


class Interpreter:
    """
    Execution engine for the QOR programming language.
    
    Attributes:
        global_vars (Dict[str, Any]): Global symbol table
        local_vars (List[Dict[str, Any]]): Stack of local scopes
        functions (Dict[str, Function]): User-defined functions
        builtins (Dict[str, callable]): Built-in functions
        output (List[str]): Captured output for testing
    """
    
    def __init__(self):
        """Initialize interpreter with empty symbol tables."""
        self.global_vars: Dict[str, Any] = {}
        self.local_vars: List[Dict[str, Any]] = []
        self.functions: Dict[str, Function] = {}
        self.builtins: Dict[str, Any] = {}
        self.output: List[str] = []
        
        # Register built-in functions
        self._register_builtins()
    
    def _register_builtins(self) -> None:
        """Register built-in mathematical functions."""
        # Built-in math functions
        self.builtins = {
            # Basic math
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            
            # Math module functions
            'sqrt': math.sqrt,
            'pow': pow,
            'exp': math.exp,
            'log': math.log,
            'log10': math.log10,
            
            # Trigonometry
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            
            # Floor/Ceil
            'floor': math.floor,
            'ceil': math.ceil,
            
            # List/String methods
            'len': len,
            'str': str,
            'int': int,
            'float': float,
        }
        
        # Add constants to global vars
        self.global_vars['pi'] = math.pi
        self.global_vars['e'] = math.e
    
    @property
    def variables(self) -> Dict[str, Any]:
        """Get current variable scope."""
        if self.local_vars:
            return self.local_vars[-1]
        return self.global_vars
    
    def get_variable(self, name: str) -> Any:
        """Get variable value from current scope."""
        # Check local scopes (most recent first)
        for scope in reversed(self.local_vars):
            if name in scope:
                return scope[name]
        
        # Check global scope
        if name in self.global_vars:
            return self.global_vars[name]
        
        raise RuntimeError(f"Undefined variable: '{name}'")
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set variable in current scope."""
        if self.local_vars:
            self.local_vars[-1][name] = value
        else:
            self.global_vars[name] = value
    
    def push_scope(self, initial_vars: Dict[str, Any] = None) -> None:
        """Push a new local scope."""
        self.local_vars.append(initial_vars or {})
    
    def pop_scope(self) -> None:
        """Pop the current local scope."""
        if self.local_vars:
            self.local_vars.pop()
    
    def visit(self, node) -> Any:
        """Dispatch method to visit appropriate node type."""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        """Fallback for unhandled node types."""
        raise RuntimeError(f"No visit method for {type(node).__name__}")
    
    def visit_NumberNode(self, node) -> float:
        """Visit a number literal node."""
        return node.value
    
    def visit_StringNode(self, node) -> str:
        """Visit a string literal node."""
        return node.value
    
    def visit_BooleanNode(self, node) -> bool:
        """Visit a boolean literal node."""
        return node.value
    
    def visit_VariableNode(self, node) -> Any:
        """Visit a variable reference node."""
        return self.get_variable(node.name)
    
    def visit_BinaryOpNode(self, node) -> Any:
        """Visit a binary operation node."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # Arithmetic operators
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
        elif node.operator == '%':
            return left % right
        elif node.operator == '**':
            return left ** right
        
        # Comparison operators
        elif node.operator == '==':
            return left == right
        elif node.operator == '!=':
            return left != right
        elif node.operator == '<':
            return left < right
        elif node.operator == '>':
            return left > right
        elif node.operator == '<=':
            return left <= right
        elif node.operator == '>=':
            return left >= right
        
        # Logical operators
        elif node.operator == 'and':
            return left and right
        elif node.operator == 'or':
            return left or right
        
        else:
            raise RuntimeError(f"Unknown operator: {node.operator}")
    
    def visit_UnaryOpNode(self, node) -> Any:
        """Visit a unary operation node."""
        operand = self.visit(node.operand)
        
        if node.operator == '-':
            return -operand
        elif node.operator == 'not':
            return not operand
        else:
            raise RuntimeError(f"Unknown unary operator: {node.operator}")
    
    def visit_AssignmentNode(self, node) -> None:
        """Visit an assignment node."""
        value = self.visit(node.value)
        self.set_variable(node.variable, value)
    
    def visit_PrintNode(self, node) -> None:
        """Visit a print statement node."""
        value = self.visit(node.expression)
        output = str(value)
        
        self.output.append(output)
        print(output)
    
    def visit_FunctionDefNode(self, node) -> None:
        """Visit a function definition node."""
        # Store function with current scope as closure
        func = Function(node.name, node.params, node.body, dict(self.global_vars))
        self.functions[node.name] = func
    
    def visit_FunctionCallNode(self, node) -> Any:
        """Visit a function call node."""
        # Check for built-in functions first
        if node.name in self.builtins:
            args = [self.visit(arg) for arg in node.args]
            try:
                return self.builtins[node.name](*args)
            except Exception as e:
                raise RuntimeError(f"Error calling built-in function '{node.name}': {e}")
        
        # Check if user-defined function exists
        if node.name not in self.functions:
            raise RuntimeError(f"Undefined function: '{node.name}'")
        
        func = self.functions[node.name]
        
        # Evaluate arguments
        args = [self.visit(arg) for arg in node.args]
        
        # Check argument count
        if len(args) != len(func.params):
            raise RuntimeError(
                f"Function '{node.name}' expects {len(func.params)} arguments, "
                f"got {len(args)}"
            )
        
        # Create new scope with parameters
        local_scope = dict(zip(func.params, args))
        self.push_scope(local_scope)
        
        try:
            # Execute function body
            result = None
            for stmt in func.body:
                self.visit(stmt)
        except ReturnValue as ret:
            result = ret.value
        finally:
            self.pop_scope()
        
        return result
    
    def visit_ReturnNode(self, node) -> None:
        """Visit a return statement node."""
        if node.value:
            value = self.visit(node.value)
        else:
            value = None
        
        raise ReturnValue(value)
    
    def visit_IfNode(self, node) -> None:
        """Visit an if/elif/else statement node."""
        # Evaluate main condition
        condition = self.visit(node.condition)
        
        if condition:
            # Execute then body
            for stmt in node.then_body:
                self.visit(stmt)
        else:
            # Check elif conditions
            executed = False
            for elif_condition, elif_body in node.elif_parts:
                if self.visit(elif_condition):
                    for stmt in elif_body:
                        self.visit(stmt)
                    executed = True
                    break
            
            # Execute else if no elif matched
            if not executed and node.else_body:
                for stmt in node.else_body:
                    self.visit(stmt)
    
    def visit_ForNode(self, node) -> None:
        """Visit a for loop node."""
        # Evaluate iterable
        iterable = self.visit(node.iterable)
        
        # Execute loop
        for value in iterable:
            self.set_variable(node.variable, value)
            for stmt in node.body:
                self.visit(stmt)
    
    def visit_WhileNode(self, node) -> None:
        """Visit a while loop node."""
        while self.visit(node.condition):
            for stmt in node.body:
                self.visit(stmt)
    
    def visit_RangeNode(self, node) -> range:
        """Visit a range node."""
        start = int(self.visit(node.start))
        stop = int(self.visit(node.stop))
        step = int(self.visit(node.step))
        
        return range(start, stop, step)
    
    def visit_ListNode(self, node) -> list:
        """Visit a list node."""
        return [self.visit(element) for element in node.elements]
    
    def visit_DictNode(self, node) -> dict:
        """Visit a dictionary node."""
        result = {}
        for key_node, value_node in node.pairs:
            key = self.visit(key_node)
            value = self.visit(value_node)
            result[key] = value
        return result
    
    def visit_IndexNode(self, node) -> Any:
        """Visit an index operation."""
        obj = self.visit(node.obj)
        index = self.visit(node.index)
        
        try:
            return obj[index]
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"Index error: {e}")
    
    def visit_MethodCallNode(self, node) -> Any:
        """Visit a method call."""
        obj = self.visit(node.obj)
        args = [self.visit(arg) for arg in node.args]
        
        # Get method from object
        try:
            method = getattr(obj, node.method)
            return method(*args)
        except AttributeError:
            raise RuntimeError(f"Object has no method '{node.method}'")
        except Exception as e:
            raise RuntimeError(f"Error calling method '{node.method}': {e}")
    
    def interpret(self, ast: List) -> None:
        """Execute a list of AST nodes."""
        for node in ast:
            self.visit(node)


# Testing
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from lexer.lexer import Lexer
    from parser.parser import Parser
    
    print("=" * 60)
    print("QOR INTERPRETER v2.5 - WITH MATH FUNCTIONS")
    print("=" * 60)
    
    # Test 1: Basic math functions
    print("\n[Test 1] Basic Math Functions")
    print("-" * 60)
    code1 = """x = abs(-10)
print(x)
y = sqrt(16)
print(y)"""
    
    print(f"Code:\n{code1}\n")
    print("Output:")
    
    interpreter1 = Interpreter()
    lexer1 = Lexer(code1)
    tokens1 = lexer1.tokenize()
    parser1 = Parser(tokens1)
    ast1 = parser1.parse()
    interpreter1.interpret(ast1)
    
    # Test 2: Pi and power
    print("\n[Test 2] Pi and Power")
    print("-" * 60)
    code2 = """radius = 5
area = pi * pow(radius, 2)
print(area)"""
    
    print(f"Code:\n{code2}\n")
    print("Output:")
    
    interpreter2 = Interpreter()
    lexer2 = Lexer(code2)
    tokens2 = lexer2.tokenize()
    parser2 = Parser(tokens2)
    ast2 = parser2.parse()
    interpreter2.interpret(ast2)
    
    # Test 3: Trigonometry
    print("\n[Test 3] Trigonometry")
    print("-" * 60)
    code3 = """angle = pi / 4
sine = sin(angle)
print(sine)"""
    
    print(f"Code:\n{code3}\n")
    print("Output:")
    
    interpreter3 = Interpreter()
    lexer3 = Lexer(code3)
    tokens3 = lexer3.tokenize()
    parser3 = Parser(tokens3)
    ast3 = parser3.parse()
    interpreter3.interpret(ast3)
    
    # Test 4: Lists
    print("\n[Test 4] Lists")
    print("-" * 60)
    code4 = """numbers = [1, 2, 3, 4, 5]
print(numbers)
first = numbers[0]
print(first)"""
    
    print(f"Code:\n{code4}\n")
    print("Output:")
    
    interpreter4 = Interpreter()
    lexer4 = Lexer(code4)
    tokens4 = lexer4.tokenize()
    parser4 = Parser(tokens4)
    ast4 = parser4.parse()
    interpreter4.interpret(ast4)
    
    # Test 5: Dictionaries
    print("\n[Test 5] Dictionaries")
    print("-" * 60)
    code5 = """person = {"name": "Ali", "age": 25}
print(person)
name = person["name"]
print(name)"""
    
    print(f"Code:\n{code5}\n")
    print("Output:")
    
    interpreter5 = Interpreter()
    lexer5 = Lexer(code5)
    tokens5 = lexer5.tokenize()
    parser5 = Parser(tokens5)
    ast5 = parser5.parse()
    interpreter5.interpret(ast5)
    
    print("\n" + "=" * 60)
    print("✅ All math tests completed!")
    print("=" * 60)
