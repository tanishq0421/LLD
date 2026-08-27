# Rate Limiter 🟡 Medium (concurrency-native — high SDE-2 signal)

**Format:** machine-coding / concurrency design (often LLD+HLD hybrid) · **Asked by:** Stripe,
Google, Amazon, Meta, Twitter, Cloudflare, Razorpay, Zomato · **Time budget:** 45–60 min ·
**Patterns:** **Strategy** (algorithm), Singleton (shared instance)

> This has grown from niche to one of the most consistently asked problems, and it's increasingly
> reframed around AI/LLM infra (RPM/TPM limits, multi-provider failover). Unlike most problems where
> concurrency is a *follow-up*, here it's **native** — the shared counter is the whole game.

---

## The prompt

> "Design a rate limiter. Given a client id, decide whether a request is allowed or should be
> throttled, based on a configured limit. Implement it with a **token bucket** first, then be ready
> to swap in a **sliding window**. Limits are per-client."

## Clarify before coding

- Per-client, per-endpoint, or global? *"Per-client to start."*
- Which algorithm? *"Token bucket first; we'll compare sliding window."*
- Single process, or distributed across many servers? *"Single process first — distributed is the follow-up."*
- What does 'allow' return — bool, or does it block/queue? *"Return allow/deny (bool)."*

## Algorithms to implement

**Token bucket:** each client has a bucket of `capacity` tokens that refills at `refill_rate`
tokens/second. A request consumes 1 token; if none available, deny. Allows short bursts up to
capacity, smooths to the refill rate. *(Great default.)*

**Sliding window (log):** allow if the number of requests in the last `window_seconds` is below
`max_requests`. Smoother than a fixed window (no boundary bursts), but stores timestamps.

Same interface `allow(client_id) -> bool`, two strategies. That's the design point.

## Core requirements

1. `TokenBucketRateLimiter(capacity, refill_rate, clock)` — per-client buckets, refill over time, cap at capacity.
2. `SlidingWindowRateLimiter(max_requests, window_seconds, clock)` — per-client request log within the window.
3. Independent state per client id.
4. **Injectable clock** so tests are deterministic (default `time.monotonic`).

## Follow-ups (escalations)

1. **Concurrency (core here):** many threads call `allow(same_client)` at once. Two threads both
   read "1 token left" and both allow → limit exceeded. Fix: guard the read-modify-write per client
   (a lock per bucket, or atomic compare-and-set). A single global lock is correct but serializes
   all clients — discuss **per-client locking**.
2. **Distributed:** limit shared across N app servers → move the counter to Redis (INCR + EXPIRE,
   or a Lua script for atomic token-bucket). Discuss the network round-trip vs accuracy trade-off.
3. **Fixed vs sliding window** boundary-burst problem; **leaky bucket** for smoothing output.
4. **LLM-infra flavor:** separate RPM and TPM (tokens-per-minute) limits, multi-provider failover,
   circuit breaker when a provider is down.

## Rubric

- **SDE-1:** correct token bucket + sliding window, per-client isolation, deterministic with clock.
- **SDE-2:** identifies the read-modify-write race precisely, proposes **per-client** (not global)
  locking, and sketches the distributed (Redis) version with its trade-offs.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
The threaded test is skipped by default — enable it when you attempt the thread-safety follow-up.
