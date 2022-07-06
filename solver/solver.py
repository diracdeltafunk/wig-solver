## MILP Set Cover Solver ##

from scipy.optimize import milp
from itertools import chain
import numpy as np


def solve(sets):
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
