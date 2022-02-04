import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

small_total_failure = []
large_total_failure = []
classic_total_failure = []
cpc_total_failure = []
small_failure_type = [[], [], []]
large_failure_type = [[], [], []]
density_list = []

for i in range(20, 71, 5):
    with open("res/density_{}.csv".format(i), 'r') as f:
        header = f.readline()
        baseline_small = 0
        baseline_large = 0
        for (idx, line) in enumerate(f.readlines()):
            baseline_small += float(line.split(',')[1])
            baseline_large += float(line.split(',')[2])
            small_failure_type[idx].append(float(line.split(',')[1]))
            large_failure_type[idx].append(float(line.split(',')[2]))
        small_total_failure.append(baseline_small)
        large_total_failure.append(baseline_large)
        classic_total_failure.append(0)
        cpc_total_failure.append(0)
    density_list.append(str(round(i/100, 2)))

plt.rcParams['font.size'] = 12

fig, ax = plt.subplots()

ax.plot([v for v in small_total_failure], label='Base Small', marker='v', fillstyle='none', color='black', lw=0.5, markersize=10)
ax.plot([v for v in large_total_failure], label='Base Large', marker='o', fillstyle='none', color='black', lw=0.5, markersize=10)
ax.plot([v for v in classic_total_failure], label='Ours Classic', marker='s', fillstyle='none', color='black', lw=0.5)
ax.plot([v for v in cpc_total_failure], label='Ours CPC', marker='x', color='black', lw=0.5, markersize=10)

ax.set_xlabel('Density')
ax.set_ylabel('Critical Failure Ratio')

plt.xticks([i for i in range(len(density_list))], density_list)

plt.legend(bbox_to_anchor=(0.62, 0.6))
# plt.show()
fig.savefig('res/fig11b.png')
print("Fig. 11b Saved")
# fig.savefig('res/fig11_density.eps', format='eps')

### Failure Type for baseline

fig, ax = plt.subplots(figsize=(7, 5))
axis_list = [i*1.1 for i in range(0, len(density_list))]

s_bar_list = [plt.bar([i-0.15 for i in axis_list], [sum(i) for i in zip(*small_failure_type)], align='center', width=0.2, color='white', edgecolor='black', hatch='//'),
              plt.bar([i-0.15 for i in axis_list], [a+b for a, b, _ in zip(*small_failure_type)], align='center', width=0.2, color='lightgray', edgecolor='black', hatch='//'),
              plt.bar([i-0.15 for i in axis_list], small_failure_type[0], align='center', width=0.2, color='lightgray', edgecolor='black'),]

l_bar_list = [plt.bar([i+0.15 for i in axis_list], [sum(i) for i in zip(*large_failure_type)], align='center', width=0.2, color='white', edgecolor='black', hatch='//'),
              plt.bar([i+0.15 for i in axis_list], [a+b for a, b, _ in zip(*large_failure_type)], align='center', width=0.2, color='lightgray', edgecolor='black', hatch='//'),
              plt.bar([i+0.15 for i in axis_list], large_failure_type[0], align='center', width=0.2, color='lightgray', edgecolor='black'),]

ax.set_xlabel('Density')
ax.set_ylabel('Critical Failure Ratio')

l1 = mpatches.Patch(color='white', hatch='///', label='Deadline Miss',)
l2 = mpatches.Patch(color='lightgray', hatch='///', label='Both')
l3 = mpatches.Patch(color='lightgray', label='Unacceptable Result')

l1.set_edgecolor('black') ; l2.set_edgecolor('black') ; l3.set_edgecolor('black')
plt.legend(handles=[l1, l2, l3], bbox_to_anchor=(0.47, 0.99))

plt.xticks(axis_list, ['S  L\n'+i for i in ['0.20', '0.25', '0.30', '0.35', '0.40', '0.45', '0.50', '0.5', '0.60', '0.65', '0.70']])

# plt.show()
# fig.savefig('res/fig11_failure.eps', format='eps')
fig.savefig('res/fig11c.png')
print("Fig. 11c Saved")