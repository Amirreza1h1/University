import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import Counter

rule = {
    ('Trusting', 'Trusting'): (-2, -2),
    ('Trusting', 'Defiant'): (-2, 5),
    ('Defiant', 'Trusting'): (5, -2),
    ('Defiant', 'Defiant'): (-100, -100)  # dead!
}

class Game():
    def __init__(self):
        pass

    def get_bot_numbers(self):
        bot_numbers = {}

        print("\nEnter the number of bots for each category:")
        bot_numbers['AlwaysBetray'] = int(input("AlwaysBetray: "))
        bot_numbers['AlwaysCooperate'] = int(input("AlwaysCooperate: "))
        bot_numbers['Random_80'] = int(input("Random-80 percent defiant: "))
        bot_numbers['Random_50'] = int(input("Random-50 percent defiant: "))
        bot_numbers['Random_20'] = int(input("Random-20 percent defiant: "))
        bot_numbers['FullAdaptiveBot'] = int(input("FullAdaptiveBot: "))

        return bot_numbers

    def play_round(self, player1, player2, round_history, full_history):
        if not player1.alive or not player2.alive:
            return 0

        # Give correct history input depending on bot type
        def get_history(player):
            if player.type == "FullAdaptive":
                return full_history
            else:
                return

        move1 = player1.play(get_history(player1))
        move2 = player2.play(get_history(player2))
        round_history.append((move1, move2))

        outcome1, outcome2 = rule[(move1, move2)]

        player1.update_score(outcome1)
        player2.update_score(outcome2)

        crash = 1 if (move1 == 'Defiant' and move2 == 'Defiant') else 0
        return crash
    
    # if there is not a crash
    def reproduce_population_first(self, population): 
        population = [player for player in population if player.alive]
        population.sort(key=lambda player: player.score, reverse=True)

        offspring = population[0].reproduce()
        print(offspring.type+ "\n")
        print(population[-1].type+ "\n")

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
            parent = top_players[i % len(top_players)]  # Cycle through top players
            child = parent.reproduce()
            offspring_pop.append(child)
            population.append(child)
        
        for ofs in offspring_pop:
            print(ofs.type)

        return population, offspring_pop
    
    def simulate_game_population(self, population, rounds=100):
        end_condition=0
        full_history = []

        type_counts = {player.type: [] for player in population}
        crash_count = []
        offspring_counts = {ptype: 0 for ptype in type_counts}
        extinct_types = {}
        game_over = False

        # Create 4 separate figures (windows)
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        fig3, ax3 = plt.subplots(figsize=(8, 6))
        fig4, ax4 = plt.subplots(figsize=(8, 6))

        def update(frame):
            nonlocal population, game_over, full_history, end_condition, rounds

            if game_over:
                return

            round_history = []

            random.shuffle(population)
            round_crashes = 0
            end_condition+=1
            i = 0
            while i < len(population) - 1:
                player1 = population[i]
                player2 = population[i + 1]
                crash = self.play_round(player1, player2, round_history, full_history)
                round_crashes += crash
                i += 2

            full_history.append(round_history)
            crash_count.append(round_crashes)

            deaths_this_round = sum(not p.alive or p.score <= 0 for p in population)

            # Remove dead bots
            population = [p for p in population if p.alive and p.score > 0]

            # Reproduction logic
            if deaths_this_round == 0:
                population, player = self.reproduce_population_first(population)
                offspring_counts[player.type] += 1
            if deaths_this_round > 0 and population:
                population, offspring_pop = self.reproduce_population_crash_top_percent(population, deaths_this_round)
                for player in offspring_pop:
                    offspring_counts[player.type] += 1

            # Count players per type
            current_counts = {ptype: 0 for ptype in type_counts}
            for player in population:
                current_counts[player.type] += 1
            for ptype in type_counts:
                type_counts[ptype].append(current_counts[ptype])

            # Extinction check
            for ptype, count in current_counts.items():
                if count == 0 and ptype not in extinct_types:
                    print(f"\n⚠️ Bot type '{ptype}' has gone extinct at round {frame+1}!")
                    extinct_types[ptype] = frame + 1  #record round of extinction

            # --- Clear and plot on separate figures ---
            ax1.clear()
            for ptype, counts in type_counts.items():
                ax1.plot(counts, label=ptype)
            ax1.set_title("Player Counts by Type")
            ax1.legend()

            ax2.clear()
            ax2.plot(crash_count, label="Crashes per Round", color='orange')
            ax2.set_title("Crashes per Round")
            ax2.legend()

            ax3.clear()
            ax3.bar(offspring_counts.keys(), offspring_counts.values())
            ax3.set_title("Offspring Generated by Type")

            ax4.clear()
            type_counter = Counter()
            scores = []
            for p in population:
                type_counter[p.type] += 1
                name = f"{p.type}_{type_counter[p.type]}"
                scores.append((name, p.score))
            scores.sort(key=lambda x: x[1], reverse=True)
            top_scores = scores[:10] 
            names, values = zip(*top_scores) if top_scores else ([], [])
            ax4.barh(names, values)
            ax4.invert_yaxis()
            ax4.set_title("Top Bots by Score")

            fig1.canvas.draw()
            fig2.canvas.draw()
            fig3.canvas.draw()
            fig4.canvas.draw()

            # Game end checks
            if end_condition==rounds:
                print(f"\n 👀 rounds ends!!")
                game_over = True
            if len(population) == 0:
                print(f"\n💀 All bots are dead at round {frame+1}! Game over.")
                game_over = True
            active_types = [ptype for ptype, count in current_counts.items() if count > 0]
            if len(active_types) == 1:
                print(f"\n🏁 Game ends at round {frame+1}: Only '{active_types[0]}' bots remain!")
                game_over = True

            if game_over:
                ani.event_source.stop()
                plot_final_overview(type_counts, crash_count, offspring_counts, population)
                return

        def plot_final_overview(type_counts, crash_count, offspring_counts, population):
            # Create 4 separate final figures
            plt.figure(figsize=(8, 6))
            for ptype, counts in type_counts.items():
                plt.plot(counts, label=ptype)
            plt.title("Final Player Counts by Type")
            plt.legend()
            plt.show()

            plt.figure(figsize=(8, 6))
            plt.plot(crash_count, color='orange', label='Crashes per Round')
            plt.title("Final Crashes per Round")
            plt.legend()
            plt.show()

            plt.figure(figsize=(8, 6))
            plt.bar(offspring_counts.keys(), offspring_counts.values(), color='skyblue')
            plt.title("Total Offspring Generated by Type")
            plt.show()

            plt.figure(figsize=(8, 6))
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
            plt.title("Final Top Bots by Score")
            plt.show()

        initial_counts = {ptype: 0 for ptype in type_counts}
        for player in population:
            initial_counts[player.type] += 1
        for ptype in type_counts:
            type_counts[ptype].append(initial_counts[ptype])

        ani = animation.FuncAnimation(fig1, update, frames=rounds, repeat=False)
        plt.show()

        #Extinction summary
        print("\n📉 Extinction Summary:")
        if extinct_types:
            for ptype, round_num in extinct_types.items():
                print(f"  - {ptype} went extinct at round {round_num}")
        else:
            print("  No bot types went extinct!")