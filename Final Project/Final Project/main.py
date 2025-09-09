from src.bot_config import BotConfig
from src.game import Game

import os


class CowardsSimulation:
    space_count = 5
    equal_count = 50
    rounds = 100

    def __init__(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
        self._print_with_equal("Welcome to the Cowards Simulation!")
        self._display_menu()

    def _print_with_equal(self, text: str) -> None:
        print("=" * self.equal_count)
        print(" " * self.space_count, text, " " * self.space_count)
        print("=" * self.equal_count)
        print("")

    def _display_menu(self):
        print("Please choose an option:")

        print("1. Manual Simulation")
        print("2. Test Case Simulation")
        print("3. Exit")

        choice = input("Enter your choice: ")
        match choice:
            case "1":
                population = self._manual_simulation()
            case "2":
                population = self._test_case_simulation()
            case "3":
                exit()

        self._start_simulation(population, self.rounds)

    def _manual_simulation(self) -> list:
        print("")
        self._print_with_equal("Manual Simulation")
        bot_config = BotConfig()
        population = bot_config.manual_configuration()
        return population

    def _test_case_simulation(self) -> list:
        print("")
        self._print_with_equal("Test Case Simulation")
        bot_config = BotConfig()
        population = bot_config.test_case_configuration()
        return population

    def _start_simulation(self, population: list, rounds: int) -> None:
        game_object = Game()
        game_object.simulate_game_population(population, rounds)


if __name__ == "__main__":
    CowardsSimulation()
