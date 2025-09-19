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

class FullAdaptiveBot(Bot_Player):
    _id_counter = 0  # unique IDs for logging

    def __init__(self):
        super().__init__("FullAdaptiveBot")
        self.id = FullAdaptiveBot._id_counter
        FullAdaptiveBot._id_counter += 1
        self.history_log = []  # store decision history for debugging

    def play(self, history):
        if not history:
            decision = "Trusting"
            self.history_log.append((0, 0, decision, 0))
            return decision

        # --- Flatten global history (list of rounds → list of matches) ---
        if isinstance(history[0], list):  
            moves = [pair for round_data in history for pair in round_data]
        else:  
            moves = history  # already flat list of (m1, m2) pairs (round 1)

        # --- Count *individual moves* ---
        defiant_count = sum(1 for m1, m2 in moves if m1 == "Defiant") + \
                        sum(1 for m1, m2 in moves if m2 == "Defiant")
        trusting_count = sum(1 for m1, m2 in moves if m1 == "Trusting") + \
                         sum(1 for m1, m2 in moves if m2 == "Trusting")
        total_moves = len(moves) * 2

        # --- Decision rule ---
        decision = "Trusting" if trusting_count < defiant_count else "Defiant"

        # --- Log for debugging ---
        self.history_log.append((defiant_count, trusting_count, decision, total_moves))
        return decision

    # print every information a single one of the FullAdaptiveBot has to do a decision
    # def print_decisions(self):
    #     print(f"\n🧠 FullAdaptiveBot {self.id} Decisions Log")
    #     print("=" * 60)
    #     for r, (d, t, choice, history_len) in enumerate(self.history_log, 1):
    #         print(
    #             f"Round {r:02d} | Defiant seen: {d:3d} | Trusting seen: {t:3d} "
    #             f"| Decision: {choice:9s} | History (moves): {history_len} | score: {self.score}"
    #         )
    #     print("=" * 60)
