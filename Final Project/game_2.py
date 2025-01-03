import random
import matplotlib.pyplot as plt
import Bots as bot
import mm as main


class Game():
    def __init__(self):
        pass

    def get_bot_numbers(self):
        bot_numbers = {}

        print("\nEnter the number of bots for each category:")
        always_betray = int(input("AlwaysBetray: "))
        always_cooperate = int(input("AlwaysCooperate: "))
        random_80_player = int(input("Random-80 percent defiant: "))
        random_50_player = int(input("Random-50 percent defiant: "))
        random_20_player = int(input("Random-20 percent defiant: "))
        adaptive_bot = int(input("AdaptiveBot: "))
        learning_bot = int(input("LearningBot: "))
        fuzzy_bot = int(input("FuzzyBot: "))

        bot_numbers['AlwaysBetray'] = always_betray
        bot_numbers['AlwaysCooperate'] = always_cooperate
        bot_numbers['Random_80'] = random_80_player
        bot_numbers['Random_50'] = random_50_player
        bot_numbers['Random_20'] = random_20_player
        bot_numbers['AdaptiveBot'] = adaptive_bot
        bot_numbers['LearningBot'] = learning_bot
        bot_numbers['FuzzyBot'] = fuzzy_bot

        return bot_numbers

        # Function to play a round between two players
    def play_round(self, player1, player2, history):
        if not player1.alive or not player2.alive:
            return history

        move1 = player1.play(history)
        move2 = player2.play(history)
        history.append((move1, move2))
        outcome1, outcome2 = main.rule[(move1, move2)]

        player1.update_score(outcome1)
        player2.update_score(outcome2)

        return history

        # Function to handle reproduction
    def reproduce_population(self, population):
        population.sort(key=lambda player: player.score, reverse=True)

        percentage_count = len(population) // 10
        number_of_dead = sum(
            1 for player in population if player.alive == False)

        # Remove lowest 10% of players if deads are not much
        if number_of_dead < percentage_count:
            population = [
                player for player in population if player.alive][:-percentage_count]

        # Add offspring from top 10% of players
        top_players = population[:percentage_count]
        offspring_pop = []
        for player in top_players:
            child = player.reproduce()
            offspring_pop.append(child)
            population.append(child)

        return population, offspring_pop

    # Main simulation function
    def simulate_game_population(self, population, rounds=100):
        history = []

        # Lists to track the number of each player type over rounds
        always_betray_count = [0]
        always_cooperate_count = [0]
        random_count = [0]
        learning_count = [0]
        total_bot_count = [len(population)]
        crash_count = []

        # Track initial player counts
        always_betray_count[0] = sum(1 for player in population if isinstance(
            player, bot.AlwaysBetray) and player.alive)
        always_cooperate_count[0] = sum(1 for player in population if isinstance(
            player, bot.AlwaysCooperate) and player.alive)
        random_count[0] = sum(1 for player in population if isinstance(
            player, bot.ProbabilisticPlayer) and player.defiant_prob == 0.8 and player.alive)
        random_count[0] = sum(1 for player in population if isinstance(
            player, bot.ProbabilisticPlayer) and player.defiant_prob == 0.5 and player.alive)
        random_count[0] = sum(1 for player in population if isinstance(
            player, bot.ProbabilisticPlayer) and player.defiant_prob == 0.2 and player.alive)
        random_count[0] = sum(1 for player in population if isinstance(
            player, bot.AdaptivePlayer) and player.alive)
        learning_count[0] = sum(1 for player in population if isinstance(
            player, bot.LearningBot) and player.alive)

        # Tracking metrics
        type_counts = {player.type: [] for player in population}
        move_counts = {"Defiant": [], "Trusting": []}
        offspring_counts = {player.type: 0 for player in population}

        for _ in range(rounds):
            random.shuffle(population)

            for i in range(0, len(population) - 1, 2):
                self.play_round(population[i], population[i + 1], history)

            population, offspring_pop = self.reproduce_population(population)

            # Track bot counts by type
            current_counts = {ptype: 0 for ptype in type_counts}
            for player in population:
                current_counts[player.type] += 1
            for ptype in type_counts:
                type_counts[ptype].append(current_counts[ptype])

            # Track moves
            round_moves = [
                move for pair in history[-len(population) // 2:] for move in pair]
            move_counts["Defiant"].append(round_moves.count("Defiant"))
            move_counts["Trusting"].append(round_moves.count("Trusting"))

            # Track offspring generation
            for player in offspring_pop:
                offspring_counts[player.type] += 1

        # Plot results
        fig, axes = plt.subplots(3, 1, figsize=(10, 14))

        # Plot type counts
        for ptype, counts in type_counts.items():
            axes[0].plot(counts, label=ptype)
        axes[0].set_title("Player Counts by Type")
        axes[0].set_xlabel("Round")
        axes[0].set_ylabel("Count")
        axes[0].legend()

        # Plot move counts
        axes[1].plot(move_counts["Defiant"], label="Defiant", color="red")
        axes[1].plot(move_counts["Trusting"], label="Trusting", color="blue")
        axes[1].set_title("Move Counts Over Time")
        axes[1].set_xlabel("Round")
        axes[1].set_ylabel("Count")
        axes[1].legend()

        # Plot offspring counts
        axes[2].bar(offspring_counts.keys(), offspring_counts.values())
        axes[2].set_title("Offspring Generated by Type")
        axes[2].set_xlabel("Player Type")
        axes[2].set_ylabel("Offspring Count")

        plt.tight_layout()
        plt.show()
