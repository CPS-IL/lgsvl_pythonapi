#! python

# The result file for this scenario are generated in Apollo, by logging speed samples to text files.
# These text files are manually copied to results directory.

import lgsvl
import os
import matplotlib.pyplot as plt

from sudden_stop import get_args, setup_ego, run_once

ego = None
sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)
result = [[],[],[]]

d  = 50
v = 1

def main():
    global ego, sim
    args = get_args()
    ego = setup_ego(args)
    input("Set up route in Apollo Dreamview and then press enter here:")

    while (True):
        i = input("Press enter to run once, else enter q or Q to exit")
        if i == "Q" or i == "q":
            break
        run_once(v, d, args)

if __name__ == "__main__":
    main()