#! python
import lgsvl
import os
import time
import argparse
import json

ego = None
collision = False
MAP = "SingleLaneRoad"
sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)
result = [[],[],[]]
APOLLO_IP = "10.0.0.6" # Modify this to Apollo Host

REQUIRE_INPUT = True
REPS = 10
d_max  = 100
d_step = 10
v_step = 5
v_max  = 40 # m/s
RUNTIME_BUFFER = 20


def get_args():
    parser = argparse.ArgumentParser(description='Lets crash some cars')
    parser.add_argument('--vehicle', default="LincolnSafety",
                        help='Vehicle in [LincolnSafety, LincolnMission]')
    parser.add_argument('--infront', action="store_true",
                        help='Obstacle in front of ego vehicle, otherwise it is in the other lane')
    parser.add_argument('--scenario', default="mission",
                        help='Scenario name in [mission, ideal, fn]. Appends to result file name.')
    args  = parser.parse_args()
    return args


def on_collision(agent1, agent2, contact):
    global collision
    print("Collision")
    collision = True
    sim.stop()


def setup_ego(args):
    global ego, sim
    if sim.current_scene == MAP:
        sim.reset()
    else:
        sim.load(MAP)

    spawns = sim.get_spawn()
    state = lgsvl.AgentState()
    state.transform = spawns[0]
    ego = sim.add_agent(args.vehicle, lgsvl.AgentType.EGO, state)
    
    ego.connect_bridge(APOLLO_IP, 9090)
    while not ego.bridge_connected:
        print("Bridge connected:", ego.bridge_connected)
        time.sleep(1)
    
    ego.on_collision(on_collision)

    sensors = ego.get_sensors()
    for s in sensors:
        assert(s.enabled)

    c = lgsvl.VehicleControl()
    c.steering = 0
    ego.apply_control(c, sticky=True)

    # Let Apollo get ego vehicle state
    sim.run(time_limit = .5)
    # print("Ego Size:", ego.bounding_box.size.x, ego.bounding_box.size.y, ego.bounding_box.size.z)
    return ego


def setup_obstace(distance, infront = True):
    spawns = sim.get_spawn()
    forward = lgsvl.utils.transform_to_forward(spawns[0])
    right = lgsvl.utils.transform_to_right(spawns[0])
    state = lgsvl.AgentState()
    if infront:
        state.transform.position = spawns[0].position + (distance * forward)
    else :
        state.transform.position = spawns[0].position + (distance * forward) - (4 * right)
    state.transform.rotation = spawns[0].rotation
    npc = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)
    return npc


def ego_set_velocity(ego, velocity):
    spawns = sim.get_spawn()
    forward = lgsvl.utils.transform_to_forward(spawns[0])
    state = ego.state
    state.velocity = forward * velocity
    ego.state = state
    c = lgsvl.VehicleControl()
    c.steering = 0
    ego.apply_control(c, sticky=False)


def run_once(v, d, args):
    global ego, sim, collision
    if REQUIRE_INPUT: input("Press enter to start one run:")
    runtime = int(d / max(v, 1)) + RUNTIME_BUFFER
    collision = False
    print("Distance =", d, "Velocity =", v, "Running for secs:", runtime)
    ego = setup_ego(args)
    spawns = sim.get_spawn()
    up = lgsvl.utils.transform_to_up(spawns[0])
    npc = setup_obstace(d, args.infront)
    ego_set_velocity(ego, v)
    time.sleep(1) # Let cyber-rt catch up
    sim.run(time_limit = runtime) # 0 means run indefinitely
    if not ego.bridge_connected:
        res = "Disconnected"
    elif collision:
        res = "Collision"
    # Ego can fall off the map, ensure that has not happened.
    elif (ego.state.transform.position.y > (-up * 1).y):
        # Origin for X seems to be at the end of map, so invert check
        if (ego.state.transform.position.x < npc.state.transform.position.x):
            res = "Safe Take Over"
        else:
            res = "Safe"
    else:
        res = "Off Map"
    return res

def merge_res(r):
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

def main():
    global ego, sim
    args = get_args()
    ego = setup_ego(args)
    input("Set up route in Apollo Dreamview and then press enter here:")

    for v in range(v_step, v_max + 1, v_step):
        for d in range(d_step, d_max + 1, d_step):
            for _ in range(REPS):
                result[0].append(v)
                result[1].append(d)
                result[2].append(run_once(v, d, args))

    with open("res_" + args.scenario + ".json", 'w') as res_file:
        json.dump(result, res_file)

if __name__ == "__main__":
    main()
