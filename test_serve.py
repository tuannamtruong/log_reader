"""Self-check for serve.py's path guard"""
import tempfile
from pathlib import Path

from serve import log_files, resolve

with tempfile.TemporaryDirectory() as tmp:
    root, outside = Path(tmp, "logs"), Path(tmp, "secret")
    root.mkdir(), outside.mkdir()
    for p in (root / "a.log", root / "b.jsonl", root / "c.txt", outside / "x.log"):
        p.write_text("[2026-01-01 00:00:00] ls\n")
    (root / "sub").mkdir()
    (root / "sub" / "d.log").write_text("")
    (root / "link.log").symlink_to(outside / "x.log")
    roots = [root.resolve()]

    assert sorted(p.name for p in log_files(roots)) == ["a.log", "b.jsonl"]
    assert resolve(root / "a.log", roots) == (root / "a.log").resolve()
    assert resolve(root / "b.jsonl", roots)
    for bad in (root / "c.txt", outside / "x.log", root / "../secret/x.log",
                root / "sub" / "d.log", root / "link.log", root / "missing.log", "/etc/passwd"):
        assert resolve(bad, roots) is None, bad
print("ok")
