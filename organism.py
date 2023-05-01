import random
import pygame
from food import Food

class Organism:
    def __init__(self, env, pos_x=None, pos_y=None, gen=0):

        self.env = env
        self.age = 0
        self._flipped = False
        self.gen = gen
        self.number = random.choice(range(0, 1000000))

        self.pos_x = pos_x
        self.pos_y = pos_y

        
        if not pos_x:
            self.pos_x = random.choice(self.env.x)
        if not pos_y:
            self.pos_y = random.choice(self.env.y)

        self.coord = (self.pos_x, self.pos_y)

        self.hp = 100
        self.hunger = 100
        self.speed = random.choice(range(1, 3))

        self.minimum_steps_to_maturity = 5 * self.env.steps_per_day
        self.pregancy_duration_steps = 2 * self.env.steps_per_day
        self.is_pregnant = False
        self.steps_pregnant = 0
        self.total_steps_last_birth = 0
        self.steps_between_births = 2 * self.env.steps_per_day

        self.target = None
        self.random_direction = random.choice(['up', 'down', 'left', 'right'])


    def select_random_neighbors(self, coords, n, radius):
        x, y = coords
        neighbors = []
        while len(neighbors) < n:
            dx, dy = random.choice([(i, j) for i in range(-radius, radius+1) for j in range(-radius, radius+1) if (i, j) != (0, 0)])
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x <= self.env.size and 0 <= new_y <= self.env.size:
                neighbors.append((new_x, new_y))
        return neighbors

    def try_to_become_pregnant(self):
        if random.randint(0, 10) < 2:
            self.is_pregnant = True
            self.steps_pregnant = 0
        return

    def give_birth(self):
        self.is_pregnant = False
        self.total_steps_last_birth = self.env.total_steps
        self.steps_pregnant = 0
        if self.hp > 50:
            self.hp -= 30
            n_children = random.choice(range(1, 2))
            next_gen = self.gen + 1
            for neighboor in self.select_random_neighbors(self.coord, n_children, 1):
                if neighboor not in self.env.organism_map.keys():

                    new_baby = Organism(self.env, pos_x=neighboor[0], pos_y=neighboor[1], gen=next_gen)
                    new_baby.draw()
                    self.env.population.append(new_baby)
        else:
            self.hp -= 10 # This is like an abortion
            new_food = Food(self.env, self.coord[0], self.coord[1])
            new_food.draw()
            self.env.food.append(new_food)


        return

    def image(self):
        if self.is_pregnant:
            image = pygame.image.load(f'res/{self.env.scale}/pregnant.png')
        elif self.age > 10:
            image = pygame.image.load(f'res/{self.env.scale}/organism.png')
        else:
            image = pygame.image.load(f'res/{self.env.scale}/baby.png')

        if self.random_direction == 'right' and not self._flipped:
            return pygame.transform.flip(image, True, False)
        elif self.random_direction == 'left' and self._flipped:
            self._flipped = False
            return pygame.transform.flip(image, True, False)
        
        else:
            if self._flipped:
                return pygame.transform.flip(image, True, False)
            else:
                return image


    @property
    def display_info(self):
        info = ""
        info += f"Type    : {type(self).__name__}\n" 
        info += f"Number  : # {self.number}\n" 
        info += f"HP      : {self.hp}\n" 
        info += f"Hunger  : {self.hunger}\n" 
        info += f"Speed   : {self.speed}\n" 
        info += f"Gen     : {self.gen}\n"
        info += f"Age     : {self.age}\n"
        info += f"Pregnant: {self.is_pregnant}\n"
        if self.is_pregnant:
            info += f"Steps pregnant: {self.steps_pregnant}\n"
        return info

    def eat(self):
        if self.coord in self.env.food_map.keys():
            food_piece = self.env.food_map[self.coord]
            self.hunger += food_piece.food_value()
            self.env.food.remove(food_piece)
            # for food in self.env.food:
            #     if food.coord == self.coord:
            #         self.env.food.remove(food)
            if self.hunger > 100:
                self.hunger = 100

    def move(self):
        for _ in range(0, self.speed):
            if self.random_direction == 'up':
                self.pos_y += 1
            elif self.random_direction == 'down':
                self.pos_y -= 1
            elif self.random_direction == 'left':
                self.pos_x -= 1
            elif self.random_direction == 'right':
                self.pos_x += 1

            if self.pos_x < 0:
                self.pos_x = self.env.size
            elif self.pos_x > self.env.size:
                self.pos_x = 0

            if self.pos_y < 0:
                self.pos_y = self.env.size
            elif self.pos_y > self.env.size:
                self.pos_y = 0

            self.random_direction = random.choice(['up', 'down', 'left', 'right'])
            self.coord = (self.pos_x, self.pos_y)
            self.eat()

    def die(self):
        self.env.population.remove(self)
        self.env.food.append(Food(self.env, pos_x=self.pos_x, pos_y=self.pos_y))
        # print(f"Organism {self.number} has died. - Gen: {self.gen} Speed: {self.speed}")
        del self

    def draw(self):
        image = self.image()
        self.colorImage = pygame.Surface(image.get_size()).convert_alpha()
        self.color = (int(255 / 100 * self.hp if self.hp > 0 else 0), 0, 0)
        self.colorImage.fill(self.color)
        image.blit(self.colorImage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        self.env.screen.blit(image, (self.coord[0] * self.env.scale, self.coord[1] * self.env.scale))
