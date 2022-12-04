import traci
import traci.constants as tc
import random
import pandas as pd
#import plotly.graph_objects as go

# Path to the osm.sumocfg file
ANEESHA_PATH = "/Users/aneesha/sumo/tools/2022-11-10-00-32-34/osm.sumocfg"
MAURA_PATH = "C:/Users/Maura/OneDrive - Northeastern University/Artificial Intelligence/Traffic_Q_Learning_Agent/osm.sumocfg"
MAURA_PATH_OPTIMAL = "C:/Users/Maura/OneDrive - Northeastern University/Artificial Intelligence/Traffic_Q_Learning_Agent/Optimized/osm.sumocfg"


class Sim():

    def __init__(self, epsilon=0.5, iters=10000, alpha=0.01, gamma=0.9, visualizer=False, qs = {}):
        # Traffic Light Junction ID
        self.junction = 'J0'
        # Full logic definition of light settings at junction
        self.full_def = traci.trafficlight.getCompleteRedYellowGreenDefinition(self.junction)[
            0]
        # Possible TLS for the junction
        self.states = [phase.state for phase in self.full_def.phases]
        # Record of Light States (one for each step in simulation)
        self.cycle = 0
        # Record of actions takenin list form and in dictionary form:
        # {0: {state_1: x steps, state_2: y steps, ...},
        #  1: {state_1: x steps, state_2: y steps, ...}
        # ...}
        self.actions_taken = []
        self.actions_dict = {self.cycle: {}}
        # Wait time of the previous step & lane current step
        self.prev_wait, self.cur_wait = None, None
        # Store lane information corresponding to the 8 lane intersection
        self.lanes = ["426843745#0", "798289594#3", "-8644213#9", "102519704#0", "426843743", "798289594#0", "8644213#8",
                      "426493699#0"]
        # Order of light states in cycle; we will optimize how long to stay in each state
        self.states_order = ['GGGgrGrrrrrrGrrrr', 'yyyyryrrrrrryrrrr', 'rrrrGrrrrGGrrrrrr', 'rrrryrrrryyrrrrrr', 'rrrrrrrrrGGGrrrrr', 'rrrrrrrrryyyrrrrr', 'rrrrrGGggrrrrGGgg', 'rrrrryyyyrrrryyyy']
        
        # The Q-values
        '''
        Store Q-values in this form:
        {lane_x_has_longest_wait: {action_1: q_val, action_2: q_val, ..., action_n: q_val}, ...,
        lane_z_has_longest_wait: {{action_1: q_val, action_2: q_val, ..., action_n: q_val}}
        '''
        self.qs = qs
        # Q-value parameters
        self.alpha, self.gamma, self.epsilon = 0.01, 0.9, epsilon
        # Step Counter
        self.step = 0
        # Number of iterations
        self.iters = iters
        # Wait Time Data & Lane - Vehicle Info
        self.data, self.vehs_data = [], []
        # Visualizing traffic data
        self.visualizer = visualizer

    def run_simulation(self):
        """
        Runs the simulation for the specified number of timesteps
        """

        while self.step < self.iters:
            # Get current light state
            # Example light state:  GGGgrGrrrrrrGrrrr
            cur_state = traci.trafficlight.getRedYellowGreenState(
                self.junction)

            # Get current longest lane
            lane = self.findHighestWaitTimeLane()

            # Get action to take
            # Exmaple action state:  GGGgrGrrrrrrGrrrr
            action = self.getAction(cur_state)

            # Set traffic light to action and move to next time step
            traci.trafficlight.setRedYellowGreenState(self.junction, action)
            traci.simulationStep()

            # Get updated wait time; reward is how much shorter the wait is now
            self.updateWaitTime()
            reward = self.prev_wait - self.cur_wait

            # Find new current longest lane
            afterStepLongestLane = self.findHighestWaitTimeLane()

            # Update Q-values            
            self.update_qs(lane, action, afterStepLongestLane, reward)

            # End simulation if there are no more cars in play
            if len(traci.vehicle.getIDList()) == 0:
                break

            self.step += 1

        if self.visualizer:
            self.visualize_traffic_data(self.data)

        return self.qs

    def visualize_traffic_data(self):
        """
        Visualizes the accumulated wait time for each lane / number of cars in each lane
        """

        wt = pd.DataFrame(self.data)
        wt.columns = ['Timestep', 'Lane', 'Wait Time']
        wt.head()

        fig = go.Figure()
        for lane in wt["Lane"].unique():

            fig.add_trace(go.Scatter(
                x=[i for i in range(1, 10000)],
                y=list(wt[wt["Lane"] == lane]["Wait Time"]),
                mode='lines',
                name=f'{lane}')
            )

            fig.update_layout(title=f'Cars Waiting in a Lane {lane}',
                              yaxis_title='Acc. Wait Times of Cars in Lane',
                              xaxis_title='Time Step')

            fig.show()
        
    def updateWaitTime(self):
        step_wait_time = 0
        # 0 for wait time if step is 0
        if self.step == 0:
            self.prev_wait = 0
            self.cur_wait = 0
        else:
            step_wait = 0
            # Iterate through all the lanes and get the cumulative wait time on that lane
            for lane in self.lanes:
                indiv_wait_time = traci.edge.getWaitingTime(lane)
                self.data.append([self.step, lane, indiv_wait_time])
                # Get total wait time of all the lanes
                step_wait += indiv_wait_time
            # Update the previous wait time and the current wait time
            self.prev_wait = self.cur_wait
            self.cur_wait = step_wait

    def findLongestQueueLane(self):
        """
        Q-Criteria #1
        Finds the lane with the most number of cars and returns this value. The intuition for the model 
        is that the lane with the highest number of cars waiting is of the highest priority to ensure 
        proper traffic flow
        """

        num_vehs = {}
        # Get number of vehicles in each lane
        for lane in self.lanes:
            num_vehs[lane] = traci.edge.getLastStepVehicleNumber(lane)
        # Append data for visualization
        self.vehs_data.append(
            [f'{self.step}@{key}@{value}' for key, value in num_vehs.items()])
        # Return the lane with most vehicles waiting
        # This is the lane that we want to begin clearing out
        return max(num_vehs, key=num_vehs.get)

    def findHighestWaitTimeLane(self):
        """
        Q-Criteria #2
        Finds the lane with where the cars in that lane have the highest accumulated wait time. The intuition 
        for the model is that a lane may have lower incoming traffic but cars in said lane will wait 
        significantly longer and we want to optimize for this 
        """

        vehs = {}
        waits = {}
        # Get number of vehicles in each lane
        for lane in self.lanes:
            vehs[lane] = traci.edge.getLastStepVehicleIDs(lane)
            waits[lane] = sum([traci.vehicle.getAccumulatedWaitingTime(
                veh_id) for veh_id in vehs[lane]])

        # Append data for visualization
        self.vehs_data.append(
            [f'{self.step}@{key}@{value}' for key, value in vehs.items()])
        # Return the lane with most vehicles waiting
        # This is the lane that we want to begin clearing out
        return max(waits, key=waits.get)

    def getQValue(self, max_lane, action):
        """
        Params:
            max_lane (int) : ID of 1 of 8 lanes in the junction
            action (str) : A legal traffic light state 

        Returns the Q-value for the specified lane and actions
        """
        
        if max_lane in self.qs:
            if action in self.qs[max_lane]:
                return self.qs[max_lane][action]
        return 0

    def computeValueFromQValues(self, lane, ryg_state):
        """
        Params:
            lane (int) : ID of 1 of 8 lanes in the junction
            ryg_state (str) : A legal traffic light state 

        Returns the Q-value of the best traffic light state for the lane with the most number of vehicles
        waiting
        """

        # Get the legal traffic light states and the lane with the most number of cars waiting
        actions = self.getLegalActions(ryg_state)
        lane = self.findHighestWaitTimeLane()
        # Q-value for the first action (placeholder for the max Q value)
        val = self.getQValue(lane, actions[0])
        # Iterate through the legal actions to find the action with the highest Q value
        for i in range(1, len(actions)):
            # If this action produces a higher Q-value, save its value
            new_val = self.getQValue(lane, actions[i])
            if new_val > val:
                val = new_val
        # Return highest Q-value
        return val

    def getLegalActions(self, ryg_state):
        """
        Params:
            ryg_state (str) : A legal traffic light state 

        Returns a list of valid traffic light states given the current one.
        """
        
        # All lights must be at least 3 steps long
        # Note: ryg_state is the same as self.actions_taken[-1]
        # Make sure enough actions have been taken - if not enough have been taken, can't check prev states
        if len(self.actions_taken) > 2:
                # If the 2 actions before this one aren't the same as this one, light must then stay the same
            if self.actions_taken[-2] != ryg_state or self.actions_taken[-3] != ryg_state:
                return [ryg_state]
        new_action = False
        if len(self.actions_taken) > 150:
            for i in range(2, 150):
                if self.actions_taken[-i] != ryg_state:
                    new_action = True
        index = self.states_order.index(ryg_state)
        next_index = index + 1
        if index == len(self.states_order) - 1:
            next_index = 0
        if not new_action:
            return [self.states_order[next_index]]
        else:
            return [self.states_order[index], self.states_order[next_index]]

    def computeActionFromQValues(self, ryg_state):
        """
        Params:
            ryg_state (str) : A legal traffic light state 

        Returns the action that yields the highest Q-value for the lane with the most number of vehicles
        waiting
        """
        
        actions = self.getLegalActions(ryg_state)
        # Action to return, initialize to first action
        action = actions[0]
        lane = self.findHighestWaitTimeLane()
        # Q value for best action
        val = self.getQValue(lane, action)
        # Iterate through the legal actions to find the action with the highest Q value
        for i in range(1, len(actions)):
            new_val = self.getQValue(lane, actions[i])
            # If this action produces a higher Q-value, save its value
            if new_val > val:
                action = actions[i]
                val = new_val
        # Return action with the highest Q-value
        return action

    def getAction(self, ryg_state):
        """
        Params:
            ryg_state (str) : A legal traffic light state 

        Either picks a random state to explore the world or the action with the highest Q-value
        based on the value of the epsilon and the flip
        """

        # Flip coin with probability epsilon
        flip = random.random()
        # If the flip is less than epsilon the agent will "explore"
        if flip < self.epsilon:
            action = random.choice(self.getLegalActions(ryg_state))
        # Otherwise, we the agent chooses the action with the highest Q-value
        else:
            action = self.computeActionFromQValues(ryg_state)
        # If action is the first in the cycle and just changed to this action, increment cycle count
        if self.states_order.index(action) == 0 and self.actions_taken[-1] != action:
                self.cycle += 1
        # Add action to log of actions taken
        self.actions_taken.append(action)
        # If cycle already in actions dictionary
        if self.cycle in self.actions_dict:
            # If action already in cycle, increment
            if action in self.actions_dict[self.cycle]:
                self.actions_dict[self.cycle][action] += 1
            # Action not already in cycle, add and set to 1
            else:
                self.actions_dict[self.cycle][action] = 1
        # Cycle not already in actions dictionary, add and set to 1 for action
        else:
            self.actions_dict[self.cycle] = {}
            self.actions_dict[self.cycle][action] = 1
        return action

    def update_qs(self, lane, action, afterStepLongestLane, reward):
        """
        Params:
            lane (int) : ID of 1 of 8 lanes in the junction
            action (str) : A legal traffic light state 
            afterStepLongestLane (int) : ID of 1 of 8 lanes in the junction with the most number of vehicles
            reward (float) : Reward calculated using the difference in current and previous wait time

        Function to update the Q-values
        """
        # Add lane to Q-value dictionary if not yet initialized
        if lane not in self.qs.keys():
            self.qs[lane] = {}
        # Q-value Update Rule
        cur_q = self.getQValue(lane, action)
        next_q = self.computeValueFromQValues(afterStepLongestLane, action)
        self.qs[lane][action] = cur_q + self.alpha * \
            (reward + self.gamma * next_q - cur_q)

 # gets the action to take (policy) for a given state
    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    # returns a dictionary storing the action to take (policy) for each state
    # I was thinking we could call this after we run the simulation to have a policy that reflects the
    # computed Q values
    def totalPolicy(self):
        policy = {}
        for state in self.states:
            policy[state] = self.getPolicy(state)
        return policy

    # run simulation with policy from the computed q values
    def run_sim_with_policy(self):
        while self.step < self.iters:
            # current light state
            cur_state = traci.trafficlight.getRedYellowGreenState(self.junction)
            # see what actions are allowed - used to make sure yellow lights last long enough
            allowed_actions = self.getLegalActions(cur_state)
            # if only one action is allowed, take that action
            action_vals = [self.getQValue(cur_state, action) for action in allowed_actions]
            # get best q value and take that action
            action = allowed_actions[max(action_vals)]
            
            # If action is the first in the cycle and just changed to this action, increment cycle count
            if self.states_order.index(action) == 0 and self.actions_taken[-1] != action:
                    self.cycle += 1
            # Add action to log of actions taken
            self.actions_taken.append(action)
            # If cycle already in actions dictionary
            if self.cycle in self.actions_dict:
                # If action already in cycle, increment
                if action in self.actions_dict[self.cycle]:
                    self.actions_dict[self.cycle][action] += 1
                # Action not already in cycle, add and set to 1
                else:
                    self.actions_dict[self.cycle][action] = 1
            # Cycle not already in actions dictionary, add and set to 1 for action
            else:
                self.actions_dict[self.cycle] = {}
                self.actions_dict[self.cycle][action] = 1
            traci.trafficlight.setRedYellowGreenState(self.junction, action)
            traci.simulationStep()

            self.step += 1

        return self.actions_dict

    def policy_from_actions(self):
        total_state_lens = {}
        # Iterate through all possible light states and set count to 0
        for state in self.states_order:
            total_state_lens[state] = 0
        # Iterate through all cycles
        for cyc in self.actions_dict.keys():
            # Add counts for all light states in cycle
            for action in self.actions_dict[cyc].keys():
                total_state_lens[action] += self.actions_dict[cyc][action]
        total_state_avg = {}
        # Iterate through all light states; divide by number of cycles to take average
        for state in total_state_lens.keys():
            total_state_avg[state] = total_state_lens[state] / self.cycle
        return total_state_avg



# HYPER PARAMETER TUNING
# if __name__ == "__main__":
#     # Random Policy for the Traffic Signals
#     # Connect to script and intiate step counter
#     for alpha in [0.01, 0.05, 0.1, 0.5, 1]:
#         for gamma in [0.5, 0.65, 0.85, 1]:
#             for epsilon in [0, 0.25, 0.5, 0.75, 1]:
#                 traci.start(["sumo", "-c", ANEESHA_PATH])
#                 print("AGE", alpha, gamma, epsilon)
#                 sim_test = Sim(epsilon=epsilon, alpha=alpha, gamma=gamma)
#                 sim_test.run_simulation()
#                 traci.close()






if __name__ == "__main__":
 
    # Run simulation as-is, with default light timing
    traci.start(["sumo", "-c", MAURA_PATH])
    step = 0
    while step < 10000:
            traci.simulationStep()
            step += 1
    traci.close()

    # Random Policy for the Traffic Signals
    # Connect to script and intiate step counter
    traci.start(["sumo", "-c", MAURA_PATH])
    sim_rand = Sim(epsilon=1)
    sim_rand.run_simulation()
    traci.close()
    '''
    # Q-Learning for the Traffic Signals
    # Connect to script and intiate step counter
    traci.start(["sumo", "-c", MAURA_PATH])
    sim_q = Sim()
    q_vals = sim_q.run_simulation()
    traci.close()
    print(q_vals)
    
    # Run with policy from Q-Learning
    traci.start(["sumo", "-c", MAURA_PATH])
    # Make new simulation with learned q values
    sim_result = Sim(qs = q_vals)
    # Run simulation
    actions = sim_result.run_sim_with_policy()
    policy = sim_result.policy_from_actions()
    print(policy)
    traci.close()
    '''
    # Run simulation with given optimal policy (manually input policy output from previous call into simulation files)
    traci.start(["sumo", "-c", MAURA_PATH_OPTIMAL])
    step = 0
    while step < 10000:
            traci.simulationStep()
            step += 1
    traci.close()


    


