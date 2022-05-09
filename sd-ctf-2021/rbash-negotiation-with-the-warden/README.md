# Rbash Negotiation with the warden

### Overview

1) Clear PATH with 6
2) Leave a note with 1 named `vuln` with the contents
```bash
#!/bin/sh
/flag
```
3) Chage permissions of `vuln` to 777 (so we can execute it)
4) Exit jail with 7
5) Run `vuln.txt` to execute script and win