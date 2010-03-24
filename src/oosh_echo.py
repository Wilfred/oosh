# echo: return a single line of data as given by arguments
import sys

args = sys.argv[1:]
pairs = []
for i in range(0, len(args), 2):
    pairs.append((args[i],args[i+1]))

droplet = dict(pairs)
sys.stdout.write(droplet.__repr__())
sys.stdout.write('\n')
