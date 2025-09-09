class BaseBotPlayer:
    """
    BaseBotPlayer is an abstract base class for bot players in a game simulation.\n
    **Attributes:**
        type (str): The type or name of the bot player.
        score (int): The current score of the bot player. Initialized to 100.
        alive (bool): Status indicating if the bot is still in the game.
    **Methods:**
        __init__(type: str) -> None:
            Initializes a new bot player with the given type, a score of 100, and alive status set to True.
        update_score(outcome: int) -> None:
            Updates the bot's score based on the outcome of a round. If the outcome is -100 or the score drops to 0 or below, sets alive to False.
        play(history: list) -> str:
            Abstract method to be implemented by subclasses. Defines the bot's move based on the game history.
        reproduce() -> "BaseBotPlayer":
            Creates and returns a new instance (offspring) of the bot player, resetting its score to the initial value.
            Handles special initialization for subclasses (e.g., ProbabilisticPlayer).
    """

    def __init__(self, type: str) -> None:
        """
        Initializes a new bot player with the given type, a score of 100, and alive status set to True.
        """
        self.type = type
        self.score = 100
        self.alive = True

    def update_score(self, outcome: int) -> None:
        """
        Updates the bot's score based on the outcome of a round. If the outcome is -100 or the score drops to 0 or below, sets alive to False.
        """
        self.score += outcome
        if outcome == -100 or self.score <= 0:
            self.alive = False

    def play(self, history: list) -> str:
        """
        Abstract method to be implemented by subclasses. Defines the bot's move based on the game history.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def reproduce(self) -> "BaseBotPlayer":
        """
        Creates and returns a new instance (offspring) of the bot player, resetting its score to the initial value.
        """
        # prevent circular imports
        from .probabilistic_player import ProbabilisticPlayer

        if isinstance(self, ProbabilisticPlayer):
            offspring = self.__class__(self.defiant_prob)
        else:
            offspring = self.__class__()
        offspring.score = 100  # Reset score to initial value
        return offspring
