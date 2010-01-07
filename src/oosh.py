#!/Usr/bin/python3

# default python interpreter facilities
# source is in /usr/lib/python3.1/cmd.py
from cmd import Cmd
# use the python history facilities
# we will modify this later for object caching alongside
import readline
# regular expressionsp
import re
import copy

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
        print("Input: ", line)
        ast = parser.parse(line)
        print("AST: ", ast)
        self.eval(ast)

    def eval(self, ast):
        if ast is None:
            print('Evaluated empty tree')
            return (None, 0)

        return_code = 0
        # sadly no case or pattern matching in python
        if ast[0] == 'sequence':
            self.eval(ast[1])
            return self.eval(ast[2])
        elif ast[0] == 'savepipe':
            (stdout, return_code) = self.eval(ast[1])
            pipe_number = ast[2][1:]
            self.saved_pipes[pipe_number] = stdout
            return (None, return_code)
        elif ast[0] == 'for':
            old_variables = self.variables.copy()
            for value in self.flatten_tree(ast[2]):
                self.variables[ast[1]] = value
                (stdout, return_code) = self.eval(ast[3])
            self.variables = old_variables
            return (None, return_code)
        elif ast[0] == 'while':
            while return_code == 0:
                (stdout, return_code) = self.eval(ast[1])
                self.eval(ast[2])
            return (None, return_code)
        elif ast[0] == 'if':
            if self.eval(ast[1]) == 0: # 0 is true for shells
                return self.eval(ast[2])
            else:
                return 0
        elif ast[0] == 'if-else':
            if self.eval(ast[1]) == 0:
                return self.eval(ast[2])
            else:
                return self.eval(ast[3])
        elif ast[0] == 'assign':
            self.variables[ast[1]] = self.flatten_tree(ast[2])[0]
            return (None, 0)
        elif ast[0] == 'derefpipe':
            pass
        elif ast[0] == 'multicommand':
            pass
        elif ast[0] == 'simplecommand':
            process = self.base_command(ast, None)
            process.wait()
            return_code = process.return_code
            stdout = process.stdout.read()
            print(stdout.decode()) # decode binary data
            return (stdout, return_code)
        elif ast[0] == 'derefmultipipe':
            pass
        elif ast[0] == 'pipedcommand':
            running_processes = []

            treepointer = ast
            firsttime = True
            # we have a tree of simple commands to evaluate
            while treepointer[0] == 'pipedcommand':
                if firsttime:
                    process = self.base_command(treepointer[1], None)
                else:
                    process = self.base_command(treepointer[1], process.stdout)
                treepointer = treepointer[2]
                running_processes.append(process)
                firsttime = False

            if firsttime:
                process = self.base_command(treepointer, None)
            else:
                process = self.base_command(treepointer, process.stdout)

            running_processes.append(process)
            for process in running_processes:
                process.wait()

            return_code = process.return_code
            stdout = process.stdout.read()
            print(stdout.decode()) # decode binary data
            return (stdout, return_code)
        elif ast[0] is None: # occurs with trailing ;
            pass
        else:
            raise UnknownTreeException

    def base_command(self, tree, stdin):
        process = Popen(self.flatten_tree(tree[1]), stdin=stdin,
                        stdout=subprocess.PIPE)
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

    def pipedcmd(self, line, pipein):
        cmd, arg, line = self.parseline(line)
        if not line:
            return pipein # do nothing with empty line
        if cmd is None or cmd == '':
            return self.default(line, pipein)
        self.lastcmd = line
        try:
            # find a command with this name
            func = getattr(programs, 'do_' + cmd)
        except AttributeError:
            return self.default(line, pipein)
        return func(arg, pipein)

    def multipipedcmd(self, line, pipes):
        # do multi pipe to start
        try:
            multipipe = [copy.deepcopy(self.saved_pipes[name]) for name in pipes]
            cmd, arg, line = self.parseline(line)
            func = getattr(programs, 'do_multi_' + cmd)
        except AttributeError:
            return self.default(line, pipeddata)
        except KeyError:
            print("You have not saved a pipe of that name. Todo: state name")
            return []
        return func(arg, multipipe)
     
    def startswithnamedpipe(self, line):
        beginning = line.split(" ")[0]
        # pipe syntax is |1+2+3 to combine saved pipes
        if re.match("\|[0-9]+(\+[0-9]+)*", beginning) is None:
            return False
        else:
            return True

    def endswithnamedpipe(self, line):
        end = line.split(" ")[-1]
        if re.match("\|[0-9]+", end) is None:
            return False
        else:
            return True

    def getpipenames(self, pipenames):
        pipes = pipenames.split("+")
        # first has leading |
        pipes[0] = pipes[0][1:]
        return pipes

    # define error message with unknown command
    def default(self, line, pipein):
        args = line.split(" ")
        self.stdout.write('oosh doesn\'t know the command \'%s\'.\n'%args[0])
        return []

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

def printstream(droplets):
    # todo: fix since it assumes all droplet entries are only strings
    if len(droplets) == 0:
        return

    # print header
    columns = []
    for droplet in droplets:
        for key in droplet.entries:
            if key not in columns:
                columns.append(key)
    print("\t".join(columns))

    # print rows
    for droplet in droplets:
        row = []
        for column in columns:
            if column not in droplet.entries:
                row.append('')
            else:
                row.append(str(droplet.entries[column]))
        print("\t".join(row))

if __name__=='__main__':
    oosh = Oosh()
    oosh.prompt = "$ "
    oosh.cmdloop("Welcome to oosh.")
