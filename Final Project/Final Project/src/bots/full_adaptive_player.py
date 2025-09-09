from .base import BaseBotPlayer


class FullAdaptivePlayer(BaseBotPlayer):
    """
    FullAdaptivePlayer is a bot player that adapts its strategy based on the history of moves.\n
    **Attributes:**
        Inherits from BaseBotPlayer.
    **Methods:**
        __init__() -> None:
            Initializes the FullAdaptivePlayer with type "FullAdaptive".
        play(history) -> str:
            Determines the next move ("Trusting" or "Defiant") based on the provided history.
            - If history is empty, returns "Trusting".
            - If history is nested (full_history), flattens it.
            - Counts the number of "Defiant" moves in the history.
            - Returns "Trusting" if the number of "Trusting" moves is greater than "Defiant" moves; otherwise, returns "Defiant".
    """

    def __init__(self) -> None:
        """
        Initializes the FullAdaptivePlayer with type `"FullAdaptive"`.
        """
        super().__init__(type="FullAdaptive")

    def play(self, history: list) -> str:
        """
        Determines the next move ("Trusting" or "Defiant") based on the provided history.
        """
        if not history:
            return "Trusting"

        # Flatten if history is nested (full_history case)
        if isinstance(history[0], list):
            moves = [move for round_data in history for move in round_data]
        else:
            moves = history  # already a flat list (like last_round)

        defiant_count = sum(
            1 for move1, move2 in moves if move1 == "Defiant" or move2 == "Defiant")
        trusting_count = (2 * len(moves)) - defiant_count

        return "Trusting" if defiant_count > trusting_count else "Defiant"
