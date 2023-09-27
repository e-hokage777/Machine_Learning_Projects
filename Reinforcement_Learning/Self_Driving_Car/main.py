import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ColorProperty, NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock

## the game class
class GameWidget(Widget):
    car = None
    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        ## adding the car to the game
        self.car = Car()
        self.add_widget(self.car)
        Clock.schedule_interval(self.update, 1/60)

    ## function to update the state of the game
    def update(self, dt):
        self.car.update(dt)

## the car class
class Car(Widget):
    ## car properties
    velocity = Vector(200,0)
    angle = NumericProperty(0)

    ## car components
    sensor1 = None
    sensor2 = None
    sensor3 = None
    def __init__(self, **kwargs):
        super(Car, self).__init__(**kwargs)
        ## setting car sizez
        self.size = (50, 10)
        self.sensor1 = Sensor(color=[1,0,0,1], offset_angle=30)
        self.sensor2 = Sensor(color=[0,1,0,1], offset_angle=0)
        self.sensor3 = Sensor(color=[0,0,1,1], offset_angle=-30)

        ## adding the sensors to the car
        self.add_widget(self.sensor1)
        self.add_widget(self.sensor2)
        self.add_widget(self.sensor3)

    ## function to update state of car
    def update(self, dt):
        # self.angle = random.randint(0,360)
        self.angle += (dt * 7)
        self.pos = self.velocity.rotate(self.angle) * dt + self.pos
        self.bound_within()

        ## updating the sensors
        self.sensor1.update(dt)
        self.sensor2.update(dt)
        self.sensor3.update(dt) 

    ## function to keep car within bounds
    def bound_within(self):
        if(self.pos[0] < 0):
            self.pos[0] = 0
        elif self.pos[0] > self.parent.width - self.width:
            self.pos[0] = self.parent.width - self.width

        if(self.pos[1] < 0):
            self.pos[1] = 0
        elif self.pos[1] > self.parent.height - self.width:
            self.pos[1] = self.parent.height - self.width ## implement here better later on

## the sensor class
class Sensor(Widget):
    color = ColorProperty([0,0,0,0])
    offset = NumericProperty(50)
    offset_angle = NumericProperty(0)
    def __init__(self, **kwargs):
        super(Sensor, self).__init__(**kwargs)
        print(self.color)
        self.size = (10,10)

    def on_parent(self, instance, parent):
        self.pos[0] = parent.pos[0] + parent.width
        self.pos[1] = parent.pos[1] + parent.height*0.5 - self.size[0]*0.5

    ## function to update sensor state
    def update(self, dt):
        new_pos = [self.parent.pos[0] + self.parent.width*0.5, self.parent.pos[1] + self.parent.height*0.5 - self.size[1]*0.5]
        self.pos = Vector(self.offset, 0).rotate(self.parent.angle + self.offset_angle) + new_pos


## the game app
class GameApp(App):
    pass


GameApp().run()