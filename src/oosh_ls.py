# echo: return a single droplet of data as given as arguments
import sys
import os
import pwd

args = sys.argv[1:]

if len(args) == 0:
    dir = os.getcwd()
else:
    dir = args[0]

for filename in os.listdir(dir):
    fullname = dir + '/' + filename
    user = pwd.getpwuid(os.stat(fullname).st_uid).pw_name
    size = os.stat(fullname).st_size
    fileinfo = [['Filename', filename], ['Owner', user],
                ['Size', size]]
    droplet = dict(fileinfo)
    sys.stdout.write(droplet.__repr__())
    sys.stdout.write('\n')

