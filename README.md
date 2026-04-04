# Multiprocess Counter in Python

## Introduction

Consider a Python program that spawns multiple processes where each process wants to increase (or decrease) a global counter.
This repository demonstrates multiple approaches to sharing state between processes.

## Solutions

### 1. Map-Reduce (`simple.py`)

Each worker process creates its own local `Counter`, does its work, and returns the counter.
The main process aggregates results using the `__add__` operator.

- **Pros**: No shared state, no locks, no race conditions. Simple and idiomatic.
- **Cons**: Only works when results can be collected after all workers finish (batch aggregation).

```bash
python simple.py
```

### 2. Client-Server with UDP (`server.py`)

The main process starts a UDP server in a background thread. Worker processes send `INC <value>` commands
over UDP, and the server thread updates the counter.

- **Pros**: Workers can update the counter in real-time without waiting for completion.
- **Cons**:
  - UDP is unreliable — messages can be silently dropped, losing increments.
  - Requires a `time.sleep()` before reading the final value, which is fragile.
  - Hardcoded host/port prevents running multiple instances concurrently.
  - Overly complex (sockets, threads, selectors, custom protocol) for a simple counter.

```bash
python server.py
```

### 3. Shared Memory (`shared.py`)

Uses `multiprocessing.Value` with a `Lock` to share a counter directly across processes.
Workers increment the shared value while holding the lock to prevent race conditions.

- **Pros**: Simple, reliable, no network overhead, deterministic results. The Pythonic way.
- **Cons**: Requires explicit locking. Lock contention can be a bottleneck under high concurrency.

```bash
python shared.py
```
