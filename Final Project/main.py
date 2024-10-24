import random
#chicken game

#rule 
rule = {
    ('Trusting', 'Trusting'): (1, 1),
    ('Trusting', 'Defiant'): (0, 3),
    ('Defiant', 'Trusting'): (3, 0),
    ('Defiant', 'Defiant'): (-100, -100) # dead!
}

class Bot_Player:
    def __init__(self, type):
        self.type = type
        self.score=100

    # def play_chicken(self, opponent):
    #     # Implement the Chicken Game logic here
    #     pass

class AlwaysBetray(Bot_Player):
    def __init__(self):
        super().__init__("AlwaysBetray")

    def play(self, history):
        return "Defiant"

class AlwaysCooperate(Bot_Player):
    def __init__(self):
        super().__init__("AlwaysCooperate")

    def play(self, history):
        return "Trusting"
    
class Copycat(Bot_Player):
    def __init__(self):
        super().__init__("Copycat")
        self.opponent_last_move = None

    def play(self, history):
        if not history:
            return "Trusting"
        else:
            self.opponent_last_move = history[-1][1]
            return self.opponent_last_move
        
class Random(Bot_Player):
    def __init__(self):
        super().__init__("Random")
        self.moves = ('Trusting', 'Defiant')

    def play(self, history):
        return random.choice(self.moves)

# def fitness(player):
#     # Define how fitness is calculated
#     pass

# def selection(population):
#     # Select the best-performing players
#     pass

# def crossover(parent1, parent2):
#     # Combine traits from parent players
#     pass

# def mutate(player):
#     # Introduce small random changes
#     pass

# Initialize population
# population = [Player(random.choice(["Cooperator", "Defector"])) for _ in range(100)]

# # Run genetic algorithm
# for generation in range(100):
#     selected = selection(population)
#     new_population = []
#     for i in range(len(selected)):
#         parent1, parent2 = random.sample(selected, 2)
#         offspring = crossover(parent1, parent2)
#         mutate(offspring)
#         new_population.append(offspring)
#     population = new_population
