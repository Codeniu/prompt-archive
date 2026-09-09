"""Prompt collection web app - single file, stdlib only."""
import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 8000
STORAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.json")
INDEX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")


def load_prompts():
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_prompts(prompts):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/" or path == "/index.html":
            try:
                with open(INDEX_FILE, "r", encoding="utf-8") as f:
                    html = f.read().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
            except FileNotFoundError:
                self._send_json(404, {"error": "index.html not found"})
        elif path == "/api/prompts":
            prompts = load_prompts()
            self._send_json(200, {"prompts": prompts})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/prompts":
            self._send_json(404, {"error": "not found"})
            return
        data = self._read_body()
        content = (data.get("content") or "").strip()
        title = (data.get("title") or "").strip()
        tags = data.get("tags") or []
        if not content:
            self._send_json(400, {"error": "content is required"})
            return
        prompts = load_prompts()
        prompt = {
            "id": uuid.uuid4().hex,
            "title": title,
            "content": content,
            "tags": tags,
            "created_at": int(time.time()),
        }
        prompts.append(prompt)
        save_prompts(prompts)
        self._send_json(201, {"prompt": prompt})

    def do_PUT(self):
        path = urlparse(self.path).path
        if not path.startswith("/api/prompts/"):
            self._send_json(404, {"error": "not found"})
            return
        target_id = path.rsplit("/", 1)[-1]
        data = self._read_body()
        content = (data.get("content") or "").strip()
        title = (data.get("title") or "").strip()
        tags = data.get("tags") or []
        if not content:
            self._send_json(400, {"error": "content is required"})
            return
        prompts = load_prompts()
        for p in prompts:
            if p.get("id") == target_id:
                p["title"] = title
                p["content"] = content
                p["tags"] = tags
                p["updated_at"] = int(time.time())
                save_prompts(prompts)
                self._send_json(200, {"prompt": p})
                return
        self._send_json(404, {"error": "prompt not found"})

    def do_DELETE(self):
        path = urlparse(self.path).path
        if not path.startswith("/api/prompts/"):
            self._send_json(404, {"error": "not found"})
            return
        target_id = path.rsplit("/", 1)[-1]
        prompts = load_prompts()
        new_prompts = [p for p in prompts if p.get("id") != target_id]
        if len(new_prompts) == len(prompts):
            self._send_json(404, {"error": "prompt not found"})
            return
        save_prompts(new_prompts)
        self._send_json(200, {"deleted": target_id})

    def log_message(self, *args):
        pass


def main():
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Prompt collector running on http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
