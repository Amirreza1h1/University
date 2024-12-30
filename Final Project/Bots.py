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

# Plays randomly (Trusting or Defiant)
# class RandomPlayer(Bot_Player):
#     def __init__(self):
#         super().__init__("Random")
#         self.moves = ('Trusting', 'Defiant')

#     def play(self, history):
#         return random.choice(self.moves)


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
        defiant_count = sum(1 for move1, move2 in history if move1 == "Defiant" or move2 == "Defiant")
        trusting_count = len(history) * 2 - defiant_count
        return "Trusting" if defiant_count > trusting_count else "Defiant"


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
