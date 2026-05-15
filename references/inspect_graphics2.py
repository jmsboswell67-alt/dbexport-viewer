"""Find an actual GRAPHIC file (not a UserTrees navView) and inspect bindings."""
import zipfile, re, base64, gzip

ARC = r'C:\Users\jmsbo\Desktop\jci\DACC1092025POSTCHANGEMARCH2025.dbexport'

def decode_b64zip(text):
    m = re.search(r'<Base64Zip[^>]*>([\s\S]*?)</Base64Zip>', text)
    if not m: return None
    return gzip.decompress(base64.b64decode(m.group(1).strip())).decode('utf-8', errors='replace')

with zipfile.ZipFile(ARC) as z:
    # Older format: filename pattern "Graphics.<Building>.<Name>.xml"
    candidates = [info for info in z.infolist()
                  if info.filename.endswith('.xml')
                  and 'Graphics.' in info.filename
                  and 'UserTrees' not in info.filename]
    print(f"Found {len(candidates)} candidate older-format graphics")

    # Pick a substantive one (Cannon Hall AHU-1 mentioned earlier)
    for info in candidates:
        if 'Cannon AHU-1' in info.filename or 'AHU-1' in info.filename:
            with z.open(info) as f:
                raw = f.read().decode('utf-8', errors='replace')
            inner = decode_b64zip(raw)
            if not inner: continue
            print(f"\n=== {info.filename} ({len(inner):,} chars) ===")
            # Look for distinctive binding patterns
            for pat_name, pat in [
                ('Item refs (full)',       r'[A-Za-z][\w\-]*:\s?[A-Za-z][\w\-]*/[\w\.\- ]+'),
                ('attrNum',                r'<attrNum>\d+</attrNum>'),
                ('attribute attrs',        r'attribute="[^"]+"'),
                ('FQR-like',               r'[Ff]ully[Qq]ualified|fqr|FQR'),
                ('any "reference" attrs', r'\breference[A-Z]\w*=' ),
                ('TSEGraph attrs',         r'attrNumReal>\d+'),
            ]:
                hits = re.findall(pat, inner)
                print(f"  {pat_name:25}: {len(hits):4} — first 3: {[h[:80] for h in hits[:3]]}")
            # Show structural overview
            print(f"\n  Element types: {sorted(set(re.findall(r'<([A-Za-z][\\w]*)', inner)))[:30]}")
            print(f"  Bytes in first 2KB: ...{inner[2000:2500]}...")
            break

    # Newer XAML — look at the section after the canvas setup
    print("\n\n--- NEWER XAML deeper look ---")
    for info in z.infolist():
        if info.filename.endswith('.xaml') and 'Graphics.' in info.filename:
            with z.open(info) as f:
                raw = f.read().decode('utf-8', errors='replace')
            inner = decode_b64zip(raw)
            if not inner: continue
            print(f"\n=== {info.filename} ({len(inner):,} chars) ===")
            # Sample text from middle of file
            mid = len(inner) // 3
            print(f"  Middle excerpt: ...{inner[mid:mid+1500]}...")
            # All distinct namespace prefixes used
            ns_attrs = re.findall(r'xmlns:(\w+)="([^"]+)"', inner)
            print(f"\n  Namespaces: {dict(ns_attrs)}")
            # Patterns to find point bindings
            for pat_name, pat in [
                ('Full Item refs',         r'(?:Metasys|[A-Z][\w\-]+):[A-Z][\w\-]+/[\w\.\- /]+'),
                ('Path= bindings',         r'Path=\w[\w.]*'),
                ('ObjectName= attrs',      r'ObjectName="[^"]+"'),
                ('FQR= attrs',             r'FQR="[^"]+"'),
                ('ItemReference= attrs',   r'ItemReference="[^"]+"'),
                ('any Reference attrs',    r'Reference="[^"]+"'),
            ]:
                hits = re.findall(pat, inner)
                print(f"  {pat_name:25}: {len(hits):4} — first 3: {[h[:90] for h in hits[:3]]}")
            break
