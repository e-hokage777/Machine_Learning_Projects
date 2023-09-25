from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, Triangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
import random


class MainWidget(Widget):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        num = random.randint(0, 3)
        print(self.center)
        center = (self.width / 2, self.height / 2)
        size = 20
        # num = 0
        self.canvas.clear()
        with self.canvas:
            match num:
                case 0:
                    Triangle(
                        points=(
                            center[0],center[1] + size,
                            center[0]+size,center[1] - size,
                            center[0]-size,center[1] - size
                        )
                    )
                case 1:
                    Triangle(
                        points=(
                            center[0]+size,center[1],
                            center[0]-size,center[1] + size,
                            center[0]-size,center[1] - size,
                        )
                    )
                case 2:
                    Triangle(
                        points=(
                            center[0],center[1] - size,
                            center[0]+size,center[1] + size,
                            center[0]-size,center[1] + size
                        )
                    )
                case 3:
                    Triangle(
                        points=(
                            center[0]-size,center[1],
                            center[0]+size,center[1] + size,
                            center[0]+size,center[1] - size,
                        )
                    )
                

class TestApp(App):
    pass


TestApp().run()
