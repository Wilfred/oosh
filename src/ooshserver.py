#!/usr/bin/python3

import socketserver
import hashlib
import oosh
from oosh import OoshError
import re
import subprocess
import socket

user_logins = {'wilfred':('6f5902ac23', 'f21627d3faf150060b0b2cb3902c05ef2fdda3ae')}
connected_machines = []
stored_data = b''

def checklogin(username, password):
    (salt, hash) = user_logins[username]
    sha1 = hashlib.sha1()
    salted_password = salt+password
    sha1.update(salted_password.encode())
    if sha1.hexdigest() == hash:
        return True
    else:
        return False

class OoshRequestHandler(socketserver.BaseRequestHandler):
    # the request handler that acts as a server
    # it is instantiated once per connection to the server
    # recognised commands: connect, disconnect, send, receive, command

    def handle(self):
        global user_logins
        global connected_machines
        global stored_data

        # self.request is the TCP socket connected to the client
        raw_request = self.request.recv(1024).strip()
        request = raw_request.decode().split()
        if len(request) < 1:
            return

        address = self.client_address[0]
        print("request is",request)

        if request[0] == 'connect':
            # authenticate if not already
            if len(request) < 3:
                self.request.send(b'Please specify a username and password')
                return
            username = request[1]
            password = request[2]
            if address not in connected_machines:
                if checklogin(username, password):
                    # stop multiple people logging in and clobbering each
                    # others' data
                    connected_machines = [address]
                    self.request.send(b'success')
                else:
                    self.request.send(b'Invalid password specified')
            else:
                # already logged in anyway
                self.request.send(b'success')

        elif self.client_address[0] in connected_machines:
            # execute requested command, or disconnect if asked
            if request[0] == 'disconnect':
                connected_machines.remove(address)
                self.request.send(b'Disconnected')
            elif request[0] == 'send':
                # transmit data from last pipeline and reset
                self.request.sendall(stored_data)
                stored_data = b''
            elif request[0] == 'receive':
                # set data for input to pipeline
                stored_data = request[1].encode()
            elif request[0] == 'command':
                (return_code, stored_data) = self.shell_command(request[1:])
                if return_code == 0:
                    self.request.send(b'success')
                else:
                    self.request.send(b'failed')
                    stored_data = b''
            else:
                error = "Invalid request:" + str(request)
                self.request.send(error.encode())
        else:
            self.request.send(b'You need to login first')

    def shell_command(self, command):
        command_name = command[0]

        if not re.match('oosh_.*', command_name) is None:
            if command_name == 'oosh_graph':
                # graph uses pycairo, which is not py3k compatible
                command = ['python'] + [command_name + '.py'] + command[1:]
            else:
                command = ['python3'] + [command_name + '.py'] + command[1:]
        try:
            if stored_data == b'':
                # no previous command in pipeline
                process = subprocess.Popen(command, stdout=subprocess.PIPE)
            else:
                previous = oosh.Oosh.pipe_from_data(None, stored_data)
                process = subprocess.Popen(command, stdin=previous,
                                           stdout=subprocess.PIPE)
            process.wait()
            return (process.returncode, process.stdout.read())
        except OSError:
            return (1, b'') # return error code to client


if __name__ == "__main__":
    HOST, PORT = "localhost", 12345

    # Create the server, binding to localhost on port 12345
    server = socketserver.TCPServer((HOST, PORT), OoshRequestHandler)
    name = socket.getfqdn()
    ip = socket.gethostbyname(socket.gethostname())
    print("Starting server at {0} ({1}) on port {2}".format(name, ip, PORT))

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
