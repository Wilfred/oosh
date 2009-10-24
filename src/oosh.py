#!/usr/bin/python3

# default python interpreter facilities
# source is in /usr/lib/python3.1/cmd.py
from cmd import Cmd
# use the python history facilities
# we will modify this later for object caching alongside
import readline

# Cmd gives us: ? (sugar for command 'help') ! (sugar for command 'shell')
# do_whatever() to implement builtins, help_whatever() to document
class Oosh(Cmd):
    objectstream = []
    # the exciting bit -- execute a command
    def onecmd(self, line):
        cmd, arg, line = self.parseline(line)
        if not line:
            return # do nothing with empty line
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if cmd == '':
            return self.default(line)
        else:
            try:
                # execute a command with this name
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line)
            return func(arg)

    # print our leftover objects after pipeline completion
    # TODO: learn arguments' purpose
    def postcmd(self, stop, line):
        for droplet in self.objectstream:
            for entry in droplet.entries:
                print(entry)
        return stop

    # define error message with unknown command
    def default(self, line):
        args = line.split(" ")
        self.stdout.write('oosh doesn\'t know the command \'%s\'. Try typing \'help\' to list commands.\n'%args[0])

    # basic builtins
    def do_exit(self, line):
        exit()
    def help_exit(self):
        self.print_topics("exit", ["Exit oosh"], 15, 80)

    def do_shell(self, line):
        print("shell escape coming soon")
    def help_shell(self):
        self.print_topics("shell [shell command]", 
                          ["Execute a command in bash"], 15, 80)

    def do_echo(self, line):
        # TODO: need to check syntax
        # TODO: need to properly input/output droplets
        columns = line.split(" ")
        self.objectstream = [Droplet(columns)]

# an object stream is made of droplets
class Droplet:
    def __init__(self, entries):
        self.entries = entries

oosh = Oosh()
oosh.prompt = "$ "
oosh.cmdloop("Welcome to oosh.")
