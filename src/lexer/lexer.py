"""
QOR Language Lexer (Lexical Analyzer) v3.0
-------------------------------------------
This module implements the lexical analysis phase of the QOR compiler.
It converts raw source code into a stream of tokens that can be processed
by the parser.

Version 3.0 adds support for:
- function, return keywords
- if, else, elif keywords
- for, while, in, range keywords
- Comparison operators (==, !=, <, >, <=, >=)
- Logical operators (and, or, not)
- Colon and indentation support

Author: QOR Development Team
License: MIT
Version: 3.0.0
"""

import re
from typing import List, Tuple

# Token type definitions
# Order matters! More specific patterns should come first
TOKEN_TYPES = [
    ('COMMENT',    r'#[^\n]*'),          # Single-line comments
    
    # Keywords (must come before ID)
    ('FUNCTION',   r'function'),         # function keyword
    ('RETURN',     r'return'),           # return keyword
    ('IF',         r'if'),               # if keyword
    ('ELIF',       r'elif'),             # elif keyword
    ('ELSE',       r'else'),             # else keyword
    ('FOR',        r'for'),              # for keyword
    ('WHILE',      r'while'),            # while keyword
    ('IN',         r'in'),               # in keyword
    ('RANGE',      r'range'),            # range keyword
    ('AND',        r'and'),              # logical and
    ('OR',         r'or'),               # logical or
    ('NOT',        r'not'),              # logical not
    ('TRUE',       r'True'),             # boolean true
    ('FALSE',      r'False'),            # boolean false
    ('PRINT',      r'print'),            # print keyword
    
    # Comparison operators (must come before single =)
    ('EQ',         r'=='),               # Equal to
    ('NEQ',        r'!='),               # Not equal to
    ('LEQ',        r'<='),               # Less than or equal
    ('GEQ',        r'>='),               # Greater than or equal
    ('LT',         r'<'),                # Less than
    ('GT',         r'>'),                # Greater than
    
    # Literals
    ('STRING',     r'"[^"]*"'),          # String literals
    ('NUMBER',     r'\d+(\.\d+)?'),      # Integer and float literals
    
    # Operators
    ('PLUS',       r'\+'),               # Addition
    ('MINUS',      r'-'),                # Subtraction
    ('MULTIPLY',   r'\*'),               # Multiplication
    ('DIVIDE',     r'/'),                # Division
    ('MODULO',     r'%'),                # Modulo
    ('POWER',      r'\*\*'),             # Power (must come before MULTIPLY)
    
    # Delimiters
    ('ASSIGN',     r'='),                # Assignment
    ('LPAREN',     r'\('),               # Left parenthesis
    ('RPAREN',     r'\)'),               # Right parenthesis
    ('LBRACKET',   r'\['),               # Left bracket
    ('RBRACKET',   r'\]'),               # Right bracket
    ('COMMA',      r','),                # Comma
    ('COLON',      r':'),                # Colon
    
    # Identifiers
    ('ID',         r'[a-zA-Z_]\w*'),     # Identifiers
    
    # Whitespace
    ('INDENT',     r'^[ \t]+'),          # Indentation at line start
    ('SKIP',       r'[ \t]+'),           # Whitespace (not at line start)
    ('NEWLINE',    r'\n'),               # Line breaks
]


class Lexer:
    """
    Lexical analyzer for the QOR programming language.
    
    The lexer performs tokenization - breaking down source code into
    meaningful chunks (tokens) that represent language elements.
    
    Attributes:
        code (str): The source code to tokenize
        pos (int): Current position in the source code
        tokens (List[Tuple[str, str]]): List of generated tokens
        line (int): Current line number for error reporting
        at_line_start (bool): Whether we're at the start of a line
    """
    
    def __init__(self, code: str):
        """
        Initialize the lexer with source code.
        
        Args:
            code (str): QOR source code to analyze
        """
        self.code = code
        self.pos = 0
        self.tokens = []
        self.line = 1
        self.at_line_start = True
    
    def tokenize(self) -> List[Tuple[str, str]]:
        """
        Convert source code into a list of tokens.
        
        Returns:
            List[Tuple[str, str]]: List of (TOKEN_TYPE, TOKEN_VALUE) tuples
            
        Raises:
            SyntaxError: If an unrecognized character sequence is encountered
        """
        while self.pos < len(self.code):
            match = None
            
            # Try to match each token type pattern
            for token_type, pattern in TOKEN_TYPES:
                # Special handling for INDENT - only at line start
                if token_type == 'INDENT' and not self.at_line_start:
                    continue
                
                regex = re.compile(pattern)
                match = regex.match(self.code, self.pos)
                
                if match:
                    text = match.group(0)
                    
                    # Skip whitespace and comments
                    if token_type not in ('SKIP', 'COMMENT', 'INDENT'):
                        token = (token_type, text)
                        self.tokens.append(token)
                        self.at_line_start = False
                    
                    # Track line numbers and line starts
                    if token_type == 'NEWLINE':
                        self.line += 1
                        self.at_line_start = True
                    
                    # Move position to end of matched text
                    self.pos = match.end()
                    break
            
            # If no pattern matched, we have a syntax error
            if not match:
                raise SyntaxError(
                    f'Unrecognized character at line {self.line}, position {self.pos}: '
                    f'"{self.code[self.pos]}"'
                )
        
        return self.tokens


# Testing
if __name__ == "__main__":
    print("=" * 60)
    print("QOR LEXER v3.0 - ADVANCED FEATURES TEST")
    print("=" * 60)
    
    # Test 1: Function definition
    print("\n[Test 1] Function Definition")
    print("-" * 60)
    test1 = """function add(a, b):
    return a + b"""
    print(f"Source:\n{test1}")
    
    lexer1 = Lexer(test1)
    tokens1 = lexer1.tokenize()
    
    print(f"\nTokens ({len(tokens1)}):")
    for i, (token_type, token_value) in enumerate(tokens1, 1):
        if token_value == '\n':
            print(f"  {i}. {token_type:12} -> '\\n'")
        else:
            print(f"  {i}. {token_type:12} -> {token_value!r}")
    
    # Test 2: If statement
    print("\n[Test 2] If Statement")
    print("-" * 60)
    test2 = """if x > 5:
    print("big")
else:
    print("small")"""
    print(f"Source:\n{test2}")
    
    lexer2 = Lexer(test2)
    tokens2 = lexer2.tokenize()
    
    print(f"\nTokens ({len(tokens2)}):")
    for i, (token_type, token_value) in enumerate(tokens2, 1):
        if token_value == '\n':
            print(f"  {i}. {token_type:12} -> '\\n'")
        else:
            print(f"  {i}. {token_type:12} -> {token_value!r}")
    
    # Test 3: For loop
    print("\n[Test 3] For Loop")
    print("-" * 60)
    test3 = """for i in range(5):
    print(i)"""
    print(f"Source:\n{test3}")
    
    lexer3 = Lexer(test3)
    tokens3 = lexer3.tokenize()
    
    print(f"\nTokens ({len(tokens3)}):")
    for i, (token_type, token_value) in enumerate(tokens3, 1):
        if token_value == '\n':
            print(f"  {i}. {token_type:12} -> '\\n'")
        else:
            print(f"  {i}. {token_type:12} -> {token_value!r}")
    
    # Test 4: Comparison and logical operators
    print("\n[Test 4] Comparisons and Logic")
    print("-" * 60)
    test4 = "if x >= 10 and y != 0:"
    print(f"Source: {test4}")
    
    lexer4 = Lexer(test4)
    tokens4 = lexer4.tokenize()
    
    print(f"\nTokens ({len(tokens4)}):")
    for i, (token_type, token_value) in enumerate(tokens4, 1):
        print(f"  {i}. {token_type:12} -> {token_value!r}")
    
    # Test 5: Math operations
    print("\n[Test 5] Advanced Math")
    print("-" * 60)
    test5 = "result = 2 ** 3 + 10 % 3"
    print(f"Source: {test5}")
    
    lexer5 = Lexer(test5)
    tokens5 = lexer5.tokenize()
    
    print(f"\nTokens ({len(tokens5)}):")
    for i, (token_type, token_value) in enumerate(tokens5, 1):
        print(f"  {i}. {token_type:12} -> {token_value!r}")
    
    print("\n" + "=" * 60)
    print("✅ All lexer v3.0 tests completed!")
    print("=" * 60)