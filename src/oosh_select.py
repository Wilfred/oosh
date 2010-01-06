import sys

args = sys.argv[1:]
pipein = sys.stdin.read().splitlines()
lines = [eval(v) for v in pipein[:-1]]
for dic in lines:
    for value in dic.values():
        if str(value) in args:
            sys.stdout.write(dic.__repr__())
            sys.stdout.write('\n')
