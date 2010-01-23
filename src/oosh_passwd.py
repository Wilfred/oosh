import sys

args = sys.argv[1:]

for line in open('/etc/passwd').readlines():
    attributes = line.split(':')
    username = attributes[0]
    uid = attributes[2]
    gid = attributes[3]
    info = attributes[4]
    home_directory = attributes[5]
    shell = attributes[6][:-1] # truncate \n
    dict = {'Username':username, 'User ID':uid, 'Group ID':gid, 
            'User ID Info':info, 'Home directory':home_directory,
            'Shell':shell}
    sys.stdout.write(dict.__repr__() + '\n')
