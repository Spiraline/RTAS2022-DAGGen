import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams['font.size'] = 12
pd_csv = pd.read_csv('res/acc.csv', header=0)

header = list(pd_csv.keys())

# Separate two subplots to make broken y-axis chart
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
fig.subplots_adjust(hspace=0.05)

ax1.boxplot(pd_csv, medianprops={'color':'gray', 'linestyle':':'}, sym='')
ax2.boxplot(pd_csv, medianprops={'color':'gray', 'linestyle':':'}, sym='')

ax1.set_ylim(0.78, 1.01)
ax2.set_ylim(0, 0.22)

# Make Broken points
ax1.spines["bottom"].set_visible(False)
ax2.spines["top"].set_visible(False)
ax1.xaxis.tick_top()
ax1.tick_params(labeltop=False)
ax2.xaxis.tick_bottom()
d = .5
kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
              linestyle="none", color='k', mec='k', mew=1, clip_on=False)
ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

# Acceptable Bar
ax1.axhline(0.95, color='black', lw=2, linestyle="--")

# X ticks
plt.xticks([i+1 for i in range(len(header))], header)

# plt.show()
fig.savefig("res/fig11_acc.png")
# fig.savefig("res/fig11_acc.eps", format='eps')