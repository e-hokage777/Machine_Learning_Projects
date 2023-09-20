from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.context_instructions import Color, PushMatrix, Rotate, PopMatrix
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.label import Label


class MainWidget(RelativeLayout):
    grid = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # self.add_widget("GridLayout")

    def pressed(self):
        for t in self.grid.tiles:
            t.action_one += 1
            t.action_two += 9
            t.action_three += 3
            t.action_four += 11


class Grid(GridLayout):
    num_cols = 5
    num_rows = 5
    tiles = []

    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)
        self.rows = self.num_rows
        self.columns = self.num_cols
        for i in range(self.num_cols * self.num_rows):
            t = Tile()
            self.tiles.append(t)
            self.add_widget(t)


class Tile(FloatLayout):
    action_one = NumericProperty(50000)
    action_two = NumericProperty(100)
    action_three = NumericProperty(0)
    action_four = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Tile, self).__init__(**kwargs)
        # with self.canvas:
        #     PushMatrix()
        #     Rotate(origin=self.center, angle=30)
        # self.add_widget(
        #     Label(
        #         text=str(str(self.action_one)),
        #         size_hint=(0.25, 0.25),
        #         pos_hint={"x": 0, "center_y": 0.5},
        #     )
        # )
        # with self.canvas:
        #     PopMatrix()
        # self.add_widget(
        #     Label(
        #         text=str(str(self.action_two)),
        #         size_hint=(0.25, 0.25),
        #         pos_hint={"center_y": 0.5, "right": 1},
        #     )
        # )


kv = Builder.load_file("any.kv")


class MainApp(App):
    def build(self):
        return kv


if __name__ == "__main__":
    MainApp().run()
