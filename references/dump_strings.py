"""Extract printable strings from a binary file (Java .class)."""
import sys, re

path = sys.argv[1]
with open(path, 'rb') as f:
    data = f.read()
# Match runs of 5+ printable chars
strings = re.findall(rb'[\x20-\x7e]{5,}', data)
for s in strings:
    print(s.decode('latin-1', errors='replace'))
