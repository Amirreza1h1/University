import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.datasets import load_iris

# Load the Iris dataset
data = load_iris()
X = data.data  # Using all four features from the dataset
initial_population = X.copy()  # Use the whole dataset as the initial population

# Define the corrected BBMO algorithm with population history tracking
def bbmo_algorithm(population, generations, crossover_rate=0.7, mutation_rate=0.1, alpha=0.95, initial_temp=1.0):
    temperature = initial_temp
    population_history = [population.copy()]  # Store initial population
    fitness_history = []  # Store fitness for each generation

    for gen in range(generations):
        new_population = []
        fitness_values = []  # Store fitness for current generation
        for queen in population:
            for drone in population:
                distance = np.linalg.norm(queen - drone)  # Calculate distance between queen and drone
                if np.random.rand() < np.exp(-distance / temperature):
                    offspring = crossover_rate * queen + (1 - crossover_rate) * drone
                    # Apply mutation
                    if np.random.rand() < mutation_rate:
                        offspring += np.random.normal(scale=0.1, size=4)  # Introduce noise for mutation
                    new_population.append(offspring)
        
        # Calculate fitness for the new population
        fitness_values = [np.linalg.norm(individual) for individual in new_population]
        
        # Keep population size constant by selecting the best individuals based on fitness
        population = sorted(new_population, key=lambda x: np.linalg.norm(x))[:len(initial_population)]
        temperature *= alpha
        population_history.append(np.array(population))  # Store each generation's population
        fitness_history.append(fitness_values)  # Store fitness for this generation

    return population[0], population_history, fitness_history

np.random.seed(42)  # For reproducibility
best_solution, population_history, fitness_history = bbmo_algorithm(initial_population, generations=80)

# Select generations for plotting
initial_gen = np.array(population_history[0])
middle_gen = np.array(population_history[len(population_history) // 2])
final_gen = np.array(population_history[-1])

# Calculate fitness for each generation for plotting
initial_fitness = [np.linalg.norm(ind) for ind in initial_gen]
middle_fitness = [np.linalg.norm(ind) for ind in middle_gen]
final_fitness = [np.linalg.norm(ind) for ind in final_gen]

# Combine fitness values to find the overall min and max for color scaling
all_fitness = initial_fitness + middle_fitness + final_fitness
fitness_min = min(all_fitness)
fitness_max = max(all_fitness)

# Plotting function
def plot_3d_population(population, fitness, title, ax):
    scatter = ax.scatter(population[:, 0], population[:, 1], population[:, 2], 
                         c=fitness, cmap='viridis', marker='o', vmin=fitness_min, vmax=fitness_max)  # Color by fitness
    ax.set_xlabel("Feature 1")
    ax.set_ylabel("Feature 2")
    ax.set_zlabel("Feature 3")
    ax.set_title(title)
    plt.colorbar(scatter, ax=ax, label='Fitness (Euclidean Norm)')  # Add color bar for fitness

# Create 3D plots for initial, middle, and final generations
fig = plt.figure(figsize=(18, 6))

# Initial Generation Plot
ax1 = fig.add_subplot(131, projection='3d')
plot_3d_population(initial_gen, initial_fitness, "Initial Generation", ax1)

# Middle Generation Plot
ax2 = fig.add_subplot(132, projection='3d')
plot_3d_population(middle_gen, middle_fitness, "Middle Generation", ax2)

# Final Generation Plot
ax3 = fig.add_subplot(133, projection='3d')
plot_3d_population(final_gen, final_fitness, "Final Generation", ax3)

plt.tight_layout()
plt.show()
