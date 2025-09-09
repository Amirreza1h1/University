import random

# Base class for a player
class Bot_Player:
    def __init__(self, type):
        self.type = type
        self.score = 100
        self.alive = True

    def update_score(self, outcome):
        self.score += outcome
        if outcome == -100 or self.score <= 0:
            self.alive = False

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

class FullAdaptivePlayer(Bot_Player):
    def __init__(self):
        super().__init__("FullAdaptive")

    def play(self, history):
        if not history:
            return "Trusting"

        # Flatten if history is nested (full_history case)
        if isinstance(history[0], list):
            moves = [m for round_data in history for m in round_data]
        else:
            moves = history  # already a flat list (like last_round)

        defiant_count = sum(1 for move1, move2 in moves if move1 == "Defiant" or move2 == "Defiant")
        trusting_count = len(moves) * 2 - defiant_count

        return "Trusting" if defiant_count > trusting_count else "Defiant"