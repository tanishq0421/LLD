"""
CHAT SYSTEM — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Users join a room; sending fans out to every OTHER member; leave removes; keep history."
    nouns -> ChatServer, ChatRoom(members, history), User(just an id) ; verbs -> create_room,
    join, leave, send, members, history

STEP 2 — ENTITIES & RELATIONSHIPS
  ChatServer ◆──── ChatRoom    COMPOSITION: rooms live and die inside the server (create_room).
  ChatRoom ◆──── history        COMPOSITION: the (sender, message) log belongs to that room alone.
  ChatRoom o──── members        AGGREGATION: the room tracks WHICH user ids are present, but a
                               user (just a string id here) exists independently of any one room
                               — the same id can join other rooms, or none.
  Users do NOT reference each other at all — see STEP 3. NO inheritance: one member type, no
  behavioural difference between users to model in the base.

STEP 3 — PATTERN? (what varies?)
  This is the textbook MEDIATOR. The naive design gives every User a list of "the other users in
  my room" and has User.send() loop over it directly — that's an O(n²) tangle: adding a member
  means pushing a reference into everyone else's list, and a User class ends up knowing about
  fan-out, membership, and messaging all at once. Instead, users only know about the ROOM; the
  ROOM is the mediator that knows the membership and does the fan-out. join()/leave() touch only
  the room's member set — no user object is ever touched when its neighbours change. This also
  cleanly separates Mediator from Observer: Observer is ONE subject broadcasting to many watchers
  that registered on IT; Mediator is many PEERS (users) that would otherwise talk directly to each
  other, now routed through a third party (the room) so they stay decoupled from one another.

STEP 4 — SOLID
  SRP  ChatRoom owns membership + fan-out + history; ChatServer only owns the room registry
       (create/lookup) — it doesn't know how a room fans messages out.
  OCP  moderation (banned words, muted users, rate limits) or DMs are new checks/methods INSIDE
       the mediator (ChatRoom/ChatServer) — no change needed to how a "user" is modeled, because
       users never held that logic to begin with.
  LSP/ISP  not meaningfully in play — no subclassing, no client is forced to depend on methods it
       doesn't use.
  DIP  ChatServer depends on room data it owns directly (no external service dependency to invert
       in the base); if persistence were added, history storage would be injected, same DI idea
       as the parking lot's clock.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (join, fan-out excluding sender, leave) ────────────
#   s = ChatServer()
#   s.create_room("r1")
#   s.join("r1", "alice"); s.join("r1", "bob"); s.join("r1", "carol")
#   s.send("r1", "alice", "hi all")            # delivered to bob, carol (NOT alice) -> ["bob","carol"]
#   s.history("r1")                            # [("alice", "hi all")]
#   s.leave("r1", "bob")                       # bob is no longer a member
#   s.send("r1", "alice", "bob left")          # -> ["carol"]  (bob no longer receives)
#   s.members("r1")                            # ["alice", "carol"]  (sorted)
#   s.send("r1", "dave", "hi")                 # ChatError: dave never joined -> not a member
#   # Flow: alice -> ChatServer.send("r1", ...) -> ChatServer looks up the ROOM (mediator) ->
#   # room computes recipients = members - {sender}, appends to its own history, returns recipients.
#   # alice and bob never reference each other directly at any point.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====


# class ChatError(Exception):
#     pass


# class ChatServer:
#     def __init__(self):
#         # LOGIC: each room is a tiny (members: set, history: list) pair. A set for members gives
#         # join() idempotence and O(1) leave() for free; the room acts as the MEDIATOR — everything
#         # about "who's in this room" and "who gets this message" lives here, never on a user.
#         self.rooms = {}   # room_id -> {"members": set(), "history": [(sender, message), ...]}

#     def create_room(self, room_id):
#         if room_id in self.rooms:
#             raise ChatError(f"room already exists: {room_id}")
#         self.rooms[room_id] = {"members": set(), "history": []}

#     def _room(self, room_id):
#         # LOGIC: shared lookup + guard, so every public method raises the same ChatError for an
#         # unknown room instead of repeating the check-and-raise five times.
#         if room_id not in self.rooms:
#             raise ChatError(f"unknown room: {room_id}")
#         return self.rooms[room_id]

#     def join(self, room_id, user_id):
#         room = self._room(room_id)
#         room["members"].add(user_id)     # LOGIC: set.add is a no-op if user_id is already present
#         # -> join() is naturally idempotent without an extra "if already a member" check.

#     def leave(self, room_id, user_id):
#         room = self._room(room_id)
#         room["members"].discard(user_id)  # LOGIC: .discard (not .remove) -> no-op if absent, no KeyError

#     def send(self, room_id, sender, message):
#         room = self._room(room_id)
#         if sender not in room["members"]:
#             raise ChatError(f"{sender} is not a member of {room_id}")
#         room["history"].append((sender, message))
#         # LOGIC: fan-out = every member EXCEPT the sender. sorted() over a set-minus gives a
#         # deterministic, alphabetically ordered recipient list, matching the contract exactly.
#         recipients = sorted(room["members"] - {sender})
#         return recipients

#     def members(self, room_id):
#         return sorted(self._room(room_id)["members"])

#     def history(self, room_id):
#         # LOGIC: return a copy so a caller mutating the returned list can't corrupt the room's
#         # own history log.
#         return list(self._room(room_id)["history"])
