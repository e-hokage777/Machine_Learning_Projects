from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ObjectProperty, ReferenceListProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, Line
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.clock import Clock

class Game(Widget):
    ## creating game variables
    MAZE_WIDTH = NumericProperty(700)
    MAZE_HEIGHT = NumericProperty(500)
    NUM_TILES_H = NumericProperty(10)
    NUM_TILES_V = NumericProperty(10)
    NUM_TILES = ReferenceListProperty(NUM_TILES_H, NUM_TILES_V)
    maze = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.init_keyboard()

    ## function to initialize keyboard
    def init_keyboard(self):
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self, 'text')
        self.keyboard.bind(on_key_down = self.keyboard_down)
    
    ## keyboard event functions
    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down = self.keyboard_down)
        self.keyboard = None

    def keyboard_down(self, keyboard, keycode, text, modifiers):
        self.maze.move_agent(keycode)



class Maze(RelativeLayout):
    agent = ObjectProperty(None)
    tile_width = 0
    tile_height = 0
    tiles = []
    def __init__(self, **kwargs):
        super(Maze, self).__init__(**kwargs)
        Clock.schedule_once(self.init_maze, 0.1)

    def init_tiles(self):
        self.tile_width = self.width/self.num_tiles[0]
        self.tile_height = self.height/self.num_tiles[1]
        
        with self.canvas.before:
            for i in range(self.num_tiles[0]):
                for j in range(self.num_tiles[1]):
                    xpos = i*self.tile_width
                    ypos = j*self.tile_height
                    Color(rgb=(0,0,0))
                    self.tiles.append(Rectangle(
                        size = (self.tile_width, self.tile_height),
                        pos = (xpos, ypos)
                    ))
                    Color(rgb=(1,1,1))
                    Line(rectangle=(xpos, ypos, self.tile_width, self.tile_height))

    def init_agent(self):
        self.agent.width = self.tile_width
        self.agent.height = self.tile_height

    def init_maze(self, dt):
        self.init_tiles()
        self.init_agent()

    ## functiont o move agent
    def move_agent(self, keycode):
        if(not self.is_at_edge(self.agent, keycode[1])):
            self.agent.move(keycode, (self.tile_width, self.tile_height))

    ## function to check whether object is at edge of maze
    def is_at_edge(self, obj, direction):
        if(obj.pos[0] >= (self.width - self.tile_width)) and direction == "right":
            return True
        elif(obj.pos[0] <= 0) and direction == "left":
            return True
        if(obj.pos[1] >= (self.height - self.tile_height)) and direction == "up":
            return True
        elif(obj.pos[1] <= 0) and direction == "down":
            return True
        
        return False
        

class Agent(Widget):
    def move(self, keycode, dist):
        vec = None
        if(keycode[1] == "right"):
            self.pos = Vector(dist[0], 0) + self.pos
        if(keycode[1] == "left"):
            self.pos = Vector(-dist[0], 0) + self.pos
        if(keycode[1] == "up"):
            self.pos = Vector(0, dist[1]) + self.pos
        if(keycode[1] == "down"):
            self.pos = Vector(0,-dist[1]) + self.pos
    


class WorldApp(App):
    pass

WorldApp().run()
