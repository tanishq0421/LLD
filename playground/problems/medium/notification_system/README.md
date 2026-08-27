# Notification System 🟡 Medium (Observer + Strategy + Adapter)

**Format:** machine-coding + OOD · **Asked by:** Amazon, Uber, LinkedIn, Twitter, Flipkart, Netflix
· **Time budget:** 60 min · **Patterns:** **Observer** (subscribers), **Strategy/Adapter**
(channels), Decorator (enrichment)

> A staple at big tech and product companies. The design lesson is decoupling **who gets notified**
> (subscribers) from **how** (channels: email/SMS/push), so both sides grow independently. Each
> channel is an **Adapter** over a real provider with its own API.

---

## The prompt

> "Design a notification system. A user can subscribe to one or more delivery channels (email, SMS,
> push). When the system notifies a user, it delivers the message through each channel that user is
> subscribed to. Adding a new channel (WhatsApp, Slack) must not require changing the core."

## Clarify before coding

- Per-user channel preferences? *"Yes — each user picks their channels."*
- One message type, or templated per channel? *"One message for now; per-channel formatting is a follow-up."*
- Real providers? *"Abstract them — the system calls a uniform `send(recipient, message)`; each
  channel adapts its provider."*
- Delivery guarantees / retries? *"Best-effort for the base; retries are a follow-up."*

## Core requirements

1. `register_channel(name, sender)` — plug in a channel; `sender(recipient, message)` is the uniform
   interface each channel adapts to.
2. `subscribe(user, channel)` / `unsubscribe(user, channel)` — per-user preferences; subscribing to
   an unregistered channel is an error.
3. `notify(user, message)` — deliver via every channel the user is subscribed to; return the list of
   channels that delivered.
4. A user with no subscriptions receives nothing (empty result), no error.

## Why these patterns

- **Adapter:** each channel wraps a provider (SES, Twilio, FCM) whose native API differs, exposing a
  uniform `send(recipient, message)`. The service never knows provider specifics.
- **Observer-ish:** users subscribe to channels; the service iterates subscribers/preferences and
  pushes — new subscribers/channels are additions, not edits.
- **Strategy:** the delivery mechanism per channel is interchangeable behind that uniform send.

## Follow-ups (escalations)

1. **Per-channel formatting** (SMS truncation, rich HTML email) — a formatting **Strategy** or **Decorator**.
2. **Topics/events:** users subscribe to event types ("order_shipped"); publishing an event fans out.
3. **Retries + dead-letter** on provider failure; **rate limiting** per user/channel.
4. **Async delivery** via a queue so `notify` doesn't block; **priority** notifications.
5. **User quiet hours / preferences engine.**

## Rubric

- **SDE-1:** correct per-user multi-channel delivery, subscribe/unsubscribe, guards.
- **SDE-2:** channels as clean Adapters (new channel = pure addition), and a coherent story for
  formatting, retries, async, and event/topic fan-out.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
