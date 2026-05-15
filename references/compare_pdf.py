import json, re
pdf = json.load(open(r'D:\metasys-viewer\references\pdf_classes_raw.json'))
html = open(r'D:\metasys-viewer\index.html', encoding='utf-8').read()
m = re.search(r'const CLASS_NAMES = \{([\s\S]*?)\};', html)
ours = dict(re.findall(r'(\d+):\s*"((?:[^"\\]|\\.)*)"', m.group(1)))

both = set(pdf) & set(ours)
only_pdf = set(pdf) - set(ours)
only_ours = set(ours) - set(pdf)
diffs = [k for k in both if pdf[k] != ours[k]]
print(f'In both: {len(both)}   PDF only: {len(only_pdf)}   Ours only: {len(only_ours)}   Differing names: {len(diffs)}')
print()
print('=== DIFFERENCES (PDF vs ours) ===')
for k in sorted(diffs, key=int):
    print(f'  cid={k:<5}  PDF: {pdf[k]!r:55}  Ours: {ours[k]!r}')
print()
print('=== PDF-only (new entries) ===')
for k in sorted(only_pdf, key=int):
    print(f'  cid={k:<5}  {pdf[k]!r}')
print()
print('=== Ours-only (kept) ===')
for k in sorted(only_ours, key=int):
    print(f'  cid={k:<5}  {ours[k]!r}')
