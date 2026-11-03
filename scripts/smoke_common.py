"""Helpers compartilhados pelos smoke tests (somente stdlib)."""
import json
import os
import re
import urllib.request
import urllib.error

VOLATILE = re.compile(r"(criado_em|created_at|updated_at|generated_at|timestamp|due_date)$")
EXTRA_HEADERS = {}


def call(base, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if os.environ.get("ADMIN_TOKEN"):
        req.add_header("X-Admin-Token", os.environ["ADMIN_TOKEN"])
    for name, value in EXTRA_HEADERS.items():
        req.add_header(name, value)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status, raw = resp.status, resp.read().decode()
    except urllib.error.HTTPError as err:
        status, raw = err.code, err.read().decode()
    try:
        parsed = json.loads(raw)
    except ValueError:
        parsed = raw
    return status, parsed


def scrub(value):
    if isinstance(value, dict):
        return {k: ("<volatile>" if VOLATILE.search(k) else scrub(v)) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


def run(base, steps):
    failures = 0
    for method, path, body, expected in steps:
        status, parsed = call(base, method, path, body)
        ok = expected is None or status == expected
        failures += 0 if ok else 1
        mark = "OK  " if ok else "FAIL"
        print(f"{mark} {method:6} {path} -> {status}")
        print("     " + json.dumps(scrub(parsed), ensure_ascii=False)[:400])
    print(f"\nRESULT: {len(steps) - failures}/{len(steps)} checks passed")
    return failures
