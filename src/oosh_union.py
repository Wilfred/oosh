import sys
import os
import oosh

args = sys.argv[1:-2] # 1st arg to n-1th arg
second_pipe_fd = int(sys.argv[-1])

first_pipe_in = sys.stdin.read().splitlines()
second_pipe_in = os.fdopen(second_pipe_fd).read().splitlines()

first_lines = oosh.get_from_pipe(first_pipe_in)
second_lines = oosh.get_from_pipe(second_pipe_in)

unioned = first_lines + second_lines

for dic in unioned:
    sys.stdout.write(dic.__repr__())
    sys.stdout.write('\n')
