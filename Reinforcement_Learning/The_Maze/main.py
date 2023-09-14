from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ObjectProperty, ReferenceListProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, Line
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



class Maze(RelativeLayout):
    tile_width = 0
    tile_height = 0
    tiles = []
    def __init__(self, **kwargs):
        super(Maze, self).__init__(**kwargs)
        Clock.schedule_once(self.init_maze, 0.1)

    def init_tiles(self):
        self.tile_width = self.width/self.num_tiles[0]
        self.tile_height = self.height/self.num_tiles[1]
        
        with self.canvas:
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

    def init_maze(self, dt):
        self.init_tiles()

class Agent(Widget):
    pass



class WorldApp(App):
    pass

WorldApp().run()
