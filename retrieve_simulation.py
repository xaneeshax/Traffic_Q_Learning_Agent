# based off of training_simulation.py in reference project
# retriving information from the vehicles in the traci simulation

import traci
import numpy as np

class Simulation:

    # i didn't use this, but ideally we would pass in values for these parameters

    # def __init__(self, sumoCMD, maxSteps, numStates):
    #
    #     self.sumoCmd = sumoCMD
    #
    #     self.step = 0
    #     # how many steps we want the simulation to run for
    #     self.max_steps = maxSteps
    #
    #     self.num_states = numStates

    # run an episode of the simulation
    def run(self):

        # sumo command
        sumocmd = ["sumo", "-c", "osm.sumocfg"]

        # start the traci simulation and connect to script
        traci.start(sumocmd)
        step = 0

        # dict to store wait time of each car in the simulation
        wait_times = {}
        while step < 1000:
            traci.simulationStep()

            cars_in_sim = traci.vehicle.getIDList()

            for car in cars_in_sim:
                indiv_wait_time = traci.vehicle.getAccumulatedWaitingTime(car)
                # update this car's wait time wait_times dict
                wait_times[car] = indiv_wait_time

            step += 1

            # todo: need to remove car from waiting time if it has cleared the intersection


        # print accumulated wait time of each car
        for entry in wait_times:
            print(wait_times[entry])

        traci.close()
        total_waiting_time = sum(wait_times.values())

        # print(total_waiting_time)



# running a simulation and printing the total waiting time for 1000 steps
if __name__ == "__main__":

    sim_object = Simulation()

    sim_object.run()

