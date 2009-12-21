# sample input:
sample = """
set y foo; 
for x in a b cde; do set y $x; end; 
if 0; echo yes; else; echo no; end;
while 1; do echo !4[0]; end;
ls /tmp | select foo |3;
|3+4 union |5
"""

# now the parsing
import ply.yacc as yacc

# get token map
from lexer import tokens

def p_commands(p):
    '''commands : for
                | while
                | if
                | assign
                | commands SEMICOLON commands
                | commands NAMEDPIPE
                | command
                |'''
    # do nothing

def p_for(p):
    '''for : FOR STRING IN values SEMICOLON DO commands SEMICOLON END'''
    # TODO: repeat command

def p_while(p):
    '''while : WHILE command SEMICOLON DO commands SEMICOLON END'''
    # TODO: repeat command

def p_if(p):
    '''if : IF command SEMICOLON commands SEMICOLON END
          | IF command SEMICOLON commands SEMICOLON ELSE SEMICOLON commands SEMICOLON END'''
    # TODO: implement if-else

def p_assign(p):
    'assign : SET STRING value'
    # TODO: variable assignment

def p_command(p):
    '''command : NAMEDPIPE simplecommand
               | simplecommand
               | MULTIPIPE mcommand
               | MULTIPIPE mcommand PIPE simplecommand'''
    # TODO: command execution

def p_values(p):
    '''values : value values
              | value'''
    
def p_value(p):
    '''value : STRING
             | VARIABLE
             | PIPEELEMENT'''

def p_simplecommand(p):
    '''simplecommand : values
                | simplecommand PIPE simplecommand'''
    # todo: command lookup and execution
    
    
def p_mcommand(p):
    '''mcommand : values'''

# Error rule for syntax errors
def p_error(p):
    if p is None:
        print("Syntax error: Expected more input")
    else:
        print("Syntax error at", p)

# Build the parser
parser = yacc.yacc()

print(sample)

lexer.input(sample)

for tok in lexer:
    print(tok)

result = parser.parse(sample)
print(result)

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
#         ::= MULTI_PIPE_IN MCOMMAND
#         ::= MULTI_PIPE_IN MCOMMAND | SIMPLECOMMAND

# // call a command
# SIMPLECOMMAND ::= command_name[@HOST] [ ARG ... ]
#          ::= SIMPLECOMMAND | SIMPLECOMMAND

# MCOMMAND ::= multipipe_command_name[@HOST] [ ARG ...]

# VALUE ::= LITERAL
#       ::= $VAR_NAME
#       ::= !PIPE_ELEMENT //nb could be variety of types

# VALUES ::= VALUE
#        ::= VALUES VALUE

# VAR // will be variables
# LITERAL //whole numbers
# VAR_NAME //any string

# # abstract syntax tree:
# class Node(object):
#     def eval(self, context):
#         raise NotImplementedError

# class Add(object):
#     def eval(self, context):
#         return self.arg1.eval(context) + self.arg2.eval(context)
# class For(object):
#     def eval(self):
        
# class While(object):
# class If(object):
# class Assign(object):
# class Sequence(object):
# class SavedPipe(object):
# class SimpleCommand(object):
#     def __init__(self):
        
