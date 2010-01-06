if __name__=='__main__':
    from oosh import Droplet

# echo: return a single droplet of data as given as arguments
import sys

args = sys.argv[1:]
droplet = Droplet(''.join(args))
sys.stdout.write(droplet.__repr__())
sys.stdout.write('\n')
