    # def reproduce_population_crash_n_top(self, population, death_number):
    #     population = [player for player in population if player.alive]
    #     population.sort(key=lambda player: player.score, reverse=True)

    #     offspring_pop = []
    #     for player in population[:death_number]:
    #         offspring_pop.append(player.reproduce())
    #         population.append(offspring_pop[-1])

    #     return population, offspring_pop

# Analyzes previous round's moves and adapts
# class FullAdaptivePlayer(Bot_Player):
#     def __init__(self):
#         super().__init__("FullAdaptive")

#     def play(self, history):
#         if not history:
#             return "Trusting"

#         weight = 1.0
#         decay = 0.9  # recent rounds matter more (lower = faster adaptation)
#         defiant_score = 0
#         trusting_score = 0

#         # Go from most recent to oldest
#         for move1, move2 in reversed(history):
#             if move1 == "Defiant":
#                 defiant_score += weight
#             else:
#                 trusting_score += weight

#             if move2 == "Defiant":
#                 defiant_score += weight
#             else:
#                 trusting_score += weight

#             weight *= decay  # reduce influence of older moves

#         ##### hint: If recent weighted defiance is higher, play Defiant, else Trusting
#         return "Trusting" if defiant_score > trusting_score else "Defiant"