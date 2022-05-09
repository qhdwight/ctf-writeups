# SymCalc.py

### Approach

1) Use `breakpoint` as your favorite word (and thus builtin)
2) Abuse the fact that `_` is punctuation and in Python is a reference to the result of the last command
3) Run `_()` to call this builtin and enter the Python debugger
4) In the Python debugger `!` can be used to run in a sub-interpreter, so run `!import os; os.system('/bin/sh')` and get the flag

### Note

This is not the intended solution, but works just the same! And in my opinion is a little simpler.
