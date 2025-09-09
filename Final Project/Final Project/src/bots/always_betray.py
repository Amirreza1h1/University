from .base import BaseBotPlayer


class AlwaysBetray(BaseBotPlayer):
    """
    AlwaysBetray is a bot player that always chooses to betray in the game.\n
    **Attributes:**
        None
    **Methods:**
        __init__() -> None:
            Initializes the AlwaysBetray bot with the type `"AlwaysBetray"`.
        play(history) -> str:
            Always returns `"Defiant"`, indicating the bot's choice to betray regardless of the game history.
    """

    def __init__(self) -> None:
        """
        Initializes the AlwaysBetray bot with the type `"AlwaysBetray"`.
        """
        super().__init__(type="AlwaysBetray")

    def play(self, history) -> str:
        """
        Always returns `"Defiant"`, indicating the bot's choice to betray regardless of the game history.
        """
        return "Defiant"
