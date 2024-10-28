import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np  # For calculating median

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
    
class LearningBot(Bot_Player):
    def __init__(self):
        super().__init__("LearningBot")
        self.history = []  # Track outcomes of past rounds

    def play(self, history):
        if len(self.history) < 5:  # Use last 5 outcomes for learning
            return "Trusting"  # Default to Trusting initially

        # Calculate the success rate of past moves
        betray_success = sum(1 for outcome in self.history if outcome == 'Defiant')
        trust_success = sum(1 for outcome in self.history if outcome == 'Trusting')

        # Adapt strategy based on success rates
        if trust_success > betray_success:
            return "Defiant"  # More successful with trusting, now betray
        else:
            return "Trusting"  # More successful with betraying, now trust

    def update_score(self, outcome):
        super().update_score(outcome)
        self.history.append("Defiant" if outcome > 0 else "Trusting")  # Record outcome


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
    lowest_players = population[-10:]
    for player in lowest_players:
        population.remove(player)

    # Reproduce 5 highest-scoring players
    highest_players = population[:10]
    for player in highest_players:
        population.append(player.reproduce())

# Main simulation function with live plot updates
def simulate_game_population(population, rounds):
    history = []

    # Lists to track the number of each player type over rounds
    always_betray_count = [0]  # Initialize with starting count
    always_cooperate_count = [0]
    random_count = [0]
    learning_count=[0]
    total_bot_count = [len(population)]  # Initialize with total bots count

    # New lists for crashes, average and median scores
    crash_count = []
    avg_scores = []
    median_scores = []
    # winning_scores = []

    # Track initial player counts
    always_betray_count[0] = sum(1 for player in population if isinstance(player, AlwaysBetray) and player.alive)
    always_cooperate_count[0] = sum(1 for player in population if isinstance(player, AlwaysCooperate) and player.alive)
    random_count[0] = sum(1 for player in population if isinstance(player, RandomPlayer) and player.alive)
    learning_count[0] = sum(1 for player in population if isinstance(player, LearningBot) and player.alive)


    # Set up live plotting
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))

    def update(frame):
        nonlocal history  # Ensure we use the outer 'history' list

        ax1.clear()
        ax2.clear()
        ax3.clear()

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
        learning_alive = sum(1 for player in population if isinstance(player, LearningBot) and player.alive)

        # Append counts
        always_betray_count.append(always_betray_alive)
        always_cooperate_count.append(always_cooperate_alive)
        random_count.append(random_alive)
        learning_count.append(learning_alive)
        total_bot_count.append(len(population))

        # Calculate average and median scores
        alive_scores = [player.score for player in population if player.alive]
        avg_scores.append(np.mean(alive_scores))
        median_scores.append(np.median(alive_scores))

        # Track and label the top 10 highest-scoring players with their types
        top_10_players = sorted([player for player in population if player.alive], key=lambda p: p.score, reverse=True)[:10]
        top_10_labels = "\n".join([f"{player.type}: {player.score}" for player in top_10_players])

        # Update the first subplot with player type counts
        ax1.plot(always_betray_count, label="Always Betray", color='red')
        ax1.plot(always_cooperate_count, label="Always Cooperate", color='blue')
        ax1.plot(random_count, label="Random", color='purple')
        ax1.plot(learning_count, label="Learning", color='green')
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

        # Update the third subplot with average, median, and top player scores
        ax3.plot(avg_scores, label="Average Score", color='green')
        ax3.plot(median_scores, label="Median Score", color='purple')
        ax3.set_title("Score Metrics and Top Players Over Rounds")
        ax3.set_xlabel("Round")
        ax3.set_ylabel("Scores")
        ax3.legend()

        # Display the top 10 players' types and scores in the third plot as a text box
        ax3.text(1.02, 0.5, f"Top 10 Players:\n{top_10_labels}", transform=ax3.transAxes, fontsize=10,
                verticalalignment='center', bbox=dict(boxstyle="round", facecolor="white", alpha=0.7))

        plt.tight_layout()


    ani = animation.FuncAnimation(fig, update, frames=rounds, repeat=False)
    plt.show()

# Get user input for the number of LearningBots
def get_bot_numbers():
    bot_numbers = {}

    print("\nEnter the number of bots for each category:")
    always_betray = int(input("AlwaysBetray: "))
    always_cooperate = int(input("AlwaysCooperate: "))
    random_player = int(input("Random: "))
    learning_bot = int(input("LearningBot: "))  # New input for LearningBot

    bot_numbers['AlwaysBetray'] = always_betray
    bot_numbers['AlwaysCooperate'] = always_cooperate
    bot_numbers['Random'] = random_player
    bot_numbers['LearningBot'] = learning_bot  # Store LearningBot number

    return bot_numbers

# Get user input for bot numbers
bot_numbers = get_bot_numbers()

# Initialize the population based on user input
population = [AlwaysBetray() for _ in range(bot_numbers['AlwaysBetray'])] + \
             [AlwaysCooperate() for _ in range(bot_numbers['AlwaysCooperate'])] + \
             [RandomPlayer() for _ in range(bot_numbers['Random'])] + \
             [LearningBot() for _ in range(bot_numbers['LearningBot'])]

rounds = 500  # Adjust the number of rounds
simulate_game_population(population, rounds)
