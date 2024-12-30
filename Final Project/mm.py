import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import Bots as bot
import game as game

# Rule of outcomes for the chicken game
rule = {
    ('Trusting', 'Trusting'): (-2, -2),
    ('Trusting', 'Defiant'): (-2, 3),
    ('Defiant', 'Trusting'): (3, -250),
    ('Defiant', 'Defiant'): (-100, -100)  # dead!
}

if __name__ == "__main__":
    my_game = game.Game()
    bot_numbers = my_game.get_bot_numbers()
    population = [bot.AlwaysBetray() for _ in range(bot_numbers['AlwaysBetray'])] + \
        [bot.AlwaysCooperate() for _ in range(bot_numbers['AlwaysCooperate'])] + \
        [bot.ProbabilisticPlayer(0.8) for _ in range(bot_numbers['Random_80'])] + \
        [bot.ProbabilisticPlayer(0.7) for _ in range(bot_numbers['Random_70'])] + \
        [bot.ProbabilisticPlayer(0.6) for _ in range(bot_numbers['Random_60'])] + \
        [bot.ProbabilisticPlayer(0.5) for _ in range(bot_numbers['Random_50'])] + \
        [bot.AdaptivePlayer() for _ in range(bot_numbers['AdaptiveBot'])] + \
        [bot.LearningBot() for _ in range(bot_numbers['LearningBot'])]
    print("")
    rounds=int(input("\nEnter number of rounds:"))
        
    # Run the simulation
    my_game.simulate_game_population(population, rounds=100)