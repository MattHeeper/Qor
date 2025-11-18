#!/usr/bin/env python3
"""
QOR Programming Language - Main Entry Point
--------------------------------------------
Run QOR programs from the command line or interactively.

Usage:
    python qor.py <filename.qor>        # Run a QOR file
    python qor.py --repl                # Start interactive mode
    python qor.py --version             # Show version
    python qor.py --help                # Show help

Author: QOR Development Team
License: MIT
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter


class QORRuntime:
    """Main QOR language runtime."""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize QOR runtime."""
        self.interpreter = Interpreter()
    
    def run_file(self, filename: str) -> None:
        """
        Execute a QOR source file.
        
        Args:
            filename (str): Path to .qor file
        """
        # Check if file exists
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        
        # Check file extension
        if not filename.endswith('.qor'):
            print(f"Warning: File '{filename}' doesn't have .qor extension")
        
        # Read source code
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
        
        # Execute
        self.run_code(code, filename)
    
    def run_code(self, code: str, filename: str = "<stdin>") -> None:
        """
        Execute QOR source code.
        
        Args:
            code (str): QOR source code
            filename (str): Source filename for error reporting
        """
        try:
            # Lexical analysis
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            # Syntax analysis
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Execution
            self.interpreter.interpret(ast)
            
        except SyntaxError as e:
            print(f"Syntax Error in {filename}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Runtime Error in {filename}: {e}")
            sys.exit(1)
    
    def repl(self) -> None:
        """Start interactive REPL (Read-Eval-Print Loop)."""
        print(f"QOR v{self.VERSION} Interactive Shell")
        print("Type 'exit' or 'quit' to exit, 'help' for help")
        print("-" * 50)
        
        while True:
            try:
                # Read
                code = input("qor> ")
                
                # Check for special commands
                if code.strip() in ('exit', 'quit'):
                    print("Goodbye!")
                    break
                
                if code.strip() == 'help':
                    self.show_help()
                    continue
                
                if code.strip() == 'vars':
                    print("Variables:", self.interpreter.variables)
                    continue
                
                if code.strip() == 'clear':
                    self.interpreter.variables.clear()
                    print("Variables cleared")
                    continue
                
                if not code.strip():
                    continue
                
                # Execute
                self.run_code(code, "<repl>")
                
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
                break
            except EOFError:
                print("\nGoodbye!")
                break
    
    def show_help(self) -> None:
        """Show REPL help."""
        print("""
QOR Interactive Shell Commands:
  exit, quit    - Exit the shell
  help          - Show this help message
  vars          - Show all variables
  clear         - Clear all variables
  
Example QOR code:
  x = 10
  y = 20
  result = x + y
  print(result)
  print("Hello, QOR!")
""")
    
    @staticmethod
    def show_version() -> None:
        """Show version information."""
        print(f"QOR Programming Language v{QORRuntime.VERSION}")
        print("Copyright (c) 2024 QOR Development Team")
        print("Licensed under MIT License")
    
    @staticmethod
    def show_usage() -> None:
        """Show usage information."""
        print("""
Usage: python qor.py [options] [file]

Options:
  <file>        Execute a QOR source file
  --repl        Start interactive REPL mode
  --version     Show version information
  --help        Show this help message

Examples:
  python qor.py examples/hello-world.qor    # Run a file
  python qor.py --repl                       # Interactive mode
""")


def main():
    """Main entry point."""
    runtime = QORRuntime()
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # No arguments - show usage
        QORRuntime.show_usage()
        sys.exit(0)
    
    arg = sys.argv[1]
    
    if arg in ('--help', '-h'):
        QORRuntime.show_usage()
    elif arg in ('--version', '-v'):
        QORRuntime.show_version()
    elif arg in ('--repl', '-r'):
        runtime.repl()
    else:
        # Assume it's a filename
        runtime.run_file(arg)


if __name__ == "__main__":
    main()