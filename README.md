# wig-solver

wig-solver is an API designed to work with its [companion chrome extension](https://github.com/diracdeltafunk/wig-solver-chrome), which finds optimal solutions to [Whenisgood](https://whenisgood.net) scheduling problems.

Actually, at its core wig-solver is nothing more than a set-cover solver, written using the scipy [milp](https://scipy.github.io/devdocs/reference/generated/scipy.optimize.milp.html) functionality.
