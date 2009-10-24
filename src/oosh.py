#!/usr/bin/python3

import readline
from cmd import Cmd

class Oosh(Cmd):
    def foo(self):
        print("hello world")

shell = Oosh()
shell.prompt = "$ "
shell.cmdloop("Welcome to oosh.")
