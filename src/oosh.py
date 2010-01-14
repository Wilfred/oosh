#!/usr/bin/python3

# default python interpreter facilities
# source is in /usr/lib/python3.1/cmd.py
from cmd import Cmd
import readline # use the python history facilities
import re # regular expressions
import sys

from ooshparse import parser

from subprocess import Popen # spawn processes
import subprocess

class Oosh(Cmd):
    def __init__(self):
        Cmd.__init__(self)
        self.saved_pipe_data = {}
        self.variables = {}

    def onecmd(self, line):
        if line.strip(' \t\n') == '':
            return
        ast = parser.parse(line)
        print("AST: ", ast)
        try:
            (stdout, return_code) = self.eval(ast, None)
            self.print_pipe(stdout)
        except OSError:
            return

    def print_pipe(self, pipe_pointer):
        # read and decode binary data in stdout
        if not pipe_pointer is None:
            content = pipe_pointer.read().decode()
            if len(content) > 0 and content[0] == '{': 
                # data conforms to oosh structure
                self.pretty_print(content)
            else:
                print(content)

    def pretty_print(self, content):
        string_lines = content.splitlines()
        lines = []
        for line in string_lines:
            if not line == '':
                lines.append(eval(line))

        header = []
        for line in lines:
            for key in line.keys():
                if key not in header:
                    header.append(key)

        # get optimum width:
        column_widths = {}
        for string in header:
            column_widths[string] = (len(string))
        for line in lines:
            for key in header:
                try:
                    value = str(line[key])
                    if len(value) > column_widths[key]:
                        column_widths[key] = len(value)
                except KeyError:
                    pass

        # print header
        header_text = ''
        for key in header:
            # print string plus requisite number of spaces
            header_text += key + ' '*(column_widths[key]-len(key)+1)
        print(header_text)
            
        for line in lines:
            line_text = ''
            for key in header:
                datum = str(line[key])
                line_text += datum + ' '*(column_widths[key]-len(datum)+1)
            print(line_text)

    def eval(self, ast, pipe_pointer, start_data=None):
        # recurse down tree, starting processes and passing pointers
        # of pipes created as appopriate. We also pass start_data to
        # simplecommand, sequence and pipedcommand from pipe dereferencing
        
        if ast is None:
            print('Evaluated empty tree')
            return (None, 0)

        if ast[0] == 'sequence':
            (stdout, returncode) = self.eval(ast[1], None, start_data)
            self.print_pipe(stdout)
            return self.eval(ast[2], None)

        elif ast[0] == 'savepipe':
            (pipe_out, return_code) = self.eval(ast[1], None, start_data)
            pipe_number = ast[2][1:]
            self.saved_pipe_data[pipe_number] = pipe_out.read()
            return (None, return_code)

        elif ast[0] == 'for':
            old_variables = self.variables.copy()
            for value in self.flatten_tree(ast[2]):
                self.variables[ast[1]] = value
                (stdout, return_code) = self.eval(ast[3], None)
                self.print_pipe(stdout)
            self.variables = old_variables
            return (None, return_code)

        elif ast[0] == 'while':
            while return_code == 0:
                (dont_care, return_code) = self.eval(ast[1], None)
                (stdout, final_return_code) = self.eval(ast[2], None)
                self.print_pipe(stdout)
            return (None, final_return_code)

        elif ast[0] == 'if':
            if self.eval(ast[1], None) == 0: # 0 is true for shells
                return self.eval(ast[2], None)
            else:
                return (None, 0)

        elif ast[0] == 'if-else':
            if self.eval(ast[1], None) == 0:
                return self.eval(ast[2], None)
            else:
                return self.eval(ast[3], None)

        elif ast[0] == 'assign':
            self.variables[ast[1]] = self.flatten_tree(ast[2])[0]
            return (None, 0)

        elif ast[0] == 'derefpipe':
            old_pipe_name = ast[1][1:] # e.g. |2
            old_pipe_data = self.saved_pipe_data[old_pipe_name]
            return self.eval(ast[2], subprocess.PIPE, old_pipe_data)

        elif ast[0] == 'simplecommand':
            process = self.base_command(ast, pipe_pointer)
            if not start_data is None:
                process.stdin.write(start_data)
                process.stdin.close()
            process.wait()
            return (process.stdout, process.returncode)

        elif ast[0] == 'derefmultipipe':
            # this is not nice code, we use cat just to create a new
            # pipe (cf 'useless use of cat')
            
            pipe_names = ast[1][1:].split('+')

            first_pipe_data = self.saved_pipe_data[pipe_names[0]]
            first_process = Popen('cat', stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)
            first_process.stdin.write(first_pipe_data)
            first_process.stdin.close()

            second_pipe_data = self.saved_pipe_data[pipe_names[1]]
            second_process = Popen('cat', stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
            second_process.stdin.write(second_pipe_data)
            second_process.stdin.close()

            # we call command, appending argument of second pipe
            command = self.flatten_tree(ast[2][1])
            command += ' ' + str(second_process.stdout.fileno())
            
            process = self.shell_command(' '.join(command),
                                         first_process.stdout)
            process.wait()
            return (process.stdout, process.returncode)

        elif ast[0] == 'pipedcommand':
            (stdout, return_code) = self.eval(ast[1], pipe_pointer, start_data)
            return self.eval(ast[2], stdout)

        elif ast[0] is None: # occurs with trailing ;
            pass

        else:
            raise UnknownTreeException

    def base_command(self, tree, stdin):
        command = ' '.join(self.flatten_tree(tree[1]))
        return self.shell_command(command, stdin)

    def shell_command(self, command_string, stdin):
        command = command_string.split(' ')
        command_name = command[0]
        if command_name == 'exit':
            sys.exit()
        if not re.match('oosh_*', command_name) is None:
            if command_name == 'oosh_graph':
                # graph uses pycairo, which is not py3k compatible
                command = ['python'] + [command_name + '.py'] + command[1:]
            else:
                command = ['python3'] + [command_name + '.py'] + command[1:]
        try:
            process = Popen(command, stdin=stdin, stdout=subprocess.PIPE)
            return process
        except OSError:
            print("No such command: ", command_name)
            raise OSError

    def flatten_tree(self, tree):
        # return a list of strings from a tree
        # handles string, values, variable trees
        if tree[0] == 'string':
            return [tree[1]]
        elif tree[0] == 'values':
            return self.flatten_tree(tree[1])+self.flatten_tree(tree[2])
        elif tree[0] == 'variable':
            return [self.variables[tree[1][1:]]]
        else:
            raise InvalidTreeException

# an object stream is made of droplets
class Droplet:
    def __init__(self, value):
        if isinstance(value, str):
            self.entries = parse(value)
        elif isinstance(value, list):
            self.entries = dict(value)
        elif isinstance(value, dict):
            self.entries = value
        else:
            raise TypeError
    def __eq__(self, other):
        return self.entries == other.entries
    def __repr__(self):
        return self.entries.__repr__()

# helper functions:
def parse(ooshstring):
    # values always take the form "name":"value", tolerating
    # newlines but we escape ""
    keyandvalue = re.findall('".*?":".*?"', ooshstring,
                             flags=re.DOTALL)
    # strip leading and trailng "
    stripped = [s[1:][:-1] for s in keyandvalue]
     # separate into column name, value pairs
    pairs = [s.split('":"') for s in stripped]
    return dict(pairs)

if __name__=='__main__':
    oosh = Oosh()
    oosh.prompt = "$ "
    oosh.cmdloop("Welcome to oosh.")
