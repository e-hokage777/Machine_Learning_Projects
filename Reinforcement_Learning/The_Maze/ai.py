import numpy as np
import random
from scipy.special import softmax

class Brain:
    def __init__(self, num_states, num_actions, gamma = 0.9, learning_rate = 0.5):
        self.q_table = np.zeros((num_states, num_actions))
        self.gamma = gamma
        self.learning_rate = learning_rate

    ## function to select next action
    def select_action(self, state):
        next_action = random.choices([0,1,2,3], softmax(self.q_table[state, :]))
        # print(next_action[0])
        return next_action[0]
    
    def update(self, last_state, next_state, action, reward):
        # print("Last State:", last_state)
        # print("Next State:", next_state)
        # print("Action:", action)
        # print("Reward:", reward)
        ## select next action to play
        q_old = self.q_table[last_state, action]
        q_opt = reward + self.gamma * max(self.q_table[next_state,:])
        loss = q_opt - q_old
        q_new = q_old + self.learning_rate*loss
        self.q_table[last_state, action] = q_new
        next_action = self.select_action(next_state)
        return next_action