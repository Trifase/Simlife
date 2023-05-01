import random
import pygame

class Food:
    def __init__(self, env, pos_x=None, pos_y=None, decay=40, gen=1, age=0):
        self.env = env
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.decay = random.randint(decay, decay*3)
        self.pollinated = False
        self.gen = gen
        self.age = age


        if not pos_x:
            self.pos_x = random.choice(self.env.x)
        if not pos_y:
            self.pos_y = random.choice(self.env.y)

        self.coord = (self.pos_x, self.pos_y)


    def food_value(self):
        return 20 if self.age > 10 else 5

    def image(self):
        return pygame.image.load(f'res/{self.env.scale}/food.png') if self.age > 10 else pygame.image.load(f'res/{self.env.scale}/sprout.png')

    @property
    def display_info(self):
        return  f"Type : {type(self).__name__}\n" \
                f"Gen  : {self.gen}\n" \
                f"Age  : {self.age}\n" \
                f"Value: {self.food_value()}\n" \
                f"Decay: {self.decay}\n" 

    def select_random_neighbors(self, coords, n, radius):
        x, y = coords
        neighbors = []
        while len(neighbors) < n:
            dx, dy = random.choice([(i, j) for i in range(-radius, radius+1) for j in range(-radius, radius+1) if (i, j) != (0, 0)])
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x <= self.env.size and 0 <= new_y <= self.env.size:
                neighbors.append((new_x, new_y))
        return neighbors


    def make_children(self):

        self.pollinated = True
        n_seeds = random.choice(range(0, 4))
        for neighboor in self.select_random_neighbors(self.coord, n_seeds, 2):
            if neighboor not in self.env.food_map.keys():
                new_food = Food(self.env, neighboor[0], neighboor[1], gen=self.gen + 1)
                new_food.draw()
                self.env.food.append(new_food)

    def draw(self):
        image = self.image()
        self.colorImage = pygame.Surface(image.get_size()).convert_alpha()
        self.color = (0, 255, 0)
        if self.decay < 10:
            self.color = (115, 130, 100)
        self.colorImage.fill(self.color)
        image.blit(self.colorImage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        self.env.screen.blit(image, (self.coord[0] * self.env.scale, self.coord[1] * self.env.scale))
