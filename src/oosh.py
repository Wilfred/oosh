#!/usr/bin/python3

# default python interpreter facilities
# source is in /usr/lib/python3.1/cmd.py
from cmd import Cmd
import readline # use the python history facilities
import re # regular expressions
import sys
import socket
import time # for time built-in

from ooshparse import parser

import subprocess

class OoshError(Exception):
    def __init__(self, message):
        self.message = message

def server_command(server_address, command):
    # send the list 'command' to server at server_address,
    # return the server's response
    PORT = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_address, PORT))
    except socket.gaierror:
        raise OoshError(server_address + " is not a valid address")
    except socket.error:
        raise OoshError("Could not connect to " + server_address)
    if command[0] in ['connect', 'disconnect', 'send', 'receive']:
        command_string = b''
    else:
        command_string = b'command '
    for word in command:
        command_string += word.encode() + b' '
    sock.send(command_string)

    received = b''
    more_data = b'initial value'
    while more_data != b'':
        more_data = sock.recv(4096)
        received += more_data
    sock.close()

    if command[0] == 'connect' and received != b'success':
        raise OoshError("Error: Could not log in")
    return received
 
def pipe_to_server(self, server_address, pipe_data):
    PORT = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_address, PORT))
    sock.send(b'receive ' + pipe_data)
    received = b''
    more_data = b'initial value'
    while more_data != b'':
        more_data = sock.recv(4096)
        received += more_data
    sock.close()
    return received

class PipePointer:
    def __init__(self, reader=None, remote_host=''):
        self.reader = reader
        self.remote_host = remote_host
    def read(self):
        if self.remote_host == '':
            # stored locally as a BufferedReader
            if self.reader is not None:
                return self.reader.read()
            else:
                return b''
        else:
            # fetch from remote server
            output = server_command(self.remote_host, ['send'])
            # print("fetched data is",output) 
            return output
    def is_empty(self):
        if self.reader is None:
            return True
        else:
            return False

class Oosh(Cmd):
    def __init__(self):
        # setup class variables
        Cmd.__init__(self)
        self.saved_pipe_data = {}
        self.variables = {}
        self.command_count = 1

    def onecmd(self, line):
        # hook from cmd.py, called for each line entered by user
        self.command_count += 1
        self.prompt = str(self.command_count) + '$ '

        self.set_colour('white')
        if line.strip(' \t\n') == '':
            self.set_colour('red')
            return

        start_time = time.time()
        timing = False
        if len(line) > 4 and line[0:4] == 'time':
            timing = True
            line = line[5:] # strip 'time' to give the actual command

        ast = parser.parse(line)
        # print("AST: ", ast)
        try:
            self.eval(ast)
        except OoshError as error:
            print(error.message)

        if timing:
            self.set_colour('purple')
            print("Time taken to run command {0} seconds".format(time.time()-start_time))
        self.set_colour('red')

    def print_pipe(self, pipe_pointer):
        # read and decode binary data in stdout
        if not pipe_pointer is None:
            content = pipe_pointer.read().decode()
            if (len(content) > 0 and content[0] == '{' 
                and 'no-print' not in debug_flags): 
                # data conforms to oosh structure
                self.pretty_print(content)
            else:
                # can't use print, gives extraneous newline
                sys.stdout.write(content)

    def pretty_print(self, content):
        string_lines = content.splitlines()
        lines = []
        for line in string_lines:
            if line[0] == '{':
                lines.append(eval(line))

        header = []
        for line in lines:
            for key in line.keys():
                if key not in header:
                    header.append(key)
        # alphabetical order looks better:
        header.sort(key=str.lower)

        # get optimum width:
        column_widths = {}
        for string in header:
            column_widths[string] = (len(string))
        for line in lines:
            for key in header:
                try:
                    value = str(line[key])
                    if len(value) > column_widths[key]:
                        column_widths[key] = len(value)
                except KeyError:
                    pass

        # print header
        header_text = ''
        for key in header:
            # print string plus requisite number of spaces
            header_text += key + ' '*(column_widths[key]-len(key)+1)
        self.set_colour('purple')
        print(header_text)
        self.set_colour('white')
            
        for line in lines:
            line_text = ''
            for key in header:
                try:
                    datum = str(line[key])
                except KeyError:
                    datum = '-'
                line_text += datum + ' '*(column_widths[key]-len(datum)+1)
            print(line_text)

    def eval(self, ast):
        self.output_for_user = []
        (final_pipe, return_code) = self.eval_tree(ast, PipePointer())
        self.output_for_user.append(final_pipe)

        for pipe in self.output_for_user:
            self.print_pipe(pipe)

    def eval_tree(self, ast, pipe_pointer):
        # recurse down tree, starting processes and passing pointers
        # of pipes created as appopriate.

        # returns a tuple (stdout_pipe_pointer, return_code)
        
        if ast is None:
            print('Evaluated empty tree')
            return (PipePointer(), 0)

        if ast[0] == 'sequence':
            (stdout, returncode) = self.eval_tree(ast[1], PipePointer())
            self.output_for_user.append(stdout)
            return self.eval_tree(ast[2], PipePointer())

        elif ast[0] == 'savepipe':
            (pipe_out, return_code) = self.eval_tree(ast[1], PipePointer())
            pipe_number = ast[2][1:]
            self.saved_pipe_data[pipe_number] = pipe_out.read()
            return (PipePointer(), return_code)

        elif ast[0] == 'for':
            old_variables = self.variables.copy()
            for value in self.flatten_tree(ast[2]):
                self.variables[ast[1]] = value
                (stdout, return_code) = self.eval_tree(ast[3], PipePointer())
                self.output_for_user.append(stdout)
            self.variables = old_variables
            return (PipePointer(), return_code)

        elif ast[0] == 'while':
            while return_code == 0:
                (dont_care, return_code) = self.eval_tree(ast[1], PipePointer())
                (stdout, final_return_code) = self.eval_tree(ast[2], PipePointer())
                self.output_for_user.append(stdout)
            return (PipePointer(), final_return_code)

        elif ast[0] == 'if':
            (stdout, return_code) = self.eval_tree(ast[1], PipePointer())
            if return_code == 0: # 0 is true for shells
                return self.eval_tree(ast[2], PipePointer())
            else:
                return (PipePointer(), 0)

        elif ast[0] == 'if-else':
            (stdout, return_code) = self.eval_tree(ast[1], PipePointer())
            if return_code == 0:
                return self.eval_tree(ast[2], PipePointer())
            else:
                return self.eval_tree(ast[3], PipePointer())

        elif ast[0] == 'assign':
            self.variables[ast[1]] = self.flatten_tree(ast[2])[0]
            return (PipePointer(), 0)

        elif ast[0] == 'derefpipe':
            # create a process to give us a stdout to pass
            # to whatever is next in the pipeline
            old_pipe_name = ast[1][1:] # e.g. |2
            try:
                old_pipe_data = self.saved_pipe_data[old_pipe_name]
                old_pipe_pointer = self.pipe_from_data(old_pipe_data)
                return self.eval_tree(ast[2], PipePointer(old_pipe_pointer))
            except KeyError:
                raise OoshError("You have not saved a pipe numbered " +
                                old_pipe_name)

        elif ast[0] == 'simplecommand':
            command = self.flatten_tree(ast[1])
            return self.shell_command(command, pipe_pointer)

        elif ast[0] == 'derefmultipipe':
            pipe_names = ast[1][1:].split('+')

            first_pipe_data = self.saved_pipe_data[pipe_names[0]]
            first_pipe_pointer = self.pipe_from_data(first_pipe_data)

            second_pipe_data = self.saved_pipe_data[pipe_names[1]]
            second_pipe_pointer = self.pipe_from_data(second_pipe_data)

            # we call command, appending argument of second pipe
            command = self.flatten_tree(ast[2][1])
            command.append(str(second_pipe_pointer.fileno()))

            # check user hasn't tried to run this remotely
            if self.specifies_location(command[0]):
                raise OoshError("Cannot run multipipe commands remotely")
            
            return self.shell_command(command, PipePointer(first_pipe_pointer))

        elif ast[0] == 'pipedcommand':
            (stdout, return_code) = self.eval_tree(ast[1], pipe_pointer)
            return self.eval_tree(ast[2], stdout)

        elif ast[0] is None: # occurs with trailing ;
            pass

        else:
            raise OoshError("Unknown tree " + str(ast))

    def pipe_from_data(self, pipe_data):
        # this is not beautiful code, we use cat just to create a new
        # pipe (cf 'useless use of cat')
        # known bug: this blocks with large amounts of data
        process = subprocess.Popen('cat', stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
        process.stdin.write(pipe_data)
        process.stdin.close()
        return process.stdout

    def decide_command_location(self, command_name, stdin):
        global debug_flags
        # determine whether user has specified
        if self.specifies_location(command_name):
            specifies_remote = True
            (command_name,address) = command_name.split('@')
        else:
            address = stdin.remote_host
            specifies_remote = False

        # determine whether previous command was remote
        if stdin.remote_host == '':
            previous_was_remote = False
        else:
            previous_was_remote = True

        # determine whether command can be safely moved
        safe_commands = ['grep', 'oosh_select', 'oosh_project', 'oosh_rename',
                         'oosh_sort']
        if 'no-command-move' in debug_flags:
            command_is_movable = False
        elif command_name in safe_commands:
            command_is_movable = True
        else:
            command_is_movable = False

        if previous_was_remote:
            previous_is_remote = True
            if specifies_remote:
                next_is_remote = True
            elif command_is_movable:
                next_is_remote = True
                
            else:
                next_is_remote = False
        else:
            previous_is_remote = False
            if specifies_remote:
                next_is_remote = True
            elif command_is_movable:
                next_is_remote = False
            else:
                next_is_remote = False

        return (previous_is_remote, next_is_remote, address)

    def shell_command(self, command, stdin):
        command_name = command[0]
        # exit if specified
        if command_name == 'exit':
            sys.exit()

        # find where to run command
        (previous_is_remote, next_is_remote, address) = self.decide_command_location(command_name, stdin)

        # prepare command string
        if self.specifies_location(command_name):
            (command_name,dont_care) = command_name.split('@')
            command[0] = command_name

        if not re.match('oosh_.*', command_name) is None:
            if command_name == 'oosh_graph':
                # graph uses pycairo, which is not py3k compatible
                command = ['python'] + [command_name + '.py'] + command[1:]
            else:
                command = ['python3'] + [command_name + '.py'] + command[1:]

        # work out where to run it then do so
        try:
            if next_is_remote:
                if not previous_is_remote:
                    # last command was local, next is remote
                    if not stdin.is_empty:
                        pipe_to_server(address, stdin.read())
                    response = server_command(address, command)
                    if response == b'success':
                        return_code = 0
                    else:
                        return_code = 1
                    return (PipePointer(remote_host=address), return_code)
                else:
                    # last command was remote, next is remote
                    # need to check we are sending to the right server
                    if stdin.remote_host == address:
                        response = server_command(address, command)
                        if response == b'success':
                            return_code = 0
                        else:
                            return_code = 1
                        return (PipePointer(remote_host=address), return_code)
                    else:
                        # get from previous server, send to next
                        # todo
                        pass
            else:
                if not previous_is_remote:
                    # last command was local, next is local
                    process = subprocess.Popen(command, stdin=stdin.reader,
                                               stdout=subprocess.PIPE)
                    return (PipePointer(process.stdout), process.returncode)
                else:
                    # last command was remote, next is local
                    remote_data = stdin.read()
                    new_pipe = self.pipe_from_data(remote_data)
                    process = subprocess.Popen(command, stdin=new_pipe,
                                               stdout=subprocess.PIPE)
                    return (PipePointer(process.stdout), process.returncode)
        except OSError:
            raise OoshError("No such command: " + command_name)
    
    def specifies_location(self, command_name):
        if re.match('.+@.+', command_name) is None:
            return False
        else:
            return True

    def flatten_tree(self, tree):
        # return a list of strings from a tree
        # handles string, values, variable trees
        if tree[0] == 'string':
            return [tree[1]]
        elif tree[0] == 'values':
            return self.flatten_tree(tree[1])+self.flatten_tree(tree[2])
        elif tree[0] == 'variable':
            try:
                variable_name = tree[1][1:]
                return [self.variables[variable_name]]
            except KeyError:
                raise OoshError("Variable " + variable_name +
                                " accessed before setting")
        else:
            raise OoshError("Invalid tree flattened: " + str(tree))

    def set_colour(self, colour='white'):
        if colour == 'white':
            sys.stdout.write('\033[0;37m')
        elif colour == 'red':
            sys.stdout.write('\033[1;31m')
        elif colour == 'purple':
            sys.stdout.write('\033[1;35m')

def get_from_pipe(pipein):
    output = []
    for value in pipein:
        if len(value) > 0 and value[0] != '\x1b':
            # avoid errors due to empty lines or escape sequences
            # (no idea how escape sequences are occurring)
            output.append(eval(value))
    return output

if __name__=='__main__':
    global debug_flags
    debug_flags = sys.argv[1:]
    oosh = Oosh()
    oosh.set_colour('red')
    oosh.prompt = "1$ "
    oosh.cmdloop("\033[0;37mWelcome to oosh.\033[1;31m")
