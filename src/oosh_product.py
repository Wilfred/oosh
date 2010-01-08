import sys
import os

args = sys.argv[1:-2] # 1st arg to n-1th arg
second_pipe_fd = int(sys.argv[-1])

first_pipe_in = sys.stdin.read().splitlines()
second_pipe_in = os.fdopen(second_pipe_fd).read().splitlines()

first_lines = [eval(v) for v in first_pipe_in[:-1]]
second_lines = [eval(v) for v in second_pipe_in[:-1]]

product = []
for left in first_lines:
    for right in second_lines:
        product.append(dict(left.values() | right.values()))

for dic in product:
    sys.stdout.write(dic.__repr__())
    sys.stdout.write('\n')
