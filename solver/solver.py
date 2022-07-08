## MILP Set Cover Solver ##

from scipy.optimize import milp
from itertools import chain
import numpy as np

# Standard set-cover solve. Find a minimum collection of sets which cover the universe.


def solveStrict(sets):
    num_sets = len(sets.keys())
    # universe is the union of the sets
    universe = set(chain(*sets.values()))
    num_elems = len(universe)
    # Minimize the number of sets
    c = np.ones(num_sets)
    # Each set must be used either 0 or 1 time
    integrality = np.ones_like(c)
    l = np.zeros_like(c)
    u = np.ones_like(c)
    # Subject to the constraint that each element appears at least once
    A = np.array([[1 if e in s else 0 for s in sets.values()]
                 for e in universe])
    b_l = np.ones(num_elems)
    b_u = np.full_like(b_l, np.inf)
    solution = milp(c=c, integrality=integrality, bounds=[
                    l, u], constraints=[A, b_l, b_u]).x
    ids_to_use = [k for (i, k) in enumerate(sets.keys()) if solution[i] == 1]
    return ids_to_use

# Relaxed set-cover solve. Find a minimum collection of sets which cover the universe, except at most k elements.


def solveRelaxed(sets, k):
    num_sets = len(sets.keys())
    # universe is the union of the sets
    universe = set(chain(*sets.values()))
    num_elems = len(universe)
    # Minimize the number of sets
    # The first num_sets variables determine if each set should be used
    # The last num_elems variables determine if each element should be forgotten
    c = np.concatenate(np.ones(num_sets), np.zeros(num_elems))
    # All variables are binary integers
    integrality = np.ones_like(c)
    l = np.zeros_like(c)
    u = np.ones_like(c)
    # Subject to the constraint that each element appears at least once,
    # unless it is forgotten, and the number of forgotten elements is
    # at most k
    A = np.append(np.array([[1 if e in s else 0 for s in sets.values()] + ([0] * i) + [1] + ([0] * (num_elems-i-1))
                            for (i, e) in enumerate(universe)]), np.concatenate(np.zeros(num_sets), np.ones(num_elems)))
    b_l = np.append(np.ones(num_elems), 0)
    b_u = np.append(np.full_like(b_l, np.inf), k)
    solution = milp(c=c, integrality=integrality, bounds=[
                    l, u], constraints=[A, b_l, b_u]).x
    ids_to_use = [k for (i, k) in enumerate(sets.keys()) if solution[i] == 1]
    return ids_to_use
