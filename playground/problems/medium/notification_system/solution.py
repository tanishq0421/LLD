"""
NOTIFICATION SYSTEM — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

WHY THIS ONE FOR BOTH: myKaarma's whole product is dealer↔customer messaging (SMS/email);
Blinkit pushes order-status updates. The design lesson — decouple WHO gets notified from HOW —
is what interviewers reward, and it shows off Observer + Adapter cleanly.

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES
  "Users subscribe to channels (email/SMS/push); notifying a user sends via each subscribed
   channel; adding a channel must not touch the core."
    nouns -> NotificationService, Channel, (User prefs) ; verbs -> register, subscribe, notify

STEP 2 — ENTITIES & RELATIONSHIPS
  Service o──── Channel        channels are REGISTERED into the service (aggregation): a channel
                               is really an ADAPTER over a provider (SES/Twilio/FCM) whose native
                               APIs differ, exposing ONE uniform send(recipient, message).
  Service ──── prefs           per-user set of channel names (who wants what).
  Service ───▶ Channel.send    the service depends on the SEND INTERFACE, never on concrete
                               providers → new provider = new adapter, zero core edits (DIP+OCP).

STEP 3 — PATTERNS (three, and they're all justified here)
  • ADAPTER   — each channel wraps a provider's odd API into send(recipient, message).
  • OBSERVER  — users subscribe; notify() fans a message out to a user's subscribed channels.
  • STRATEGY  — the delivery mechanism per channel is interchangeable behind that uniform send.
  This is a rare case where naming 2–3 patterns is correct because 2–3 forces genuinely vary
  (provider API, subscriber set, delivery mechanism). Still start simple; don't add formatting/
  retry machinery until asked.

STEP 4 — SOLID + FOLLOW-UPS
  OCP  a new channel (WhatsApp/Slack) = register a new sender, no edit to notify().
  SRP  the service routes; each channel/adapter talks to one provider.
  FOLLOW-UPS to mention: per-channel formatting (Strategy/Decorator), retries + dead-letter,
  ASYNC delivery via a queue so notify() doesn't block, event/topic fan-out.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (wire channels once, then notify) ─────────────────
#   svc = NotificationService()
#   svc.register_channel("email", lambda to, msg: ses.send(to, msg))    # each sender = an ADAPTER
#   svc.register_channel("sms",   lambda to, msg: twilio.text(to, msg)) #   over a real provider's API
#   svc.subscribe("u1", "email"); svc.subscribe("u1", "sms")            # u1's per-user prefs
#   svc.notify("u1", "Order shipped")   # walk channels in reg order; for each u1 subscribed to,
#                                       #   call sender(u1, msg) → returns ["email", "sms"]
#   svc.notify("u2", "hi")              # u2 has no prefs → [] (no error)
#   # Flow:  producer/event → Service.notify → each subscribed Channel(adapter) → provider.send(...).
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====


# class NotificationError(Exception):
#     pass


# class NotificationService:
#     def __init__(self):
#         # channels: name -> sender callable. `sender(recipient, message)` is the UNIFORM
#         # interface every provider-adapter conforms to. Dict preserves registration order,
#         # which we use for deterministic delivery order.
#         self.channels = {}
#         self.prefs = {}      # user_id -> set of channel names they've subscribed to

#     def register_channel(self, name, sender):
#         # `sender` is the adapter: it hides whether it's really Twilio, SES, FCM, etc.
#         self.channels[name] = sender

#     def subscribe(self, user, channel):
#         if channel not in self.channels:
#             raise NotificationError("channel not registered")
#         # setdefault + set = idempotent (subscribing twice doesn't double-deliver).
#         self.prefs.setdefault(user, set()).add(channel)

#     def unsubscribe(self, user, channel):
#         self.prefs.get(user, set()).discard(channel)   # no-op if not subscribed

#     def notify(self, user, message):
#         subs = self.prefs.get(user, set())              # a user with no prefs → nothing, no error
#         delivered = []
#         # iterate CHANNELS (registration order) and deliver to the ones this user wants →
#         # deterministic order, and the service never hard-codes provider specifics.
#         for name, sender in self.channels.items():
#             if name in subs:
#                 sender(user, message)
#                 delivered.append(name)
#         return delivered
