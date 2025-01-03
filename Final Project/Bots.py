import random

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
        if isinstance(self, ProbabilisticPlayer):
            offspring = self.__class__(self.defiant_prob)
        else:
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

# Plays randomly with a given probability of choosing Defiant
class ProbabilisticPlayer(Bot_Player):
    def __init__(self, defiant_prob):
        super().__init__(f"Prob{int(defiant_prob * 100)}Defiant")
        self.defiant_prob = defiant_prob

    def play(self, history):
        return "Defiant" if random.random() < self.defiant_prob else "Trusting"

# Analyzes previous round's moves and adapts
class AdaptivePlayer(Bot_Player):
    def __init__(self):
        super().__init__("Adaptive")

    def play(self, history):
        if not history:
            return "Trusting"
        defiant_count = sum(
            1 for move1, move2 in history if move1 == "Defiant" or move2 == "Defiant")
        trusting_count = len(history) * 2 - defiant_count
        return "Trusting" if defiant_count > trusting_count else "Defiant"

# # Fuzzy Logic Bot
# class FuzzyLogicBot(Bot_Player):
#     def __init__(self):
#         super().__init__("FuzzyLogicBot")

#     def play(self, history):
#         if not history:
#             return "Trusting"
#         defiant_ratio = sum(
#             1 for move1, move2 in history if move1 == "Defiant") / len(history)
#         if defiant_ratio > 0.7:
#             return "Defiant"  # Opponent mostly defiant
#         elif defiant_ratio < 0.3:
#             return "Trusting"  # Opponent mostly trusting
#         return "Defiant" if self.score > 50 else "Trusting"
