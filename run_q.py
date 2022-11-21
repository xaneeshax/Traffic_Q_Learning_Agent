<<<<<<< HEAD
import traci
import traci.constants as tc
import random

class Sim():

    def __init__(self, epsilon = 0.5, iters = 1000):
        # Traffic light junction ID
        self.junction = 'J0'
        # Full logic definition of light settings at junction
        self.full_def = traci.trafficlight.getCompleteRedYellowGreenDefinition(self.junction)[0]
        # Possible traffic light states for this junction
        self.states = [phase.state for phase in self.full_def.phases]
        # Record of light states (one for each step in simulation)
        self.actions_taken = []
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
        self.epsilon = epsilon
        self.step = 0
        # Number of iterations
        self.iters = iters

    def run_simulation(self):
        
        while self.step < self.iters:
            # Get current light state
            cur_state = traci.trafficlight.getRedYellowGreenState(self.junction)
            # Get action to take
            action = self.getAction(cur_state)
            # Set traffic light to action and step
            traci.trafficlight.setRedYellowGreenState(self.junction, action)
            traci.simulationStep()

            # Get updated wait time; reward is how much shorter the wait is now
            self.updateWaitTime()
            reward = self.prev_wait - self.cur_wait
            # Get current longest lane
            lane = self.findLongestQueueLane()
            # Find new current longest lane
            afterStepLongestLane = self.findLongestQueueLane()
            # Update q values
            self.update_qs(lane, action, afterStepLongestLane, reward)

            # End simulation if there are no more cars in play
            if len(traci.vehicle.getIDList()) == 0:
                break

            self.step += 1

    def updateWaitTime(self):
        step_wait_time = 0
        # 0 for wait time if step is 0
        if self.step == 0:
            self.prev_wait = 0
            self.cur_wait = 0
        else:
            step_wait = 0
            for lane in self.lanes:
                # Get wait time in late
                indiv_wait_time = traci.edge.getWaitingTime(lane)
                step_wait += indiv_wait_time
            self.prev_wait = self.cur_wait
            self.cur_wait = step_wait

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
        # Yellow light must be at least 3 steps long to avoid emergency stops
        # Note: ryg_state is the same as self.actions_taken[-1]
        if 'y' in ryg_state:
            # Make sure enough actions have been taken - if not enough have been taken, can't check prev states
            if len(self.actions_taken) > 2:
                # If the 2 actions before this one aren't the same as this one, light must then stay the same
                if self.actions_taken[-2] != ryg_state or self.actions_taken[-3] != ryg_state:
                    return [ryg_state]
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
            action =  random.choice(self.getLegalActions(ryg_state))
        else:
            action = self.computeActionFromQValues(ryg_state)
        self.actions_taken.append(action)
        return action


    def update_qs(self, lane, action, afterStepLongestLane, reward):
        # Initialize nested dictionary if not yet initialized
        if lane not in self.qs.keys():
            self.qs[lane] = {}
        cur_q = self.getQValue(lane, action)
        next_q = self.computeValueFromQValues(afterStepLongestLane, action)
        self.qs[lane][action] = cur_q + self.alpha * (reward + self.gamma * next_q - cur_q)


if __name__ == "__main__":
    # Run randomly
    # Connect to Script and intiate step counter
    traci.start(["sumo", "-c", "C:/Users/Maura/OneDrive - Northeastern University/Artificial Intelligence/Traffic_Q_Learning_Agent/osm.sumocfg"])
        #["sumo", "-c",
        #"/Users/aneesha/sumo/tools/2022-11-10-00-32-34/osm.sumocfg"])
    sim_rand = Sim(epsilon = 1)
    sim_rand.run_simulation()
    #print(sim_rand.actions_taken)
    print(sim_rand.qs)
    traci.close()

    # Run with q learning
    # Connect to Script and intiate step counter
    traci.start(["sumo", "-c", "C:/Users/Maura/OneDrive - Northeastern University/Artificial Intelligence/Traffic_Q_Learning_Agent/osm.sumocfg"])
        #["sumo", "-c",
        #"/Users/aneesha/sumo/tools/2022-11-10-00-32-34/osm.sumocfg"])
    sim_q = Sim()
    sim_q.run_simulation()
    #print(sim_q.actions_taken)
    print(sim_q.qs)
    traci.close()
=======
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

            # End simulation if there are no more cars in play
            if len(traci.vehicle.getIDList()) == 0:
                break

            step += 1

    def updateWaitTime(self, step):
        step_wait_time = 0
        # 0 for wait time if step is 0
        if step == 0:
            self.prev_wait = 0
            self.cur_wait = 0
        else:
            step_wait = 0
            for lane in self.lanes:
                # Get wait time in late
                indiv_wait_time = traci.edge.getWaitingTime(lane)
                step_wait += indiv_wait_time
            self.prev_wait = self.cur_wait
            self.cur_wait = step_wait

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


if __name__ == "__main__":

    # Connect to Script and intiate step counter
    traci.start(["sumo", "-c", "C:/Users/Maura/OneDrive - Northeastern University/Artificial Intelligence/Traffic_Q_Learning_Agent/osm.sumocfg"])
        #["sumo", "-c",
        #"/Users/aneesha/sumo/tools/2022-11-10-00-32-34/osm.sumocfg"])
    sim = Sim()
    sim.run_simulation()
    print(sim.actions_taken)
    print(sim.qs)
    traci.close()
>>>>>>> 3af2b03521fb3cb4a345c3792f9f88a8b140b9a7
