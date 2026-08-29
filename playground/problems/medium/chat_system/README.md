# Chat / Messaging System 🟡 Medium (Mediator pattern)

**Format:** machine-coding + OOD · **Asked by:** Slack/Meta-style messaging rounds, and as the
classic **Mediator** problem · **Time budget:** 60 min · **Patterns:** **Mediator** (room relays
messages), Observer (delivery)

> The textbook **Mediator** problem. Instead of every user holding references to every other user
> (an O(n²) tangle), a `ChatRoom` sits in the middle: users talk *to the room*, and the room fans
> messages out. Add/remove a user without touching anyone else.

---

## The prompt

> "Design a group chat system. Users join a room; when a user sends a message to the room, every
> other member receives it. Users can leave. Keep the room's message history. A user must be a member
> to send."

## Clarify before coding

- Group rooms, direct messages, or both? *"Group rooms for the base; DMs are a follow-up."*
- Does the sender receive their own message? *"No — only the other members."*
- Persist history? *"Yes, per room."*
- Delivery guarantees / online-offline? *"Best-effort fan-out for the base."*

## Core requirements

1. `create_room(room_id)` (error on duplicate).
2. `join(room_id, user_id)` / `leave(room_id, user_id)`.
3. `send(room_id, sender, message)` — deliver to all members except the sender; return the sorted
   list of recipient ids. Sender must be a member (`ChatError`).
4. `history(room_id)` → list of `(sender, message)` in order; `members(room_id)` → sorted member ids.

## Why Mediator

Without it, each `User` would keep references to all other users and broadcast directly — adding a
user means updating everyone (tight coupling, O(n²) links). The **ChatRoom is the mediator**: users
depend only on the room, the room knows the members and does the fan-out. New member types, moderation,
or filtering all live in the mediator, not spread across users. (Contrast with Observer: Observer is
one subject → many watchers; Mediator coordinates many peers talking to each other.)

## Follow-ups (escalations)

1. **Direct (1:1) messages** and multiple rooms per user.
2. **Moderation** in the mediator: banned words, muted users, rate limiting per user.
3. **Delivery/read receipts, typing indicators, presence** (online/offline).
4. **Offline delivery:** queue messages for absent members (bridges into pub/sub + offsets).
5. **Scale:** sharding rooms across servers; ordering guarantees.

## Rubric

- **SDE-1:** correct fan-out (excluding sender), membership rules, history, guards.
- **SDE-2:** clean Mediator (users coupled only to the room), can add moderation/DMs/offline delivery
  in the mediator without changing users, and articulates Mediator vs Observer.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
