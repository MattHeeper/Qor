"""
QOR Language Lexer (Lexical Analyzer) v2.0
-------------------------------------------
This module implements the lexical analysis phase of the QOR compiler.
It converts raw source code into a stream of tokens that can be processed
by the parser.

Version 2.0 adds support for:
- print keyword
- String literals
- Parentheses for function calls
- Comments support

Author: QOR Development Team
License: MIT
Version: 2.0.0
"""

import re
from typing import List, Tuple

# Token type definitions
# Each tuple contains (TOKEN_NAME, REGEX_PATTERN)
# Order matters! More specific patterns should come first
TOKEN_TYPES = [
    ('COMMENT',  r'#[^\n]*'),          # Single-line comments (e.g., # this is a comment)
    ('PRINT',    r'print'),            # print keyword - must come before ID
    ('STRING',   r'"[^"]*"'),          # String literals (e.g., "hello world")
    ('NUMBER',   r'\d+(\.\d+)?'),      # Integer and float literals (e.g., 42, 3.14)
    ('PLUS',     r'\+'),               # Addition operator
    ('MINUS',    r'-'),                # Subtraction operator
    ('MULTIPLY', r'\*'),               # Multiplication operator
    ('DIVIDE',   r'/'),                # Division operator
    ('ASSIGN',   r'='),                # Assignment operator
    ('LPAREN',   r'\('),               # Left parenthesis
    ('RPAREN',   r'\)'),               # Right parenthesis
    ('COMMA',    r','),                # Comma separator
    ('ID',       r'[a-zA-Z_]\w*'),     # Identifiers (variable names, keywords)
    ('SKIP',     r'[ \t]+'),           # Whitespace (spaces and tabs) - ignored
    ('NEWLINE',  r'\n'),               # Line breaks
]


class Lexer:
    """
    Lexical analyzer for the QOR programming language.
    
    The lexer performs tokenization - breaking down source code into
    meaningful chunks (tokens) that represent language elements like
    numbers, operators, and identifiers.
    
    Attributes:
        code (str): The source code to tokenize
        pos (int): Current position in the source code
        tokens (List[Tuple[str, str]]): List of generated tokens
        line (int): Current line number for error reporting
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
    
    def tokenize(self) -> List[Tuple[str, str]]:
        """
        Convert source code into a list of tokens.
        
        This method iterates through the source code character by character,
        matching patterns against the defined token types. When a match is found,
        it creates a token and advances the position.
        
        Returns:
            List[Tuple[str, str]]: List of (TOKEN_TYPE, TOKEN_VALUE) tuples
            
        Raises:
            SyntaxError: If an unrecognized character sequence is encountered
            
        Example:
            >>> lexer = Lexer('print("Hello")')
            >>> tokens = lexer.tokenize()
            >>> print(tokens)
            [('PRINT', 'print'), ('LPAREN', '('), ('STRING', '"Hello"'), ('RPAREN', ')')]
        """
        while self.pos < len(self.code):
            match = None
            
            # Try to match each token type pattern
            for token_type, pattern in TOKEN_TYPES:
                regex = re.compile(pattern)
                match = regex.match(self.code, self.pos)
                
                if match:
                    text = match.group(0)
                    
                    # Skip whitespace and comments (don't add to token list)
                    if token_type not in ('SKIP', 'COMMENT'):
                        token = (token_type, text)
                        self.tokens.append(token)
                    
                    # Track line numbers for error reporting
                    if token_type == 'NEWLINE':
                        self.line += 1
                    
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


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("QOR LEXER v2.0 - TEST SUITE")
    print("=" * 60)
    
    # Test case 1: Hello World with print
    print("\n[Test 1] Hello World")
    print("-" * 60)
    test1 = 'print("Hello, QOR!")'
    print(f"Source: {test1}")
    
    lexer1 = Lexer(test1)
    tokens1 = lexer1.tokenize()
    
    print(f"Tokens ({len(tokens1)}):")
    for i, (token_type, token_value) in enumerate(tokens1, 1):
        print(f"  {i}. {token_type:12} -> {token_value!r}")
    
    # Test case 2: Variable assignment with arithmetic
    print("\n[Test 2] Arithmetic Operations")
    print("-" * 60)
    test2 = "x = 10 + 5"
    print(f"Source: {test2}")
    
    lexer2 = Lexer(test2)
    tokens2 = lexer2.tokenize()
    
    print(f"Tokens ({len(tokens2)}):")
    for i, (token_type, token_value) in enumerate(tokens2, 1):
        print(f"  {i}. {token_type:12} -> {token_value!r}")
    
    # Test case 3: Multi-line with print
    print("\n[Test 3] Multi-line Program")
    print("-" * 60)
    test3 = """# Calculate sum
x = 10
y = 20
result = x + y
print("Result:")
print(result)"""
    print(f"Source:\n{test3}")
    
    lexer3 = Lexer(test3)
    tokens3 = lexer3.tokenize()
    
    print(f"\nTokens ({len(tokens3)}):")
    for i, (token_type, token_value) in enumerate(tokens3, 1):
        if token_value == '\n':
            print(f"  {i}. {token_type:12} -> '\\n'")
        else:
            print(f"  {i}. {token_type:12} -> {token_value!r}")
    
    # Test case 4: Float numbers
    print("\n[Test 4] Float Numbers")
    print("-" * 60)
    test4 = "pi = 3.14159"
    print(f"Source: {test4}")
    
    lexer4 = Lexer(test4)
    tokens4 = lexer4.tokenize()
    
    print(f"Tokens ({len(tokens4)}):")
    for i, (token_type, token_value) in enumerate(tokens4, 1):
        print(f"  {i}. {token_type:12} -> {token_value!r}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)