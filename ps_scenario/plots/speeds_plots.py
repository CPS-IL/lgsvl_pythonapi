import matplotlib.pyplot as plt
import numpy as np
import os


# https://www.geeksforgeeks.org/get-parent-of-current-directory-using-python/
# function to get parent
def getParent(path, levels = 1):
    common = path
    for i in range(levels + 1):
        common = os.path.dirname(common)
    return common, os.path.relpath(path, common)

# Due to manual start of simulation, variable amounts of samples are collected before actual start
# This function removes such preceding saples.
def remove_leading_junk(speeds):
    for i,speed in enumerate(speeds):
        if speed >= 1:
            break
    if i > 0:
        return speeds[i :]
    else:
        return speeds

# https://stackoverflow.com/questions/33159134/matplotlib-y-axis-label-with-multiple-colors
def multicolor_ylabel(ax,list_of_strings,list_of_colors,axis='x',anchorpad=0,**kw):
    """this function creates axes labels with multiple colors
    ax specifies the axes object where the labels should be drawn
    list_of_strings is a list of all of the text items
    list_if_colors is a corresponding list of colors for the strings
    axis='x', 'y', or 'both' and specifies which label(s) should be drawn"""
    from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, HPacker, VPacker

    # x-axis label
    if axis=='x' or axis=='both':
        boxes = [TextArea(text, textprops=dict(color=color, ha='left',va='bottom',**kw)) 
                    for text,color in zip(list_of_strings,list_of_colors) ]
        xbox = HPacker(children=boxes,align="center",pad=0, sep=5)
        anchored_xbox = AnchoredOffsetbox(loc=3, child=xbox, pad=anchorpad,frameon=False,bbox_to_anchor=(0.2, -0.09),
                                          bbox_transform=ax.transAxes, borderpad=0.)
        ax.add_artist(anchored_xbox)

    # y-axis label
    if axis=='y' or axis=='both':
        boxes = [TextArea(text, textprops=dict(color=color, ha='left',va='bottom',rotation=90,**kw)) 
                     for text,color in zip(list_of_strings[::-1],list_of_colors) ]
        ybox = VPacker(children=boxes,align="center", pad=0, sep=5)
        anchored_ybox = AnchoredOffsetbox(loc=3, child=ybox, pad=anchorpad, frameon=False, bbox_to_anchor=(-0.15, -0.15), 
                                          bbox_transform=ax.transAxes, borderpad=0.)
        ax.add_artist(anchored_ybox)

file_path = os.path.abspath(__file__)
scenarios_dir_path, _ = getParent(file_path, 1)
results_dir = os.path.join(scenarios_dir_path, "results")

fig, ax = plt.subplots(2, 1, figsize =(4, 1.5), sharex=True, sharey=True)

with open(os.path.join(results_dir, 'speed_mission.txt')) as f:
    mission_speeds = [float(line.rstrip()) for line in f]
with open(os.path.join(results_dir, 'speed_ps.txt')) as f:
    ps_speeds = [float(line.rstrip()) for line in f]

mission_speeds = remove_leading_junk(mission_speeds)
ps_speeds = remove_leading_junk(ps_speeds)

sample_count = min(len(mission_speeds), len(ps_speeds))
X = np.arange(0, sample_count * 0.01, 0.01)

mission_speeds = mission_speeds[: sample_count]
ps_speeds = ps_speeds[: sample_count]

ax[0].plot(X, mission_speeds, color="red", label="Mission")
ax[1].plot(X, ps_speeds, color="green", label="$\mathcal{PS}$")

ax[0].set_ylim(0, 11)
ax[1].set_ylim(0, 11)
ax[0].set_xlim(0, 31)
ax[1].set_xlim(0, 31)

ax[0].legend(loc="lower center")
ax[1].legend(loc="lower center")

multicolor_ylabel(ax[1], ["","Speed (m/s)"], ['black','white'], axis='y')
plt.xlabel("Time (s)")

plt.savefig(os.path.join(results_dir, "speeds.pdf"), format='pdf', bbox_inches='tight')