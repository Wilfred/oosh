import CairoPlot
import cairo
import sys

args = sys.argv[1:]
chart_type = args[0]
variable_x = args[1]
variable_y = args[2]

pipein = sys.stdin.read().splitlines()
lines = [eval(v) for v in pipein[:-1]]

if chart_type == 'pie':
    pie_data = {}
    for line in lines:
        name = line[variable_x]
        value = int(float(line[variable_y]))
        if value > 0:
            pie_data[name] = value
    CairoPlot.pie_plot("pie1", pie_data, 600, 400, shadow=True)

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
    CairoPlot.bar_plot ('bar1', data, 600, 400, border=20, grid=True,
                        rounded_corners=True, h_labels=labels)

