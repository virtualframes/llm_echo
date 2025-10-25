import os
import json
import tempfile
import hashlib


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def atomic_write_json(path, data):
    dir_path = os.path.dirname(path) or "."
    ensure_dir(dir_path)
    fd, tmp = tempfile.mkstemp(dir=dir_path, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, sort_keys=True, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def sha256_hex_of_str(s: str):
    if isinstance(s, str):
        b = s.encode("utf-8")
    else:
        b = s
    return hashlib.sha256(b).hexdigest()


def sha256_hex_of_obj(obj):
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return sha256_hex_of_str(s)
