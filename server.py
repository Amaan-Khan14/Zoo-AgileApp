#!/usr/bin/env python3
"""
Zoo Sprint Simulation - local server

Run:  python server.py
Then open the address it prints (http://localhost:8000)

All board data is stored in zoo-data.json in this same folder.
That file IS the database. Back it up, email it, edit it - it's plain text.
"""
import http.server, socketserver, json, os, shutil, threading, webbrowser
from datetime import datetime

PORT = int(os.environ.get("PORT", 8000))
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "zoo-data.json")
BACKUPS = os.path.join(HERE, "backups")

EMPTY = {"kanban": {}, "notes": {}, "updated": "", "savedBy": ""}
_lock = threading.Lock()


def load():
    if not os.path.exists(DB):
        return dict(EMPTY)
    try:
        with open(DB, "r", encoding="utf-8") as f:
            d = json.load(f)
        for k, v in EMPTY.items():
            d.setdefault(k, v)
        return d
    except Exception as e:
        print("  ! zoo-data.json unreadable (%s) - starting empty" % e)
        return dict(EMPTY)


def save(data):
    with _lock:
        # keep a rolling backup so a bad save never loses the session
        if os.path.exists(DB):
            os.makedirs(BACKUPS, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            try:
                shutil.copy2(DB, os.path.join(BACKUPS, "zoo-data-%s.json" % stamp))
                files = sorted(os.listdir(BACKUPS))
                for old in files[:-20]:
                    os.remove(os.path.join(BACKUPS, old))
            except Exception:
                pass
        data["updated"] = datetime.now().isoformat(timespec="seconds")
        tmp = DB + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
        os.replace(tmp, DB)
        return data


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def log_message(self, fmt, *args):
        try:
            first = str(args[0]) if args else ""
        except Exception:
            first = ""
        if "/api/" not in first:
            super().log_message(fmt, *args)

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/state"):
            return self._json(load())
        if self.path.startswith("/favicon.ico"):
            return self._favicon()
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def _favicon(self):
        # 1x1 icon so the browser stops requesting a file that isn't there
        import base64
        ico = base64.b64decode("AAABAAEAAQEAAAEAIAAwAAAAFgAAACgAAAABAAAAAgAAAAEAIAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAABPj2r/AAAAAA==")
        self.send_response(200)
        self.send_header("Content-Type", "image/x-icon")
        self.send_header("Content-Length", str(len(ico)))
        self.send_header("Cache-Control", "max-age=86400")
        self.end_headers()
        self.wfile.write(ico)


    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self):
        if not self.path.startswith("/api/state"):
            return self._json({"error": "not found"}, 404)
        try:
            n = int(self.headers.get("Content-Length", 0))
            incoming = json.loads(self.rfile.read(n) or b"{}")
        except Exception as e:
            return self._json({"error": str(e)}, 400)
        cur = load()
        cur["kanban"] = incoming.get("kanban", cur["kanban"])
        cur["notes"] = incoming.get("notes", cur["notes"])
        cur["savedBy"] = incoming.get("savedBy", "")
        saved = save(cur)
        print("  saved %s cards, %s notes  [%s]" % (
            len(saved["kanban"]), len(saved["notes"]), saved["updated"]))
        return self._json(saved)

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        # a dropped connection is not worth a stack trace
        pass


def local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    if not os.path.exists(DB):
        save(dict(EMPTY))
        print("Created zoo-data.json")

    url = "http://localhost:%d" % PORT
    print("\n" + "=" * 62)
    print("  ZOO SPRINT SIMULATION")
    print("=" * 62)
    print("  Facilitator :  %s" % url)
    print("  Same wifi   :  http://%s:%d" % (local_ip(), PORT))
    print("  Database    :  %s" % DB)
    print("  Backups     :  ./backups/  (last 20 saves)")
    print("\n  Anyone on the same wifi can open the second link and")
    print("  see the live board. Stop the server with Ctrl+C.")
    print("=" * 62 + "\n")

    try:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    except Exception:
        pass

    with Server(("0.0.0.0", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopped. Your data is safe in zoo-data.json\n")
