from oosh import Droplet

# basics
def do_exit(line, pipein):
    exit()
    return [] # by convention

def do_shell(line, pipein):
    print("shell escape coming soon")
    return []

def do_echo(line, pipein):
    if line == '':
        return []
    # echo text data inputted by user, drop pipe in
    return [Droplet(line)]

# relational commands
def do_select(line, pipein):
    # may be better to use similar arguments to rename
    args = line.split(" ") # command name is not passed
    for droplet in pipein:
        for entry in droplet.entries:
            if entry not in args:
                del droplet.entries[entry]
    return pipein

def do_rename(line, pipein):
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

import re

def do_project(line, pipein):
    # this duplicates some of select's functionality
    args = re.findall('".*?"', line, flags=re.DOTALL)
    # strip "
    projected = [s[1:][:-1] for s in args]
    for droplet in pipein:
        for entry in list(droplet.entries):
            if entry not in projected:
                del droplet.entries[entry]
    return pipein

# relational commands that take multiple pipes in
def do_multi_union(line, pipesin):
    pipeout = []
    for pipe in pipesin:
        for droplet in pipe:
            # no duplicates:
            if droplet not in pipeout:
                pipeout.append(droplet)
    return pipeout

def do_multi_difference(line, pipesin):
    if len(pipesin) == 0:
        return []
    # we do (a-b)-c (left associative) n-ary set difference
    pipeout = pipesin[0]
    for i in range(1,len(pipesin)):
        for droplet in pipesin[i]:
            if droplet in pipeout:
                pipeout.remove(droplet)
    return pipeout

def do_multi_product(line, pipesin):
    # left associative 2-ary set product
    if len(pipesin) == 0:
        return []
    pipeout = pipesin[0]:
    for x in pipesin[0]:
        for y in pipesin[1]:
            result = x.entries.items() | y.entries.items()
            pipeout.append(Droplet(dict(result)))
    return pipeout
  
# interesting data commands
import os
import pwd

def do_ls(line, pipein):
    pipeout = []
    for filename in os.listdir("."):
        user = pwd.getpwuid(os.stat(filename).st_uid).pw_name
        size = os.stat(filename).st_size
        fileinfo = [['Filename', filename], ['Owner', user],
                    ['Size', size]]
        pipeout.append(Droplet(fileinfo))
    return pipeout
