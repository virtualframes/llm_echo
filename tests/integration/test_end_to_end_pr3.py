import pytest
import os
import subprocess
import threading
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler


class MockDeepseekHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_response(404)
            self.end_headers()
            return
        content_length = int(self.headers.get("Content-Length", 0))
        _body = self.rfile.read(content_length)  # ignored for mock
        response = {
            "id": "mock-1",
            "object": "chat.completion",
            "choices": [{"message": {"role": "assistant", "content": "mocked reply"}}],
        }
        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_mock_server(server):
    server.serve_forever()


def test_end_to_end_pr3():
    # Start a mock server on an ephemeral port
    server = HTTPServer(("127.0.0.1", 0), MockDeepseekHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=start_mock_server, args=(server,), daemon=True)
    thread.start()

    # Give server a short moment to start
    time.sleep(0.05)

    # Set the mock URL to the ephemeral port
    os.environ["DEEPSEEKMOCKURL"] = f"http://127.0.0.1:{port}/v1/chat/completions"

    # Run the pipeline with mock deepseek
    command = [
        "python",
        "workflows/pipeline.py",
        "--mock-deepseek",
        "--limit",
        "10",
        "--outdir",
        "out/pr3_test",
    ]

    result = subprocess.run(
        command, capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "."}
    )

    # If it failed, show stdout/stderr to make CI logs actionable
    assert (
        result.returncode == 0
    ), f"Pipeline failed (rc={result.returncode})\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    # Check that the provenance bundle was created
    provenance_bundle_path = ".github/PROVENANCE"
    assert os.path.exists(provenance_bundle_path)

    # Shutdown server (serve_forever is on daemon thread so process exit will clean up)
    server.shutdown()
    server.server_close()
