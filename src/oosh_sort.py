import sys
import operator
import oosh
from oosh import OoshError

args = sys.argv[1:]
if len(args) < 1:
    print("Usage: oosh_sort columnname")
    sys.exit(1)

sort_on = args[0]
pipein = sys.stdin.read().splitlines()
lines = oosh.get_from_pipe(pipein)
# check we are sorting on a valid column
if len(lines) > 0 and sort_on not in lines[0].keys():
    print(sort_on,"is not a valid column name")
    sys.exit(1)  

# treat data numerically if possible, it comes in as a string
# preferring whole numbers if possible
is_numeric = True
for line in lines:
    try:
        line[sort_on] = int(line[sort_on])
    except ValueError:
        try:
            line[sort_on] = float(line[sort_on])
        except ValueError:
            is_numeric = False
            break
# if we have mixed data, we may have converted to float/int, so revert
if not is_numeric:
    for line in lines:
        line[sort_on] = str(line[sort_on])

lines.sort(key=operator.itemgetter(sort_on))
for dic in lines:
    sys.stdout.write(dic.__repr__() + '\n')

