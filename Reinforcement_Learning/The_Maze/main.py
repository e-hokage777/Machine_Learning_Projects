from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
    ListProperty,
    StringProperty
)
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, Line
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.clock import Clock

import random
import numpy as np

from ai import Brain


class Game(Widget):
    ## creating game variables
    MAZE_WIDTH = NumericProperty(700)
    MAZE_HEIGHT = NumericProperty(500)
    NUM_TILES_H = NumericProperty(10)
    NUM_TILES_V = NumericProperty(10)
    NUM_TILES = ReferenceListProperty(NUM_TILES_H, NUM_TILES_V)
    NUM_ENEMIES = 5
    maze = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.init_keyboard()

    ## function to initialize keyboard
    def init_keyboard(self):
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self, "text")
        self.keyboard.bind(on_key_down=self.keyboard_down)

    ## keyboard event functions
    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.keyboard_down)
        self.keyboard = None

    def keyboard_down(self, keyboard, keycode, text, modifiers):
        self.maze.update_agent(keycode)


class Maze(RelativeLayout):
    agent = ObjectProperty(None)
    tile_width = 0
    tile_height = 0
    num_tiles = None  ## this value is set in the kivy file
    tiles = []
    goal_idx = None
    enemies_idxs = []
    tile_reward_array = None
    q_grid = None

    def __init__(self, **kwargs):
        super(Maze, self).__init__(**kwargs)
        Clock.schedule_once(self.init_maze, 0.1)

    def init_tiles(self):
        self.tile_width = self.width / self.num_tiles[0]
        self.tile_height = self.height / self.num_tiles[1]
        self.goal_idx = (self.num_tiles[0] - 1, self.num_tiles[1] - 1)

        ## setting up pit locations
        enemies_xs = random.sample(
            [r for r in range(self.num_tiles[0])], self.num_enemies
        )
        enemies_ys = random.sample(
            [r for r in range(self.num_tiles[1])], self.num_enemies
        )
        self.enemies_idxs = list(zip(enemies_xs, enemies_ys))

        with self.canvas.before:
            tile_img = "assets/tile.png"
            enemy_img = "assets/enemy.png"
            for i in range(self.num_tiles[0]):
                for j in range(self.num_tiles[1]):
                    xpos = i * self.tile_width
                    ypos = j * self.tile_height
                    if (i, j) == self.goal_idx:
                        Color(rgb=(0, 1, 0))
                    elif (i, j) in self.enemies_idxs:
                        Color(rgb=(1, 0, 0))
                    # else:
                    #     Color(rgba=(1, 1, 1))
                    self.tiles.append(
                        Rectangle(
                            size=(self.tile_width, self.tile_height),
                            pos=(xpos, ypos),
                            source=tile_img,
                        )
                    )

                    if (i, j) in self.enemies_idxs:
                        Color("transparent")
                        Rectangle(
                            size=(self.tile_width, self.tile_height),
                            pos=(xpos, ypos),
                            source=enemy_img,
                        )

                    Color(rgb=(1, 1, 1))
                    Line(rectangle=(xpos, ypos, self.tile_width, self.tile_height))

    def init_tile_reward_array(self):
        self.tile_reward_array = np.zeros((self.num_tiles[0], self.num_tiles[1]))
        self.tile_reward_array[self.goal_idx] = 1

        for coords in self.enemies_idxs:
            self.tile_reward_array[coords] = -1

    def init_agent(self):
        self.agent.width = self.tile_width
        self.agent.height = self.tile_height
        self.agent.pos_idxs = [0, 0]
        self.agent.brain = Brain(self.num_tiles[0] * self.num_tiles[1], 4)

    def init_q_grid(self):
        self.q_grid = QGrid(
            num_tiles_x = self.num_tiles[0],
            num_tiles_y = self.num_tiles[1],
            size=self.size,
            tile_width=self.tile_width,
            tile_height=self.tile_height
        )
        self.add_widget(self.q_grid)

    def init_maze(self, dt):
        self.init_tiles()
        self.init_tile_reward_array()
        self.init_agent()
        self.init_q_grid()

    def reset_game(self):
        self.agent.reset()

    ## functiont to move agent
    def update_agent(self, keycode):
        if not self.is_at_edge(self.agent, keycode[1]):
            self.agent.update(
                keycode[1], (self.tile_width, self.tile_height), self.tile_reward_array
            )

        ## resetting player position when goal reached
        if (
            self.agent.pos_idxs[0] == self.goal_idx[0]
            and self.agent.pos_idxs[1] == self.goal_idx[1]
        ):
            self.reset_game()

    ## function to update the q_grid
    def update_q_grid(self, state):
        q_table = self.agent.brain.q_table
        print(q_table)
        self.q_grid.tiles[state].action_0 = f"{(q_table[state, 0]):{.2}}"
        self.q_grid.tiles[state].action_1 = f"{(q_table[state, 1]):{.2}}"
        self.q_grid.tiles[state].action_2 = f"{(q_table[state, 2]):{.2}}"
        self.q_grid.tiles[state].action_3 = f"{(q_table[state, 3]):{.2}}"

    ## function to convert from state in index

    ## function to check whether object is at edge of maze
    def is_at_edge(self, obj, direction):
        if (obj.pos_idxs[0] >= self.num_tiles[0] - 1) and direction == "right":
            return True
        elif (obj.pos_idxs[0] <= 0) and direction == "left":
            return True
        if (obj.pos_idxs[1] >= self.num_tiles[1] - 1) and direction == "up":
            return True
        elif (obj.pos_idxs[1] <= 0) and direction == "down":
            return True

        return False

        ## some old logic that might be useful later
        # if(obj.pos[0] >= (self.width - self.tile_width)) and direction == "right":
        #     return True
        # elif(obj.pos[0] <= 0) and direction == "left":
        #     return True
        # if(obj.pos[1] >= (self.height - self.tile_height)) and direction == "up":
        #     return True
        # elif(obj.pos[1] <= 0) and direction == "down":
        #     return True


class QTile(FloatLayout):
    action_0 = StringProperty('0')
    action_1 = StringProperty('0')
    action_2 = StringProperty('0')
    action_3 = StringProperty('0')
    # actions = ListProperty([action_0, action_1, action_2, action_3])

    def __init__(self, **kwargs):
        super(QTile, self).__init__(**kwargs)


class QGrid(FloatLayout):
    tile_width = NumericProperty(0)
    tile_height = NumericProperty(0)
    num_tiles_x = NumericProperty(0)
    num_tiles_y = NumericProperty(0)
    tiles = []
    def __init__(self, **kwargs):
        super(QGrid, self).__init__(**kwargs)
        # for i in range(self.rows * self.cols):
        #     tile = QTile()
        #     self.tiles.append(tile)
        #     self.add_widget(tile)
        for i in range(self.num_tiles_y):
            for j in range(self.num_tiles_x):
                ypos = i * self.tile_height
                xpos = j * self.tile_width 
                tile = QTile(width =self.tile_width, height=self.tile_height, pos=(xpos, ypos))
                self.tiles.append(tile)
                self.add_widget(tile)



class Agent(Widget):
    last_state = 0

    ## function to reset player to beginning of world
    def reset(self):
        self.pos = (0, 0)
        self.pos_idxs = [0, 0]

    def move(self, action, dist):
        if action == "right":
            self.pos_idxs[0] = self.pos_idxs[0] + 1
        if action == "left":
            self.pos_idxs[0] = self.pos_idxs[0] - 1
        if action == "up":
            self.pos_idxs[1] = self.pos_idxs[1] + 1
        if action == "down":
            self.pos_idxs[1] = self.pos_idxs[1] - 1
        self.pos = (self.pos_idxs[0] * dist[0], self.pos_idxs[1] * dist[1])

    def update(self, action, dist, reward_array):
        self.move(action, dist)
        reward = reward_array[self.pos_idxs[0], self.pos_idxs[1]]
        print(self.pos_idxs)
        next_state = self.pos_to_state(self.pos_idxs)
        action = self.action_to_ind(action)
        self.brain.update(self.last_state, next_state, action, reward)
        ## updating the qgrid
        self.parent.update_q_grid(self.last_state)
        self.last_state = next_state

    ## function to convert position to state
    def pos_to_state(self, idxs):
        return idxs[1] * self.parent.num_tiles[1] + idxs[0]

    ## function to convert action in words to index
    def action_to_ind(self, action):
        match action:
            case "up":
                return 0
            case "right":
                return 1
            case "down":
                return 2
            case "left":
                return 3
            case _:
                print(action)
                return 4


class WorldApp(App):
    pass


WorldApp().run()
