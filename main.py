import pygame
from env import Environment
import matplotlib.pyplot as plt



# size of the square environment
SIZE = 50

# number of initial organisms
N = 30

# food density as a percentage of the environment area
FOOD_DENSITY = 0.1

# This is the sprite default size, and used to convert simulation cells coordinate in the pixel grid
SCALE_FACTOR = 20

pygame.init()

env = Environment(size=SIZE, scale=SCALE_FACTOR, food_density=FOOD_DENSITY, n=N, fps=100)

print(env.info)

# This is blocking - with i= 0, it will run forever
env.simulate(i=0) 

food = env.food_count
population = env.pop_count

# create a simple matplotlib graph with two lines for food and population
fig, ax = plt.subplots()
ax.plot(food, 'g-', label='food')
ax.plot(population, 'r-', label='population')
ax.set_xlabel('time ticks')
ax.set_ylabel('food/population')
ax.legend()
# save the figure in a file
fig.savefig('food_population.png')
