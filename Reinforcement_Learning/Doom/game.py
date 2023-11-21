import gymnasium as gym
from vizdoom import gymnasium_wrapper

## creating the environment
doom_env = gym.make("VizdoomCorridor-v0", render_mode="human")

## creating the brain


## beginning game
observation, info = doom_env.reset()
# game loop