import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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


def simulate_game_population(population, rounds):
    history = []
    
    # Lists to track the number of each player type over rounds
    always_betray_count = []
    always_cooperate_count = []
    copycat_count = []
    random_count = []
    total_bot_count = []  # Track the total number of bots
    
    # New lists for crashes and sum of scores
    crash_count = []
    winner_sum_per_round = []
    
    for round_num in range(rounds):
        print(f"\n--- Round {round_num + 1} ---")
        
        # Pair up players randomly for each round and display pairs
        random.shuffle(population)
        i = 0
        round_crashes = 0  # Count crashes for the current round
        
        print("Player pairs:")
        while i < len(population) - 1:
            player1 = population[i]
            player2 = population[i + 1]
            
            print(f"Pair: ({player1.type}, {player2.type})")  # Displaying each pair
            
            # Play a round and update history
            history = play_round(player1, player2, history)
            
            # If both players crash (both played "Defiant"), increment the crash counter
            if not player1.alive or not player2.alive:
                round_crashes += 1
                print(f"Crash detected: {player1.type} and {player2.type} both eliminated.")
            
            # Reproduce the winner or handle the crash case
            reproduce_winner(player1, player2, population)
            i += 2  # Move to the next pair
        
        # Sum the scores of all players still alive
        winner_sum = sum(player.score for player in population if player.alive)
        winner_sum_per_round.append(winner_sum)
        crash_count.append(round_crashes)

        # Count surviving players of each type
        always_betray_alive = sum(1 for player in population if isinstance(player, AlwaysBetray) and player.alive)
        always_cooperate_alive = sum(1 for player in population if isinstance(player, AlwaysCooperate) and player.alive)
        copycat_alive = sum(1 for player in population if isinstance(player, Copycat) and player.alive)
        random_alive = sum(1 for player in population if isinstance(player, RandomPlayer) and player.alive)
        
        # Append the counts to their respective lists
        always_betray_count.append(always_betray_alive)
        always_cooperate_count.append(always_cooperate_alive)
        copycat_count.append(copycat_alive)
        random_count.append(random_alive)
        total_bot_count.append(len(population))  # Record total number of bots

        # Display updated player counts and current crash count for this round
        print(f"End of Round {round_num + 1}:")
        print(f"  AlwaysBetray: {always_betray_alive}, AlwaysCooperate: {always_cooperate_alive}, Copycat: {copycat_alive}, Random: {random_alive}")
        print(f"  Total Bots: {len(population)}")
        print(f"  Crashes this round: {round_crashes}")
        print(f"  Sum of Winners' Scores: {winner_sum}")
    
    # Plot the number of each player type over time
    plt.figure(figsize=(10, 8))
    
    # First plot: Number of each type and total bots
    plt.subplot(2, 1, 1)
    plt.plot(always_betray_count, label="Always Betray", color='red')
    plt.plot(always_cooperate_count, label="Always Cooperate", color='blue')
    plt.plot(copycat_count, label="Copycat", color='green')
    plt.plot(random_count, label="Random", color='purple')
    plt.plot(total_bot_count, label="Total Bots", color='black', linestyle='--')
    plt.title("Number of Surviving Players by Type Over Rounds")
    plt.xlabel("Round")
    plt.ylabel("Number of Surviving Players")
    plt.legend()
    
    # Second plot: Crashes and winner sum per round
    plt.subplot(2, 1, 2)
    plt.plot(crash_count, label="Crashes per Round", color='orange')
    plt.plot(winner_sum_per_round, label="Sum of Winners' Scores", color='brown')
    plt.title("Crashes and Sum of Winner Scores per Round")
    plt.xlabel("Round")
    plt.ylabel("Count / Score Sum")
    plt.legend()
    
    plt.tight_layout()
    plt.show()



import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Rule of outcomes for the chicken game
rule = {
    ('Trusting', 'Trusting'): (0, 0),
    ('Trusting', 'Defiant'): (1, 3),
    ('Defiant', 'Trusting'): (3, 1),
    ('Defiant', 'Defiant'): (-100, -100)  # dead!
}

# Base class for a player
class Bot_Player:
    def __init__(self, type):
        self.type = type
        self.score = 100
        self.alive = True

    def update_score(self, outcome):
        if outcome == -100:
            self.alive = False
        self.score += outcome

    def play(self, history):
        raise NotImplementedError("Subclasses should implement this!")

    def reproduce(self):
        offspring = self.__class__()
        offspring.score = 100  # Reset score to initial value
        return offspring

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
        return history, 0  # No crash if one or both players are not alive

    move1 = player1.play(history)
    move2 = player2.play(history)
    history.append((move1, move2))
    outcome1, outcome2 = rule[(move1, move2)]

    # Update the players' scores
    player1.update_score(outcome1)
    player2.update_score(outcome2)

    # Count a crash if both players chose 'Defiant'
    crash = 1 if (move1 == 'Defiant' and move2 == 'Defiant') else 0
    return history, crash

# Function to handle reproduction based on top and bottom scores
def reproduce_population(population):
    # Sort population by score
    population.sort(key=lambda player: player.score, reverse=True)

    # Remove the 5 lowest-scoring players
    lowest_players = population[-5:]
    for player in lowest_players:
        population.remove(player)

    # Reproduce 5 highest-scoring players
    highest_players = population[:5]
    for player in highest_players:
        population.append(player.reproduce())

# Main simulation function with live plot updates
def simulate_game_population(population, rounds):
    history = []

    # Lists to track the number of each player type over rounds
    always_betray_count = [0]  # Initialize with starting count
    always_cooperate_count = [0]
    random_count = [0]
    total_bot_count = [len(population)]  # Initialize with total bots count

    # New lists for crashes
    crash_count = []

    # Track initial player counts
    always_betray_count[0] = sum(1 for player in population if isinstance(player, AlwaysBetray) and player.alive)
    always_cooperate_count[0] = sum(1 for player in population if isinstance(player, AlwaysCooperate) and player.alive)
    random_count[0] = sum(1 for player in population if isinstance(player, RandomPlayer) and player.alive)

    # Set up live plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    def update(frame):
        nonlocal history  # Ensure we use the outer 'history' list

        ax1.clear()
        ax2.clear()

        random.shuffle(population)
        i = 0
        round_crashes = 0  # Count crashes for the current round

        while i < len(population) - 1:
            player1 = population[i]
            player2 = population[i + 1]

            # Play a round, update history, and count crashes
            history, crash = play_round(player1, player2, history)
            round_crashes += crash

            i += 2

        # Perform reproduction based on the highest and lowest scores
        reproduce_population(population)

        # Track crashes
        crash_count.append(round_crashes)

        # Shuffle the population after each round
        random.shuffle(population)

        # Track player types
        always_betray_alive = sum(1 for player in population if isinstance(player, AlwaysBetray) and player.alive)
        always_cooperate_alive = sum(1 for player in population if isinstance(player, AlwaysCooperate) and player.alive)
        random_alive = sum(1 for player in population if isinstance(player, RandomPlayer) and player.alive)

        # Append counts
        always_betray_count.append(always_betray_alive)
        always_cooperate_count.append(always_cooperate_alive)
        random_count.append(random_alive)
        total_bot_count.append(len(population))

        # Update the first subplot with player type counts
        ax1.plot(always_betray_count, label="Always Betray", color='red')
        ax1.plot(always_cooperate_count, label="Always Cooperate", color='blue')
        ax1.plot(random_count, label="Random", color='purple')
        ax1.plot(total_bot_count, label="Total Bots", color='black', linestyle='--')
        ax1.set_title("Number of Surviving Players by Type Over Rounds")
        ax1.set_xlabel("Round")
        ax1.set_ylabel("Number of Surviving Players")
        ax1.legend()

        # Update the second subplot with crashes
        ax2.plot(crash_count, label="Crashes per Round", color='orange')
        ax2.set_title("Crashes per Round")
        ax2.set_xlabel("Round")
        ax2.set_ylabel("Count")
        ax2.legend()

        plt.tight_layout()

    ani = animation.FuncAnimation(fig, update, frames=rounds, repeat=False)
    plt.show()

def get_bot_numbers():
    bot_numbers = {}

    print("\nEnter the number of bots for each category:")
    always_betray = int(input("AlwaysBetray: "))
    always_cooperate = int(input("AlwaysCooperate: "))
    random_player = int(input("Random: "))

    bot_numbers['AlwaysBetray'] = always_betray
    bot_numbers['AlwaysCooperate'] = always_cooperate
    bot_numbers['Random'] = random_player

    return bot_numbers

# Get user input for bot numbers
bot_numbers = get_bot_numbers()

# Initialize the population based on user input
population = [AlwaysBetray() for _ in range(bot_numbers['AlwaysBetray'])] + \
             [AlwaysCooperate() for _ in range(bot_numbers['AlwaysCooperate'])] + \
             [RandomPlayer() for _ in range(bot_numbers['Random'])]

rounds = 500  # Adjust the number of rounds
simulate_game_population(population, rounds)