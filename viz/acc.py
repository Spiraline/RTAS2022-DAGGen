import matplotlib.pyplot as plt
import pandas as pd

plot_df = pd.read_csv('res/acc.csv', header=None)

plt.rcParams['font.size'] = 12

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
fig.subplots_adjust(hspace=0.05)

ax1.boxplot([plot_df[0], plot_df[1], plot_df[2], plot_df[3]], medianprops={'color':'gray', 'linestyle':':'}, sym='')
ax2.boxplot([plot_df[0], plot_df[1], plot_df[2], plot_df[3]], medianprops={'color':'gray', 'linestyle':':'}, sym='')

ax1.set_ylim(0.78, 1.01)
ax2.set_ylim(0, 0.22)

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
plt.xticks([1, 2, 3, 4], ['Base Small', 'Base Large', 'Ours Classic', 'Ours CPC'])

plt.show()
fig.savefig("res/fig11_acc.eps", format='eps')