import sys
import os

args = sys.argv[1:-2] # 1st arg to n-1th arg
second_pipe_fd = int(sys.argv[-1])

first_pipe_in = sys.stdin.read().splitlines()
second_pipe_in = os.fdopen(second_pipe_fd).read().splitlines()

first_lines = [eval(v) for v in first_pipe_in]
second_lines = [eval(v) for v in second_pipe_in]

product = []
for left in first_lines:
    for right in second_lines:
        item = dict(left.items() | right.items())
        product.append(item)

# note the loop below will go into an infinite loop for large datasets
# where large is >200
for dic in product:
    sys.stdout.write(dic.__repr__() + '\n')
