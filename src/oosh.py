#!/usr/bin/python3

# default python interpreter facilities
# source is in /usr/lib/python3.1/cmd.py
from cmd import Cmd
# use the python history facilities
# we will modify this later for object caching alongside
import readline
# regular expressions
import re
# list files for ls command
import os
# to enable us to convert user ids to strings
import pwd

# Cmd gives us: ? (sugar for command 'help') ! (sugar for command 'shell')
# do_whatever() to implement builtins, help_whatever() to document

class Oosh(Cmd):
    # the exciting bit -- execute a command
    def onecmd(self, line):
        # split pipe and evaluate
        pipeddata = []
        for section in line.split('|'):
            pipeddata = self.pipedcmd(section, pipeddata)
        printstream(pipeddata)

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
        # may be better to use similar arguments to rename
        args = line.split(" ") # command name is not passed
        for droplet in pipein:
            for entry in droplet.entries:
                if entry not in args:
                    del droplet.entries[entry]
        return pipein
    def help_select(self):
        self.print_topics("select [column1 column2 ...]", 
                          ["Only returns droplets with the column names given (assumes column names are single word)"], 15, 80)

    def do_rename(self, line, pipein):
        args = re.findall('".*?"', line, flags=re.DOTALL)
        # strip "
        changes = [s[1:][:-1] for s in args]
        if len(changes) % 2 != 0:
            print('rename requires an even number of arguments')
            raise PipeError
        else:
            for droplet in pipein:
                for entry in list(droplet.entries):
                    # iterate over replacements
                    for i in range(0,len(changes),2):
                        if changes[i] == entry:
                            value = droplet.entries.pop(entry)
                            droplet.entries[changes[i+1]] = value
            return pipein

    def do_project(self, line, pipein):
        # this duplicates some of select's functionality
        args = re.findall('".*?"', line, flags=re.DOTALL)
        # strip "
        projected = [s[1:][:-1] for s in args]
        for droplet in pipein:
            for entry in list(droplet.entries):
                if entry not in projected:
                    del droplet.entries[entry]
        return pipein

    def do_ls(self, line, pipein):
        pipeout = []
        for filename in os.listdir("."):
            user = pwd.getpwuid(os.stat(filename).st_uid).pw_name
            size = os.stat(filename).st_size
            fileinfo = [['Filename', filename], ['Owner', user],
                        ['Size', size]]
            pipeout.append(Droplet(fileinfo))
        return pipeout

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
