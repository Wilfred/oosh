import sys

args = sys.argv[1:]
if len(args) < 1:
    print("Usage: oosh_project column1 column2 ...")
    sys.exit(1)
pipein = sys.stdin.read().splitlines()
lines = [eval(v) for v in pipein[:-1]]
for dic in lines:
    for key in list(dic.keys()):
        if key not in args:
            del dic[key]
    sys.stdout.write(dic.__repr__())
    sys.stdout.write('\n')
