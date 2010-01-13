import ply.lex as lex

# reserved words
reserved = {
   'for' : 'FOR',
   'in' : 'IN',
   'end' : 'END',
   'while' : 'WHILE',
   'do' : 'DO',
   'if' : 'IF',
   'else' : 'ELSE',
   'set' : 'SET',
}

# remaining token names
tokens = ['PIPE', 'NAMEDPIPE', 'MULTIPIPE', 'VARIABLE',
          'STRING', 'QUOTEDSTRING', 'SEMICOLON'] + list(reserved.values())

# regex for simple tokens (do we want case sensitivity?)
t_SEMICOLON = r';'
t_PIPE = r'\|'
t_NAMEDPIPE = r'\|[0-9]+' # e.g. |1 |2 |345
t_MULTIPIPE = r'\|[0-9]+\+[0-9]+' # e.g. |1+2 |2+34
t_VARIABLE = r'\$[a-zA-Z][a-zA-Z0-9]*' # e.g. $x $f00bar

# ignored characters: spaces, tabs and newlines
t_ignore = ' \t\n'

# in the unlikely event of lexing errors:
def t_error(t):
    print("Lexing error from input", t.value[0])
    t.lexer.skip(1)

def t_STRING(t): # any command name or argument
    r'[a-zA-Z0-9.\-/_]+'
    t.type = reserved.get(t.value,'STRING') # check for reserved words
    return t
def t_QUOTEDSTRING(t): # any argument of the form 'xyz % !'
    r'\'[a-zA-Z0-9 !%]*?\''
    t.value = t.value[1:-1] # strip leading and trailing '
    return t

lexer = lex.lex()
