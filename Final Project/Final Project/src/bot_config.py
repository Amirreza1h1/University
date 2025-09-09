from .bots import AlwaysBetray, AlwaysCooperate, ProbabilisticPlayer, FullAdaptivePlayer

from typing import List, Union, Dict
import json
import os


class BotConfig:
    """
    BotConfig provides methods to configure and generate populations of different bot types for simulation.\n
    **Methods:**
        - _generate_population(bots_count: Dict[str, int]): 
            Static method that creates a list of bot instances based on the specified counts for each bot type.

        - manual_configuration():
            Prompts the user to manually input the number of bots for each category and returns the generated population.

        - test_case_configuration():
            Loads predefined test case configurations from a JSON file, allows the user to select a scenario, and returns the corresponding population.
    """

    @staticmethod
    def _generate_population(bots_count: Dict[str, int]) -> List[Union[AlwaysBetray, AlwaysCooperate, ProbabilisticPlayer, FullAdaptivePlayer]]:
        population = []

        population += [
            AlwaysBetray() for _ in range(bots_count["AlwaysBetray"])
        ]
        population += [
            AlwaysCooperate() for _ in range(bots_count["AlwaysCooperate"])
        ]
        population += [
            ProbabilisticPlayer(defiant_prob=0.8) for _ in range(bots_count["Random-80"])
        ]
        population += [
            ProbabilisticPlayer(defiant_prob=0.5) for _ in range(bots_count["Random-50"])
        ]
        population += [
            ProbabilisticPlayer(defiant_prob=0.2) for _ in range(bots_count["Random-20"])
        ]
        population += [
            FullAdaptivePlayer() for _ in range(bots_count["FullAdaptiveBot"])
        ]

        return population

    def manual_configuration(self) -> List[Union[AlwaysBetray, AlwaysCooperate, ProbabilisticPlayer, FullAdaptivePlayer]]:
        bots_count = {}
        print("Enter the number of bots for each category:")

        bots_count["AlwaysBetray"] = int(input("AlwaysBetray: "))
        bots_count["AlwaysCooperate"] = int(input("AlwaysCooperate: "))
        bots_count["Random-80"] = int(input("Random-80 percent defiant: "))
        bots_count["Random-50"] = int(input("Random-50 percent defiant: "))
        bots_count["Random-20"] = int(input("Random-20 percent defiant: "))
        bots_count["FullAdaptiveBot"] = int(input("FullAdaptiveBot: "))

        population = self._generate_population(bots_count)
        return population

    def test_case_configuration(self) -> List[Union[AlwaysBetray, AlwaysCooperate, ProbabilisticPlayer, FullAdaptivePlayer]]:
        json_data, bots_count = {}, {}
        scenario_list = []

        with open(f"{os.getcwd()}/test/test_cases.json", "r") as f:
            json_data = json.load(f)

        print("Available Test Cases:\n")

        for _, value in json_data.items():
            scenario_list.append(value["scenario"].strip().upper())

            print("Scenario:", value["scenario"])
            print("Description:", value["description"])
            print("Purpose:", value["purpose"])
            print("-" * 40)
            print("Bot Counts: ")
            for bot, count in value["bots"].items():
                print(f"  {bot}: {count}")
            print("\n")

        choice = (
            input("Enter the test case scenario (e.g., S1, S2, ...): ")
            .strip()
            .upper()
        )

        match choice:
            case x if x in scenario_list:
                for _, value in json_data.items():
                    if value["scenario"] == choice:
                        bots_count = value["bots"]
                        break
            case _:
                print("🛑 Invalid scenario choice. Please try again.")
                exit()

        population = self._generate_population(bots_count)
        return population
