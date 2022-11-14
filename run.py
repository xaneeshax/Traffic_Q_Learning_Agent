import traci
import traci.constants as tc
import random


def run_simulation():

    step = 0
    # Store wait time of each car in the simulation
    wait_times = {}
    # Get wait time accumulated at each step
    step_time = {-1: 0}

    while step < 100:
        # Take the next step
        traci.simulationStep()

        # Cars in the current frame
        cars_in_sim = traci.vehicle.getIDList()

        # Traffic Lights in the Intersection (should be about 18)
        traffic_lights = traci.trafficlight.getIDList()
        print("tls", traffic_lights)

        # End simulation if there are no more cars in play
        if len(cars_in_sim) == 0:
            break

        step_time[step] = sum(
            [traci.vehicle.getAccumulatedWaitingTime(car) for car in cars_in_sim]) - step_time[step - 1]
        # print(step_time)

        for car in cars_in_sim:
            indiv_wait_time = traci.vehicle.getAccumulatedWaitingTime(car)
            #print("Lane ID", traci.vehicle.getLaneID(car))
            #print("Upcoming Traffic Lights: ", traci.vehicle.getNextTLS(car))
            # print(car, traci.vehicle.getSpeed(
            #     car), traci.vehicle.getDistance(car))

            # update this car's wait time wait_times dict
            wait_times[car] = indiv_wait_time

        for light in traffic_lights:
            tl_state = traci.trafficlight.getRedYellowGreenState(light)
            tl_phase_duration = traci.trafficlight.getPhaseDuration(light)
            # Get info about the traffic light settings
            # tl_lanes_controlled = traci.trafficlight.getControlledLanes(light)
            # tl_program = traci.trafficlight.getCompleteRedYellowGreenDefinition(light)
            tl_next_switch = traci.trafficlight.getNextSwitch(light)
            # print(step, "tl", tl_state, tl_phase_duration, tl_lanes_controlled,
            #       tl_program, tl_next_switch)

        step += 1

    total_waiting_time = sum(wait_times.values())
    traci.close()


def set_tfl():
    # Setting traffic light timtes
    # REF: https://sumo.dlr.de/docs/TraCI/Change_Traffic_Lights_State.html
    traffic_signal = ["rrrrrrGGGGgGGGrr", "yyyyyyyyrrrrrrrr", "rrrrrGGGGGGrrrrr",
                      "rrrrryyyyyyrrrrr", "GrrrrrrrrrrGGGGg", "yrrrrrrrrrryyyyy"]
    tfl = "cluster_1325750409_61423879_7746155458"
    traci.trafficlight.setPhaseDuration(
        tfl, random.randrange(1, 10))
    traci.trafficlight.setRedYellowGreenState(
        tfl, random.choice(traffic_signal))
    print("here")
    traci.close()


if __name__ == "__main__":

    # Connect to Script and intiate step counter
    traci.start(
        ["sumo", "-c", "/Users/aneesha/sumo/tools/2022-11-10-00-32-34/osm.sumocfg"])
    run_simulation()
    set_tfl()
