# mini-compiler-project
Implemented a compiler frontend in Python including tokenization, parsing, AST construction, semantic analysis, and execution. Supports control flow and expressions, showcasing key compiler design principles.

## Working Procedure

### 🔹 Step 1: Lexical Analysis (Lexer)
- Converts source code into tokens
- Handles keywords, identifiers, operators

### 🔹 Step 2: Parsing (Syntax Analysis)
- Converts tokens into AST
- Uses recursive descent parsing

### 🔹 Step 3: AST Generation
- Represents program structure as a tree

### 🔹 Step 4: Semantic Analysis
- Detects undefined variables
- Validates expressions

### 🔹 Step 5: Interpretation
- Executes AST step-by-step
- Maintains variable environment

## How to Run
python main.py

## Features

- Lexical Analysis (Tokenization)
- Recursive Descent Parsing
- Abstract Syntax Tree (AST)
- Semantic Error Checking
- Intermediate Code Generation (IR)
- Interpreter Execution
- Supports loops and conditionals

## Intermediate Representation (IR)

The compiler generates three-address code as an intermediate representation.

### Example Output:
t1 = x * y
t2 = t1 + 2
z = t2
print z

## Tech Stack
- Python
- Compiler Design Concepts
