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

# current location of oosh programs:
# todo: create /usr/bin equivalent
import programs

class Oosh(Cmd):
    savedpipes = {}

    def onecmd(self, line):
        # split command and evaluate, honouring numbered pipes
        pipeddata = []

        if self.startswithnamedpipe(line):
            pipes = self.getpipenames(line.split(" ")[0])
            line = line.lstrip('|0123456789+')
            if len(pipes) == 1:
                pipeddata = self.savedpipes[pipes[0]]
            else:
                pipeddata = self.multipipedcmd(line, pipes)
                # now strip the part of the command we executed
                line = " ".join(line.split(" ")[2:])

        if not self.endswithnamedpipe(line):
            for section in line.split('|'):
                pipeddata = self.pipedcmd(section, pipeddata)
            printstream(pipeddata)
        else:
            lasttoken = line.split(" ")[-1]
            pipename = self.getpipenames(lasttoken)[0]
            line = line.rstrip('|0123456789')
            for section in line.split('|'):
                pipeddata = self.pipedcmd(section, pipeddata)
            # save our piped data
            self.savedpipes[pipename] = pipeddata

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
