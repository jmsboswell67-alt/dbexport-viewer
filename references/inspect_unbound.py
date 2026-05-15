"""Inspect the UnboundReferences CSV."""
import csv, collections

path = r'C:\Users\jmsbo\Desktop\jci\UnboundReferences.csv'

rows = []
with open(path, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Total rows: {len(rows)}")
print(f"Columns: {list(rows[0].keys())}")
print()

# Distribution of reference types
types = collections.Counter(r['Reference Type'] for r in rows)
print("Reference Types:")
for t, n in types.most_common():
    print(f"  {n:>5}  {t}")
print()

# Distinct referring items
referring = collections.Counter(r['Referring Item'] for r in rows)
print(f"Distinct referring items: {len(referring)}")
print("Top referring items (most broken refs each):")
for ref, n in referring.most_common(15):
    print(f"  {n:>4}  {ref}")
print()

# Distinct referenced items (the "dead" things)
referenced = collections.Counter(r['Referenced Item'] for r in rows)
print(f"Distinct referenced (dead) items: {len(referenced)}")
print("Top referenced items (most references TO each dead item):")
for ref, n in referenced.most_common(15):
    print(f"  {n:>4}  {ref}")
print()

# Group by referring engine (the engine that contains the broken refs)
def engine_of(ref):
    if ':' not in ref: return '?'
    return ref.split(':', 1)[1].split('/', 1)[0]

ref_engines = collections.Counter(engine_of(r['Referring Item']) for r in rows)
print("Referring engines:")
for e, n in ref_engines.most_common():
    print(f"  {n:>5}  {e}")
print()

# Identify "totally dead programs": programs where ALL their refs are unbound
prog_pattern = collections.Counter()
for r in rows:
    ref = r['Referring Item']
    if '/Programming.' in ref:
        # Just take up to first dot after Programming
        prog = ref.split('/Programming.', 1)[1].split('.')[0]
        prog_pattern[prog] += 1
print(f"Distinct broken Programming blocks: {len(prog_pattern)}")
print("Top broken Programs:")
for p, n in prog_pattern.most_common(15):
    print(f"  {n:>4}  Programming.{p}")
