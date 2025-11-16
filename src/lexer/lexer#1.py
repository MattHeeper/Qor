"""
QOR Language Lexer (Lexical Analyzer)
--------------------------------------
This module implements the lexical analysis phase of the QOR compiler.
It converts raw source code into a stream of tokens that can be processed
by the parser.

Author: QOR Development Team
License: MIT
Version: 1.0.0
"""

import re
from typing import List, Tuple

# Token type definitions
# Each tuple contains (TOKEN_NAME, REGEX_PATTERN)
TOKEN_TYPES = [
    ('NUMBER',   r'\d+'),              # Integer literals (e.g., 42, 123)
    ('PLUS',     r'\+'),               # Addition operator
    ('MINUS',    r'-'),                # Subtraction operator
    ('MULTIPLY', r'\*'),               # Multiplication operator
    ('DIVIDE',   r'/'),                # Division operator
    ('ASSIGN',   r'='),                # Assignment operator
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
            >>> lexer = Lexer("x = 10")
            >>> tokens = lexer.tokenize()
            >>> print(tokens)
            [('ID', 'x'), ('ASSIGN', '='), ('NUMBER', '10')]
        """
        while self.pos < len(self.code):
            match = None
            
            # Try to match each token type pattern
            for token_type, pattern in TOKEN_TYPES:
                regex = re.compile(pattern)
                match = regex.match(self.code, self.pos)
                
                if match:
                    text = match.group(0)
                    
                    # Skip whitespace tokens (don't add to token list)
                    if token_type != 'SKIP':
                        token = (token_type, text)
                        self.tokens.append(token)
                    
                    # Move position to end of matched text
                    self.pos = match.end()
                    break
            
            # If no pattern matched, we have a syntax error
            if not match:
                raise SyntaxError(
                    f'Unrecognized character at position {self.pos}: '
                    f'"{self.code[self.pos]}"'
                )
        
        return self.tokens


# Example usage and testing
if __name__ == "__main__":
    # Test case 1: Simple assignment with arithmetic
    test_code = "x = 10 + 5"
    
    print("QOR Lexer Test")
    print("=" * 50)
    print(f"Source code: {test_code}")
    print("-" * 50)
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    print("Generated tokens:")
    for token_type, token_value in tokens:
        print(f"  {token_type:12} -> '{token_value}'")
    
    print("=" * 50)
    print("Lexer test completed successfully!")