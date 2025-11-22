"""
QOR Language Parser v2.0
-------------------------
This module implements the syntax analysis phase of the QOR compiler.
It takes tokens from the lexer and builds an Abstract Syntax Tree (AST)
that represents the program structure.

Version 2.0 adds support for:
- Function definitions and calls
- If/elif/else statements
- For and while loops
- Comparison and logical operators
- Return statements

Author: QOR Development Team
License: MIT
Version: 2.0.0
"""

from typing import List, Tuple, Any, Optional


class ASTNode:
    """Base class for all Abstract Syntax Tree nodes."""
    pass


class NumberNode(ASTNode):
    """Represents a numeric literal."""
    def __init__(self, value: str):
        self.value = float(value) if '.' in value else int(value)
    
    def __repr__(self):
        return f"Number({self.value})"


class StringNode(ASTNode):
    """Represents a string literal."""
    def __init__(self, value: str):
        self.value = value[1:-1]  # Remove quotes
    
    def __repr__(self):
        return f"String({self.value!r})"


class BooleanNode(ASTNode):
    """Represents a boolean literal."""
    def __init__(self, value: str):
        self.value = value == 'True'
    
    def __repr__(self):
        return f"Boolean({self.value})"


class VariableNode(ASTNode):
    """Represents a variable reference."""
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"Variable({self.name})"


class BinaryOpNode(ASTNode):
    """Represents a binary operation."""
    def __init__(self, left: ASTNode, operator: str, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


class UnaryOpNode(ASTNode):
    """Represents a unary operation (e.g., not, -)."""
    def __init__(self, operator: str, operand: ASTNode):
        self.operator = operator
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand})"


class AssignmentNode(ASTNode):
    """Represents a variable assignment."""
    def __init__(self, variable: str, value: ASTNode):
        self.variable = variable
        self.value = value
    
    def __repr__(self):
        return f"Assignment({self.variable} = {self.value})"


class PrintNode(ASTNode):
    """Represents a print statement."""
    def __init__(self, expression: ASTNode):
        self.expression = expression
    
    def __repr__(self):
        return f"Print({self.expression})"


class FunctionDefNode(ASTNode):
    """Represents a function definition."""
    def __init__(self, name: str, params: List[str], body: List[ASTNode]):
        self.name = name
        self.params = params
        self.body = body
    
    def __repr__(self):
        return f"FunctionDef({self.name}, params={self.params}, body={len(self.body)} stmts)"


class FunctionCallNode(ASTNode):
    """Represents a function call."""
    def __init__(self, name: str, args: List[ASTNode]):
        self.name = name
        self.args = args
    
    def __repr__(self):
        return f"FunctionCall({self.name}, args={self.args})"


class ReturnNode(ASTNode):
    """Represents a return statement."""
    def __init__(self, value: Optional[ASTNode] = None):
        self.value = value
    
    def __repr__(self):
        return f"Return({self.value})"


class IfNode(ASTNode):
    """Represents an if/elif/else statement."""
    def __init__(self, condition: ASTNode, then_body: List[ASTNode], 
                 elif_parts: List[Tuple[ASTNode, List[ASTNode]]] = None,
                 else_body: List[ASTNode] = None):
        self.condition = condition
        self.then_body = then_body
        self.elif_parts = elif_parts or []
        self.else_body = else_body or []
    
    def __repr__(self):
        return f"If(condition={self.condition}, then={len(self.then_body)} stmts)"


class ForNode(ASTNode):
    """Represents a for loop."""
    def __init__(self, variable: str, iterable: ASTNode, body: List[ASTNode]):
        self.variable = variable
        self.iterable = iterable
        self.body = body
    
    def __repr__(self):
        return f"For({self.variable} in {self.iterable}, body={len(self.body)} stmts)"


class WhileNode(ASTNode):
    """Represents a while loop."""
    def __init__(self, condition: ASTNode, body: List[ASTNode]):
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"While(condition={self.condition}, body={len(self.body)} stmts)"


class RangeNode(ASTNode):
    """Represents a range() call."""
    def __init__(self, start: ASTNode, stop: Optional[ASTNode] = None, step: Optional[ASTNode] = None):
        if stop is None:
            self.start = NumberNode('0')
            self.stop = start
            self.step = NumberNode('1')
        else:
            self.start = start
            self.stop = stop
            self.step = step or NumberNode('1')
    
    def __repr__(self):
        return f"Range({self.start}, {self.stop}, {self.step})"


class ListNode(ASTNode):
    """Represents a list literal."""
    def __init__(self, elements: List[ASTNode]):
        self.elements = elements
    
    def __repr__(self):
        return f"List([{', '.join(str(e) for e in self.elements)}])"


class DictNode(ASTNode):
    """Represents a dictionary literal."""
    def __init__(self, pairs: List[Tuple[ASTNode, ASTNode]]):
        self.pairs = pairs
    
    def __repr__(self):
        return f"Dict({len(self.pairs)} pairs)"


class IndexNode(ASTNode):
    """Represents indexing operation (list[0] or dict['key'])."""
    def __init__(self, obj: ASTNode, index: ASTNode):
        self.obj = obj
        self.index = index
    
    def __repr__(self):
        return f"Index({self.obj}[{self.index}])"


class MethodCallNode(ASTNode):
    """Represents a method call (obj.method(args))."""
    def __init__(self, obj: ASTNode, method: str, args: List[ASTNode]):
        self.obj = obj
        self.method = method
        self.args = args
    
    def __repr__(self):
        return f"MethodCall({self.obj}.{self.method}({len(self.args)} args))"


class Parser:
    """Syntax analyzer for the QOR programming language."""
    
    def __init__(self, tokens: List[Tuple[str, str]]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        """Move to the next token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def peek(self, offset: int = 1) -> Optional[Tuple[str, str]]:
        """Look ahead at token without consuming it."""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: str) -> str:
        """Verify current token matches expected type and advance."""
        if self.current_token is None:
            raise SyntaxError(f"Expected {token_type}, got end of input")
        
        if self.current_token[0] != token_type:
            raise SyntaxError(
                f"Expected {token_type}, got {self.current_token[0]} "
                f"('{self.current_token[1]}')"
            )
        
        value = self.current_token[1]
        self.advance()
        return value
    
    def skip_newlines(self):
        """Skip any newline tokens."""
        while self.current_token and self.current_token[0] == 'NEWLINE':
            self.advance()
    
    def parse(self) -> List[ASTNode]:
        """Parse the token stream and build AST."""
        statements = []
        
        while self.current_token is not None:
            self.skip_newlines()
            if self.current_token is None:
                break
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            
            self.skip_newlines()
        
        return statements
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement."""
        if not self.current_token:
            return None
        
        token_type = self.current_token[0]
        
        if token_type == 'PRINT':
            return self.parse_print()
        elif token_type == 'FUNCTION':
            return self.parse_function_def()
        elif token_type == 'RETURN':
            return self.parse_return()
        elif token_type == 'IF':
            return self.parse_if()
        elif token_type == 'FOR':
            return self.parse_for()
        elif token_type == 'WHILE':
            return self.parse_while()
        elif token_type == 'ID':
            # Could be assignment or function call
            next_token = self.peek()
            if next_token and next_token[0] == 'ASSIGN':
                return self.parse_assignment()
            elif next_token and next_token[0] == 'LPAREN':
                return self.parse_expression()  # Function call as statement
            else:
                return self.parse_expression()
        else:
            return self.parse_expression()
    
    def parse_print(self) -> PrintNode:
        """Parse print statement."""
        self.expect('PRINT')
        self.expect('LPAREN')
        expr = self.parse_expression()
        self.expect('RPAREN')
        return PrintNode(expr)
    
    def parse_assignment(self) -> AssignmentNode:
        """Parse assignment."""
        var_name = self.expect('ID')
        self.expect('ASSIGN')
        expr = self.parse_expression()
        return AssignmentNode(var_name, expr)
    
    def parse_function_def(self) -> FunctionDefNode:
        """Parse function definition."""
        self.expect('FUNCTION')
        name = self.expect('ID')
        self.expect('LPAREN')
        
        # Parse parameters
        params = []
        if self.current_token and self.current_token[0] != 'RPAREN':
            params.append(self.expect('ID'))
            while self.current_token and self.current_token[0] == 'COMMA':
                self.advance()
                params.append(self.expect('ID'))
        
        self.expect('RPAREN')
        self.expect('COLON')
        self.skip_newlines()
        
        # Parse body (simplified - single statement for now)
        body = []
        body.append(self.parse_statement())
        
        return FunctionDefNode(name, params, body)
    
    def parse_return(self) -> ReturnNode:
        """Parse return statement."""
        self.expect('RETURN')
        
        if self.current_token and self.current_token[0] != 'NEWLINE':
            value = self.parse_expression()
            return ReturnNode(value)
        
        return ReturnNode()
    
    def parse_if(self) -> IfNode:
        """Parse if/elif/else statement."""
        self.expect('IF')
        condition = self.parse_expression()
        self.expect('COLON')
        self.skip_newlines()
        
        # Parse then body
        then_body = [self.parse_statement()]
        self.skip_newlines()
        
        # Parse elif parts
        elif_parts = []
        while self.current_token and self.current_token[0] == 'ELIF':
            self.advance()
            elif_condition = self.parse_expression()
            self.expect('COLON')
            self.skip_newlines()
            elif_body = [self.parse_statement()]
            elif_parts.append((elif_condition, elif_body))
            self.skip_newlines()
        
        # Parse else
        else_body = []
        if self.current_token and self.current_token[0] == 'ELSE':
            self.advance()
            self.expect('COLON')
            self.skip_newlines()
            else_body = [self.parse_statement()]
        
        return IfNode(condition, then_body, elif_parts, else_body)
    
    def parse_for(self) -> ForNode:
        """Parse for loop."""
        self.expect('FOR')
        var_name = self.expect('ID')
        self.expect('IN')
        iterable = self.parse_expression()
        self.expect('COLON')
        self.skip_newlines()
        
        body = [self.parse_statement()]
        
        return ForNode(var_name, iterable, body)
    
    def parse_while(self) -> WhileNode:
        """Parse while loop."""
        self.expect('WHILE')
        condition = self.parse_expression()
        self.expect('COLON')
        self.skip_newlines()
        
        body = [self.parse_statement()]
        
        return WhileNode(condition, body)
    
    def parse_expression(self) -> ASTNode:
        """Parse expression with logical operators."""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR."""
        node = self.parse_logical_and()
        
        while self.current_token and self.current_token[0] == 'OR':
            self.advance()
            right = self.parse_logical_and()
            node = BinaryOpNode(node, 'or', right)
        
        return node
    
    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND."""
        node = self.parse_logical_not()
        
        while self.current_token and self.current_token[0] == 'AND':
            self.advance()
            right = self.parse_logical_not()
            node = BinaryOpNode(node, 'and', right)
        
        return node
    
    def parse_logical_not(self) -> ASTNode:
        """Parse logical NOT."""
        if self.current_token and self.current_token[0] == 'NOT':
            self.advance()
            operand = self.parse_logical_not()
            return UnaryOpNode('not', operand)
        
        return self.parse_comparison()
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison operators."""
        node = self.parse_arithmetic()
        
        if self.current_token and self.current_token[0] in ('EQ', 'NEQ', 'LT', 'GT', 'LEQ', 'GEQ'):
            op_map = {
                'EQ': '==', 'NEQ': '!=', 'LT': '<', 
                'GT': '>', 'LEQ': '<=', 'GEQ': '>='
            }
            operator = op_map[self.current_token[0]]
            self.advance()
            right = self.parse_arithmetic()
            node = BinaryOpNode(node, operator, right)
        
        return node
    
    def parse_arithmetic(self) -> ASTNode:
        """Parse arithmetic: term ((PLUS | MINUS) term)*"""
        node = self.parse_term()
        
        while self.current_token and self.current_token[0] in ('PLUS', 'MINUS'):
            operator = self.current_token[1]
            self.advance()
            right = self.parse_term()
            node = BinaryOpNode(node, operator, right)
        
        return node
    
    def parse_term(self) -> ASTNode:
        """Parse term: factor ((MULTIPLY | DIVIDE | MODULO) factor)*"""
        node = self.parse_power()
        
        while self.current_token and self.current_token[0] in ('MULTIPLY', 'DIVIDE', 'MODULO'):
            operator = self.current_token[1]
            self.advance()
            right = self.parse_power()
            node = BinaryOpNode(node, operator, right)
        
        return node
    
    def parse_power(self) -> ASTNode:
        """Parse power: factor (POWER factor)*"""
        node = self.parse_factor()
        
        while self.current_token and self.current_token[0] == 'POWER':
            self.advance()
            right = self.parse_factor()
            node = BinaryOpNode(node, '**', right)
        
        return node
    
    def parse_factor(self) -> ASTNode:
        """Parse factor: NUMBER | STRING | BOOLEAN | ID | LIST | DICT | (expression) | function_call | range"""
        token = self.current_token
        
        if not token:
            raise SyntaxError("Unexpected end of input")
        
        if token[0] == 'NUMBER':
            self.advance()
            return NumberNode(token[1])
        
        elif token[0] == 'STRING':
            self.advance()
            return StringNode(token[1])
        
        elif token[0] in ('TRUE', 'FALSE'):
            self.advance()
            return BooleanNode(token[1])
        
        elif token[0] == 'RANGE':
            return self.parse_range()
        
        elif token[0] == 'LBRACKET':
            return self.parse_list()
        
        elif token[0] == 'LBRACE':
            return self.parse_dict()
        
        elif token[0] == 'ID':
            name = token[1]
            self.advance()
            
            # Check for method call (obj.method())
            if self.current_token and self.current_token[0] == 'DOT':
                self.advance()
                method_name = self.expect('ID')
                self.expect('LPAREN')
                
                args = []
                if self.current_token and self.current_token[0] != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.current_token and self.current_token[0] == 'COMMA':
                        self.advance()
                        args.append(self.parse_expression())
                
                self.expect('RPAREN')
                return MethodCallNode(VariableNode(name), method_name, args)
            
            # Check for indexing (obj[index])
            elif self.current_token and self.current_token[0] == 'LBRACKET':
                self.advance()
                index = self.parse_expression()
                self.expect('RBRACKET')
                return IndexNode(VariableNode(name), index)
            
            # Check for function call
            elif self.current_token and self.current_token[0] == 'LPAREN':
                self.advance()
                args = []
                
                if self.current_token and self.current_token[0] != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.current_token and self.current_token[0] == 'COMMA':
                        self.advance()
                        args.append(self.parse_expression())
                
                self.expect('RPAREN')
                return FunctionCallNode(name, args)
            
            return VariableNode(name)
        
        elif token[0] == 'LPAREN':
            self.advance()
            node = self.parse_expression()
            self.expect('RPAREN')
            return node
        
        elif token[0] == 'MINUS':
            self.advance()
            operand = self.parse_factor()
            return UnaryOpNode('-', operand)
        
        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")
    
    def parse_range(self) -> RangeNode:
        """Parse range() call."""
        self.expect('RANGE')
        self.expect('LPAREN')
        
        args = [self.parse_expression()]
        
        while self.current_token and self.current_token[0] == 'COMMA':
            self.advance()
            args.append(self.parse_expression())
        
        self.expect('RPAREN')
        
        if len(args) == 1:
            return RangeNode(args[0])
        elif len(args) == 2:
            return RangeNode(args[0], args[1])
        elif len(args) == 3:
            return RangeNode(args[0], args[1], args[2])
        else:
            raise SyntaxError("range() takes 1-3 arguments")
    
    def parse_list(self) -> ListNode:
        """Parse list literal: [1, 2, 3]"""
        self.expect('LBRACKET')
        
        elements = []
        if self.current_token and self.current_token[0] != 'RBRACKET':
            elements.append(self.parse_expression())
            
            while self.current_token and self.current_token[0] == 'COMMA':
                self.advance()
                if self.current_token and self.current_token[0] == 'RBRACKET':
                    break  # Trailing comma
                elements.append(self.parse_expression())
        
        self.expect('RBRACKET')
        return ListNode(elements)
    
    def parse_dict(self) -> DictNode:
        """Parse dictionary literal: {"key": "value", "age": 25}"""
        self.expect('LBRACE')
        
        pairs = []
        if self.current_token and self.current_token[0] != 'RBRACE':
            # Parse first pair
            key = self.parse_expression()
            self.expect('COLON')
            value = self.parse_expression()
            pairs.append((key, value))
            
            # Parse remaining pairs
            while self.current_token and self.current_token[0] == 'COMMA':
                self.advance()
                if self.current_token and self.current_token[0] == 'RBRACE':
                    break  # Trailing comma
                
                key = self.parse_expression()
                self.expect('COLON')
                value = self.parse_expression()
                pairs.append((key, value))
        
        self.expect('RBRACE')
        return DictNode(pairs)


# Testing
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from lexer.lexer import Lexer
    
    print("=" * 60)
    print("QOR PARSER v2.0 - ADVANCED FEATURES TEST")
    print("=" * 60)
    
    # Test 1: Function
    print("\n[Test 1] Function Definition")
    print("-" * 60)
    code1 = """function add(a, b):
    return a + b"""
    print(f"Code:\n{code1}\n")
    
    lexer1 = Lexer(code1)
    tokens1 = lexer1.tokenize()
    parser1 = Parser(tokens1)
    ast1 = parser1.parse()
    print(f"AST: {ast1}")
    
    # Test 2: If statement
    print("\n[Test 2] If Statement")
    print("-" * 60)
    code2 = """if x > 5:
    print("big")"""
    print(f"Code:\n{code2}\n")
    
    lexer2 = Lexer(code2)
    tokens2 = lexer2.tokenize()
    parser2 = Parser(tokens2)
    ast2 = parser2.parse()
    print(f"AST: {ast2}")
    
    # Test 3: For loop
    print("\n[Test 3] For Loop")
    print("-" * 60)
    code3 = """for i in range(5):
    print(i)"""
    print(f"Code:\n{code3}\n")
    
    lexer3 = Lexer(code3)
    tokens3 = lexer3.tokenize()
    parser3 = Parser(tokens3)
    ast3 = parser3.parse()
    print(f"AST: {ast3}")
    
    # Test 4: Lists
    print("\n[Test 4] Lists")
    print("-" * 60)
    code4 = "numbers = [1, 2, 3]"
    print(f"Code: {code4}\n")
    
    lexer4 = Lexer(code4)
    tokens4 = lexer4.tokenize()
    parser4 = Parser(tokens4)
    ast4 = parser4.parse()
    print(f"AST: {ast4}")
    
    # Test 5: Dictionaries
    print("\n[Test 5] Dictionaries")
    print("-" * 60)
    code5 = 'person = {"name": "Ali", "age": 25}'
    print(f"Code: {code5}\n")
    
    lexer5 = Lexer(code5)
    tokens5 = lexer5.tokenize()
    parser5 = Parser(tokens5)
    ast5 = parser5.parse()
    print(f"AST: {ast5}")
    
    # Test 6: List indexing
    print("\n[Test 6] List Indexing")
    print("-" * 60)
    code6 = "x = numbers[0]"
    print(f"Code: {code6}\n")
    
    lexer6 = Lexer(code6)
    tokens6 = lexer6.tokenize()
    parser6 = Parser(tokens6)
    ast6 = parser6.parse()
    print(f"AST: {ast6}")
    
    print("\n" + "=" * 60)
    print("✅ Parser v2.0 tests completed!")
    print("=" * 60)
