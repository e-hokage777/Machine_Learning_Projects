import torch
import torch.nn as nn
import torch.nn.functional as F

import random

import os


class Network(nn.Module):
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

        # print(q_values)
        return q_values


class ReplayMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []

    ## function to push into the memory
    def push(self, event):
        self.memory.append(event)

        if len(self.memory) > self.capacity:
            del self.memory[0]

    ## function to select `batch_size` samples
    def sample(self, batch_size):
        samples = zip(*random.sample(self.memory, batch_size))
        return map(
            lambda x: torch.tensor(torch.cat(x, 0)), samples
        )  ## check here well


class Dqn:
    def __init__(self, input_size, nb_actions, gamma):
        self.gamma = gamma
        self.reward_window = []
        self.model = Network(input_size, nb_actions)
        self.memory = ReplayMemory(100000)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.last_state = torch.Tensor(input_size).unsqueeze(0)
        self.last_action = 0
        self.last_reward = 0

    ## function to select an action
    def select_action(self, state):
        probs = F.softmax(self.model(state) * 100)
        action = probs.multinomial(1)
        return action.item()

    ## function to learn
    def learn(self, batch_state, batch_next_state, batch_reward, batch_action):
        outputs = self.model(batch_state).gather(1, batch_action.unsqueeze(1)).squeeze(1)
        next_outputs = self.model(batch_next_state).detach().max(1)[0]
        targets = batch_reward + self.gamma * next_outputs
        td_loss = F.smooth_l1_loss(outputs, targets)
        self.optimizer.zero_grad()
        td_loss.backward()
        self.optimizer.step()

    ## function that handles update of brain and function return
    def update(self, new_signal, reward):
        ## learning
        if len(self.memory.memory) > 100:
            self.learn(*self.memory.sample(100))

        # print(reward)

        ## adding new item to memory
        new_state = torch.tensor(new_signal).unsqueeze(0)
        self.memory.push([self.last_state, new_state, torch.tensor([reward]), torch.tensor([self.last_action])]) # confused about here
        # print([self.last_state, new_state, torch.tensor([reward]), torch.tensor([self.last_action])])
        ## selection a new action to play
        action = self.select_action(new_state)

        ## updating the lasts
        self.last_state = new_state
        self.last_reward = reward
        self.last_action = action

        ## adding to reward window
        if len(self.reward_window) > 1000:
            del self.reward_window[0]

        self.reward_window.append(reward)

        ## returning action to play
        return action

    ## function to score using sliding window
    def score(self):
        return sum(self.reward_window)/(len(self.reward_window)+1)
    

    def save(self):
        torch.save(
            {"state_dict": self.model.state_dict(), "optimizer_state": self.optimizer.state_dict()},
            "last_brain.pth"
        )

    def load(self):
        filename = "last_brain.pth"
        if os.path.isfile(filename):
            checkpoint = torch.load(filename)
            self.model.load_state_dict(checkpoint["state_dict"])
            self.optimizer.load_state_dict(checkpoint["optimizer_state"])
            print("done")
        else:
            print("No saved data found")