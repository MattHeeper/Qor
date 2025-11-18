"""
QOR Language Parser v1.0
-------------------------
This module implements the syntax analysis phase of the QOR compiler.
It takes tokens from the lexer and builds an Abstract Syntax Tree (AST)
that represents the program structure.

Supported grammar (initial):
- assignment: ID = expression
- expression: term ((PLUS | MINUS) term)*
- term: factor ((MULTIPLY | DIVIDE) factor)*
- factor: NUMBER | ID | (expression)
- print_statement: PRINT(expression)

Author: QOR Development Team
License: MIT
Version: 1.0.0
"""

from typing import List, Tuple, Any, Optional


class ASTNode:
    """
    Base class for all Abstract Syntax Tree nodes.
    
    Each node represents a syntactic construct in the QOR language.
    """
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
        # Remove surrounding quotes
        self.value = value[1:-1]
    
    def __repr__(self):
        return f"String({self.value!r})"


class VariableNode(ASTNode):
    """Represents a variable reference."""
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"Variable({self.name})"


class BinaryOpNode(ASTNode):
    """Represents a binary operation (e.g., addition, subtraction)."""
    def __init__(self, left: ASTNode, operator: str, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


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


class Parser:
    """
    Syntax analyzer for the QOR programming language.
    
    The parser implements a recursive descent parser that builds
    an Abstract Syntax Tree (AST) from a stream of tokens.
    
    Attributes:
        tokens (List[Tuple[str, str]]): List of tokens from lexer
        pos (int): Current position in token list
        current_token (Tuple[str, str]): Current token being processed
    """
    
    def __init__(self, tokens: List[Tuple[str, str]]):
        """
        Initialize parser with tokens.
        
        Args:
            tokens (List[Tuple[str, str]]): Token stream from lexer
        """
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        """Move to the next token in the stream."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def expect(self, token_type: str) -> str:
        """
        Verify current token matches expected type and advance.
        
        Args:
            token_type (str): Expected token type
            
        Returns:
            str: Token value
            
        Raises:
            SyntaxError: If token type doesn't match
        """
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
    
    def parse(self) -> List[ASTNode]:
        """
        Parse the token stream and build AST.
        
        Returns:
            List[ASTNode]: List of statement nodes
        """
        statements = []
        
        while self.current_token is not None:
            # Skip newlines
            if self.current_token[0] == 'NEWLINE':
                self.advance()
                continue
            
            # Parse statement
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def parse_statement(self) -> Optional[ASTNode]:
        """
        Parse a single statement.
        
        Returns:
            ASTNode: Statement node (assignment or print)
        """
        # Print statement
        if self.current_token[0] == 'PRINT':
            return self.parse_print()
        
        # Assignment statement
        elif self.current_token[0] == 'ID':
            # Look ahead to see if it's an assignment
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1][0] == 'ASSIGN':
                return self.parse_assignment()
            else:
                # Just an expression (for future use)
                return self.parse_expression()
        
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")
    
    def parse_print(self) -> PrintNode:
        """
        Parse print statement: print(expression)
        
        Returns:
            PrintNode: Print statement node
        """
        self.expect('PRINT')
        self.expect('LPAREN')
        
        expr = self.parse_expression()
        
        self.expect('RPAREN')
        
        return PrintNode(expr)
    
    def parse_assignment(self) -> AssignmentNode:
        """
        Parse assignment: ID = expression
        
        Returns:
            AssignmentNode: Assignment statement node
        """
        var_name = self.expect('ID')
        self.expect('ASSIGN')
        expr = self.parse_expression()
        
        return AssignmentNode(var_name, expr)
    
    def parse_expression(self) -> ASTNode:
        """
        Parse expression: term ((PLUS | MINUS) term)*
        
        Returns:
            ASTNode: Expression node
        """
        node = self.parse_term()
        
        while (self.current_token and 
               self.current_token[0] in ('PLUS', 'MINUS')):
            operator = self.current_token[1]
            self.advance()
            right = self.parse_term()
            node = BinaryOpNode(node, operator, right)
        
        return node
    
    def parse_term(self) -> ASTNode:
        """
        Parse term: factor ((MULTIPLY | DIVIDE) factor)*
        
        Returns:
            ASTNode: Term node
        """
        node = self.parse_factor()
        
        while (self.current_token and 
               self.current_token[0] in ('MULTIPLY', 'DIVIDE')):
            operator = self.current_token[1]
            self.advance()
            right = self.parse_factor()
            node = BinaryOpNode(node, operator, right)
        
        return node
    
    def parse_factor(self) -> ASTNode:
        """
        Parse factor: NUMBER | STRING | ID | (expression)
        
        Returns:
            ASTNode: Factor node
        """
        token = self.current_token
        
        if token[0] == 'NUMBER':
            self.advance()
            return NumberNode(token[1])
        
        elif token[0] == 'STRING':
            self.advance()
            return StringNode(token[1])
        
        elif token[0] == 'ID':
            self.advance()
            return VariableNode(token[1])
        
        elif token[0] == 'LPAREN':
            self.advance()
            node = self.parse_expression()
            self.expect('RPAREN')
            return node
        
        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")


# Testing
if __name__ == "__main__":
    # We need to import the lexer
    import sys
    sys.path.append('..')
    
    # For testing, we'll create tokens manually
    # In real usage, you'd get these from the Lexer
    
    print("=" * 60)
    print("QOR PARSER v1.0 - TEST SUITE")
    print("=" * 60)
    
    # Test 1: Simple assignment
    print("\n[Test 1] Simple Assignment")
    print("-" * 60)
    tokens1 = [
        ('ID', 'x'),
        ('ASSIGN', '='),
        ('NUMBER', '10'),
    ]
    print(f"Tokens: {tokens1}")
    
    parser1 = Parser(tokens1)
    ast1 = parser1.parse()
    
    print(f"AST: {ast1}")
    
    # Test 2: Arithmetic expression
    print("\n[Test 2] Arithmetic Expression")
    print("-" * 60)
    tokens2 = [
        ('ID', 'x'),
        ('ASSIGN', '='),
        ('NUMBER', '10'),
        ('PLUS', '+'),
        ('NUMBER', '5'),
    ]
    print(f"Tokens: {tokens2}")
    
    parser2 = Parser(tokens2)
    ast2 = parser2.parse()
    
    print(f"AST: {ast2}")
    
    # Test 3: Print statement
    print("\n[Test 3] Print Statement")
    print("-" * 60)
    tokens3 = [
        ('PRINT', 'print'),
        ('LPAREN', '('),
        ('STRING', '"Hello, QOR!"'),
        ('RPAREN', ')'),
    ]
    print(f"Tokens: {tokens3}")
    
    parser3 = Parser(tokens3)
    ast3 = parser3.parse()
    
    print(f"AST: {ast3}")
    
    # Test 4: Complex expression
    print("\n[Test 4] Complex Expression")
    print("-" * 60)
    tokens4 = [
        ('ID', 'result'),
        ('ASSIGN', '='),
        ('NUMBER', '10'),
        ('PLUS', '+'),
        ('NUMBER', '5'),
        ('MULTIPLY', '*'),
        ('NUMBER', '2'),
    ]
    print(f"Tokens: {tokens4}")
    print("Expression: result = 10 + 5 * 2")
    
    parser4 = Parser(tokens4)
    ast4 = parser4.parse()
    
    print(f"AST: {ast4}")
    print("Note: Should respect operator precedence (5*2 first)")
    
    print("\n" + "=" * 60)
    print("✅ All parser tests completed!")
    print("=" * 60)