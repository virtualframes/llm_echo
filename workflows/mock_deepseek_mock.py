#!/usr/bin/env python3
# Minimal mock server implementing POST /v1/chat/completions
# No external deps (uses http.server)

from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class Handler(BaseHTTPRequestHandler):
    def _set_json(self, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self._set_json(404)
            self.wfile.write(json.dumps({"error": "not found"}).encode())
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode() if length else ""
        # Optionally, you can parse body to create a tailored response.
        response = {
            "id": "mock-1",
            "object": "chat.completion",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "This is a mocked response.",
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }
        self._set_json(200)
        self.wfile.write(json.dumps(response).encode())


if __name__ == "__main__":
    httpd = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Mock Deepseek server listening on 8000")
    httpd.serve_forever()
