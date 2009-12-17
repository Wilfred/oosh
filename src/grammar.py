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
tokens = ['PIPE', 'NAMEDPIPE', 'MULTIPIPE', 'VARIABLE', 'PIPEELEMENT',
          'STRING', 'SEMICOLON'] + list(reserved.values())

# regex for simple tokens (do we want case sensitivity?)
t_SEMICOLON = r';'
t_PIPE = r'\|'
t_NAMEDPIPE = r'\|[0-9]+' # e.g. |1 |2 |345
t_MULTIPIPE = r'\|[0-9]+\+[0-9]+' # e.g. |1+2 |2+34
t_VARIABLE = r'\$[a-zA-Z][a-zA-Z0-9]*' # e.g. $x $f00bar
t_PIPEELEMENT = r'\![0-9]+\[[0-9]+\]' # e.g. !345[2] (second element of
                                     # saved pipe 345)

# ignored characters: spaces, tabs and newlines
t_ignore = ' \t\n'

# in the unlikely event of lexing errors:
def t_error(t):
    print("Lexing error from input", t.value[0])
    t.lexer.skip(1)

def t_STRING(t): # any command name or argument
    r'[a-zA-Z0-9.\-/]+'
    t.type = reserved.get(t.value,'STRING') # check for reserved words
    return t


lexer = lex.lex()

# sample input:
sample = """
set y foo; 
for x in a b cde; do set y $x; end; 
if 0; echo yes; echo no; end;
while 1; do echo blah; end;
ls /tmp | select foo |3;
|3+4 union |5
"""

lexer.input(sample)

print(sample)
# tokenise sample
for tok in lexer:
    print(tok)

# // based on fish grammar, only enough to demonstrate pipe structure
# // fish grammar is modified bash grammar, see http://lwn.net/Articles/136232/
# // fish closes most blocks with 'end', cf bash's 'fi' and 'done'
# // no function calls, function definition, case
# // variable assignment differs from fish

# COMMANDS ::= FOR
#          ::= WHILE
#          ::= IF
#          ::= ASSIGN
#          ::= COMMANDS; COMMANDS
#          ::= COMMANDS NAMED_PIPE_OUT
#          ::= COMMAND

# FOR ::= for VAR_NAME in VALUES; COMMANDS; end;

# // while and if use the return value as a conditional, typically
# // from the 'test' command
# WHILE ::= while COMMAND; do COMMANDS; end;
# IF ::= if COMMAND; COMMANDS; end;
#    ::= if COMMAND; COMMANDS; else COMMANDS; end;

# ASSIGN ::= set VAR_NAME VALUE

# // syntax differs substantially here
# // a command may be piped into others
# COMMAND ::= NAMED_PIPE_IN SCOMMAND
#         ::= SCOMMAND
#         ::= MULTI_PIPE_IN MCOMMAND
# 	::= MULTI_PIPE_IN MCOMMAND | SCOMMAND

# // call a command
# SCOMMAND ::= command_name[@HOST] [ ARG ... ]
#          ::= SCOMMAND | SCOMMAND

# MCOMMAND ::= multipipe_command_name[@HOST] [ ARG ...]

# VALUE ::= LITERAL
#       ::= $VAR_NAME
#       ::= !PIPE_ELEMENT //nb could be variety of types

# VAR // will be variables
# LITERAL //whole numbers
# VAR_NAME //any string
