#!/usr/bin/python3

# default python interpreter facilities
# source is in /usr/lib/python3.1/cmd.py
from cmd import Cmd
# use the python history facilities
# we will modify this later for object caching alongside
import readline

# Cmd gives us: ? (sugar for command 'help') ! (sugar for command 'shell')
# and do_whatever() to implement builtins
class Oosh(Cmd):
    # the exciting bit -- execute command
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

shell = Oosh()
shell.prompt = "$ "
shell.cmdloop("Welcome to oosh.")
