"""Look up the Fusion API in the stubs that ship with the INSTALLED build (version-matched truth).

  python fapi.py <regex>              classes and members whose NAME matches (case-insensitive)
  python fapi.py -c <Class>           one class: bases, doc, every member with its first doc line
  python fapi.py -m <Class.member>    full docstring and signature of one member
  python fapi.py -d <regex>           search inside docstrings (slower, more hits)
  python fapi.py --preview <module>   list preview (may change) classes in a module
  python fapi.py --build              print which build the stubs come from
Add -n 60 to raise the result cap (default 40). Modules: core fusion drawing cam electron sim volume.
"""
import ast
import glob
import os
import re
import sys
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.expandvars(r"%LOCALAPPDATA%\Autodesk\webdeploy\production")
MODS = ["core", "fusion", "drawing", "cam", "electron", "sim", "volume"]


def find_build():
    hits = glob.glob(os.path.join(ROOT, "*", "API", "Python", "packages", "adsk", "defs", "adsk", "fusion.py"))
    if not hits:
        sys.exit("no Fusion API stubs under " + ROOT)
    hits.sort(key=os.path.getmtime, reverse=True)
    return os.path.dirname(hits[0])


def sig_of(fn):
    a = fn.args
    parts = []
    pos = a.posonlyargs + a.args
    defaults = [None] * (len(pos) - len(a.defaults)) + list(a.defaults)
    for arg, d in zip(pos, defaults):
        if arg.arg == "self":
            continue
        s = arg.arg
        if arg.annotation is not None:
            s += ": " + ast.unparse(arg.annotation)
        if d is not None:
            s += " = " + ast.unparse(d)
        parts.append(s)
    ret = (" -> " + ast.unparse(fn.returns)) if fn.returns is not None else ""
    return "(" + ", ".join(parts) + ")" + ret


def load(d):
    idx = []  # (module, class, member, kind, sig, doc, bases)
    for m in MODS:
        p = os.path.join(d, m + ".py")
        if not os.path.exists(p):
            continue
        tree = ast.parse(open(p, encoding="utf-8").read())
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            bases = ", ".join(ast.unparse(b) for b in node.bases)
            idx.append((m, node.name, "", "class", "", ast.get_docstring(node) or "", bases))
            seen_prop = set()
            for b in node.body:
                if isinstance(b, ast.FunctionDef):
                    if b.name.startswith("_"):
                        continue
                    decos = [ast.unparse(x) for x in b.decorator_list]
                    if any(x.endswith(".setter") for x in decos):
                        idx.append((m, node.name, b.name, "setter", "", "", ""))
                        continue
                    kind = "property" if "property" in decos else ("static" if "staticmethod" in decos else "method")
                    if kind == "property":
                        seen_prop.add(b.name)
                    idx.append((m, node.name, b.name, kind, sig_of(b), ast.get_docstring(b) or "", ""))
                elif isinstance(b, ast.Assign):
                    for t in b.targets:
                        if isinstance(t, ast.Name) and not t.id.startswith("_"):
                            idx.append((m, node.name, t.id, "enum", "= " + ast.unparse(b.value), "", ""))
    return idx


PREVIEW_RE = re.compile(r"\*\*\s*This (?:class|function|property) is a preview feature[^*]*\*\*")


def first(doc):
    # Collapse the stubs' "** This <kind> is a preview feature ... **" banner to one tag.
    doc = PREVIEW_RE.sub("[PREVIEW]", doc)
    lines = [x.strip() for x in doc.strip().splitlines() if x.strip()]
    s = " ".join(lines[:2]) if lines and lines[0] == "[PREVIEW]" else (lines[0] if lines else "")
    return s[:200]


def writable(idx):
    return {(m, c, n) for (m, c, n, k, *_rest) in idx if k == "setter"}


def show(rows, idx, cap):
    w = writable(idx)
    for (m, c, n, k, s, doc, bases) in rows[:cap]:
        if k == "class":
            print(f"{m}.{c}  [class{(' : ' + bases) if bases else ''}]  {first(doc)}")
        elif k == "enum":
            print(f"{m}.{c}.{n} {s}")
        else:
            rw = " (read/write)" if (m, c, n) in w else (" (read-only)" if k == "property" else "")
            print(f"{m}.{c}.{n}{s if k != 'property' else ''}  [{k}{rw}]  {first(doc)}")
    if len(rows) > cap:
        print(f"... {len(rows) - cap} more (raise with -n)")


def main(argv):
    cap = 40
    if "-n" in argv:
        i = argv.index("-n")
        cap = int(argv[i + 1])
        del argv[i:i + 2]
    d = find_build()
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    if argv[0] == "--build":
        print(d)
        print("stub mtime:", os.path.getmtime(os.path.join(d, "fusion.py")))
        return
    idx = load(d)
    if argv[0] == "-c":
        name = argv[1]
        cls = [r for r in idx if r[1].lower() == name.lower() and r[3] == "class"]
        if not cls:
            sys.exit("no class " + name)
        m, c, _, _, _, doc, bases = cls[0]
        print(f"{m}.{c} : {bases}\n{doc}\n")
        mem = [r for r in idx if r[0] == m and r[1] == c and r[3] not in ("class", "setter")]
        show(mem, idx, 10000)
        return
    if argv[0] == "-m":
        c, n = argv[1].split(".", 1)
        rows = [r for r in idx if r[1].lower() == c.lower() and r[2].lower() == n.lower() and r[3] != "setter"]
        w = writable(idx)
        for (m, c2, n2, k, s, doc, _b) in rows:
            rw = " (read/write)" if (m, c2, n2) in w else ""
            print(f"{m}.{c2}.{n2}{s}  [{k}{rw}]\n{doc}\n")
        if not rows:
            print("not found")
        return
    if argv[0] == "--preview":
        mod = argv[1]
        rows = [r for r in idx if r[0] == mod and r[3] == "class" and "preview feature" in r[5]]
        show(rows, idx, 10000)
        return
    if argv[0] == "-d":
        rx = re.compile(argv[1], re.I)
        rows = [r for r in idx if r[3] != "setter" and rx.search(r[5])]
        show(rows, idx, cap)
        return
    rx = re.compile(argv[0], re.I)
    rows = [r for r in idx if r[3] != "setter" and (rx.search(r[2]) if r[2] else rx.search(r[1]))]
    rows.sort(key=lambda r: (r[3] != "class", r[0] != "fusion", r[1], r[2]))
    show(rows, idx, cap)


if __name__ == "__main__":
    main(sys.argv[1:])
