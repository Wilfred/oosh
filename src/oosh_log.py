import sys

args = sys.argv[1:]

for line in open('/home/wilfred/scratch/daemon.log').readlines():
    attributes = line.split(' ')
    month = attributes[0]
    day = attributes[1]
    time = attributes[2]
    host = attributes[3]
    daemon = attributes[4][:-1] # truncate trailing :
    message = ' '.join(attributes[5:])[:-1] # remainder of line, but truncate \n
    dict = {'Month':month, 'Day':day, 'Time':time, 'Host':host, 'Daemon':daemon,
            'Message':message}
    sys.stdout.write(dict.__repr__() + '\n')
