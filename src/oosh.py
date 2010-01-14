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
        self.saved_pipes = {}
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

    def eval(self, ast, pipe_pointer):
        if ast is None:
            print('Evaluated empty tree')
            return (None, 0)

        if ast[0] == 'sequence':
            (stdout, returncode) = self.eval(ast[1], None)
            self.print_pipe(stdout)
            return self.eval(ast[2], None)

        elif ast[0] == 'savepipe':
            (pipe_out, return_code) = self.eval(ast[1], None)
            pipe_number = ast[2][1:]
            self.saved_pipes[pipe_number] = pipe_out
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
                (dont_care, return_code) = self.eval(ast[1])
                (stdout, final_return_code) = self.eval(ast[2])
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
            pipe_name = ast[1][1:]
            return self.eval(ast[2], self.saved_pipes[pipe_name])

        elif ast[0] == 'simplecommand':
            try:
                process = self.base_command(ast, pipe_pointer)
                process.wait()
                return (process.stdout, process.returncode)
            except OSError:
                command_name = ast[1][1]
                print("No such command:",command_name)
                raise OSError

        elif ast[0] == 'derefmultipipe':
            # call command, appending argument of second pipe
            pipe_names = ast[1][1:].split('+')
            second_pipe_pointer = self.saved_pipes[pipe_names[1]]
            command = self.flatten_tree(ast[2][1])
            command += ' ' + str(second_pipe_pointer.fileno())
            process = Popen(command,
                            stdin=self.saved_pipes[pipe_names[0]],
                            stdout=subprocess.PIPE)
            return (process.stdout, process.returncode)

        elif ast[0] == 'pipedcommand':
            (stdout, return_code) = self.eval(ast[1], pipe_pointer)
            return self.eval(ast[2], stdout)

        elif ast[0] is None: # occurs with trailing ;
            pass

        else:
            raise UnknownTreeException

    def base_command(self, tree, stdin):
        command = self.flatten_tree(tree[1])
        command_name = command[0]
        if command_name == 'exit':
            sys.exit()
        if not re.match('oosh_*', command_name) is None:
            if command_name == 'oosh_graph':
                # graph uses pycairo, which is not py3k compatible
                command = ['python'] + [command_name + '.py'] + command[1:]
            else:
                command = ['python3'] + [command_name + '.py'] + command[1:]
        process = Popen(command, stdin=stdin, stdout=subprocess.PIPE)
        return process

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
