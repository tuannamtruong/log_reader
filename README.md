# Logs Reader

Reading logs with .log / .jsonl format.

## 1. Run

```bash
python3 serve.py
python3 serve.py DIR... --port 9000   # other folders or port
```

Without the server, open `index.html` directly and drop log files onto the page.

## 2. Features

- Sidebar lists the log files in each folder, newest first, plus "All files" and the last 10 opened.
- Commands group into sessions by `session` id, or by time gap (default 30 min) when the entry has none.
- Search matches command and description text.
- "Hide read-only" (off by default) hides commands that only read (`ls`, `grep`, `git status`, …). The verb list is
  `READ` in `index.html`.

## 3. Log formats

| File | Entry |
| --- | --- |
| `.log` | `[YYYY-MM-DD HH:MM:SS] command`, command may span lines |
| `.jsonl` | one JSON object per line: `ts`, `cmd`, optional `desc`, `cwd`, `session` |

## 4. Security

The server binds to `127.0.0.1`, rejects any `Host` other than `localhost` / `127.0.0.1` (DNS rebinding) and serves only `.log` / `.jsonl` files directly inside the given folders.
No subfolders, `..`, or symlinks pointing out.