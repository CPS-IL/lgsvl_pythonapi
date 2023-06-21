#!/usr/bin/env python3

import matplotlib.pyplot as plt
import math
import numpy as np
import json
import os
import sys


results_dir = None
hatches = ['/', '\\', '\\/...', '//', '-',  '|', '+']
REPS = 10 # For each configuration we run 10 repetitions
v_max_safe = 17.71 # Based on analysis presented in the paper.
v_max = 40 # maximum speed for testing, higher values were also run, but results for all speeds >= 40 are identical

# https://www.geeksforgeeks.org/get-parent-of-current-directory-using-python/
# function to get parent
def getParent(path, levels = 1):
    common = path
    for i in range(levels + 1):
        common = os.path.dirname(common)
    return common, os.path.relpath(path, common)

def merge_res_wc(r):
    if "Collision" in r:
        return "Collision"
    elif "Safe Take Over" in r:
        return "Safe Take Over"
    elif "Safe" in r:
        return "Safe"
    elif "Off Map" in r:
        return "Off Map"
    else:
        assert(0)

def count_res(res_files):
    c_collision = 0
    c_takeover = 0
    c_stop = 0
    c_offmap = 0
    for res_file in res_files.values():
        with open(res_file[1]) as f:
            results = json.load(f)
            for i,r in enumerate(results[2]):
                if results[0][i] > v_max: # we ran higher v but > 40 is not included in plots
                    continue
                if r == "Collision":
                    c_collision += 1
                elif r == "Safe":
                    c_stop += 1 
                elif r == "Off Map":
                    c_offmap += 1
                elif r == "Safe Take Over":
                    c_takeover += 1
    c_total = c_collision + c_stop + c_takeover + c_offmap
    print ("Invalid Ratio", c_offmap/c_total)

def plot_one_res_everything(res_file, name):
    with open(res_file[1]) as f:
        results = json.load(f)

    _, ax = plt.subplots(figsize=(3, 3))
    ax.set_ylim(0, max(results[0]) + 2) # Velocity
    ax.set_xlim(0, max(results[1]) + 5) # Distance
    plt.axhline(y=v_max_safe, color='blue', linestyle='--')

    line_x = range(0, max(results[1]) + 5, 1)
    line_y = [math.sqrt(2 * 7.5 * x) for x in line_x]
    # line = Line2D(line_x, line_y)

    ax.fill_between(line_x, line_y, color='#2ca02c', alpha=.2)
    i = 0
    while (i < len(results[0])):
        if results[0][i] <= v_max: # we ran higher v but > 40 yields no new results
            r = merge_res_wc(results[2][i : i + REPS])
            if r == "Collision":
                ax.scatter (results[1][i], results[0][i], c='#d62728', marker='x')
            elif r == "Safe":
                ax.scatter (results[1][i], results[0][i], c='#2ca02c', marker='o')
            elif r == "Off Map":
                ax.scatter (results[1][i], results[0][i], c='blue', marker='o')
            elif r == "Safe Take Over":
                ax.scatter (results[1][i], results[0][i], c='#2ca02c', marker='+')
        i += REPS

    plt.grid(False)
    plt.xlabel("Initial Distance d(0) (m)")
    plt.ylabel("Initial velocity v(0) (m/s)")
    plt.ylim(0, v_max + 3)
    
    plt.savefig(os.path.join(results_dir, name + ".pdf"), format='pdf', bbox_inches='tight')


def plot_all_res_collision_speeds():
    fig = plt.subplots(figsize =(6, 3))
    
    speed_bucket_max = [0, 10, 20, 30, 40, 50]
    barWidth = 1/len(speed_bucket_max)
    br = []
    hatch_index = 0
    # set height of bar
    for res_file in res_files.values():
        data =  np.random.randint(1, 51, 6)

        # Set position of bar on X axis    
        if len(br) == 0: br = np.arange(len(data))
        else: br = [x + barWidth for x in br]

        # Make the plot
        plt.bar(br, data, width = barWidth, label = res_file[0], hatch = hatches[hatch_index],
                edgecolor ='black')
        hatch_index += 1
    
    # Adding Xticks
    plt.xlabel('Collision Speed (m/s)')
    plt.ylabel('Count')
    plt.xticks([r + barWidth for r in range(len(data))],
            ['0', '0-10', '10-20', '20-30', '30-40', "40-50"])
    
    plt.legend(loc='upper center', ncol=2, bbox_to_anchor=(0.5, 1.25))
    plt.savefig(os.path.join(results_dir, "collision_speeds.pdf"), format='pdf', bbox_inches='tight')
    sys.exit(-1)

def plot_all_res_outcomes(res_files, vms, below_only):
    fig = plt.subplots(figsize =(5, 2))
    outcomes = [
        "Collision\n" + "Safety " + u'\u2718' + "\n" + "Mission " + u'\u2718' + "\n",
        "Safe Stop\n" + "Safety " + u'\u2714' + "\n" + "Mission " + u'\u2718' + "\n",
        "Safe Pass\n" + "Safety " + u'\u2714' + "\n" + "Mission " + u'\u2714' + "\n"
        ]
    barWidth = 1/5
    br = []
    hatch_index = 0
    # set height of bar
    for res_file in res_files.values():
        with open(res_file[1]) as f:
            results = json.load(f)

        data = [0, 0, 0] # Collision, Safe Stop, Safe Overtake
        for i in range(len(results[2])):
            if results[0][i] > v_max:
                continue
            if below_only:
                if results[0][i] > vms:
                    continue
            else:
                if results[0][i] <= vms:
                    continue

            if results[2][i] == "Collision":
                data[0] += 1
            elif results[2][i] == "Safe":
                data[1] += 1
            elif results[2][i] == "Off Map":
                pass # Ignore cases when vehicle goes off map
            elif results[2][i] == "Safe Take Over":
                data[2] += 1
       
        # Set position of bar on X axis    
        if len(br) == 0: br = np.arange(len(data))
        else: br = [x + barWidth for x in br]

        # Make the plot
        plt.bar(br, data, width = barWidth, label = res_file[0], hatch = hatches[hatch_index],
                edgecolor ='black')
        hatch_index += 1

    plt.ylabel('Count')
    plt.xticks([r + barWidth for r in range(len(data))], outcomes)
    plt.ylim(0,500)

    if below_only:
        plt.legend(bbox_to_anchor=(1.01, .25, .2, 0.1), loc="lower left", mode="expand", borderaxespad=0, ncol=1)
        output_name = "outcomes_below.pdf"
    else:
        output_name = "outcomes_above.pdf"
    plt.savefig(os.path.join(results_dir, output_name), format='pdf', bbox_inches='tight')



file_path = os.path.abspath(__file__)
scenarios_dir_path, _ = getParent(file_path, 1)
results_dir = os.path.join(scenarios_dir_path, "results")


res_files = {
   "Mission_Only"  : ["$\mathcal{MO}$",               os.path.join(results_dir, 'res_mission.json')],
   "Mission_Crash" : ["$\mathcal{MC}$",  os.path.join(results_dir, 'res_ideal.json')],
   "Force_FN"      : ["$\mathcal{FI}$", os.path.join(results_dir, 'res_fn.json')],
}

count_res(res_files)

plot_all_res_outcomes(res_files, v_max_safe, True)
plot_all_res_outcomes(res_files, v_max_safe, False)

for name in res_files:
    plot_one_res_everything(res_files[name], name)
