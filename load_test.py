"""Bounded, localhost-only load tester for the accompanying lab endpoint."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

MAX_REQUESTS = 1000
MAX_CONCURRENCY = 20


def validate_target(target: str) -> None:
    parsed = urlparse(target)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("target must be a valid HTTP(S) URL")
    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError as exc:
        raise ValueError("target must use a loopback IP address") from exc
    if not address.is_loopback:
        raise ValueError("safety restriction: only 127.0.0.0/8 or ::1 is allowed")


def send_one(target: str, payload: bytes) -> tuple[bool, str]:
    request = Request(target, data=payload, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            response.read()
            return 200 <= response.status < 300, str(response.status)
    except (HTTPError, URLError, TimeoutError) as exc:
        return False, type(exc).__name__


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a safe localhost-only HTTP load test")
    parser.add_argument("--target", default="http://127.0.0.1:8765/echo")
    parser.add_argument("--requests", type=int, default=10)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--payload", default='{"demo":"local"}')
    args = parser.parse_args()

    validate_target(args.target)
    if not 1 <= args.requests <= MAX_REQUESTS:
        parser.error(f"--requests must be between 1 and {MAX_REQUESTS}")
    if not 1 <= args.concurrency <= MAX_CONCURRENCY:
        parser.error(f"--concurrency must be between 1 and {MAX_CONCURRENCY}")
    try:
        json.loads(args.payload)
    except json.JSONDecodeError as exc:
        parser.error(f"--payload must be valid JSON: {exc}")

    payload = args.payload.encode("utf-8")
    print(f"URL: {args.target}")
    print(f"Payload: {args.payload}")
    print(f"Requests: {args.requests}; concurrent: {args.concurrency}")
    started = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(send_one, args.target, payload) for _ in range(args.requests)]
        for future in as_completed(futures):
            results.append(future.result())
    elapsed = time.perf_counter() - started
    successful = sum(ok for ok, _ in results)
    print(f"Successful: {successful}/{args.requests}")
    print(f"Failed: {args.requests - successful}")
    print(f"Elapsed: {elapsed:.3f}s; throughput: {args.requests / elapsed:.2f} req/s")
    return 0 if successful == args.requests else 1


if __name__ == "__main__":
    raise SystemExit(main())
