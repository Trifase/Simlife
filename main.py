import os
from random import choice

import imageio
import matplotlib.pyplot as plt
import pygame
import time

def mstime():
    return round(time.time() * 1000)





class Environment:
    def __init__(self, size=1000, food_density=0.10, n=20, regrowth=True, regrowth_rate=5, food_decay=True, screen=None):
        self.size = size
        self.n = n
        self.x = range(0, size)
        self.y = range(0, size)
        self.steps_per_day = 20
        self.default_generations = 20

        self.food_density = food_density
        self.food_decay = food_decay
        self.regrowth = regrowth
        self.regrowth_rate = regrowth_rate
        self.food = []
        # self.add_food_to_env(int(self.size**2 * self.food_density))
        self.population = self.create_population()

        self.generation = 0
        self.steps_today = 0
        self.day_complete = False

        self.scale = 10
        self.screen = screen
        if not self.screen:
            self.screen = pygame.display.set_mode((self.size * self.scale, self.size * self.scale))
        self.clock = pygame.time.Clock()


        self.info = f"""Environment created with {self.size}x{self.size} area and {self.n} organisms.
        Food density is {self.food_density} and regrowth_rate is {self.regrowth_rate}."""

        self.post_init()

    def post_init(self):
        initial_food = int(self.size**2 * self.food_density)
        self.add_food_to_env(initial_food)
        # self.plot('gen_0000_initial_state')

    @property
    def food_map(self):
        return {food.coord: food for food in self.food}

    def run_step(self):

        print(f'[{self.generation + 1}] Running step {self.steps_today + 1}/{self.steps_per_day}...')
        self.steps_today += 1
        for organism in self.population:

            # Basic rate of hunger depletion
            organism.hunger -= 1

            # Bottom out hunger at -20
            if organism.hunger < -20:
                organism.hunger = -20

            # With hunger negative, organism loses hp
            if organism.hunger <= 0:
                organism.hp -= 2

            # With hunger positive, organism gains hp
            if organism.hunger > 0:
                organism.hp += 1

            # Top out hp at 100
            if organism.hp > 100:
                organism.hp = 100

            # If organism has no hp, it dies
            if organism.hp == 0:
                organism.die()
            else:
                organism.move()

        for food in self.food:
            if self.food_decay:
                food.decay -= 1
                if food.decay == 0:
                    self.food.remove(food)

        if self.steps_today == self.steps_per_day:
            self.day_complete = True

    def add_food_to_env(self, n=None):
        if not n:
            n = self.regrowth_rate
        self.food = self.food + self.create_food(n)

    def begin_day(self):
        if self.regrowth:
            self.add_food_to_env()

    def draw(self):
        self.screen.fill((255,255,255))
        for organism in self.population:
            organism.draw()
        for food in self.food:
            food.draw()
        pygame.display.flip()


    def end_day(self):
        # If for whatever reasons there are orgasnism alive with no hp, kill them
        survivors = [org for org in self.population if org.hp > 0]
        # children = [Organism(self, parent=org, gen=org.gen + 1) for org in survivors]
        # reset the hunger of the survivors
        # for survivor in survivors:
        #     survivor.hunger = 0

        # mutate the children?
        self.generation += 1
        self.population = survivors# + children
        self.steps_today = 0
        self.day_complete = False

    def simulate(self, i:int=None, graphs:bool=True, frequency:str='step', gif:bool=True):
        """
        This will run the simulation for i generations. i is inherited from the Environment class, but can be overridden here.

        Args:
            i (int, optional): Number of days to simulate. Defaults to None, which will use the default_generations value.
            graphs (bool, optional): enable the generation of matplotlib graphs. Defaults to True.
            frequency (str, optional): determines the frequency of matplotlig graphs. Can be 'step' or 'day'. Defaults to 'step'.
            gif (bool, optional): enable the generation of a gif at the end of the simulation. Defaults to True.
        """
        if not i:
            i = self.default_generations
        print(f'Simulating {i} generations...')

        while self.generation < i:

            self.time_last_step = mstime()
            while mstime() < self.time_last_step + 200:
                time.sleep(0.02)
            self.run_step()
            # self.clock.tick(6)
            gen = self.generation + 1
            step = self.steps_today + 1

            self.draw()
            if graphs and frequency == 'step':
                self.plot(f'gen_{gen:02d}_step_{step:02d}')

            if self.day_complete:
                print()
                print(f"Generation {gen:02d} complete: {len(self.population)} organisms remain.")
                print(f"There are {len(self.food)} food items remaining.")
                for organism in self.population:
                    print(f"Organism #{organism.number} has {organism.hp} hp and {organism.hunger} hunger.")
                print()

                if graphs and frequency == 'day':
                    self.plot(f'gen_{gen:02d}')
                self.end_day()
                self.begin_day()

        print('Simulation complete.')
        if gif:
            self.create_gif()
        return

    def create_population(self):
        return [Organism(self) for x in range(0, self.n)]

    def get_positions(self):
        return [organism.coord for organism in self.population]

    def create_food(self, n=None):
        if not n:
            n = int((self.size**2 * self.food_density))
        print(f"Adding {n} food items to the environment...")
        return [Food(self) for x in range(0, n)]

    def get_food_positions(self, n=None):
        return [food.coord for food in self.food]
    
    def plot(self, filename):
        fig, ax = plt.subplots()
        # Organisms
        ax.plot([organism.pos_x for organism in self.population], [organism.pos_y for organism in self.population], 'rD')
        # Food
        ax.plot([food.pos_x for food in self.food], [food.pos_y for food in self.food], 'g.', markersize=2)
        title = f'Generation {self.generation + 1} - Step {self.steps_today + 1}'
        plt.title(title)
        
        plt.xlim([-2, self.size + 2])
        plt.ylim([-2, self.size + 2])
        plt.savefig(f'frames/{filename}.png')
        plt.close()

    def create_gif(self, duration=0.5, gif_filename='timelapse.gif'):
        print("Making a gif...")
        frames = []
        file_names = sorted((fn for fn in os.listdir('frames') if fn.endswith('.png')))
        for filename in file_names:
            frames.append(imageio.imread(f"frames/{filename}"))
        imageio.mimsave(gif_filename, frames, format='GIF', duration=duration)

class Food:
    def __init__(self, env, pos_x=None, pos_y=None, decay=60):
        self.env = env
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.decay = decay
        self.image = pygame.image.load('res/food.png')

        if not pos_x:
            self.pos_x = choice(self.env.x)
        if not pos_y:
            self.pos_y = choice(self.env.y)

        self.coord = (self.pos_x, self.pos_y)
        self.food_value = 1

    def draw(self):
        self.colorImage = pygame.Surface(self.image.get_size()).convert_alpha()
        self.color = (0, 255, 0)
        self.colorImage.fill(self.color)
        self.image.blit(self.colorImage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        self.env.screen.blit(self.image, (self.coord[0] * self.env.scale, self.coord[1] * self.env.scale))

class Organism:
    def __init__(self, env, gen=0, parent=None):
        self.image = pygame.image.load('res/organism.png')
        self.env = env
        self.parent = parent
        self.gen = gen
        self.number = choice(range(0, 1000000))

        self.pos_x = choice(self.env.x)
        self.pos_y = choice(self.env.y)
        self.coord = (self.pos_x, self.pos_y)


        self.hp = 100
        self.hunger = 100
        self.speed = choice(range(1, 3))

        self.minimum_days_to_maturity = 3
        self.pregancy_duration = 2
        self.is_pregnant = False

        self.days_alive = 0


        self.random_direction = choice(['up', 'down', 'left', 'right'])

    def eat(self):
        if self.coord in self.env.get_food_positions():
            self.hunger += 20
            self.env.food.remove(self.env.food_map[self.coord])
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

            self.random_direction = choice(['up', 'down', 'left', 'right'])
            self.coord = (self.pos_x, self.pos_y)
            self.eat()

    def die(self):
        self.env.population.remove(self)
        self.env.food.append(Food(self.env, pos_x=self.pos_x, pos_y=self.pos_y))
        print(f"Organism {self.number} has died.")
        del self

    def draw(self):
        self.colorImage = pygame.Surface(self.image.get_size()).convert_alpha()
        self.color = (int(255 / 100 * self.hp if self.hp > 0 else 0), 0, 0)
        self.colorImage.fill(self.color)
        self.image.blit(self.colorImage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        self.env.screen.blit(self.image, (self.coord[0] * self.env.scale, self.coord[1] * self.env.scale))

SIZE = 100
SCALE_FACTOR = 10

pygame.init()


env = Environment(size=SIZE, food_density=0.2, n=50, food_decay=False, regrowth=False)
env.screen.fill((255, 255, 255))

print(env.info)

env.simulate(20, graphs=False, gif=False)
# env.create_gif(duration=0.1, gif_filename='timelapse_fast.gif')