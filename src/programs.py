from oosh import Droplet

# basics
def do_help(line, pipein):
    super(Oosh, self).do_help(line)
    return []

def do_exit(line, pipein):
    exit()
    return [] # by convention
def help_exit():
    self.print_topics("exit", ["Exit oosh"], 15, 80)
    
def do_shell(line, pipein):
    print("shell escape coming soon")
    return []
def help_shell():
    self.print_topics("shell [shell command]", 
                      ["Execute a command in bash"], 15, 80)
    
def do_echo(line, pipein):
    # echo text data inputted by user, drop pipe in
    return [Droplet(line)]
def help_echo():
    self.print_topics("echo [item1, item2, ...]", 
                      ["Create a list of items for the pipe"], 15, 80)

# relational commands
def do_select(line, pipein):
    # may be better to use similar arguments to rename
    args = line.split(" ") # command name is not passed
    for droplet in pipein:
        for entry in droplet.entries:
            if entry not in args:
                del droplet.entries[entry]
    return pipein
def help_select():
    self.print_topics("select [column1 column2 ...]", 
                      ["Only returns droplets with the column names given (assumes column names are single word)"], 15, 80)

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
