import random
import matplotlib.pyplot as plt

# Rule of outcomes for the chicken game
rule = {
    ('Trusting', 'Trusting'): (1, 1),
    ('Trusting', 'Defiant'): (0, 3),
    ('Defiant', 'Trusting'): (3, 0),
    ('Defiant', 'Defiant'): (-100, -100)  # dead!
}

# Base class for a player
class Bot_Player:
    def __init__(self, type):
        self.type = type
        self.score = 100
        self.alive = True

    def update_score(self, outcome):
        self.score += outcome

    def play(self, history):
        raise NotImplementedError("Subclasses should implement this!")

    def reproduce(self):
        # Create a copy of itself (used for reproduction)
        return self.__class__()

# Always betrays (plays 'Defiant')
class AlwaysBetray(Bot_Player):
    def __init__(self):
        super().__init__("AlwaysBetray")

    def play(self, history):
        return "Defiant"

# Always cooperates (plays 'Trusting')
class AlwaysCooperate(Bot_Player):
    def __init__(self):
        super().__init__("AlwaysCooperate")

    def play(self, history):
        return "Trusting"

# Copy the opponent's last move
class Copycat(Bot_Player):
    def __init__(self):
        super().__init__("Copycat")
        self.opponent_last_move = None

    def play(self, history):
        if not history:
            return "Trusting"  # Default to Trusting on the first move
        else:
            self.opponent_last_move = history[-1][1]
            return self.opponent_last_move

# Plays randomly (Trusting or Defiant)
class RandomPlayer(Bot_Player):
    def __init__(self):
        super().__init__("Random")
        self.moves = ('Trusting', 'Defiant')

    def play(self, history):
        return random.choice(self.moves)

# Function to play a round between two players
def play_round(player1, player2, history):
    if not player1.alive or not player2.alive:
        return history  # Skip the round if either player is not alive

    move1 = player1.play(history)
    move2 = player2.play(history)
    history.append((move1, move2))
    outcome1, outcome2 = rule[(move1, move2)]
    # print(outcome1)
    # print(outcome2)

    
    # Update the players' scores
    player1.update_score(outcome1)
    player2.update_score(outcome2)
    
    return history

# Reproduce the winner of the round, handling crash cases
def reproduce_winner(player1, player2, population):
    # Check if both players crashed (both played "Defiant")
    if not player1.alive or not player2.alive:
        # Remove both players from the population
        population.remove(player1)
        population.remove(player2)
        return
    
    if player1.score > player2.score:
        loser = player2
        winner = player1
    elif player2.score > player1.score:
        loser = player1
        winner = player2
    else:  # In case of a tie, randomly pick one to reproduce
        winner, loser = random.choice([(player1, player2), (player2, player1)])

    # Replace the loser in the population with a clone of the winner
    population.remove(loser)
    population.append(winner.reproduce())

# Simulate the game between a population of players and track the number of each type surviving
def simulate_game_population(population, rounds):
    history = []
    
    # Lists to track the number of each player type over rounds
    always_betray_count = []
    always_cooperate_count = []
    copycat_count = []
    random_count = []
    
    for _ in range(rounds):
        # Pair up players randomly for each round
        random.shuffle(population)
        i = 0
        while i < len(population) - 1:
            player1 = population[i]
            player2 = population[i + 1]
            history = play_round(player1, player2, history)
            
            # Reproduce the winner or handle crash case
            reproduce_winner(player1, player2, population)
            i += 2  # Move to the next pair
        
        # Count surviving players of each type
        always_betray_alive = sum(1 for player in population if isinstance(player, AlwaysBetray) and player.alive)
        always_cooperate_alive = sum(1 for player in population if isinstance(player, AlwaysCooperate) and player.alive)
        copycat_alive = sum(1 for player in population if isinstance(player, Copycat) and player.alive)
        random_alive = sum(1 for player in population if isinstance(player, RandomPlayer) and player.alive)
        
        always_betray_count.append(always_betray_alive)
        always_cooperate_count.append(always_cooperate_alive)
        copycat_count.append(copycat_alive)
        random_count.append(random_alive)
    
    # Plot the number of each player type over time
    plt.plot(always_betray_count, label="Always Betray", color='red')
    plt.plot(always_cooperate_count, label="Always Cooperate", color='blue')
    plt.plot(copycat_count, label="Copycat", color='green')
    plt.plot(random_count, label="Random", color='purple')

    plt.title("Number of Surviving Players by Type Over Rounds")
    plt.xlabel("Round")
    plt.ylabel("Number of Surviving Players")
    plt.legend()
    plt.show()


def get_bot_numbers():
    bot_numbers = {}
    
    print("\nEnter the number of bots for each category:")
    always_betray = int(input("AlwaysBetray: "))
    always_cooperate = int(input("AlwaysCooperate: "))
    copycat = int(input("Copycat: "))
    random_player = int(input("Random: "))
    
    bot_numbers['AlwaysBetray'] = always_betray
    bot_numbers['AlwaysCooperate'] = always_cooperate
    bot_numbers['Copycat'] = copycat
    bot_numbers['Random'] = random_player
    
    return bot_numbers

# Get user input for bot numbers
bot_numbers = get_bot_numbers()

# Initialize the population based on user input
population = []
for _ in range(bot_numbers['AlwaysBetray']):
    population.append(AlwaysBetray())
for _ in range(bot_numbers['AlwaysCooperate']):
    population.append(AlwaysCooperate())
for _ in range(bot_numbers['Copycat']):
    population.append(Copycat())
for _ in range(bot_numbers['Random']):
    population.append(RandomPlayer())


# Generate a population of players
# def generate_population(n):
#     population = []

#     # for _ in range(n // 4):
#     #     population.append(AlwaysBetray())
#     #     population.append(AlwaysCooperate())
#     #     population.append(Copycat())
#     #     population.append(RandomPlayer())
#     return population

# # Number of players and rounds
# population_size = 200  # Adjust population size as needed
rounds = 500  # Adjust the number of rounds

# # Create the population and simulate the game
# population = generate_population(population_size)
simulate_game_population(population, rounds)

# population = []
# for i in range(4):
#     x = int(input(
#         "Enter the number of bots per category:AlwaysBetray,AlwaysCooperate,Copycat,Random:"))
#     population.append(x)