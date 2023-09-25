from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen

class MenuWidget(Screen):
    def change_game_mode(self, auto):
        self.manager.get_screen("game").auto_agent=auto

    ## function to change number of rows of maze
    def change_maze_rows(self,rows):
        if rows == "":
            return
        
        rows = int(rows)
        if(3<rows<=10):
            self.manager.get_screen("game").NUM_TILES_H = rows

    ## function to change number of cols of maze
    def change_maze_cols(self,cols):
        if cols == "":
            return
        
        cols = int(cols)
        if(3<cols<=10):
            self.manager.get_screen("game").NUM_TILES_V = cols

    ## function to change number of enemies in game
    def change_num_enemies(self, number):
        if number == "":
            return
        
        number = int(number)
        ## getting maze dimension
        maze_dim = self.manager.get_screen("game").NUM_TILES_V * self.manager.get_screen("game").NUM_TILES_H
        if(0<number<=(maze_dim)-1):
            self.manager.get_screen("game").NUM_ENEMIES = number

    
    ## function to change game speed
    def change_game_speed(self, speed):
        self.manager.get_screen("game").game_speed = speed


