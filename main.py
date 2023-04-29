from random import choice
import imageio
import matplotlib.pyplot as plt


class Environment:
    def __init__(self, size=1000, food_density=0.10, n=20, regrowth=5):
        self.size = size
        self.n = n
        self.x = range(0, size)
        self.y = range(0, size)
        self.steps_per_day = 20
        self.default_generations = 20

        self.food_density = food_density
        self.regrowth = regrowth
        self.food = self.create_food()
        self.add_food_to_env(int(self.size**2 * self.food_density))
        self.population = self.create_population()

        self.generation = 0
        self.steps_today = 0
        self.day_complete = False

    def run_step(self):
        print(f'[{self.generation + 1}] Running step {self.steps_today + 1}/{self.steps_per_day}...')
        self.steps_today += 1
        for organism in self.population:

            organism.hunger -= 1

            if organism.hunger < -20:
                organism.hunger = -20


            if organism.hunger <= 0:
                organism.hp -= 2

            if organism.hunger > 0:
                organism.hp += 1

            if organism.hp > 100:
                organism.hp = 100

            if organism.hp == 0:
                organism.die()
            else:
                organism.move()

        for food in self.food:
            food.decay -= 1
            if food.decay == 0:
                self.food.remove(food)
        if self.steps_today == self.steps_per_day:
            self.day_complete = True

    def add_food_to_env(self, n=None):
        if not n:
            n = self.regrowth
        self.food = self.food + self.create_food(n)

    def next_gen(self):
        self.add_food_to_env()
        self.generation += 1
        self.steps_today = 0

        survivors = [org for org in self.population if org.hp > 0]
        # children = [Organism(self, parent=org, gen=org.gen + 1) for org in survivors]
        # reset the hunger of the survivors
        # for survivor in survivors:
        #     survivor.hunger = 0

        # mutate the children?
        self.population = survivors# + children
        self.day_complete = False

    def simulate(self, i=None, graphs=True):
        if not i:
            i = self.default_generations
        print(f'Simulating {i} generations...')

        while self.generation < i:
            self.run_step()
            if graphs:
                self.plot(f'gen_{self.generation + 1}_step_{self.steps_today}')

            if self.day_complete:
                print()
                print(f"Generation {self.generation + 1} complete: {len(self.population)} organisms remain.")
                print(f"There are {len(self.food)} food items remaining.")
                for organism in self.population:
                    print(f"Organism #{organism.number} has {organism.hp} hp and {organism.hunger} hunger.")
                print()
                self.next_gen()

        print('Simulation complete.')
        self.create_gif()
        return

    def create_population(self):
        return [Organism(self) for x in range(0, self.n)]

    def get_positions(self):
        return [organism.coord for organism in self.population]

    def create_food(self, n=None):
        if not n:
            n = int((self.size**2 * self.food_density))

        return [Food(self) for x in range(0, n)]

    def get_food_positions(self, n=None):
        return [food.coord for food in self.food]
    
    def plot(self, filename):
        fig, ax = plt.subplots()
        # Organisms
        ax.plot([organism.pos_x for organism in self.population], [organism.pos_y for organism in self.population], 'rD')
        # Food
        ax.plot([food.pos_x for food in self.food], [food.pos_y for food in self.food], 'g+')
        
        plt.xlim([-2, self.size + 2])
        plt.ylim([-2, self.size + 2])
        plt.savefig(f'frames/{filename}.png')
        plt.close()

    def create_gif(self):
        print("Making a gif...")
        frames = []
        for g in range(self.default_generations):
            for s in range(self.steps_per_day):
                frames.append(imageio.imread(f'frames/gen_{g + 1}_step_{s + 1}.png'))
        imageio.mimsave('timelapse.gif', frames, format='GIF', duration=0.1)


class Food:
    def __init__(self, env, pos_x=None, pos_y=None, decay=30):
        self.env = env
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.decay = decay

        if not pos_x:
            self.pos_x = choice(self.env.x)
        if not pos_y:
            self.pos_y = choice(self.env.y)

        self.coord = (self.pos_x, self.pos_y)
        self.food_value = 1



class Organism:
    def __init__(self, env, gen=0, parent=None):
        self.env = env
        self.parent = parent
        self.gen = gen
        self.number = choice(range(0, 1000000))

        self.pos_x = choice(self.env.x)
        self.pos_y = choice(self.env.y)
        self.coord = (self.pos_x, self.pos_y)


        self.hp = 100
        self.hunger = 100
        self.speed = 1

        self.minimum_days_to_maturity = 3
        self.pregancy_duration = 2
        self.is_pregnant = False

        self.days_alive = 0


        self.random_direction = choice(['up', 'down', 'left', 'right'])

    def eat(self):
        if self.coord in self.env.get_food_positions():
            self.hunger += 20
            for food in self.env.food:
                if food.coord == self.coord:
                    self.env.food.remove(food)
            if self.hunger > 100:
                self.hunger = 100

    def move(self):

        if self.random_direction == 'up':
            self.pos_y += self.speed
        elif self.random_direction == 'down':
            self.pos_y -= self.speed
        elif self.random_direction == 'left':
            self.pos_x -= self.speed
        elif self.random_direction == 'right':
            self.pos_x += self.speed

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


env = Environment(size=10, food_density=0.05, n=5)
env.simulate(20, graphs=True)
# env.create_gif()