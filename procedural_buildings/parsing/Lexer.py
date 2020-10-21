from sly import Lexer as SlyLexer

class Lexer(SlyLexer):
    tokens = {
      IDENT,
      INT,
      PLUS,
      TIMES,
      MINUS,
      DIVIDE,
      ASSIGN,
      COLON,
      ARROW,
      SPLIT,
      REPEAT,
      REPEATN,
      COMP,
      ROTATE,
      RESIZESCOPE,
      TRANSLATE,
      LPAR,
      RPAR,
      LCURL,
      RCURL,
      BAR,
      COMMA,
      COLOUR,
      NEWLINE,
      FLOAT,
      AXIS,
      PRIMITIVE,
      TILDE,
      FACE,
      FACENAME,
      RAND,
      RANDINT,
      PI,
      NIL,
      EQ,
      NEQ,
      GT,
      LT,
      GTE,
      LTE,
    }

    # Tokens
    AXIS = r'[xyz]'
    IDENT = r'[a-zA-Z_][a-zA-Z0-9_]*'
    IDENT['split'] = SPLIT
    IDENT['repeat'] = REPEAT
    IDENT['repeatN'] = REPEATN
    IDENT['comp'] = COMP
    IDENT['colour'] = COLOUR
    IDENT['R'] = ROTATE
    IDENT['S'] = RESIZESCOPE
    IDENT['T'] = TRANSLATE
    IDENT['I'] = PRIMITIVE
    IDENT['f'] = FACE
    IDENT['top'] = FACENAME
    IDENT['bottom'] = FACENAME
    IDENT['front'] = FACENAME
    IDENT['back'] = FACENAME
    IDENT['left'] = FACENAME
    IDENT['right'] = FACENAME
    IDENT['rand'] = RAND
    IDENT['randint'] = RANDINT
    IDENT['pi'] = PI
    IDENT['nil'] = NIL

    # Special symbols
    ARROW = r'-->'
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    EQ = r'=='
    NEQ = r'!='
    GTE = r'>='
    LTE = r'<='
    GT = r'>'
    LT = r'<'
    ASSIGN = r'='
    COLON = r':'
    LPAR = r'\('
    RPAR = r'\)'
    LCURL = r'\{'
    RCURL = r'\}'
    COMMA = r','
    BAR = r'\|'
    TILDE = r'\~'



    # Ignored pattern
    ignore = ' \t'
    ignore_comment = r'\#.*'

    # Extra action for newlines
    @_(r'\n+')
    def NEWLINE(self, t):
        self.lineno += t.value.count('\n')
        return t

    @_(r'\d+\.\d+')
    def FLOAT(self, t):
        t.value = float(t.value)   # Convert to a numeric value
        return t

    @_(r'\d+')
    def INT(self, t):
        t.value = int(t.value)   # Convert to a numeric value
        return t

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1