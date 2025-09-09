import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import Counter

from .constants import RULES


class Game:

    def play_round(self, player1, player2, round_history, last_round, full_history):
        if not player1.alive or not player2.alive:
            return 0

        # Give correct history input depending on bot type
        def get_history(player):
            if player.type == "FullAdaptive":
                return full_history
            elif player.type == "RoundAdaptive":
                return last_round
            else:
                return

        move1 = player1.play(get_history(player1))
        move2 = player2.play(get_history(player2))
        round_history.append((move1, move2))

        outcome1, outcome2 = RULES[(move1, move2)]

        player1.update_score(outcome1)
        player2.update_score(outcome2)

        crash = 1 if (move1 == 'Defiant' and move2 == 'Defiant') else 0
        return crash

    # if there is not a crash
    def reproduce_population_first(self, population):
        population = [player for player in population if player.alive]
        population.sort(key=lambda player: player.score, reverse=True)

        offspring = population[0].reproduce()
        population.pop(-1)
        population.append(offspring)

        return population, offspring

    def reproduce_population_crash_top_percent(self, population, death_number):
        population = [player for player in population if player.alive]
        population.sort(key=lambda player: player.score, reverse=True)

        percentage_count = max(1, len(population) // 10)  # Ensure at least one
        top_players = population[:percentage_count]

        offspring_pop = []
        for i in range(death_number):
            # Cycle through top players
            parent = top_players[i % len(top_players)]
            child = parent.reproduce()
            offspring_pop.append(child)
            population.append(child)

        return population, offspring_pop

    def simulate_game_population(self, population, rounds=100):
        end_condition = 0
        round_histories = []
        full_history = []

        type_counts = {player.type: [] for player in population}
        crash_count = []
        offspring_counts = {ptype: 0 for ptype in type_counts}
        extinct_types = set()
        game_over = False

        fig, axes = plt.subplots(4, 1, figsize=(12, 20))

        def update(frame):
            nonlocal population, game_over, full_history, end_condition, rounds

            if game_over:
                return

            # Always plot the population before the round for axes[0]
            for ax in axes:
                ax.clear()
            for ptype, counts in type_counts.items():
                axes[0].plot(counts, label=ptype)
            axes[0].set_title("Player Counts by Type (Before Round)")
            axes[0].set_xlabel("Round")
            axes[0].set_ylabel("Count")
            axes[0].legend()

            # Add margin between plots for readability
            plt.subplots_adjust(hspace=0.4)

            round_history = []
            last_round = round_histories[-1] if round_histories else []

            random.shuffle(population)
            round_crashes = 0
            end_condition += 1
            i = 0
            while i < len(population) - 1:
                player1 = population[i]
                player2 = population[i + 1]
                crash = self.play_round(
                    player1, player2, round_history, last_round, full_history)
                round_crashes += crash
                i += 2

            round_histories.append(round_history)
            full_history.extend(round_histories)
            crash_count.append(round_crashes)

            deaths_this_round = sum(
                not p.alive or p.score <= 0 for p in population)

            # Remove dead bots
            population = [p for p in population if p.alive and p.score > 0]

            # Count players per type
            current_counts = {ptype: 0 for ptype in type_counts}
            for player in population:
                current_counts[player.type] += 1
            for ptype in type_counts:
                type_counts[ptype].append(current_counts[ptype])

            # Extinction check
            for ptype, count in current_counts.items():
                if count == 0 and ptype not in extinct_types:
                    print(
                        f"\n⚠️ Bot type '{ptype}' has gone extinct at round {frame+1}!")
                    extinct_types.add(ptype)

            # game over condition
            if end_condition == rounds:
                print(f"\n 👀 rounds ends!!")
                game_over = True

            if len(population) == 0:
                print(f"\n💀 All bots are dead at round {frame+1}! Game over.")
                game_over = True

            active_types = [ptype for ptype,
                            count in current_counts.items() if count > 0]
            if len(active_types) == 1:
                print(
                    f"\n🏁 Game ends at round {frame+1}: Only '{active_types[0]}' bots remain!")
                game_over = True

            if game_over:
                ani.event_source.stop()
                plot_final_overview(type_counts, crash_count,
                                    offspring_counts, population)
                return

            if deaths_this_round == 0:
                population, player = self.reproduce_population_first(
                    population)
                offspring_counts[player.type] += 1

            # Call reproduction if anyone died
            if deaths_this_round > 0 and population:
                population, offspring_pop = self.reproduce_population_crash_top_percent(
                    population, deaths_this_round)
                for player in offspring_pop:
                    offspring_counts[player.type] += 1

            # axes[1]: Crashes per round
            axes[1].plot(crash_count, label="Crashes per Round",
                         color='orange')
            axes[1].set_title("Crashes per Round")
            axes[1].set_xlabel("Round")
            axes[1].set_ylabel("Count")
            axes[1].legend()

            # axes[2]: Pie chart for offspring counts
            offspring_labels = list(offspring_counts.keys())
            offspring_sizes = list(offspring_counts.values())
            if sum(offspring_sizes) > 0:
                axes[2].pie(offspring_sizes, labels=offspring_labels,
                            autopct='%1.1f%%', startangle=90)
                axes[2].set_title("Offspring Distribution by Type (Pie Chart)")
            else:
                axes[2].text(0.5, 0.5, 'No Offspring Yet',
                             ha='center', va='center')
                axes[2].set_title("Offspring Distribution by Type (Pie Chart)")

            # Subplot 4: Sorted list of all bots by score (Top N shown if too many)
            type_counter = Counter()
            scores = []
            for p in population:
                type_counter[p.type] += 1
                name = f"{p.type}_{type_counter[p.type]}"
                scores.append((name, p.score))
            scores.sort(key=lambda x: x[1], reverse=True)

            top_scores = scores[:10]
            names, values = zip(*top_scores) if top_scores else ([], [])

            axes[3].barh(names, values)
            axes[3].invert_yaxis()  # Highest score on top
            axes[3].set_title("Top Bots by Score (Sorted)")
            axes[3].set_xlabel("Score")
            axes[3].set_ylabel("Bot ID")
            print(len(population))
            plt.tight_layout()

        def plot_final_overview(type_counts, crash_count, offspring_counts, population):
            plt.figure(figsize=(15, 20))

            # Plot 1
            plt.subplot(4, 1, 1)
            for ptype, counts in type_counts.items():
                plt.plot(counts, label=ptype)
            plt.title("Final Player Counts by Type")
            plt.xlabel("Round")
            plt.ylabel("Count")
            plt.legend()

            # Plot 2
            plt.subplot(4, 1, 2)
            plt.plot(crash_count, color='orange', label='Crashes per Round')
            plt.title("Final Crashes per Round")
            plt.xlabel("Round")
            plt.ylabel("Count")
            plt.legend()

            # Plot 3
            plt.subplot(4, 1, 3)
            plt.bar(offspring_counts.keys(),
                    offspring_counts.values(), color='skyblue')
            plt.title("Total Offspring Generated by Type")
            plt.xlabel("Player Type")
            plt.ylabel("Offspring Count")

            # Plot 4 — Top 10 Bots by Score
            plt.subplot(4, 1, 4)
            type_counter = Counter()
            scores = []
            for p in population:
                type_counter[p.type] += 1
                name = f"{p.type}_{type_counter[p.type]}"
                scores.append((name, p.score))

            scores.sort(key=lambda x: x[1], reverse=True)
            top_scores = scores[:10] if scores else []
            names, values = zip(*top_scores) if top_scores else ([], [])

            plt.barh(names, values)
            plt.gca().invert_yaxis()
            plt.tick_params(axis='y', labelsize=6)
            plt.title("Final Top Bots by Score")
            plt.xlabel("Score")
            plt.ylabel("Bot ID")

            plt.tight_layout()
            plt.show()

        initial_counts = {ptype: 0 for ptype in type_counts}
        for player in population:
            initial_counts[player.type] += 1
        for ptype in type_counts:
            type_counts[ptype].append(initial_counts[ptype])
        ani = animation.FuncAnimation(fig, update, frames=rounds, repeat=False)
        plt.show()
