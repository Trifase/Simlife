from random import sample, choice

class Environment:
    def __init__(self, size=1000, food_density=0.10):
        self.size = size
        self.food_density = food_density
        self.x = range(0, size)
        self.food_pos = sample(self.x, int(size * food_density))

class Organism:
    def __init__(self, env, parent=None):
        self.env = env
        self.food = 0
        self.pos = choice(self.env.x)
        self.speed = 1
        self.direction = choice[1, -1]

print()