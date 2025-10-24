import os, json, tempfile, hashlib

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def atomicwritejson(path, data):
    dirpath = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=dirpath, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, sort_keys=True, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

def sha256hexof(obj_str):
    h = hashlib.sha256()
    if isinstance(obj_str, str):
        obj_str = obj_str.encode("utf-8")
    h.update(obj_str)
    return h.hexdigest()
