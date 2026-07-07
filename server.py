#!/usr/bin/env python3
import json
import os
import random
import time
import uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
WORLD_W = 2200
WORLD_H = 1500
players = {}
chat = []

SPAWNS = [
    (1100, 760), (1040, 720), (1160, 720), (1100, 840), (980, 820),
    (1240, 820), (960, 640), (1260, 650), (850, 780), (1350, 780)
]

COLORS = {"red", "blue", "green", "yellow", "purple", "pink", "orange", "white", "black", "cyan"}
STYLES = {"warrior", "chef", "mason", "cleaner", "coder", "wanderer", "merchant", "knight"}

def now():
    return time.time()

def clamp(v, a, b):
    try:
        v = float(v)
    except Exception:
        v = a
    return max(a, min(b, v))

def clean_text(s, limit=80):
    if not isinstance(s, str):
        s = ""
    s = s.replace("\r", " ").replace("\n", " ").strip()
    while "  " in s:
        s = s.replace("  ", " ")
    return s[:limit]

def cleanup():
    t = now()
    dead = [pid for pid, p in players.items() if t - p.get("last", 0) > 45]
    for pid in dead:
        players.pop(pid, None)
    if len(chat) > 80:
        del chat[:-80]

class Handler(BaseHTTPRequestHandler):
    server_version = "OpenWorldH5/0.1"

    def log_message(self, fmt, *args):
        return

    def send_json(self, data, code=200):
        raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        if n > 4096:
            n = 4096
        raw = self.rfile.read(n) if n else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        cleanup()
        path = urlparse(self.path).path
        if path == "/" or path == "/index.html":
            fp = os.path.join(ROOT, "index.html")
            data = open(fp, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/state":
            self.send_json({
                "ok": True,
                "time": now(),
                "world": {"w": WORLD_W, "h": WORLD_H},
                "players": list(players.values()),
                "chat": chat[-60:],
            })
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        cleanup()
        path = urlparse(self.path).path
        data = self.read_json()
        if path == "/join":
            pid = uuid.uuid4().hex[:10]
            name = clean_text(data.get("name"), 14) or "无名玩家"
            color = data.get("color") if data.get("color") in COLORS else "cyan"
            style = data.get("style") if data.get("style") in STYLES else "wanderer"
            x, y = random.choice(SPAWNS)
            p = {
                "id": pid, "name": name, "color": color, "style": style,
                "x": x + random.randint(-40, 40), "y": y + random.randint(-40, 40),
                "dir": "down", "bubble": "", "bubbleAt": 0, "last": now(),
            }
            players[pid] = p
            chat.append({"sys": True, "name": "系统", "text": f"{name} 进入了游戏人生广场", "t": now()})
            self.send_json({"ok": True, "id": pid, "player": p, "world": {"w": WORLD_W, "h": WORLD_H}})
            return
        if path == "/update":
            pid = data.get("id")
            p = players.get(pid)
            if not p:
                self.send_json({"ok": False, "error": "not_joined"}, 404)
                return
            p["x"] = clamp(data.get("x", p["x"]), 24, WORLD_W - 24)
            p["y"] = clamp(data.get("y", p["y"]), 24, WORLD_H - 24)
            d = data.get("dir")
            if d in {"up", "down", "left", "right"}:
                p["dir"] = d
            p["last"] = now()
            self.send_json({"ok": True})
            return
        if path == "/say":
            pid = data.get("id")
            p = players.get(pid)
            if not p:
                self.send_json({"ok": False, "error": "not_joined"}, 404)
                return
            text = clean_text(data.get("text"), 80)
            if text:
                p["bubble"] = text
                p["bubbleAt"] = now()
                p["last"] = now()
                chat.append({"id": pid, "name": p["name"], "style": p["style"], "color": p["color"], "text": text, "t": now()})
            self.send_json({"ok": True})
            return
        if path == "/leave":
            pid = data.get("id")
            p = players.pop(pid, None)
            if p:
                chat.append({"sys": True, "name": "系统", "text": f"{p['name']} 离开了广场", "t": now()})
            self.send_json({"ok": True})
            return
        self.send_json({"ok": False, "error": "not_found"}, 404)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "80"))
    print(f"OpenWorldH5 listening on 0.0.0.0:{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
