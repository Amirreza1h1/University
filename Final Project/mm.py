import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import Bots as bot

# Rule of outcomes for the chicken game
rule = {
    ('Trusting', 'Trusting'): (-2, -2),
    ('Trusting', 'Defiant'): (-2, 3),
    ('Defiant', 'Trusting'): (3, -250),
    ('Defiant', 'Defiant'): (-100, -100)  # dead!
}

if __name__ == "__main__":
    bot_numbers = bot.Bot_Player.get_bot_numbers()
    population = [bot.AlwaysBetray() for _ in range(bot_numbers['AlwaysBetray'])] + \
        [bot.AlwaysCooperate() for _ in range(bot_numbers['AlwaysCooperate'])] + \
        [bot.RandomPlayer() for _ in range(bot_numbers['Random'])] + \
        [bot.LearningBot() for _ in range(bot_numbers['LearningBot'])]
    print("")
    rounds=int(input("\nEnter number of rounds:"))