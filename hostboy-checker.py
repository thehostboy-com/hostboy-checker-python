#!/usr/bin/env python3
import hashlib
import json
import os
import platform
import tempfile
import time
import uuid
import urllib.error
import urllib.request
from urllib.parse import urlparse


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def main():
    endpoint = os.environ.get("HOSTBOY_REPORT_URL", "")
    key = os.environ.get("HOSTBOY_CHECKER_KEY", "")
    parsed_endpoint = urlparse(endpoint)
    local_http = parsed_endpoint.scheme == "http" and parsed_endpoint.hostname == "127.0.0.1" and not parsed_endpoint.username and not parsed_endpoint.password
    if not key or not (parsed_endpoint.scheme == "https" or local_http) or not parsed_endpoint.hostname or parsed_endpoint.username or parsed_endpoint.password or parsed_endpoint.fragment:
        raise RuntimeError("Configure an HTTPS report URL and checker key")
    block = b"a" * 1048576
    started = time.perf_counter()
    for _ in range(32):
        hashlib.sha256(block).digest()
    hash_ms = (time.perf_counter() - started) * 1000
    disk_ms = None
    try:
        with tempfile.TemporaryDirectory(prefix="hostboy-") as directory:
            path = os.path.join(directory, "block")
            started = time.perf_counter()
            with open(path, "wb") as output:
                output.write(block)
            with open(path, "rb") as source:
                source.read()
            disk_ms = (time.perf_counter() - started) * 1000
    except OSError:
        pass
    payload = json.dumps({"runtime": "python", "schemaVersion": 1, "version": platform.python_version(), "suite": "hostboy-v1", "requestId": uuid.uuid4().hex,
                          "hashMs": hash_ms, "diskMs": disk_ms, "memoryLimitBytes": None,
                          "availableParallelism": os.cpu_count()}).encode()
    opener = urllib.request.build_opener(NoRedirectHandler)
    for attempt in range(3):
        request = urllib.request.Request(endpoint, data=payload, method="POST", headers={
            "Authorization": "Bearer " + key, "Content-Type": "application/json"})
        try:
            with opener.open(request, timeout=10) as response:
                if response.status == 201:
                    break
                if response.status < 500 or attempt == 2:
                    raise RuntimeError("Report rejected (HTTP %s)" % response.status)
        except urllib.error.HTTPError as error:
            if error.code < 500 or attempt == 2:
                raise RuntimeError("Report rejected (HTTP %s)" % error.code) from error
        except (OSError, urllib.error.URLError, TimeoutError) as error:
            if attempt == 2:
                raise RuntimeError("TheHostBoy report was not accepted") from error
        if attempt < 2:
            time.sleep(0.25 * (2 ** attempt))
    print("TheHostBoy report accepted")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error), file=__import__("sys").stderr)
        raise SystemExit(1)
