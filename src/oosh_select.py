import sys

args = sys.argv[1:]

if len(args) < 2:
    print("Usage: oosh_select colname value1 value2 ... ")
    sys.exit(1)

colname = args[0]
values = args[1:]

pipein = sys.stdin.read().splitlines()
lines = [eval(v) for v in pipein[:-1]]
for dic in lines:
    if dic[colname] in values:
        sys.stdout.write(dic.__repr__())
        sys.stdout.write('\n')
