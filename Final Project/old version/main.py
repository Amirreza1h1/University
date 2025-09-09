import Bots as bot
import game as game

if __name__ == "__main__":
    my_game = game.Game()
    bot_numbers = my_game.get_bot_numbers()
    population = [bot.AlwaysBetray() for _ in range(bot_numbers['AlwaysBetray'])] + \
        [bot.AlwaysCooperate() for _ in range(bot_numbers['AlwaysCooperate'])] + \
        [bot.ProbabilisticPlayer(0.8) for _ in range(bot_numbers['Random_80'])] + \
        [bot.ProbabilisticPlayer(0.5) for _ in range(bot_numbers['Random_50'])] + \
        [bot.ProbabilisticPlayer(0.2) for _ in range(bot_numbers['Random_20'])] + \
        [bot.FullAdaptiveBot() for _ in range(bot_numbers['FullAdaptiveBot'])]
    
    print("")
    rounds = int(input("\nEnter number of rounds:"))

    # Run the simulation
    my_game.simulate_game_population(population, rounds)