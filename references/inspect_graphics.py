"""Decode a sample older-format .xml graphic and newer-format .xaml graphic
to find the binding patterns we'll need to extract."""
import zipfile, re, base64, gzip, os
from collections import Counter

ARC = r'C:\Users\jmsbo\Desktop\jci\DACC1092025POSTCHANGEMARCH2025.dbexport'

def find_and_decode_graphic(suffix):
    """Find one graphic file with the given suffix and decode its Base64Zip content."""
    with zipfile.ZipFile(ARC) as z:
        for info in z.infolist():
            if info.filename.lower().endswith(suffix.lower()) and 'graphics' in info.filename.lower():
                with z.open(info) as f:
                    raw = f.read().decode('utf-8', errors='replace')
                m = re.search(r'<Base64Zip[^>]*>([\s\S]*?)</Base64Zip>', raw)
                if not m:
                    continue
                try:
                    inner = gzip.decompress(base64.b64decode(m.group(1).strip())).decode('utf-8', errors='replace')
                    return info.filename, inner
                except Exception as e:
                    print(f"  decode fail on {info.filename}: {e}")
                    continue
    return None, None

# ----- Older XML graphic -----
name, inner = find_and_decode_graphic('.xml')
if inner:
    print(f"=== OLDER FORMAT: {name} ({len(inner):,} chars decoded) ===")
    print(inner[:1500])
    print()
    print("...")
    # Look for likely binding markers
    print("--- Pattern hunting ---")
    for pat_name, pat in [
        ('Item references (NAE-style)',  r'[A-Za-z0-9\-]+:\s?[A-Za-z0-9\-]+/[\w\.\- ]+'),
        ('FQR strings',                   r'fqr["\>][^<"]*'),
        ('attribute= refs',               r'attribute="[^"]*"'),
        ('attrNum hints',                 r'attrNum>\d+'),
        ('binding markers',               r'binding|BIND|reference', ),
    ]:
        hits = re.findall(pat, inner)
        print(f"  {pat_name:30}: {len(hits):4} hits — first 2: {hits[:2]}")
    print()

# ----- Newer XAML graphic -----
name, inner = find_and_decode_graphic('.xaml')
if inner:
    print(f"=== NEWER FORMAT: {name} ({len(inner):,} chars decoded) ===")
    print(inner[:1500])
    print()
    print("...")
    print("--- Pattern hunting ---")
    for pat_name, pat in [
        ('Item references',               r'[A-Za-z0-9\-]+:\s?[A-Za-z0-9\-]+/[\w\.\- ]+'),
        ('Binding extensions',            r'{Binding[^}]*}'),
        ('Metasys: references',           r'Metasys:[^"\']+'),
        ('ObjRef= attributes',            r'ObjRef="[^"]*"'),
        ('attribute= bindings',           r'attribute="[^"]*"'),
        ('PresentValue refs',             r'PresentValue|present_value'),
    ]:
        hits = re.findall(pat, inner)
        print(f"  {pat_name:30}: {len(hits):4} hits — first 2: {hits[:2]}")
