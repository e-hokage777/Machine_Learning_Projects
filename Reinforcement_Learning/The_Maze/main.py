from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
    ListProperty,
    StringProperty
)

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, Line, Triangle
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang.builder import Builder

import random
import numpy as np

## importing the ai module
from ai import Brain

## builing the menu kivy file
Builder.load_file("menu/menu.kv")

## creating the screen manager
class WindowManager(ScreenManager):
    pass

class Game(Screen):
    ## creating game variables
    MAZE_WIDTH = NumericProperty(700)
    MAZE_HEIGHT = NumericProperty(500)
    NUM_TILES_H = NumericProperty(5)
    NUM_TILES_V = NumericProperty(5)
    NUM_TILES = ReferenceListProperty(NUM_TILES_H, NUM_TILES_V)
    NUM_ENEMIES = NumericProperty(5)
    maze = ObjectProperty(None)
    game_start = False
    game_mode_btn_text = StringProperty("START")
    auto_agent = True
    maze_initialized = False
    game_speed = 30

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
        if not self.auto_agent:
            self.maze.update_agent(keycode[1])

    ## function to toggle the opacity of qgrid
    def toggle_qgrid_display(self):
        self.maze.q_grid.opacity = 1 - self.maze.q_grid.opacity

    ## function to toggle the opacity of policy grid
    def toggle_policy_grid_display(self):
        self.maze.p_grid.opacity = 1 - self.maze.p_grid.opacity

    def toggle_game_mode(self):
        self.game_start = not self.game_start
        self.game_mode_btn_text = "PAUSE" if self.game_start else "RESUME"

    def on_pre_enter(self):
        if not self.maze_initialized:
            self.maze.init_maze()
            self.maze_initialized = True


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
    agent_actions = ["up", "right", "down", "left"]

    def __init__(self, **kwargs):
        super(Maze, self).__init__(**kwargs)
        # Clock.schedule_once(self.init_maze, 0.1)

    def init_tiles(self):
        self.tile_width = self.width / self.num_tiles[0]
        self.tile_height = self.height / self.num_tiles[1]
        self.goal_idx = (self.num_tiles[0] - 1, self.num_tiles[1] - 1)

        ## setting up enemy locations
        all_pos = []
        for i in range(self.num_tiles[0]):
            for j in range(self.num_tiles[1]):
                all_pos.append((i,j))
        
        random.shuffle(all_pos)
        count = 0

        while len(self.enemies_idxs) < self.num_enemies:
            if not (all_pos[count] == self.goal_idx) :
                self.enemies_idxs.append(all_pos[count])
            count+=1


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

    ## function to setup qgrid
    def init_q_grid(self):
        self.q_grid = QGrid(
            num_tiles_x = self.num_tiles[0],
            num_tiles_y = self.num_tiles[1],
            size=self.size,
            tile_width=self.tile_width,
            tile_height=self.tile_height
        )

        self.add_widget(self.q_grid)

    ## function to setup policy grid
    def init_p_grid(self):
        self.p_grid = PGrid(
            num_tiles_x = self.num_tiles[0],
            num_tiles_y = self.num_tiles[1],
            size=self.size,
            tile_width=self.tile_width,
            tile_height=self.tile_height
        )

        self.add_widget(self.p_grid)


    def init_maze(self):
        self.init_tiles()
        self.init_tile_reward_array()
        self.init_agent()
        self.init_q_grid()
        self.init_p_grid()

        ## automating game if preset
        if self.parent.auto_agent:
            Clock.schedule_interval(self.auto_update_agent, 1/(self.parent.game_speed))

    def reset_game(self):
        self.agent.reset()

    ## functiont to move agent
    def update_agent(self, action):
        if self.parent.game_start:
            self.agent.update(
                action, (self.tile_width, self.tile_height), self.tile_reward_array
            )

        ## resetting player position when goal reached
        if (
            self.agent.pos_idxs[0] == self.goal_idx[0]
            and self.agent.pos_idxs[1] == self.goal_idx[1]
        ):
            self.reset_game()

    def auto_update_agent(self, dt):
        action = self.agent.next_action
        self.update_agent(self.agent_actions[action])

    ## function to update the q_grid
    def update_q_grid(self, state):
        q_table = self.agent.brain.q_table
        self.q_grid.tiles[state].action_0 = f"{round(q_table[state, 0],2)}"
        self.q_grid.tiles[state].action_1 = f"{round(q_table[state, 1],2)}"
        self.q_grid.tiles[state].action_2 = f"{round(q_table[state, 2],2)}"
        self.q_grid.tiles[state].action_3 = f"{round(q_table[state, 3],2)}"


    ## function to update the policy grid
    def update_p_grid(self, state):
        q_table = self.agent.brain.q_table
        self.p_grid.tiles[state].update(np.argmax(q_table[state, :]))

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

class QTile(FloatLayout):
    action_0 = NumericProperty(0)
    action_1 = NumericProperty(1)
    action_2 = NumericProperty(2)
    action_3 = NumericProperty(3)
    actions = ListProperty([action_0, action_1, action_2, action_3])
    def __init__(self, **kwargs):
        super(QTile, self).__init__(**kwargs)


class QTile(FloatLayout):
    action_0 = StringProperty('0')
    action_1 = StringProperty('0')
    action_2 = StringProperty('0')
    action_3 = StringProperty('0')

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
        for i in range(self.num_tiles_y):
            for j in range(self.num_tiles_x):
                ypos = i * self.tile_height
                xpos = j * self.tile_width 
                tile = QTile(width =self.tile_width, height=self.tile_height, pos=(xpos, ypos))
                self.tiles.append(tile)
                self.add_widget(tile)


## Policy Grid Class
class PGrid(FloatLayout):
    tile_width = NumericProperty(0)
    tile_height = NumericProperty(0)
    num_tiles_x = NumericProperty(0)
    num_tiles_y = NumericProperty(0)
    tiles = []
    def __init__(self, **kwargs):
        super(PGrid, self).__init__(**kwargs)
        for i in range(self.num_tiles_y):
            for j in range(self.num_tiles_x):
                ypos = i * self.tile_height
                xpos = j * self.tile_width 
                tile = PTile(width =self.tile_width, height=self.tile_height, pos=(xpos, ypos))
                self.tiles.append(tile)
                self.add_widget(tile)

class PTile(FloatLayout):
    direction = NumericProperty(0)
    triangle = None
    tsize = 20
    def __init__(self, **kwargs):
        super(PTile, self).__init__(**kwargs)
        self.size_hint = None, None
        self.tsize = self.width*0.1
        with self.canvas.before:
            Color(rgba=(1,1,1,0.8))
            self.triangle = Triangle(points=(
                self.center[0],self.center[1] + self.tsize,
                self.center[0]+self.tsize,self.center[1] - self.tsize,
                self.center[0]-self.tsize,self.center[1] - self.tsize
            ))

    def update(self, direction):
        points = self.triangle.points
        match direction:
            case 0:
                points=(self.center[0],self.center[1] + self.tsize,
                        self.center[0]+self.tsize,self.center[1] - self.tsize,
                        self.center[0]-self.tsize,self.center[1] - self.tsize
                        )
            case 1:
                points=(
                    self.center[0]+self.tsize,self.center[1],
                    self.center[0]-self.tsize,self.center[1] + self.tsize,
                    self.center[0]-self.tsize,self.center[1] - self.tsize,
                    )
            case 2:
                points=(
                    self.center[0],self.center[1] - self.tsize,
                    self.center[0]+self.tsize,self.center[1] + self.tsize,
                    self.center[0]-self.tsize,self.center[1] + self.tsize
                    )
            case 3:
                points=(
                    self.center[0]-self.tsize,self.center[1],
                    self.center[0]+self.tsize,self.center[1] + self.tsize,
                    self.center[0]+self.tsize,self.center[1] - self.tsize,
                    )
            
        self.triangle.points = points
                


class Agent(Widget):
    last_state = 0
    next_action = 0

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

        ## bringing player back when outside grid
        if self.pos_idxs[0] < 0:
            self.pos_idxs[0] = 0
        if(self.pos_idxs[0] >= self.parent.num_tiles[0]):
            self.pos_idxs[0] = self.parent.num_tiles[0]-1
        if self.pos_idxs[1] < 0:
            self.pos_idxs[1] = 0
        if(self.pos_idxs[1] >= self.parent.num_tiles[1]):
            self.pos_idxs[1] = self.parent.num_tiles[1]-1

        ## update the players position
        self.pos = (self.pos_idxs[0] * dist[0], self.pos_idxs[1] * dist[1])

    def update(self, action, dist, reward_array):
        self.move(action, dist)
        reward = reward_array[self.pos_idxs[0], self.pos_idxs[1]]
        next_state = self.pos_to_state(self.pos_idxs)
        action = self.action_to_ind(action)
        self.next_action = self.brain.update(self.last_state, next_state, action, reward)
        ## updating the qgrid
        self.parent.update_q_grid(self.last_state)
        ## updating the policy grid
        self.parent.update_p_grid(self.last_state)
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
