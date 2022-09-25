#!/usr/bin/env python3

from z3 import *
from numpy import *


def find_many(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]


s = Solver()

M = [Bool(f"M_{i+1}") for i in range(14*14)]

s.add([Sum([If(m, 1, 0) for m in M[chunk*14:(chunk+1)*14]])
      == 3 for chunk in range(14)])

s.add([Sum([If(m, 1, 0) for m in M[chunk:chunk + 14*14:14]])
      == 3 for chunk in range(14)])

puzzle = 'aaaaabbbbcccddaaaaabbbbccccdaaeaaabbbccccdaaefaabbbcccgdeeefffffbccggdfeeffffggggggdfffffffhhhgggdffffhhhhhhgggdffijjjjhkkllmdiiijjkkkkkllmmiijjjkkkklllmmiijjjkkkklllmmijjjjjkknnllmmijjjjnnnnnllll'

for c in set(puzzle):
    s.add(Sum([If(M[index], 1, 0) for index in find_many(puzzle, c)]) == 3)

indices = [-1, -15, -14, -13, +1, +13, +14, +15]

# Check that no neighbors are 1's for each cell
for i in range(14*14):
    for index in indices:
        j = i + index
        # Handle edge case
        if 0 <= j < 14 * 14 and abs((j // 14) - (i // 14)) <= 1 and abs((j % 14) - (i % 14)) <= 1:
            s.add(Not(And(M[i], M[j])))

result = s.check()

if result == sat:
    M = [is_true(s.model()[m]) for m in M]
    print(''.join('1' if m else '0' for m in M))
    M = array(M, dtype=int)
    # Print as 14x4 matrix by unflattening array
    print(M.reshape(14, 14))
