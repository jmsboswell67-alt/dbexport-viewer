"""Look at the START of the decoded older graphic — not the middle (which was binary)."""
import zipfile, re, base64, gzip
ARC = r'C:\Users\jmsbo\Desktop\jci\DACC1092025POSTCHANGEMARCH2025.dbexport'
with zipfile.ZipFile(ARC) as z:
    for info in z.infolist():
        if 'Graphics.Cannon Hall.Cannon AHU-1.xml' in info.filename:
            with z.open(info) as f:
                raw = f.read().decode('utf-8', errors='replace')
            m = re.search(r'<Base64Zip[^>]*>([\s\S]*?)</Base64Zip>', raw)
            inner = gzip.decompress(base64.b64decode(m.group(1).strip())).decode('utf-8', errors='replace')

            print(f"=== {info.filename} (decoded {len(inner):,} chars) ===")
            print()
            print("--- First 1200 chars ---")
            print(inner[:1200])
            print()
            print("--- Last 800 chars ---")
            print(inner[-800:])
            print()

            # Find each unique full Metasys item ref
            refs = sorted(set(re.findall(r'[A-Z][A-Za-z0-9\-]+:[A-Za-z0-9\-]+/[\w\.\- ]+(?:\.[\w\-]+)*', inner)))
            print(f"\n--- Distinct Metasys-style item refs found: {len(refs)} ---")
            for r in refs[:25]:
                print(f"  {r}")
            break
