import ply.yacc as yacc

# we need to know the tokens of our language
from ooshlex import tokens

def p_commands(p):
    '''commands : for
                | while
                | if
                | assign
                | command'''
    p[0] = p[1]

def p_commands_sequence(p):
    'commands : commands SEMICOLON commands'
    p[0] = ('sequence', p[1], p[3])

def p_commands_namedpipe(p):
    'commands : commands NAMEDPIPE'
    p[0] = ('savepipe', p[1], p[2])

def p_commands_empty(p):
    'commands : '
    pass

def p_for(p):
    '''for : FOR STRING IN values SEMICOLON DO commands SEMICOLON END'''
    p[0] = ('for', p[2], p[4], p[7])

def p_while(p):
    '''while : WHILE command SEMICOLON DO commands SEMICOLON END'''
    p[0] = ('while', p[2], p[5])

def p_if(p):
    '''if : IF command SEMICOLON commands SEMICOLON END
          | IF command SEMICOLON commands SEMICOLON ELSE SEMICOLON commands SEMICOLON END'''
    if len(p) == 6:
        p[0] = ('if', p[2], p[4])
    else:
        p[0] = ('if-else', p[2], p[4], p[8])

def p_assign(p):
    'assign : SET STRING value'
    p[0] = ('assign', p[2], p[3])

def p_command_simple(p):
    'command : simplecommand'
    p[0] = p[1]
  
def p_command_namedpipe(p):
    'command : NAMEDPIPE simplecommand'
    p[0] = ('derefpipe', p[1], p[2])

def p_command_multipipe(p):
    '''command : MULTIPIPE multicommand
               | MULTIPIPE multicommand PIPE simplecommand'''
    if len(p) == 3:
        p[0] = ('derefmultipipe', p[1], p[2])
    else:
        p[0] = ('pipedcommand', ('derefmultipipe', p[1], p[2]), p[3])

def p_values(p):
    '''values : value values
              | value'''
    if len(p) == 3:
        p[0] = ('values', p[1], p[2])
    else:
        p[0] = p[1]

def p_value(p):
    '''value : STRING
             | VARIABLE
             | QUOTEDSTRING'''
    if p[1][0] == '$':
        p[0] = ('variable', p[1])
    else:
        p[0] = ('string', p[1])

def p_simplecommand(p):
    '''simplecommand : values
                | simplecommand PIPE simplecommand'''
    if len(p) == 2:
        p[0] = ('simplecommand', p[1])
    else:
        p[0] = ('pipedcommand', p[1], p[3])
    
def p_multicommand(p):
    '''multicommand : values'''
    p[0] = ('muticommand', p[1])

# Error rule for syntax errors
def p_error(p):
    if p is None:
        print("Syntax error: Expected more input")
    else:
        print("Syntax error at", p)

# Build the parser
parser = yacc.yacc()

if __name__ == '__main__':
    sample = """
set y foo; 
for x in a b cde; do set y $x; end; 
if 0; echo yes; else; echo no; end;
while 1; do echo foo; end;
ls /tmp | select foo |3;
|3+4 union |5
"""
    print(sample)
    print(parser.parse(sample))

# based on fish grammar, only enough to demonstrate pipe structure
# fish grammar is modified bash grammar, see http://lwn.net/Articles/136232/
# fish closes most blocks with 'end', cf bash's 'fi' and 'done'
# no function calls, function definition, case

# COMMANDS ::= FOR
#          ::= WHILE
#          ::= IF
#          ::= ASSIGN
#          ::= COMMANDS; COMMANDS
#          ::= COMMANDS NAMED_PIPE_OUT // consider echo hello |1; echo bye
#          ::= COMMAND

# FOR ::= for VAR_NAME in VALUES; COMMANDS; end;

# // while and if use the return value as a conditional, typically
# // from the 'test' command
# WHILE ::= while COMMAND; do COMMANDS; end;
# IF ::= if COMMAND; COMMANDS; end;
#    ::= if COMMAND; COMMANDS; else; COMMANDS; end;

# ASSIGN ::= set VAR_NAME VALUE

# // syntax differs substantially here
# // a command may be piped into others
# COMMAND ::= NAMED_PIPE_IN SIMPLECOMMAND
#         ::= SIMPLECOMMAND
#         ::= MULTI_PIPE_IN MULTICOMMAND
#         ::= MULTI_PIPE_IN MULTICOMMAND | SIMPLECOMMAND

# // call a command
# SIMPLECOMMAND ::= command_name[@HOST] [ ARG ... ]
#          ::= SIMPLECOMMAND | SIMPLECOMMAND

# MULTICOMMAND ::= multipipe_command_name[@HOST] [ ARG ...]

# VALUE ::= LITERAL
#       ::= $VAR_NAME
#       ::= !PIPE_ELEMENT //nb could be variety of types

# VALUES ::= VALUE
#        ::= VALUES VALUE

# VAR // will be variables
# VAR_NAME //any string
