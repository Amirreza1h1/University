# Bot Society

A bot simulation for my bachelor's final project. The idea is to put different
strategies in the same population and see how they survive over several rounds.
Some bots always cooperate, some always betray, and others make random choices
or react to the history of previous moves.

Bots gain and lose points when they meet. Bots that lose all their points die,
while successful bots can reproduce. The plots show how the population changes
as the game runs.

The original version uses terminal input and Matplotlib. There is also a
[desktop version](software/README.md) with a PySide6 interface and saved game history.

## Running the original code

You need Python 3 and Matplotlib. Run these commands from the project folder:

```shell
python -m pip install matplotlib
python main.py
```

The program asks how many bots you want from each type, then asks for the number
of rounds. For a first run, try 20 of each type and 100 rounds:

```text
Enter the number of bots for each category:
AlwaysBetray: 20
AlwaysCooperate: 20
Random-80 percent defiant: 20
Random-50 percent defiant: 20
Random-20 percent defiant: 20
FullAdaptiveBot: 20

Enter number of rounds: 100
```

This starts a game with 120 bots. Use whole numbers, at least two bots in total,
and a positive round count. You can enter zero for any strategy you want to leave out.

The simulation method has a default of 100 rounds, but `main.py` still requires
you to type a number. Leaving the prompt blank will cause an error.

## Bot types

Each bot starts with 100 points. In a match it chooses either `Trusting`
(cooperate) or `Defiant` (betray).

| Bot | Behavior |
| --- | --- |
| `AlwaysBetray` | Always chooses Defiant. |
| `AlwaysCooperate` | Always chooses Trusting. |
| `ProbabilisticPlayer(0.8)` | Has an 80% chance of choosing Defiant. Appears as `Prob80Defiant` in the plots. |
| `ProbabilisticPlayer(0.5)` | Has a 50% chance of choosing Defiant. Appears as `Prob50Defiant` in the plots. |
| `ProbabilisticPlayer(0.2)` | Has a 20% chance of choosing Defiant. Appears as `Prob20Defiant` in the plots. |
| `FullAdaptiveBot` | Counts the moves in the supplied history and chooses the less common one. |

The adaptive bot chooses Trusting when it has seen more Defiant moves. Otherwise,
it chooses Defiant, including when the counts are equal or there is no history
yet. It uses the history of the population's matches. Each adaptive bot also
keeps a `history_log` of its decisions for debugging.

## Game rules

The score changes are defined in the `rule` dictionary in `game.py`:

| First bot | Second bot | First bot's score change | Second bot's score change |
| --- | --- | ---: | ---: |
| Trusting | Trusting | -2 | -2 |
| Trusting | Defiant | -2 | +5 |
| Defiant | Trusting | +5 | -2 |
| Defiant | Defiant | -100 | -100 |

Two Defiant moves cause a **crash**, killing both bots. In the original code,
receiving exactly `-100` kills a bot even if it has more than 100 points.
A score of zero or less also causes death.

Each round, the population is shuffled and split into pairs. Every paired bot
plays once. If there is an odd number of bots, the last one skips that round.
After the matches, dead bots are removed and reproduction takes place.

If nobody died, the strongest bot produces one offspring and the weakest bot is
removed. If bots died and there are survivors, the top 10% of survivors reproduce
until the dead bots have been replaced. This percentage is rounded down, with
at least one parent. Parents are taken in order and reused if necessary.

Offspring keep their parent's strategy and start with 100 points. Random bots
also keep their parent's probability. The population size stays the same after
reproduction unless every bot has died.

The game ends when it reaches the round limit, all bots die, or only one strategy
remains. Starting with just one strategy can therefore end the game after the
first round.

## Results

There are four live plots:

- **Player counts:** how many bots of each type remain after reproduction.
- **Crashes:** how many pairs chose mutual defiance in each round.
- **Offspring:** the total number of offspring produced by each type.
- **Top scores:** the ten highest-scoring bots still alive, or fewer if there
  are fewer survivors.

The offspring count includes bots that later die, so it can be much larger than
the current population. A strategy with the most bots also does not necessarily
have the highest-scoring individual.

At the end, the program opens the final plots and prints extinction information
in the terminal. The final plots use separate `plt.show()` calls; close the plot
windows if the program is waiting before showing the next figure or summary.
You can save figures using the save button in the Matplotlib window.

Here is an example exported from the desktop version. In this run, the whole
population eventually died:

![Final population, crashes, offspring, and scores from a run with no survivors](docs/images/final-results.png)

The desktop app puts all four plots in one view. It also fixes the history issue
mentioned below, so its results may differ from the original simulation.

## Files and settings

- [main.py](main.py) reads the inputs, creates the bots, and starts the game.
- [Bots.py](Bots.py) contains the strategies, score updates, and offspring creation.
- [game.py](game.py) handles the rules, rounds, reproduction, and plots.
- [software/](software/README.md) contains the desktop application.

To try different payoffs, edit `rule` near the top of `game.py`. Starting scores
are set in `Bot_Player.__init__()` and `Bot_Player.reproduce()` in `Bots.py`;
change both if you want new bots and offspring to start with the same score.
The three random probabilities are passed to `ProbabilisticPlayer` in `main.py`.

The reproduction percentage is calculated in
`Game.reproduce_population_crash_top_percent()`. The check for ending with one
strategy is inside the animation's update function in `game.py`.

Remember that death on a `-100` outcome is handled separately in
`Bot_Player.update_score()`. Editing the payoff table alone does not change that
condition or which moves count as a crash.

## Notes on the original version

Input handling is basic: blank or non-numeric input raises an error, and negative
counts or an empty population are not supported. The plots need a desktop
environment where Matplotlib can open windows.

There is also an issue in the original history handling. The round loop appends
the same `round_history` list after every match. When the adaptive bot reads it,
some moves are counted more than once. The desktop engine counts each match once.

The original version has no saved game history or seed prompt. Repeating the same
inputs can give different results because pairing and random decisions change
between runs.

For editable rules, a seed setting, pause/resume, and saved results, open
[software/software.exe](software/software.exe) on Windows. Instructions for
that version are in [software/README.md](software/README.md).
