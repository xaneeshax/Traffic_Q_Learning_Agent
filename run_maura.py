import traci
import traci.constants as tc
import random

class Sim():

    def __init__(self):
        # Traffic light junction ID
        self.junction = 'J0'
        # Full logic definition of light settings at junction
        self.full_def = traci.trafficlight.getCompleteRedYellowGreenDefinition(self.junction)[0]
        # Possible traffic light states for this junction
        self.states = [phase.state for phase in self.full_def.phases]
        # Record of light states (one for each step in simulation)
        self.actions_taken = []
        # Store wait time of each car in the simulation
        self.wait_times = {}
        # Get wait time accumulated at each step
        self.step_time = {-1: 0}

        # Store wait time by lane
        self.wait_times_by_lane = {}
        # Get wait time accumulated at each step
        self.step_time_by_lane = {-1: 0}

        # Store lane information
        self.lanes = ["426843745#0", "798289594#3", "-8644213#9", "102519704#0", "426843743", "798289594#0", "8644213#8",
                      "426493699#0"]
        #phases_0 = (traci.trafficlight.Phase(duration=20.0,
        #state='GGGgrGrrrrrrGrrrr', minDur=20.0, maxDur=20.0, next=()))
        #print(phases_0)
        #logic = traci.trafficlight.Logic(programID='0', type=0,
        #currentPhaseIndex=0, phases = phases_0, subParameter={})
        #traci.trafficlight.setRedYellowGreenState(self.junction,
        #'GGGgrGrrrrrrGrrrr')
        #print(traci.trafficlight.getRedYellowGreenState(self.junction))

    def run_simulation_random(self):
        
        step = 0
        
        while step < 100:
            # Get current light state
            cur_state = traci.trafficlight.getRedYellowGreenState(self.junction)

            # Get possible actions, choose one randomly and save value, take step in simulation
            actions = self.getLegalActions(cur_state)
            action = random.choice(actions)
            self.actions_taken.append(action)
            traci.trafficlight.setRedYellowGreenState(self.junction, action)
            traci.simulationStep()

            #print(self.getWaitTime(step))
            
            '''
            for light in traffic_lights:
                tl_state = traci.trafficlight.getRedYellowGreenState(light)
                tl_phase_duration = traci.trafficlight.getPhaseDuration(light)
                # Get info about the traffic light settings
                # tl_lanes_controlled =
                # traci.trafficlight.getControlledLanes(light)
                # tl_program =
                # traci.trafficlight.getCompleteRedYellowGreenDefinition(light)
                tl_next_switch = traci.trafficlight.getNextSwitch(light)
                # print(step, "tl", tl_state, tl_phase_duration,
                # tl_lanes_controlled,
                #       tl_program, tl_next_switch)
                '''
            # End simulation if there are no more cars in play
            if len(traci.vehicle.getIDList()) == 0:
                break

            step += 1

        total_waiting_time = sum(self.wait_times.values())
        #print(self.actions_taken)
        #traci.close()

    def getWaitTime(self, step):
        step_wait_time = 0
        # Cars in the current frame
        #cars_in_sim = traci.vehicle.getIDList()

        #self.step_time[step] = sum([traci.vehicle.getAccumulatedWaitingTime(car) for car in cars_in_sim]) - self.step_time[step - 1]
        #print(self.step_time)
        #for car in cars_in_sim:
        #    indiv_wait_time = traci.vehicle.getAccumulatedWaitingTime(car)
            # update this car's wait time wait_times dict
        #    self.wait_times[car] = indiv_wait_time
        #    step_wait_time += indiv_wait_time
        self.step_time_by_lane[step] = sum([traci.edge.getWaitingTime(edge) for edge in self.lanes]) - self.step_time_by_lane[step - 1]
        for lane in self.lanes:
            indiv_wait_time = traci.edge.getWaitingTime(edge)
            self.wait_times_by_lane[lane] = indiv_wait_time
            step_wait_time += indiv_wait_time
        return step_wait_time

        '''
        # Traffic Lights in the Intersection (should be about 18)
        traffic_lights = traci.trafficlight.getIDList()
        #print("tls", traffic_lights)
        #print(traci.trafficlight.getCompleteRedYellowGreenDefinition(self.junction))
        '''
        
            #print("Lane ID", traci.vehicle.getLaneID(car))
            #print("Upcoming Traffic Lights: ",
            #traci.vehicle.getNextTLS(car))
            # print(car, traci.vehicle.getSpeed(
            #     car), traci.vehicle.getDistance(car))

            

    def getQValue(self):
        return 0

    def computeValueFromQValues(self):
        return 0

    def getLegalActions(self, ryg_state):
        # Here I just manually found what legal following states are
        # Pulled ones that follow rules from all light states given by SUMO
        # Self (don't change), or a red can become green, a yellow can become
        # red, a green can become yellow
        if ryg_state == 'GGGgrGrrrrrrGrrrr':
            return [ryg_state, 'yyyyryrrrrrryrrrr']
        if ryg_state == 'yyyyryrrrrrryrrrr':
            return [ryg_state, 'rrrrGrrrrGGrrrrrr', 'rrrrrrrrrGGGrrrrr', 'rrrrrGGggrrrrGGgg']
        if ryg_state == 'rrrrGrrrrGGrrrrrr':
            return [ryg_state, 'rrrryrrrryyrrrrrr']
        if ryg_state == 'rrrryrrrryyrrrrrr':
            return [ryg_state, 'GGGgrGrrrrrrGrrrr', 'rrrrrGGggrrrrGGgg']
        if ryg_state == 'rrrrrrrrrGGGrrrrr':
            return [ryg_state, 'rrrrrrrrryyyrrrrr']
        if ryg_state == 'rrrrrrrrryyyrrrrr':
            return [ryg_state, 'GGGgrGrrrrrrGrrrr', 'rrrrrGGggrrrrGGgg']
        if ryg_state == 'rrrrrGGggrrrrGGgg':
            return [ryg_state, 'rrrrryyyyrrrryyyy']
        if ryg_state == 'rrrrryyyyrrrryyyy':
            return [ryg_state, 'rrrrrrrrrGGGrrrrr', 'rrrrGrrrrGGrrrrrr']
        raise Exception('Unknown light state encountered - don\'t know possible next moves')

    def getActionFromQValues(self):
        return 0

    def getAction(self):
        return 'GGGgrGrrrrrrGrrrr'

    def set_tfl(self):
        # Setting traffic light timtes
        # REF: https://sumo.dlr.de/docs/TraCI/Change_Traffic_Lights_State.html
        traffic_signal = ["rrrrrrGGGGgGGGrr", "yyyyyyyyrrrrrrrr", "rrrrrGGGGGGrrrrr",
                          "rrrrryyyyyyrrrrr", "GrrrrrrrrrrGGGGg", "yrrrrrrrrrryyyyy"]
        tfl = "J0"
        #traci.trafficlight.setPhaseDuration(
        #    tfl, random.randrange(1, 10))
        #traci.trafficlight.setRedYellowGreenState(
        #    tfl, random.choice(traffic_signal))
        #print("here")
        print(traci.trafficlight.getPhase(tfl))
        traci.close()

    


if __name__ == "__main__":

    # Connect to Script and intiate step counter
    traci.start(["sumo", "-c", "C:/Users/Maura/OneDrive - Northeastern University/Artificial Intelligence/Traffic_Q_Learning_Agent/osm.sumocfg"])
        #["sumo", "-c",
        #"/Users/aneesha/sumo/tools/2022-11-10-00-32-34/osm.sumocfg"])
    sim = Sim()
    sim.run_simulation_random()
    #sim.set_tfl()
    traci.close()
