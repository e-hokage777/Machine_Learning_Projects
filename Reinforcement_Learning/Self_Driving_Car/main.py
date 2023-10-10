import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ColorProperty, NumericProperty, ReferenceListProperty
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.context_instructions import Color
from kivy.vector import Vector
from kivy.clock import Clock

import numpy as np

from ai import Dqn


## the game class
class GameWidget(Widget):
    car = None
    car_margin = NumericProperty(10)
    paint_widget = None
    goal_x = NumericProperty(0)
    goal_y = NumericProperty(0)
    goal_margin = NumericProperty(20)

    ## sand
    sand = None
    sand_spread = 10

    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        ## adding the paint widget
        self.paint_widget = PaintWidget()
        self.add_widget(self.paint_widget)
        ## adding the car to the game
        self.car = Car()
        self.add_widget(self.car)
        Clock.schedule_interval(self.update, 1/60)

    def on_parent(self, instance, parent):
        if parent:
            self.sand = np.zeros((parent.width, parent.height))
            self.goal_x = self.goal_margin
            self.goal_y = parent.height - self.goal_margin

    ## function to make sand
    def make_sand(self, point):
        ## !!!  THINK ABOUT THE EDGES LATER !!! ##
        self.sand[
            point[0] - self.sand_spread : point[0] + self.sand_spread,
            point[1] - self.sand_spread : point[1] + self.sand_spread,
        ] = 1

    ## function to update the state of the game
    def update(self, dt):
        self.car.update(dt)

        if self.car.distance < 100:
            self.goal_x = self.width - self.goal_x
            self.goal_y = self.height - self.goal_y
            print("goaaaalllllllll!!!!!!!!!!!!!!!")


## the car class
class Car(Widget):
    ## car properties
    velocity = Vector(0, 0)
    normal_velocity = Vector(6, 0)
    sand_velocity = Vector(1, 0)
    angle = NumericProperty(0)
    car_width = NumericProperty(40)
    car_height = NumericProperty(10)
    reward = 0
    distance = 0
    last_distance = 0

    ## car components
    sensor1 = None
    sensor2 = None
    sensor3 = None

    def __init__(self, **kwargs):
        super(Car, self).__init__(**kwargs)
        ## setting car sizez
        self.size = (self.car_width, self.car_height)
        self.sensor1 = Sensor(color=[1, 0, 0, 1], offset_angle=30)
        self.sensor2 = Sensor(color=[0, 1, 0, 1], offset_angle=0)
        self.sensor3 = Sensor(color=[0, 0, 1, 1], offset_angle=-30)

        ## adding the sensors to the car
        self.add_widget(self.sensor1)
        self.add_widget(self.sensor2)
        self.add_widget(self.sensor3)

        ## instanting brain
        self.brain = Dqn(5, 3, 0.9)

    ## function to update state of car
    def update(self, dt):
        velocity = self.normal_velocity
        ## getting distance from goal
        self.distance = np.sqrt(
            (self.x - self.parent.goal_x) ** 2 + (self.y - self.parent.goal_y) ** 2
        )
        if self.parent.sand[int(self.pos[0]), int(self.pos[1])] == 1:
            velocity = self.sand_velocity
            self.reward = -1
        else:
            velocity = self.normal_velocity
            self.reward = -0.2
            if self.distance < self.last_distance:
                self.reward = 0.1

        ## getting car's orientation from goal
        goal_dist_x = self.parent.goal_x - self.x
        goal_dist_y = self.parent.goal_y - self.y
        orientation = Vector(*self.velocity).angle((goal_dist_x, goal_dist_y)) / 180

        ## bounding car within bounds
        self.bound_within()

        ## updating brain and getting next action to play
        action = self.brain.update(
            [
                self.sensor1.signal,
                self.sensor2.signal,
                self.sensor3.signal,
                orientation,
                -orientation,
            ],
            self.reward,
        )
        
        rotation = [0, 20, -20][action]
        self.angle = (self.angle + rotation) % 360
        self.velocity = velocity.rotate(self.angle)
        self.pos = self.velocity + self.pos

        ## updating the sensors
        self.sensor1.update(dt)
        self.sensor2.update(dt)
        self.sensor3.update(dt)

        self.last_distance = self.distance

    ## function to keep car within bounds
    def bound_within(self):
        if self.pos[0] < self.parent.car_margin:
            self.pos[0] = self.parent.car_margin
            self.reward = -1
        elif self.pos[0] > self.parent.width - self.width - self.parent.car_margin:
            self.pos[0] = self.parent.width - self.width - self.parent.car_margin
            self.reward = -1

        if self.pos[1] < self.parent.car_margin:
            self.pos[1] = self.parent.car_margin
            self.reward = -1
        elif self.pos[1] > self.parent.height - self.width - self.parent.car_margin:
            self.pos[1] = (
                self.parent.height - self.width - self.parent.car_margin
            )  ## implement here better later on
            self.reward = -1


## the sensor class
class Sensor(Widget):
    radius = NumericProperty(10)
    signal = NumericProperty(0)
    color = ColorProperty([0, 0, 0, 0])
    offset = NumericProperty(50)
    offset_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Sensor, self).__init__(**kwargs)
        self.size = (10, 10)

    def on_parent(self, instance, parent):
        self.pos[0] = parent.pos[0] + parent.width
        self.pos[1] = parent.pos[1] + parent.height * 0.5 - self.size[0] * 0.5

    ## function to update sensor state
    def update(self, dt):
        new_pos = [
            self.parent.pos[0] + self.parent.width * 0.5,
            self.parent.pos[1] + self.parent.height * 0.5 - self.size[1] * 0.5,
        ]
        self.pos = (
            Vector(self.offset, 0).rotate(self.parent.angle + self.offset_angle)
            + new_pos
        )

        sand_map = self.parent.parent.sand
        ind_x = int(self.pos[0])
        ind_y = int(self.pos[1])
        self.signal = int(
            np.sum(
                sand_map[
                    ind_x - self.radius : ind_x + self.radius,
                    ind_y - self.radius : ind_y + self.radius,
                ]
            )
            / 400
        )

        world = self.parent.parent
        if (
            self.x > world.width - world.car_margin
            or self.x < world.car_margin
            or self.y > world.height - world.car_margin
            or self.y < world.car_margin
        ):
            self.signal = 1.0


## paint widget
class PaintWidget(Widget):
    sand_color = ColorProperty("#e6aa3c")
    lines = []

    def __init__(self, **kwargs):
        super(PaintWidget, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        with self.canvas.before:
            Color(rgb=self.sand_color)
            line = Line(points=(touch.x, touch.y), width=5)
            touch.ud["current_line"] = line
            self.lines.append(line)
        # return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        with self.canvas.before:
            touch.ud["current_line"].points += [touch.x, touch.y]

        self.parent.make_sand((int(touch.x), int(touch.y)))


## the game app
class GameApp(App):
    pass


GameApp().run()
