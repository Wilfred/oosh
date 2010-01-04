#!/usr/bin/python3

# default python interpreter facilities
# source is in /usr/lib/python3.1/cmd.py
from cmd import Cmd
# use the python history facilities
# we will modify this later for object caching alongside
import readline
# regular expressions
import re
import copy

from ooshparse import parser
# current location of oosh programs:
# todo: create /usr/bin equivalent
# import programs

from subprocess import Popen # spawn processes
import subprocess

class Oosh(Cmd):
    def __init__(self):
        Cmd.__init__(self)
        self.savedpipes = {}
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
            return 0

        runningprocesses = []
        returncode = 0
        # sadly no case or pattern matching in python
        if ast[0] == 'sequence':
            self.eval(ast[1])
            return self.eval(ast[2])
        elif ast[0] == 'savepipe':
            # todo: need to save data
            return self.eval(ast[2])
        elif ast[0] == 'for':
            oldvariables = self.variables.copy()
            for value in self.flattentree(ast[2]):
                self.variables[ast[1]] = value
                returncode = self.eval(ast[3])
            self.variables = oldvariables
            return returncode
        elif ast[0] == 'while':
            while returncode == 0:
                returncode = self.eval(ast[1])
                self.eval(ast[2])
            return returncode
        elif ast[0] == 'if':
            if self.eval(ast[1]) == 0: # 0 is true for shells
                self.eval(ast[2])
        elif ast[0] == 'if-else':
            if self.eval(ast[1]) == 0:
                self.eval(ast[2])
            else:
                self.eval(ast[3])
        elif ast[0] == 'assign':
            self.variables[ast[1]] = self.flattentree(ast[2])[0]
        elif ast[0] == 'derefpipe':
            pass
        elif ast[0] == 'multicommand':
            pass
        elif ast[0] == 'simplecommand':
            process = self.basecommand(ast, None, True)
            returncode = process.returncode
            runningprocesses.append(process)
        elif ast[0] == 'derefmultipipe':
            pass
        elif ast[0] == 'pipedcommand':
            treepointer = ast
            firsttime = True
            # we have a tree of simple commands to evaluate
            while treepointer[0] == 'pipedcommand':
                if firsttime:
                    proc = self.basecommand(treepointer[1], None)
                else:
                    proc = self.basecommand(treepointer[1], proc.stdout)
                treepointer = treepointer[2]
                runningprocesses.append(proc)
                firsttime = False

            if firsttime:
                proc = self.basecommand(treepointer, None, True)
            else:
                proc = self.basecommand(treepointer, proc.stdout, True)
            runningprocesses.append(proc)
            returncode = proc.returncode

        elif ast[0] is None: # occurs with trailing ;
            pass
        else:
            raise UnknownTreeException

        for process in runningprocesses:
            process.wait()
        return returncode

    def basecommand(self, tree, stdin, isend=False):
        if isend:
            proc = Popen(self.flattentree(tree[1]), stdin=stdin)
        else:
            proc = Popen(self.flattentree(tree[1]), stdin=stdin,
                         stdout=subprocess.PIPE)
        return proc

    def flattentree(self, tree):
        # return a list of strings from a tree
        # handles string, values, variable trees
        if tree[0] == 'string':
            return [tree[1]]
        elif tree[0] == 'values':
            return self.flattentree(tree[1])+self.flattentree(tree[2])
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
            multipipe = [copy.deepcopy(self.savedpipes[name]) for name in pipes]
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
