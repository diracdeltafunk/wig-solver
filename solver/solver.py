## MILP Set Cover Solver ##

from scipy.optimize import milp
from itertools import chain
import numpy as np

# Utility function


def onehot(n, i, value_on=1, value_off=0):
    return ([value_off] * i) + [value_on] + ([value_off] * (n-i-1))

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
                    l, u], constraints=[A, b_l, b_u])
    if not solution.success:
        return None
    solution = solution.x
    ids_to_use = [k for (i, k) in enumerate(sets.keys()) if solution[i] == 1]
    return ids_to_use

# Relaxed set-cover solve. Find a minimum collection of sets which cover the universe, except at most k elements.


def solveRelaxed(sets, k):
    num_sets = len(sets.keys())
    # universe is the union of the sets
    universe = set(chain(*sets.values()))
    num_elems = len(universe)
    # We want to minimize the number of sets
    # The first num_sets variables determine if each set should be used
    # The last num_elems variables determine if each element should be forgotten
    # We also give a slight penalty to forgetting, so that we never forget more elements
    # than necessary. This penalty is small enough that it'll be worth it to forget
    # every element if it allows us to use one fewer set.
    c = np.concatenate([np.ones(num_sets), np.reciprocal(
        np.full(num_elems, num_elems+1))])
    # All variables are binary integers
    integrality = np.ones_like(c)
    l = np.zeros_like(c)
    u = np.ones_like(c)
    # Subject to the constraint that each element appears at least once,
    # unless it is forgotten, and the number of forgotten elements is
    # at most k
    A = np.array([[1 if e in s else 0 for s in sets.values()] + onehot(num_elems, i)
                  for (i, e) in enumerate(universe)] + [([0] * num_sets) + ([-1] * num_elems)])
    b_l = np.append(np.ones(num_elems), -k)
    b_u = np.full_like(b_l, np.inf)
    solution = milp(c=c, integrality=integrality, bounds=[
                    l, u], constraints=[A, b_l, b_u])
    if not solution.success:
        return None
    solution = solution.x
    ids_to_use = [k for (i, k) in enumerate(sets.keys()) if solution[i] == 1]
    return ids_to_use

# Transposed solver. Find at most k sets which cover the maximum number of elements.


def solveTranspose(sets, k):
    num_sets = len(sets.keys())
    # universe is the union of the sets
    universe = set(chain(*sets.values()))
    num_elems = len(universe)
    # We want to maximize the number of elements covered
    # The first num_sets variables determine if each set should be used
    # The last num_elems variables determine if each is covered
    # We also give a slight penalty to using a set, so that we never use more sets
    # than necessary. This penalty is small enough that it'll be worth it to use all the sets
    # if it allows one more element to be covered.
    c = np.concatenate([np.full(num_sets, 1/(num_sets+1)),
                       np.full(num_elems, -1)])
    # All variables are binary integers
    integrality = np.ones_like(c)
    l = np.zeros_like(c)
    u = np.ones_like(c)
    # Subject to the constraint that each element is covered iff it is in a set that is used,
    # and the number of used sets is at most k.
    preA = [[onehot(num_sets, i, -1) + onehot(num_elems, j) for (i, s) in enumerate(
        sets.values()) if e in s] + [[1 if e in s else 0 for s in sets.values()] + onehot(num_elems, j, -1)] for (j, e) in enumerate(universe)]
    A = np.array([x for xs in preA for x in xs] +
                 [([-1] * num_sets) + ([0] * num_elems)])
    preb_l = [[0 for s in sets.values() if e in s] + [0] for e in universe]
    b_l = np.array([x for xs in preb_l for x in xs] + [-k], dtype=float)
    b_u = np.full_like(b_l, np.inf)
    solution = milp(c=c, integrality=integrality, bounds=[
                    l, u], constraints=[A, b_l, b_u])
    if not solution.success:
        print(solution.message)
        return None
    solution = solution.x
    ids_to_use = [k for (i, k) in enumerate(sets.keys()) if solution[i] == 1]
    return ids_to_use
