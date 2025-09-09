from random import random

from .base import BaseBotPlayer


class ProbabilisticPlayer(BaseBotPlayer):
    """
    A bot player that chooses its action probabilistically based on a given probability.\n
    **Attributes:**
        defiant_prob (float): The probability with which the player chooses the "Defiant" action.
    **Methods:**
        __init__(defiant_prob: float) -> None:
            Initializes the ProbabilisticPlayer with a given defiant probability.
        play(history: list) -> str:
            Returns "Defiant" with probability `defiant_prob`, otherwise returns "Trusting".
            The `history` parameter can be used to inform decisions, but is unused in this implementation.
    """

    def __init__(self, defiant_prob: float) -> None:
        """
        Initializes the ProbabilisticPlayer with a given defiant probability.
        """
        super().__init__(type=f"Prob{int(defiant_prob * 100)}Defiant")
        self.defiant_prob = defiant_prob

    def play(self, history: list) -> str:
        """
        Chooses "Defiant" with probability `defiant_prob`, otherwise "Trusting".
        """
        return "Defiant" if random() < self.defiant_prob else "Trusting"
