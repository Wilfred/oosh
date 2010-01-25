if __name__=='__main__':
    from oosh import Droplet

# ps: list running processes on this system
import subprocess
import sys

raw_data = subprocess.getoutput('ps -eo user,pid,pcpu,pmem,comm --no-header')
lines = raw_data.split('\n')
tidy_data = [line.split() for line in lines]
named_data = [zip(['User', 'PID', 'CPU %', 'Memory %', 'Command'],
                  line) for line in tidy_data]

droplets = [dict(line) for line in named_data]
for droplet in droplets:
    sys.stdout.write(droplet.__repr__())
    sys.stdout.write('\n')

