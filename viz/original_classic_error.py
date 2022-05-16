import matplotlib.pyplot as plt
import csv

plt.rcParams['font.size'] = 12

x = []
y = []
with open('res/error_ratio.csv') as f:
    rd = csv.reader(f)
    for line in rd:
        x.append(float(line[0]))
        y.append(float(line[1]))

fig, ax = plt.subplots()

ax.plot(y, marker='o', fillstyle='none', color='black', lw=0.5)

ax.set_xlabel('Density')
ax.set_ylabel('Original Classic Failure')

plt.xticks([i for i in range(len(x))], x)

plt.show()
# fig.savefig('res/fig11b.png')
# print("Fig. 11b Saved")