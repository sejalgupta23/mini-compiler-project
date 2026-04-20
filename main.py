"""
Mini Compiler Front-End in Python
===================================
Pipeline: Source Code → Lexer (Tokens) → Parser → AST → Semantic Checker
Supports: arithmetic expressions, variables, if/else, while loops, print
"""
 
import re
from dataclasses import dataclass, field
from typing import List, Optional, Any
 

# 1. TOKEN DEFINITIONS
 
TOKEN_SPEC = [
    ('NUMBER',   r'\d+(\.\d*)?'),
    ('STRING',   r'"[^"]*"'),
    ('IF',       r'\bif\b'),
    ('ELSE',     r'\belse\b'),
    ('WHILE',    r'\bwhile\b'),
    ('PRINT',    r'\bprint\b'),
    ('TRUE',     r'\bTrue\b'),
    ('FALSE',    r'\bFalse\b'),
    ('ID',       r'[A-Za-z_]\w*'),
    ('OP',       r'==|!=|<=|>=|[+\-*/=<>]'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('SEMI',     r';'),
    ('COMMA',    r','),
    ('SKIP',     r'[ \t\n]+'),
    ('MISMATCH', r'.'),
]
 
@dataclass
class Token:
    type: str
    value: str
    line: int
 
 
# 2. LEXER
 
class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.pattern = re.compile(
            '|'.join(f'(?P<{name}>{regex})' for name, regex in TOKEN_SPEC)
        )
 
    def tokenize(self) -> List[Token]:
        line = 1
        for mo in self.pattern.finditer(self.source):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP':
                line += value.count('\n')
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Unexpected character {value!r} at line {line}")
            self.tokens.append(Token(kind, value, line))
        return self.tokens
 
 
# 3. AST NODE DEFINITIONS
 
@dataclass
class NumberNode:
    value: float
 
@dataclass
class StringNode:
    value: str
 
@dataclass
class BoolNode:
    value: bool
 
@dataclass
class VarNode:
    name: str
 
@dataclass
class BinOpNode:
    op: str
    left: Any
    right: Any
 
@dataclass
class AssignNode:
    name: str
    value: Any
 
@dataclass
class IfNode:
    condition: Any
    then_body: List[Any]
    else_body: List[Any]
 
@dataclass
class WhileNode:
    condition: Any
    body: List[Any]
 
@dataclass
class PrintNode:
    value: Any
 
@dataclass
class ProgramNode:
    statements: List[Any]
 
 
# 4. PARSER  (Recursive Descent)
 
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
 
    def peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
 
    def consume(self, expected_type: str = None) -> Token:
        tok = self.peek()
        if tok is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type and tok.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {tok.type} ({tok.value!r}) at line {tok.line}")
        self.pos += 1
        return tok
 
    def parse(self) -> ProgramNode:
        stmts = []
        while self.peek():
            stmts.append(self.parse_statement())
        return ProgramNode(stmts)
 
    def parse_statement(self) -> Any:
        tok = self.peek()
        if tok.type == 'IF':
            return self.parse_if()
        elif tok.type == 'WHILE':
            return self.parse_while()
        elif tok.type == 'PRINT':
            return self.parse_print()
        elif tok.type == 'ID' and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].value == '=':
            return self.parse_assign()
        else:
            expr = self.parse_expr()
            if self.peek() and self.peek().type == 'SEMI':
                self.consume('SEMI')
            return expr
 
    def parse_assign(self) -> AssignNode:
        name = self.consume('ID').value
        self.consume('OP')  # '='
        value = self.parse_expr()
        if self.peek() and self.peek().type == 'SEMI':
            self.consume('SEMI')
        return AssignNode(name, value)
 
    def parse_if(self) -> IfNode:
        self.consume('IF')
        self.consume('LPAREN')
        condition = self.parse_expr()
        self.consume('RPAREN')
        then_body = self.parse_block()
        else_body = []
        if self.peek() and self.peek().type == 'ELSE':
            self.consume('ELSE')
            else_body = self.parse_block()
        return IfNode(condition, then_body, else_body)
 
    def parse_while(self) -> WhileNode:
        self.consume('WHILE')
        self.consume('LPAREN')
        condition = self.parse_expr()
        self.consume('RPAREN')
        body = self.parse_block()
        return WhileNode(condition, body)
 
    def parse_print(self) -> PrintNode:
        self.consume('PRINT')
        self.consume('LPAREN')
        value = self.parse_expr()
        self.consume('RPAREN')
        if self.peek() and self.peek().type == 'SEMI':
            self.consume('SEMI')
        return PrintNode(value)
 
    def parse_block(self) -> List[Any]:
        self.consume('LBRACE')
        stmts = []
        while self.peek() and self.peek().type != 'RBRACE':
            stmts.append(self.parse_statement())
        self.consume('RBRACE')
        return stmts
 
    def parse_expr(self) -> Any:
        return self.parse_comparison()
 
    def parse_comparison(self) -> Any:
        left = self.parse_additive()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('==', '!=', '<', '>', '<=', '>='):
            op = self.consume('OP').value
            right = self.parse_additive()
            left = BinOpNode(op, left, right)
        return left
 
    def parse_additive(self) -> Any:
        left = self.parse_multiplicative()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('+', '-'):
            op = self.consume('OP').value
            right = self.parse_multiplicative()
            left = BinOpNode(op, left, right)
        return left
 
    def parse_multiplicative(self) -> Any:
        left = self.parse_primary()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('*', '/'):
            op = self.consume('OP').value
            right = self.parse_primary()
            left = BinOpNode(op, left, right)
        return left
 
    def parse_primary(self) -> Any:
        tok = self.peek()
        if tok is None:
            raise SyntaxError("Unexpected end of expression")
        if tok.type == 'NUMBER':
            self.consume()
            return NumberNode(float(tok.value))
        elif tok.type == 'STRING':
            self.consume()
            return StringNode(tok.value[1:-1])
        elif tok.type == 'TRUE':
            self.consume()
            return BoolNode(True)
        elif tok.type == 'FALSE':
            self.consume()
            return BoolNode(False)
        elif tok.type == 'ID':
            self.consume()
            return VarNode(tok.value)
        elif tok.type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expr()
            self.consume('RPAREN')
            return expr
        else:
            raise SyntaxError(f"Unexpected token {tok.value!r} at line {tok.line}")
 
 
# 5. AST PRINTER

class ASTPrinter:
    def print(self, node, indent=0):
        pad = "  " * indent
        if isinstance(node, ProgramNode):
            print(f"{pad}Program")
            for s in node.statements:
                self.print(s, indent + 1)
        elif isinstance(node, AssignNode):
            print(f"{pad}Assign: {node.name}")
            self.print(node.value, indent + 1)
        elif isinstance(node, BinOpNode):
            print(f"{pad}BinOp: {node.op}")
            self.print(node.left, indent + 1)
            self.print(node.right, indent + 1)
        elif isinstance(node, IfNode):
            print(f"{pad}If")
            print(f"{pad}  Condition:")
            self.print(node.condition, indent + 2)
            print(f"{pad}  Then:")
            for s in node.then_body:
                self.print(s, indent + 2)
            if node.else_body:
                print(f"{pad}  Else:")
                for s in node.else_body:
                    self.print(s, indent + 2)
        elif isinstance(node, WhileNode):
            print(f"{pad}While")
            print(f"{pad}  Condition:")
            self.print(node.condition, indent + 2)
            print(f"{pad}  Body:")
            for s in node.body:
                self.print(s, indent + 2)
        elif isinstance(node, PrintNode):
            print(f"{pad}Print")
            self.print(node.value, indent + 1)
        elif isinstance(node, NumberNode):
            print(f"{pad}Number({node.value})")
        elif isinstance(node, StringNode):
            print(f"{pad}String({node.value!r})")
        elif isinstance(node, BoolNode):
            print(f"{pad}Bool({node.value})")
        elif isinstance(node, VarNode):
            print(f"{pad}Var({node.name})")
        else:
            print(f"{pad}{node}")
 
 
# 6. SEMANTIC CHECKER
 
class SemanticChecker:
    def __init__(self):
        self.symbol_table = {}
        self.errors = []
 
    def check(self, node):
        if isinstance(node, ProgramNode):
            for s in node.statements:
                self.check(s)
        elif isinstance(node, AssignNode):
            self.check(node.value)
            self.symbol_table[node.name] = True
        elif isinstance(node, VarNode):
            if node.name not in self.symbol_table:
                self.errors.append(f"Undefined variable: '{node.name}'")
        elif isinstance(node, BinOpNode):
            self.check(node.left)
            self.check(node.right)
        elif isinstance(node, IfNode):
            self.check(node.condition)
            for s in node.then_body:
                self.check(s)
            for s in node.else_body:
                self.check(s)
        elif isinstance(node, WhileNode):
            self.check(node.condition)
            for s in node.body:
                self.check(s)
        elif isinstance(node, PrintNode):
            self.check(node.value)
 
    def report(self):
        if self.errors:
            print("\n[Semantic Errors]")
            for e in self.errors:
                print(f"  ✗ {e}")
        else:
            print("\n[Semantic Check] ✓ No errors found.")
        return len(self.errors) == 0
 
 
# 7. INTERPRETER (Executes the AST)

class Interpreter:
    def __init__(self):
        self.env = {}
 
    def run(self, node):
        if isinstance(node, ProgramNode):
            for s in node.statements:
                self.run(s)
        elif isinstance(node, AssignNode):
            self.env[node.name] = self.eval(node.value)
        elif isinstance(node, PrintNode):
            print(self.eval(node.value))
        elif isinstance(node, IfNode):
            if self.eval(node.condition):
                for s in node.then_body:
                    self.run(s)
            else:
                for s in node.else_body:
                    self.run(s)
        elif isinstance(node, WhileNode):
            while self.eval(node.condition):
                for s in node.body:
                    self.run(s)
        else:
            self.eval(node)
 
    def eval(self, node):
        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, BoolNode):
            return node.value
        elif isinstance(node, VarNode):
            if node.name not in self.env:
                raise RuntimeError(f"Undefined variable: '{node.name}'")
            return self.env[node.name]
        elif isinstance(node, BinOpNode):
            l, r = self.eval(node.left), self.eval(node.right)
            ops = {'+': lambda a,b: a+b, '-': lambda a,b: a-b,
                   '*': lambda a,b: a*b, '/': lambda a,b: a/b,
                   '==': lambda a,b: a==b, '!=': lambda a,b: a!=b,
                   '<': lambda a,b: a<b,  '>': lambda a,b: a>b,
                   '<=': lambda a,b: a<=b,'>=': lambda a,b: a>=b}
            return ops[node.op](l, r)
        raise RuntimeError(f"Unknown node: {type(node)}")
 

# 8. INTERMEDIATE REPRESENTATION (IR)

class IRGenerator:
    def __init__(self):
        self.temp_count = 0
        self.code = []

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def generate(self, node):
        if isinstance(node, NumberNode):
            return node.value

        elif isinstance(node, VarNode):
            return node.name

        elif isinstance(node, BinOpNode):
            left = self.generate(node.left)
            right = self.generate(node.right)
            temp = self.new_temp()
            self.code.append(f"{temp} = {left} {node.op} {right}")
            return temp

        elif isinstance(node, AssignNode):
            value = self.generate(node.value)
            self.code.append(f"{node.name} = {value}")

        elif isinstance(node, PrintNode):
            value = self.generate(node.value)
            self.code.append(f"print {value}")

    def print_ir(self):
        print("\n" + "=" * 50)
        print("STAGE 3: INTERMEDIATE CODE (IR)")
        print("=" * 50)
        for line in self.code:
            print(line)


# 9. MAIN — Run the full pipeline

SOURCE = """
x = 10;
y = 3;
z = x * y + 2;
print(z);
 
if (z > 30) {
    print("z is large");
} else {
    print("z is small");
}
 
i = 0;
while (i < 4) {
    print(i);
    i = i + 1;
}
"""
 
if __name__ == "__main__":
    print("=" * 50)
    print("STAGE 1: LEXER")
    print("=" * 50)
    lexer = Lexer(SOURCE)
    tokens = lexer.tokenize()
    for tok in tokens:
        print(f"  {tok.type:10s} {tok.value!r}")
 
    print("\n" + "=" * 50)
    print("STAGE 2: PARSER → AST")
    print("=" * 50)
    parser = Parser(tokens)
    ast = parser.parse()
    ASTPrinter().print(ast)

    # IR GENERATION
    ir = IRGenerator()
    for stmt in ast.statements:
        ir.generate(stmt)

    ir.print_ir()
 
    print("\n" + "=" * 50)
    print("STAGE 4: SEMANTIC CHECK")
    print("=" * 50)
    checker = SemanticChecker()
    checker.check(ast)
    checker.report()
 
    print("\n" + "=" * 50)
    print("STAGE 5: EXECUTION (Interpreter)")
    print("=" * 50)
    Interpreter().run(ast)
    