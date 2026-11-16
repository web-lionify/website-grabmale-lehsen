import pathlib, re, sys
root = pathlib.Path(sys.argv[1])
def color(cls):
    c = cls.split()
    if "cta" in c: return "dark"
    if "section-alt" in c: return "white"
    if "page-head" in c: return "stone"
    return "bg"
bad = 0
for f in sorted(list(root.glob("*.html")) + list(root.glob("friedhofssatzungen/*.html"))):
    s = f.read_text(encoding="utf-8")
    m = re.search(r"<main[^>]*>(.*)</main>", s, re.S)
    if not m: continue
    body = m.group(1)
    # top-level sections only: track nesting depth
    seq = []; depth = 0
    for t in re.finditer(r"<(/?)section\b([^>]*)>", body):
        if t.group(1):
            depth -= 1; continue
        if depth == 0:
            cm = re.search(r'class="([^"]*)"', t.group(2))
            seq.append(cm.group(1) if cm else "")
        depth += 1
    cols = [color(c) for c in seq]
    for i in range(1, len(cols)):
        if cols[i] == cols[i-1]:
            bad += 1
            print(f"{f.relative_to(root)}: [{seq[i-1]}] -> [{seq[i]}] beide {cols[i]}")
print("Konflikte:", bad)
