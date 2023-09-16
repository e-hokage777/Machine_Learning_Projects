import numpy as np

class Brain:
    def __init__(self, num_states, num_actions, gamma = 0.9):
        self.q_table = np.zeros((num_states, num_actions))
    
    def update(self, last_state, next_state, action, reward):
        print("Last State:", last_state)
        print("Next State:", next_state)
        print("Action:", action)
        print("Reward:", reward)