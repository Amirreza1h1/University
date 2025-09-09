from .base import BaseBotPlayer


class AlwaysCooperate(BaseBotPlayer):
    """
    AlwaysCooperate is a bot player that always chooses to cooperate in every round.\n
    **Attributes:**
        None
    **Methods:**
        __init__() -> None:
            Initializes the AlwaysCooperate bot with the type `"AlwaysCooperate"`.
        play(history) -> str:
            Returns the action `"Trusting"` regardless of the game history, representing unconditional cooperation.
    """

    def __init__(self) -> None:
        """
        Initializes the AlwaysCooperate bot with the type `"AlwaysCooperate"`.
        """
        super().__init__(type="AlwaysCooperate")

    def play(self, history) -> str:
        """
        Returns the action `"Trusting"` regardless of the game history, representing unconditional cooperation.
        """
        return "Trusting"
