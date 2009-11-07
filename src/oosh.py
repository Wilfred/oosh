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
class Oosh(Cmd):
    # the exciting bit -- execute a command
    def onecmd(self, line):
        # split pipe and evaluate
        pipeddata = []
        for section in line.split('|'):
            pipeddata = self.pipedcmd(section, pipeddata)

        # print result of pipe
        x = 1
        for droplet in pipeddata:
            print("row", x)
            x += 1
            droplet.print()

    def pipedcmd(self, line, pipein):
        cmd, arg, line = self.parseline(line)
        if not line:
            return [] # do nothing with empty line
        if cmd is None or cmd == '':
            return self.default(line, pipein)
        self.lastcmd = line
        try:
            # find a command with this name
            func = getattr(self, 'do_' + cmd)
        except AttributeError:
            return self.default(line, pipein)
        return func(arg, pipein)

    # define error message with unknown command
    def default(self, line, pipein):
        args = line.split(" ")
        self.stdout.write('oosh doesn\'t know the command \'%s\'. Try typing \'help\' to list commands.\n'%args[0])
        return []

    # basic builtins
    def do_help(self, line, pipein):
        super(Oosh, self).do_help(line)
        return []
    def do_exit(self, line, pipein):
        exit()
        return [] # by convention
    def help_exit(self):
        self.print_topics("exit", ["Exit oosh"], 15, 80)

    def do_shell(self, line, pipein):
        print("shell escape coming soon")
        return []
    def help_shell(self):
        self.print_topics("shell [shell command]", 
                          ["Execute a command in bash"], 15, 80)

    def do_echo(self, line, pipein):
        # echo text data inputted by user, drop pipe in
        return [Droplet(line)]
    def help_echo(self):
        self.print_topics("echo [item1, item2, ...]", 
                          ["Create a list of items for the pipe"], 15, 80)

    def do_select(self, line, pipein):
        args = line.split(" ") # command name is not passed
        pipeout = []
        # refactor me!
        for droplet in pipein:
            selected = []
            for entry in droplet.entries:
                for columnname in args:
                    name = entry[0]
                    if name == columnname:
                        selected.append(entry)
            pipeout.append(Droplet(selected))
        return pipeout
    def help_select(self):
        self.print_topics("select [column1 column2 ...]", 
                          ["Only returns droplets with the column names given (assumes column names are single word)"], 15, 80)

    def do_rename(self, line, pipein):
        args = re.findall('".*?"', line, flags=re.DOTALL)
        # strip "
        replacements = [s[1:][:-1] for s in args]
        if len(replacements) % 2 != 0:
            print('rename requires an even number of arguments')
            raise PipeError
        else:
            for droplet in pipein:
                for e in range(droplet.entries):
                    # iterate over replacements
                    for i in range(0,len(replacements),2):
                        if replacement[i] = droplet.entries[e]:
                            droplet.entries[e] = replacement[i+1]
            return pipein

# an object stream is made of droplets
class Droplet:
    def __init__(self, value):
        if isinstance(value, str):
            self.entries = parse(value)
        elif isinstance(value, list):
            self.entries = value
        else:
            raise TypeError
    def print(self):
        print(self.entries)

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
    return pairs

if __name__=='__main__':
    oosh = Oosh()
    oosh.prompt = "$ "
    oosh.cmdloop("Welcome to oosh.")
