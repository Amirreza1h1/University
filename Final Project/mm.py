import numpy as np
from deap import base, creator, tools, algorithms

# Define the payoff matrices for both games
evolution_of_trust_payoff = {
    ('Trusting', 'Trusting'): (2, 2),
    ('Trusting', 'Defiant'): (0, 0),
    ('Defiant', 'Trusting'): (0, 0),
    ('Defiant', 'Defiant'): (-1, -1)
}

chicken_game_payoff = {
    ('Swerve', 'Swerve'): (2, 2),
    ('Swerve', 'Drive Straight'): (-1, 1),
    ('Drive Straight', 'Swerve'): (1, -1),
    ('Drive Straight', 'Drive Straight'): (0, 0)
}

# Create the fitness function
def fitness(individual):
    evotrust_fitness = 0
    chicken_fitness = 0
    
    # Map Evolution of Trust types to Chicken Game actions
    evotrust_to_chicken = {
        'Trusting': 'Swerve',
        'Defiant': 'Drive Straight'
    }
    
    for i in range(len(individual)):
        evotrust_action = individual[i]
        chicken_action = evotrust_to_chicken[evotrust_action]
        
        evotrust_fitness += evolution_of_trust_payoff[(evotrust_action, evotrust_action)][0] + \
                           chicken_game_payoff[(chicken_action, chicken_action)][0]
        
        chicken_fitness += chicken_game_payoff[(chicken_action, chicken_action)][0]
    
    return sum(evotrust_fitness), sum(chicken_fitness)

# Create the genetic algorithm
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=fitness)

toolbox = base.Toolbox()
toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=100)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Register the fitness function
toolbox.register("evaluate", fitness)

# Register selection, mutation, and crossover operators
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("crossover", tools.cxTwoPoint)

# Set up the genetic algorithm parameters
pop_size = 100
generations = 50
mutation_rate = 0.05
crossover_prob = 0.7

# Run the genetic algorithm
population = toolbox.population(n=pop_size)
for gen in range(generations):
    offspring = algorithms.varAnd(population, toolbox, cxpb=crossover_prob, mutpb=mutation_rate)
    fits = toolbox.map(toolbox.evaluate, offspring)
    
    # Select the fittest individuals
    selected_offspring = toolbox.select(offspring, k=len(population))
    
    population = selected_offspring
    
    print(f"Generation {gen+1}: Average fitness - Evolution of Trust: {-sum(fits)/len(fits)}, Chicken Game: {-sum(fits)/len(fits)}")

# Print the final results
print("\nFinal population:")
for individual in population:
    print(individual)