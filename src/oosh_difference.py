import sys
import os

args = sys.argv[1:-2] # 1st arg to n-1th arg
second_pipe_fd = int(sys.argv[-1])

first_pipe_in = sys.stdin.read().splitlines()
second_pipe_in = os.fdopen(second_pipe_fd).read().splitlines()

first_lines = [eval(v) for v in first_pipe_in]
second_lines = [eval(v) for v in second_pipe_in]

difference = []
for line in first_lines:
    if not line in second_lines:
        difference.append(line)

for dic in difference:
    sys.stdout.write(dic.__repr__())
    sys.stdout.write('\n')
