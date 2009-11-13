#!/usr/bin/python3

# default python interpreter facilities
# source is in /usr/lib/python3.1/cmd.py
from cmd import Cmd
# use the python history facilities
# we will modify this later for object caching alongside
import readline
# regular expressions
import re

# Cmd gives us: ? (sugar for command 'help') ! (sugar for command 'shell')
# do_whatever() to implement builtins, help_whatever() to document

# current location of oosh programs:
# todo: create /usr/bin equivalent
import programs

class Oosh(Cmd):
    savedpipes = {}

    # the exciting bit -- execute a command
    def onecmd(self, line):
        # split pipe and evaluate, honouring numbered pipes at end
        pipeddata = []
        lasttoken = line.split(" ")[-1]
        if re.match("\|[0-9]+", lasttoken) is None:
            for section in line.split('|'):
                pipeddata = self.pipedcmd(section, pipeddata)
            printstream(pipeddata)
        else: # we have a numbered pipe
            line = " ".join(line.split(" ")[:-1]) # remove end pipe
            for section in line.split('|'):
                pipeddata = self.pipedcmd(section, pipeddata)
            # save our piped data
            self.savedpipes[lasttoken[1:]] = pipeddata

    def pipedcmd(self, line, pipein):
        cmd, arg, line = self.parseline(line)
        if not line:
            return [] # do nothing with empty line
        if cmd is None or cmd == '':
            return self.default(line, pipein)
        self.lastcmd = line
        try:
            # find a command with this name
            func = getattr(programs, 'do_' + cmd)
        except AttributeError:
            return self.default(line, pipein)
        return func(arg, pipein)

    # define error message with unknown command
    def default(self, line, pipein):
        args = line.split(" ")
        self.stdout.write('oosh doesn\'t know the command \'%s\'. Try typing \'help\' to list commands.\n'%args[0])
        return []

# an object stream is made of droplets
class Droplet:
    def __init__(self, value):
        if isinstance(value, str):
            self.entries = parse(value)
        elif isinstance(value, list):
            self.entries = dict(value)
        else:
            raise TypeError

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
    # todo: needs to be generic, currently assumes first droplet
    # chacterises all following droplets and order is unchanged
    if len(droplets) == 0:
        return

    header = ""
    for key in droplets[0].entries:
        header += key
        header += "\t"
    print(header[:-1])

    # now print values we have collected
    for droplet in droplets:
        row = ""
        for entry in droplet.entries:
            row += str(droplet.entries[entry])
            row += "\t"
        print(row[:-1])

if __name__=='__main__':
    oosh = Oosh()
    oosh.prompt = "$ "
    oosh.cmdloop("Welcome to oosh.")
