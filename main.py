from random import sample, choice

class Environment:
    def __init__(self, size=1000, food_density=0.10, n=20):
        self.size = size
        self.n = n
        self.x = range(0, size)
        self.y = range(0, size)

        self.food_density = food_density
        self.food_pos = self.get_food_positions()
        self.population = self.create_population()

    def create_population(self):
        return [Organism(self) for x in range(0, self.n)]

    def get_positions(self):
        return [organism.coord for organism in self.population]

    def create_food(self):
        return [Food(self) for x in range(0, int((self.size * self.food_density)))]
    
    def get_food_positions(self):
        return [food.coord for food in self.create_food()]

class Food:
    def __init__(self, env):
        self.env = env
        self.pos_x = choice(self.env.x)
        self.pos_y = choice(self.env.y)
        self.coord = (self.pos_x, self.pos_y)
        self.food_value = 1

class Organism:
    def __init__(self, env, parent=None):
        self.env = env
        self.food = 0
        self.pos_x = choice(self.env.x)
        self.pos_y = choice(self.env.y)
        self.coord = (self.pos_x, self.pos_y)
        self.speed = 1
        self.direction = choice(['up', 'down', 'left', 'right'])

        def eat(self):
            if self.food < 2 and self.coor in self.env.food_pos:
                self.food += 1
                self.env.food_pos.remove(self.coord)

        def move(self):
            if self.food < 2:
                if self.direction == 'up':
                    self.pos_y += self.speed
                elif self.direction == 'down':
                    self.pos_y -= self.speed
                elif self.direction == 'left':
                    self.pos_x -= self.speed
                elif self.direction == 'right':
                    self.pos_x += self.speed

            if self.pos_x < 0:
                self.pos_x = self.env.size
            elif self.pos_x > self.env.size:
                self.pos_x = 0

            if self.pos_y < 0:
                self.pos_y = self.env.size
            elif self.pos_y > self.env.size:
                self.pos_y = 0

            self.coord = (self.pos_x, self.pos_y)
            self.eat()
            

env = Environment(size=10, food_density=0.2, n=5)
