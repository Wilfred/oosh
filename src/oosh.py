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
            for entry in droplet.entries:
                print(entry)

    def pipedcmd(self, line, pipein):
        cmd, arg, line = self.parseline(line)
        if not line:
            return [] # do nothing with empty line
        if cmd is None or cmd == '':
            return self.default(line)
        self.lastcmd = line
        try:
            # find a command with this name
            func = getattr(self, 'do_' + cmd)
        except AttributeError:
            return self.default(line)
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
        # echo text data inputted by user
        # TODO: need to properly input/output droplets
        return [Droplet(line)]

    def do_select(self, line):
        return []

# an object stream is made of droplets
class Droplet:
    def __init__(self, valuestring):
        # values always take the form "name":"value", tolerating
        # newlines but we escape ""
        values = re.findall('".*?":".*?"', valuestring,
                            flags=re.DOTALL)
        for value in values:
            # strip leading and trailing ", replace ":" with :
            value = value[1:][:-1].replace('":"',':').replace('""','"')
        
        self.entries = values

if __name__=='__main__':
    oosh = Oosh()
    oosh.prompt = "$ "
    oosh.cmdloop("Welcome to oosh.")
