#!/usr/bin/env python3
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
SUFFIXES = {".log", ".jsonl"}


def log_files(roots):
    """Log files directly inside each root, newest first per root."""
    for root in roots:
        files = [p for p in root.glob("*") if resolve(p, roots)]
        yield from sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def resolve(path, roots):
    """The real path if it is a log file directly inside one of roots, else None."""
    p = Path(path).resolve()
    return p if p.suffix in SUFFIXES and p.is_file() and p.parent in roots else None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Reject other hostnames so a DNS-rebinding page can't read the logs.
        if self.headers.get("Host", "").rsplit(":", 1)[0] not in ("localhost", "127.0.0.1"):
            return self.send(403, "text/plain", b"forbidden host")
        url = urlparse(self.path)
        roots = self.server.roots
        if url.path == "/":
            self.send(200, "text/html; charset=utf-8", (HERE / "index.html").read_bytes())
        elif url.path == "/api/files":
            files = [{"path": str(p), "name": p.name, "dir": str(p.parent), "size": p.stat().st_size}
                     for p in log_files(roots)]
            self.send(200, "application/json", json.dumps(files).encode())
        elif url.path == "/api/file" and (p := resolve(parse_qs(url.query).get("path", [""])[0], roots)):
            self.send(200, "text/plain; charset=utf-8", p.read_bytes())
        else:
            self.send(404, "text/plain", b"not found")

    def send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="*", default=["~/.claude/logs"])
    ap.add_argument("--port", type=int, default=8700)
    args = ap.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.roots = [Path(d).expanduser().resolve() for d in args.dirs]
    print(f"Serving {', '.join(map(str, server.roots))} on http://localhost:{args.port}")
    server.serve_forever()
