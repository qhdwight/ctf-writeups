# Rbash Negotiation with the warden

## Overview

1) Clear PATH with 6
2) Leave a note with 1 named `vuln` with the contents
```bash
#!/bin/sh
/flag
```
3) Chage permissions of `vuln`
4) Exit jail with 7
5) Run `vuln.txt` to execute script and win

## Explanation

Clearing away all our path entries makes our path equal to "", the empty string.
According to Linux this means that only our current working directory is in the path.
This is handy since all of our notes are placed in our working directory.
Setting the permissions to 777 makes it executable, readable, and writable to everyone.
The shebang is important as it tells bash to execute it when we do `vuln.txt` in rbash.
