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
        offspring = self.__class__()
        offspring.score = 100  # Reset score to initial value
        return offspring
    
    @staticmethod
    def get_bot_numbers():
        bot_numbers = {}

        print("\nEnter the number of bots for each category:")
        always_betray = int(input("AlwaysBetray: "))
        always_cooperate = int(input("AlwaysCooperate: "))
        random_player = int(input("Random: "))
        learning_bot = int(input("LearningBot: "))

        bot_numbers['AlwaysBetray'] = always_betray
        bot_numbers['AlwaysCooperate'] = always_cooperate
        bot_numbers['Random'] = random_player
        bot_numbers['LearningBot'] = learning_bot

        return bot_numbers

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
