import sys
import operator
from oosh import OoshError

args = sys.argv[1:]
sort_on = args[0]
pipein = sys.stdin.read().splitlines()
lines = [eval(v) for v in pipein[:-1]]
try:
    lines.sort(key=operator.itemgetter(sort_on))
    for dic in lines:
        sys.stdout.write(dic.__repr__())
        sys.stdout.write('\n')
except KeyError:
    print(sort_on,"is not a valid column name")
    sys.exit(1)
