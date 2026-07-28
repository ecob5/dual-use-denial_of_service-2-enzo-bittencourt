# Safe Local Load-Test Demonstrator

This repository contains a bounded, local-only HTTP load-test demonstrator. It is intended for a controlled lab and does not contact public domains or spoof source IP addresses.

## Start time

2026-07-26T20:47:12-03:00

## Run

In one terminal:

```powershell
python local_target.py
```

In another:

```powershell
python load_test.py --target http://127.0.0.1:8765/echo --requests 25 --concurrency 5 --payload '{"demo":"local"}'
```

The client logs the requested URL, payload, configured request count, and concurrency, then reports successful and failed requests, elapsed time, and throughput.

Safety controls reject non-loopback targets and cap requests at 1,000 and concurrency at 20. The target server binds only to `127.0.0.1`.

## End time

2026-07-26 T21:47 -03:00
