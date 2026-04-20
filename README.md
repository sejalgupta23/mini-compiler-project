# mini-compiler-project
Implemented a compiler frontend in Python including tokenization, parsing, AST construction, semantic analysis, and execution. Supports control flow and expressions, showcasing key compiler design principles.

**Working Procedure**
**Step 1:** Lexical Analysis (Lexer)
Input source code is converted into tokens
Tokens include:
Keywords (if, while, print)
Identifiers (x, y)
Operators (+, *, ==)

**Step 2:** Parsing (Syntax Analysis)
Tokens are converted into an Abstract Syntax Tree (AST)
Uses Recursive Descent Parsing

**Step 3:** AST Generation
Tree representation of program structure
Each node represents:
Operations
Variables
Control flow

**Step 4:** Semantic Analysis
Checks:
Undefined variables
Correct usage of expressions

**Step 5:** Interpretation (Execution)
Executes AST step-by-step
Maintains environment (variables)
