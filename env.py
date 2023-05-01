
import time

import pygame

from food import Food
from organism import Organism


def mstime():
    return round(time.time() * 1000)

class Environment:
    def __init__(self, size=1000, food_density=0.10, n=20, regrowth=True, regrowth_rate=5, food_decay=True, screen=None, scale=10, fps=5):
        self.size = size
        self.n = n
        self.x = range(0, size)
        self.y = range(0, size)
        self.steps_per_day = 20
        self.default_days = 20

        self.food_density = food_density
        self.food_decay = food_decay
        self.regrowth = regrowth
        self.regrowth_rate = regrowth_rate
        self.food = []
        self.first_time_food = True


        self.day = 0
        self.steps_today = 0
        self.day_complete = False
        self.total_steps = 0

        self.sim_fps = fps
        self.scale = scale
        self.screen = screen
        if not self.screen:
            self.screen = pygame.display.set_mode((self.size * self.scale + 400, self.size * self.scale))

        self.population = self.create_population()
        self.clock = pygame.time.Clock()
        self.end_simulation = False
        self.pause_simulation = False
        self.inspection_mode = False

        self.pop_count = []
        self.food_count = []


        self.info = f"Environment created with {self.size}x{self.size} area and {self.n} organisms.\n" \
            f"Food density is {self.food_density} and regrowth_rate is {self.regrowth_rate}.\n" \
            f"Regrowth is set to {self.regrowth} and food_decay is set to {self.food_decay}." \

        self.post_init()

    def post_init(self):
        initial_food = int(self.size**2 * self.food_density)
        self.add_food_to_env(initial_food)

    @property
    def sidebar(self):
        return self.size * self.scale + 10
    
    def sidebar_info_text(self):
        info_text = ""
        info_text += f"Day: {self.day}\n"
        info_text += f"Steps Today: {self.steps_today}\n"
        info_text += f"Food: {len(self.food)}\n"
        info_text += f"Population: {len(self.population)}\n"
        return info_text

    @property
    def food_map(self):
        return {food.coord: food for food in self.food}
    
    @property
    def organism_map(self):
        return {organism.coord: organism for organism in self.population}

    def run_step(self):

        # print(f'[{self.day + 1}] Running step {self.steps_today + 1}/{self.steps_per_day}...')
        self.steps_today += 1
        self.total_steps += 1
        self.pop_count.append(len(self.population))
        self.food_count.append(len(self.food))

        # This is where we check for a pause button, or a stop button, or an inspection button
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end_simulation = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.pause_simulation = not self.pause_simulation
                elif event.key == pygame.K_q:
                        self.end_simulation = True
                elif event.key == pygame.K_i:
                        self.inspection_mode = not self.inspection_mode



        for organism in self.population:
            # You lived another day! Huzzah!
            organism.age += 1

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

            if organism.is_pregnant:
                organism.steps_pregnant += 1

            # We check if it's time to become pregnant
            if (
                not organism.is_pregnant
                and organism.age > organism.minimum_steps_to_maturity
                and self.total_steps - organism.total_steps_last_birth > organism.steps_between_births

            ):
                organism.try_to_become_pregnant()

            # We check if it's time to give birth
            if (
                organism.is_pregnant
                and organism.steps_pregnant >= organism.pregancy_duration_steps
            ):
                organism.give_birth()

        for food in self.food:
            food.age += 1
            if self.food_decay:
                food.decay -= 1
                if food.decay == 0:
                    self.food.remove(food)
            if food.decay < 6 and not food.pollinated:
                food.make_children()

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

        # We print a little summary on the side of the screen
        info_text = self.sidebar_info_text()
        font = pygame.font.SysFont('Consolas', 20)
        text = font.render(info_text, True, pygame.color.Color('Black'))
        self.screen.blit(text, (self.size * self.scale + 10, 0))

        pygame.display.flip()

    def end_day(self):
        # If for whatever reasons there are orgasnism alive with no hp, kill them
        survivors = [org for org in self.population if org.hp > 0]
        # children = [Organism(self, parent=org, gen=org.gen + 1) for org in survivors]
        # reset the hunger of the survivors
        # for survivor in survivors:
        #     survivor.hunger = 0

        # mutate the children?
        self.day += 1
        self.population = survivors# + children
        self.steps_today = 0
        self.day_complete = False

    def simulate(self, i:int=None):
        """
        This will run the simulation for i days. i is inherited from the Environment class, but can be overridden here.

        Args:
            i (int, optional): Number of days to simulate. Defaults to None, which will use the default_days value.
         
        """
        if i is None:
            i = self.default_days

        if i == 0:
            i = 99999999999

        # print(f'Simulating {i} days...')

        while self.day < i:

            # Checks that at least 1/sim_fps seconds have passed from the start of the previous step.
            # (for example, if sim_fps is 5, we want to wait 200ms between steps)
            self.time_last_step = mstime()
            while mstime() < self.time_last_step + (1000 // self.sim_fps):
                time.sleep(0.01)


            # Here we check if we have, for some reason, to end the simulation
            if self.end_simulation:
                break

            # Here we check if we have to pause the simulation
            if self.pause_simulation:
                pause_text = pygame.font.SysFont('Consolas', self.size).render('PAUSA', True, pygame.color.Color('Black'))
                text_width = pause_text.get_width()
                text_height = pause_text.get_height()
                self.screen.blit(pause_text,
                                (int(self.size * self.scale / 2) - int(text_width / 2),
                                 int(self.size * self.scale / 2) - int(text_height / 2))
                                 )
                pygame.display.flip()

                # Mentre siamo in pausa, non succede niente. L'unica cosa che facciamo è
                # ascoltare eventi, per uscire dalla pausa o dalla simulazione.
                while self.pause_simulation:
                    time.sleep(0.1)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.end_simulation = True
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                self.pause_simulation = not self.pause_simulation

            if self.inspection_mode:
                pause_text = pygame.font.SysFont('Consolas', 40).render('INSPECTION MODE', True, pygame.color.Color('Black'))
                text_width = pause_text.get_width()
                text_height = pause_text.get_height()
                self.screen.blit(pause_text,
                                (int(self.size * self.scale / 2) - int(text_width / 2),
                                 int(self.size * self.scale) - int(text_height))
                                 )
                pygame.display.flip()

                while self.inspection_mode:
                    time.sleep(0.1)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.end_simulation = True
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                            self.inspection_mode = not self.inspection_mode
                        if event.type == pygame.MOUSEBUTTONUP:
                            mouse_pos = pygame.mouse.get_pos()

                            entity = self.get_entity_on_coord(mouse_pos)
                            if entity:
                                pygame.draw.rect(self.screen, pygame.color.Color('White'), pygame.Rect(self.size * self.scale + 10, 200,
                                                                                                       self.size * self.scale + 400, 
                                                                                                       self.size * self.scale))
                                info_text = entity.display_info
                                font = pygame.font.SysFont('Consolas', 20)
                                text = font.render(info_text, True, pygame.color.Color('Black'))
                                self.screen.blit(text, (self.size * self.scale + 10, 200))
                                pygame.display.flip()


            # This is where all the movements, eating, death and birth happens
            # This is also where day_complete is set, if conditions are met
            self.run_step()


            # This will draw the whole frame
            self.draw()

            # This will stop the cycle of steps for today, end the current day and begin a new day.
            if self.day_complete:
                # print()
                # print(f"Day {gen:02d} complete: {len(self.population)} organisms remain.")
                # print(f"There are {len(self.food)} food items remaining.")
                # for organism in self.population:
                #     print(f"Organism #{organism.number} has {organism.hp} hp and {organism.hunger} hunger.")
                # print()


                # Here we kill, birth and advance the day. This is where we set day_complete to False.
                self.end_day()

                # This is where we add food to the environment, if regrowth is enabled.
                self.begin_day()
                # print(self.pop_count)
                # print(self.food_count)
                # print()



        # print('Simulation complete.')
        # print(f'The simulation lasted {self.day} days.')
        return

    def create_population(self):
        return [Organism(self) for x in range(0, self.n)]

    def get_positions(self):
        return [organism.coord for organism in self.population]

    def get_entity_on_coord(self, mouse_pos):
        coord = (mouse_pos[0] // self.scale, mouse_pos[1] // self.scale)
        if self.food_map.get(coord):
            return self.food_map.get(coord)
        elif self.organism_map.get(coord):
            return self.organism_map.get(coord)
        else:
            return None

    def create_food(self, n=None):
        if not n:
            n = int((self.size**2 * self.food_density))
        # print(f"Adding {n} food items to the environment...")
        if self.first_time_food:
            self.first_time_food = False
            return [Food(self, age=11) for x in range(0, n)]
        else:
            return [Food(self) for x in range(0, n)]

    def get_food_positions(self, n=None):
        return [food.coord for food in self.food]
