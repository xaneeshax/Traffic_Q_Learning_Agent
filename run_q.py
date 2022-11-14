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
        #self.step_time = {-1: 0}

        # Store wait time by lane
        #self.wait_times_by_lane = {}
        # Get wait time accumulated at each step
        #self.step_time_by_lane = {-1: 0}
        
        # Wait time prev step
        self.prev_wait = None
        # Wait time by lane current step
        self.cur_wait = None

        # Store lane information
        self.lanes = ["426843745#0", "798289594#3", "-8644213#9", "102519704#0", "426843743", "798289594#0", "8644213#8",
                      "426493699#0"]

        # Store q values in this form:
        # {lane_x_has_most_cars: {action_1: q_val, action_2: q_val, ..., action_n: q_val}, ...,
        # lane_z_has_most_cars: {{action_1: q_val, action_2: q_val, ..., action_n: q_val}}
        self.qs = {}
        self.alpha = 0.01
        self.gamma = 0.9
        self.epsilon = 0.5
        #phases_0 = (traci.trafficlight.Phase(duration=20.0,
        #state='GGGgrGrrrrrrGrrrr', minDur=20.0, maxDur=20.0, next=()))
        #print(phases_0)
        #logic = traci.trafficlight.Logic(programID='0', type=0,
        #currentPhaseIndex=0, phases = phases_0, subParameter={})
        #traci.trafficlight.setRedYellowGreenState(self.junction,
        #'GGGgrGrrrrrrGrrrr')
        #print(traci.trafficlight.getRedYellowGreenState(self.junction))

    def run_simulation(self):
        step = 0
        
        while step < 10000:
            # Get current light state
            cur_state = traci.trafficlight.getRedYellowGreenState(self.junction)

            # Get possible actions, choose one randomly and save value, take step in simulation
            #actions = self.getLegalActions(cur_state)
            #action = random.choice(actions)
            action = self.getAction(cur_state)
            self.actions_taken.append(action)
            # Get current longest lane
            lane = self.findLongestQueueLane()
            # Current wait times
            #self.getWaitTime(step)
            # Set traffic light and step
            traci.trafficlight.setRedYellowGreenState(self.junction, action)
            traci.simulationStep()

            # Get updated wait time; reward is how much shorter the wait is now
            self.updateWaitTime(step)
            reward = self.prev_wait - self.cur_wait
            # Find new current longest lane
            afterStepLongestLane = self.findLongestQueueLane()
            # Update q values
            self.update_qs(lane, action, afterStepLongestLane, reward)

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

        #total_waiting_time = sum(self.wait_times.values())
        #print(self.actions_taken)
        #print(self.qs)
        #traci.close()

    def updateWaitTime(self, step):
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
        if step == 0:
            self.prev_wait = 0
            self.cur_wait = 0
        else:
            step_wait = 0
            for lane in self.lanes:
                indiv_wait_time = traci.edge.getWaitingTime(lane)
                # update this car's wait time wait_times dict
                self.wait_times[lane] = indiv_wait_time
                step_wait += indiv_wait_time
            self.prev_wait = self.cur_wait
            self.cur_wait = step_wait
            
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
        if step == 0:
            self.step_time_by_lane[0] = sum([traci.edge.getWaitingTime(lane) for lane in self.lanes])
        else:
            self.step_time_by_lane[step] = sum([traci.edge.getWaitingTime(lane) for lane in self.lanes]) - self.step_time_by_lane[step - 1]
        for lane in self.lanes:
            indiv_wait_time = traci.edge.getWaitingTime(lane)
            self.wait_times_by_lane[lane].append(indiv_wait_time)
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

    def findLongestQueueLane(self):
        num_vehs = {}
        for lane in self.lanes:
            num_vehs[lane] = traci.edge.getLastStepVehicleNumber(lane)
        # Get lane with most vehicles waiting
        return max(num_vehs, key = num_vehs.get)
        

    def getQValue(self, max_lane, action):
        if max_lane in self.qs:
            if action in self.qs[max_lane]:
                return self.qs[max_lane][action]
        return 0

    def computeValueFromQValues(self, lane, ryg_state):
        actions = self.getLegalActions(ryg_state)
        lane = self.findLongestQueueLane()
        # Current max value is first action
        val = self.getQValue(lane, actions[0])
        # Iterate through actions
        for i in range(1, len(actions)):
            # If this action produces a higher Q value, save it as val
            new_val = self.getQValue(lane, actions[i])
            if new_val > val:
                val = new_val
        return val

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

    def computeActionFromQValues(self, ryg_state):
        actions = self.getLegalActions(ryg_state)
        # Action to return, initialize to first action
        action = actions[0]
        lane = self.findLongestQueueLane()
        # Q value for best action
        val = self.getQValue(lane, action)
        # Iterate through all actions
        for i in range(1, len(actions)):
            new_val = self.getQValue(lane, actions[i])
            # If this actions's Q value is greater than current, save action and update val
            if new_val > val:
                action = actions[i]
                val = new_val
        return action

    def getAction(self, ryg_state):
        # Flip coin with probability epsilon
        flip = random.random()
        if flip < self.epsilon:
            return random.choice(self.getLegalActions(ryg_state))
        return self.computeActionFromQValues(ryg_state)

    def update_qs(self, lane, action, afterStepLongestLane, reward):
        # Initialize nested dictionary if not yet initialized
        if lane not in self.qs.keys():
            self.qs[lane] = {}
        cur_q = self.getQValue(lane, action)
        next_q = self.computeValueFromQValues(afterStepLongestLane, action)
        self.qs[lane][action] = cur_q + self.alpha * (reward + self.gamma * next_q - cur_q)

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
    sim.run_simulation()
    #sim.set_tfl()
    traci.close()
