import torch
import torch.nn as nn
import torch.nn.functional as F

import random


class Network(nn.model):
    def __init__(self, input_size, nb_actions):
        super(Network, self).__init__()
        self.nb_actions = nb_actions

        ## creating the full connections
        self.fc1 = nn.Linear(input_size, 30)
        self.fc2 = nn.Linear(30, nb_actions)

    ## creating the forward propagation function
    def forward(self, state):
        out1 = F.relu(self.fc1(state))
        q_values = self.fc2(out1)

        return q_values


class ReplayMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []

    ## function to push into the memory
    def push(self, event):
        self.memory.append(event)

        if event.length > self.capacity:
            del self.memory[0]

    ## function to select `batch_size` samples
    def sample(self, batch_size):
        samples = zip(*random.sample(self.memory, batch_size))
        return map(lambda x: torch.tensor(x, requires_grad=True).reshape(-1,1), samples) ## check here well
    


class Dqn:
    def __init__(self, input_size, nb_actions, gamma):
        self.gamma = gamma
        self.reward_window = []
        self.network = Network(input_size, nb_actions)
        self.memory = ReplayMemory(100000)
        self.optimizer = torch.optim.Adam(self.model.parameters, lr=0.001)
        self.last_state = torch.randn(input_size).unsqueeze(0)
        self.last_action = 0
        self.last_reward = 0

    ## function to select an action
    def select_action(self, state):
        probs = F.softmax(self.model(state)*7)
        action = probs.multinomial(1)
        return action.item()