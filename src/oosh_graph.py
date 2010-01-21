import CairoPlot
import cairo
import sys

pipein = sys.stdin.read().splitlines()
lines = [eval(v) for v in pipein[:-1]]

args = sys.argv[1:]
if len(args) < 4:
    print "usage: chart_type label variable filename"
    sys.exit()

chart_type = args[0]
variable_x = args[1]
variable_y = args[2]
file_name = args[3]

if chart_type == 'pie':
    pie_data = {}
    for line in lines:
        name = line[variable_x]
        value = int(float(line[variable_y]))
        if value > 0:
            pie_data[name] = value
    CairoPlot.pie_plot(file_name, pie_data, 800, 600, shadow=True)

elif chart_type == 'bar':
    bar_data = {}
    data = []
    labels = []
    for line in lines:
        name = line[variable_x]
        value = float(line[variable_y])
        if value > 0:
            labels.append(name)
            data.append(value)
    CairoPlot.bar_plot (file_name, data, 800, 600, border=20, grid=True,
                        rounded_corners=True, h_labels=labels) 

