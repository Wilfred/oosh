import socketserver
import hashlib
import oosh
from oosh import OoshError
import re

user_logins = {'wilfred':('6f5902ac23', 'f21627d3faf150060b0b2cb3902c05ef2fdda3ae')}
connected_machines = []
stored_data = []

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

    def handle(self):
        # self.request is the TCP socket connected to the client
        raw_request = self.request.recv(1024).strip()
        request = raw_request.decode().split()
        address = self.client_address[0]
        print("request is",request)

        if request[0] == 'connect':
            # authenticate if not already
            username = request[1]
            password = request[2]
            if address not in connected_machines:
                if checklogin(username, password):
                    connected_machines.append(address)
                    self.request.send(b'Connected')
                else:
                    self.request.send(b'Invalid password specified')
        elif self.client_address[0] in connected_machines:
            # execute requested command, or disconnect if asked
            if request[0] == 'disconnect':
                connected_machines.remove(address)
                self.request.send(b'Disconnected')
            elif request[0] == 'send':
                data_to_send = ''
                for line in stored_data:
                    data_to_send += line.__repr__() + '\n'
                self.request.send(data_to_send.encode())
                stored_data = []
            elif request[0] == 'command':
                try:
                    self.shell_command(request[1:])
                except OoshError as error:
                    self.request.send(error.message.encode())
                    stored_data = []
            else:
                error = "Invalid request:" + str(request)
                self.request.send(error.encode())
        else:
            self.request.send(b'You need to login first')

    def shell_command(self, command_string):
        if not re.match('oosh_.*', command_name) is None:
            if command_name == 'oosh_graph':
                # graph uses pycairo, which is not py3k compatible
                command = ['python'] + [command_name + '.py'] + command[1:]
            else:
                command = ['python3'] + [command_name + '.py'] + command[1:]
        try:
            process = subprocess.Popen(command, stdin=stdin, stdout=subprocess.PIPE)
            return process
        except OSError:
            raise OoshError("No such command: " + command_name)


if __name__ == "__main__":
    HOST, PORT = "localhost", 12345

    # Create the server, binding to localhost on port 12345
    server = socketserver.TCPServer((HOST, PORT), OoshRequestHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
