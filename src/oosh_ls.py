if __name__=='__main__':
    from oosh import Droplet

# echo: return a single droplet of data as given as arguments
import sys
import os
import pwd

args = sys.argv[1:]

if len(args) == 0:
    dir = "."
else:
    dir = args[0]

for filename in os.listdir("."):
    user = pwd.getpwuid(os.stat(filename).st_uid).pw_name
    size = os.stat(filename).st_size
    fileinfo = [['Filename', filename], ['Owner', user],
                ['Size', size]]
    droplet = Droplet(fileinfo)
    sys.stdout.write(droplet.__repr__())
    sys.stdout.write('\n')

