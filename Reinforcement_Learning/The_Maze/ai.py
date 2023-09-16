import numpy as np

class Brain:
    def __init__(self, num_states, num_actions, gamma = 0.9, learning_rate = 0.5):
        self.q_table = np.zeros((num_states, num_actions))
        self.gamma = gamma
        self.learning_rate = learning_rate
    
    def update(self, last_state, next_state, action, reward):
        print("Last State:", last_state)
        print("Next State:", next_state)
        print("Action:", action)
        print("Reward:", reward)
        ## select next action to play
        q_old = self.q_table[last_state, action]
        q_opt = reward + self.gamma * max(self.q_table[next_state,:])
        loss = q_opt - q_old
        q_new = q_old + self.learning_rate*loss
        self.q_table[last_state, action] = q_new
        print(self.q_table)