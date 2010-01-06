import sys

args = sys.argv[1:]

fromlist = [args[i] for i in range(0,len(args),2)]
tolist = [args[i] for i in range(1,len(args),2)]


pipein = sys.stdin.read().splitlines()
lines = [eval(v) for v in pipein[:-1]]
for dic in lines:
    for key in list(dic.keys()):
        for i in range(len(fromlist)):
              if key==fromlist[i]:
                  old_value = dic[key]
                  del dic[key]
                  dic[tolist[i]] = old_value
    sys.stdout.write(dic.__repr__())
    sys.stdout.write('\n')
