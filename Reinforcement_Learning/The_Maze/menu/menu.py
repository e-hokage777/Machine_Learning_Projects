from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen

class MenuWidget(Screen):
    def change_game_mode(self, auto):
        print(auto)
        self.manager.get_screen("game").auto_agent=auto