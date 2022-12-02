import traci
import traci.constants as tc
import random
import pandas as pd
#import plotly.graph_objects as go

# Path to the osm.sumocfg file
ANEESHA_PATH = "/Users/aneesha/sumo/tools/2022-11-10-00-32-34/osm.sumocfg"
MAURA_PATH = "C:/Users/Maura/OneDrive - Northeastern University/Artificial Intelligence/Traffic_Q_Learning_Agent/osm.sumocfg"


class Sim():

    def __init__(self, epsilon=0.5, iters=10000, alpha=0.01, gamma=0.9, visualizer=False):
        # Traffic Light Junction ID
        self.junction = 'J0'
        # Full logic definition of light settings at junction
        self.full_def = traci.trafficlight.getCompleteRedYellowGreenDefinition(self.junction)[
            0]
        # Possible TLS for the junction
        self.states = [phase.state for phase in self.full_def.phases]
        # Record of Light States (one for each step in simulation)
        self.actions_taken = []
        # Wait time of the previous step & lane current step
        self.prev_wait, self.cur_wait = None, None
        # Store lane information corresponding to the 8 lane intersection
        self.lanes = ["426843745#0", "798289594#3", "-8644213#9", "102519704#0", "426843743", "798289594#0", "8644213#8",
                      "426493699#0"]
        # The Q-values
        '''
        Store Q-values in this form:
        {lane_x_has_most_cars: {action_1: q_val, action_2: q_val, ..., action_n: q_val}, ...,
        lane_z_has_most_cars: {{action_1: q_val, action_2: q_val, ..., action_n: q_val}}
        '''
        self.qs = {}
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
        Runs the simulation for teh specified number of timesteps
        """

        while self.step < self.iters:
            # Get current light state
            # Example light state:  GGGgrGrrrrrrGrrrr
            cur_state = traci.trafficlight.getRedYellowGreenState(
                self.junction)

            # Get action to take
            # Exmaple action state:  GGGgrGrrrrrrGrrrr
            action = self.getAction(cur_state)

            # Set traffic light to action and move to next time step
            traci.trafficlight.setRedYellowGreenState(self.junction, action)
            traci.simulationStep()

            # Get updated wait time; reward is how much shorter the wait is now
            self.updateWaitTime()
            reward = self.prev_wait - self.cur_wait

            # Get current longest lane
            lane = self.findLongestQueueLane()

            # Find new current longest lane
            afterStepLongestLane = self.findLongestQueueLane()

            # Update Q-values            
            self.update_qs(lane, action, afterStepLongestLane, reward)

            # End simulation if there are no more cars in play
            if len(traci.vehicle.getIDList()) == 0:
                break

            self.step += 1

        if self.visualizer:
            self.visualize_traffic_data(self.data)

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

        num_vehs = {}
        # Get number of vehicles in each lanFe
        for lane in self.lanes:
            num_vehs[lane] = traci.edge.getLastStepVehicleIDs(lane)
            num_vehs[lane] = sum([traci.vehicle.getAccumulatedWaitingTime(
                veh_id) for veh_id in num_vehs[lane]])

        # Append data for visualization
        self.vehs_data.append(
            [f'{self.step}@{key}@{value}' for key, value in num_vehs.items()])
        # Return the lane with most vehicles waiting
        # This is the lane that we want to begin clearing out
        return max(num_vehs, key=num_vehs.get)

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
        lane = self.findLongestQueueLane()
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
        
        # Yellow light must be at least 3 steps long to avoid emergency stops
        # Note: ryg_state is the same as self.actions_taken[-1]
        if 'y' in ryg_state:
            # Make sure enough actions have been taken - if not enough have been taken, can't check prev states
            if len(self.actions_taken) > 2:
                # If the 2 actions before this one aren't the same as this one, light must then stay the same
                if self.actions_taken[-2] != ryg_state or self.actions_taken[-3] != ryg_state:
                    return [ryg_state]
        # Self (don't change), or a red can become green, a yellow can become red, a green can become yellow
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
        raise Exception(
            'Unknown light state encountered - don\'t know possible next moves')

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
        lane = self.findLongestQueueLane()
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
        # Add action to log of actions taken
        self.actions_taken.append(action)
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
    # Random Policy for the Traffic Signals
    # Connect to script and intiate step counter
    traci.start(["sumo", "-c", ANEESHA_PATH])
    sim_rand = Sim(epsilon=1)
    sim_rand.run_simulation()
    # print(sim_rand.actions_taken)
    # print(sim_rand.qs)
    traci.close()

    # Q-Learning for the Traffic Signals
    # Connect to script and intiate step counter
    traci.start(["sumo", "-c", ANEESHA_PATH])
    sim_q = Sim()
    sim_q.run_simulation()
    # print(sim_q.actions_taken)
    # print(sim_q.qs)
    traci.close()