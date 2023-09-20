from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle


class MainWidget(Widget):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.add_widget(TestWidget(sekmeth="firing"))


    def on_size(self, instance, wind_size):
        # with self.canvas.before:
        #     Color(rgb=(1, 1, 1))
        #     Rectangle(size=self.size, pos=self.pos)
        pass


class TestWidget(BoxLayout):
    sekmeth = StringProperty("")
    value = StringProperty("0")
    num = NumericProperty(0)

    def __init__(self, **kwargs):
        super(TestWidget, self).__init__(**kwargs)
        self.add_widget(Button(text=self.sekmeth, on_press=self.press))
        self.l = Label(text=self.value)
        # l.bind(text=self.value)
        self.add_widget(self.l)

    def on_value(self, a,b):
        self.l.text = b

    def press(self, instance):
        self.sekmeth = "changed"
        self.num += 1
        self.value = str(self.num)
    
    def on_size(self, **args):
        pass



class TestApp(App):
    pass


TestApp().run()

# class Some:
#     name = None
#     def __init__(self):
#         pass

# print(dir(Some))