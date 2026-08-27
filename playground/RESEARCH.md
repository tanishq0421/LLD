# LLD Interview Research — Findings & Sources

Compiled from internet research (2022–2026), focused on **SDE-1 → SDE-2** rounds at
Indian + global product companies. This is the evidence base behind the problem selection,
difficulty tiers, and follow-ups in `problems/`.

---

## A. The canonical, most-frequently-asked problems (ranked)

### Tier 1 — appear constantly ("must-know")
| Problem | Companies cited | Notes |
|---|---|---|
| **Parking Lot** | Amazon, Google, Microsoft, Adobe, Uber, Grab, Gojek | #1 most-asked; escalates to "two cars race for one spot" (concurrency) |
| **Elevator / Lift** | Amazon, Microsoft, Uber, Google, Adobe, Lyft | State + Strategy + Observer; escalates to multi-elevator dispatch |
| **LRU Cache / in-memory KV** | Google, Amazon, Microsoft, Meta, Adobe, Netflix | Often extended to LFU or TTL |
| **Splitwise / expense-sharing** | Swiggy, Amazon, Razorpay, Indian fintech | "Settle balances / simplify debts" extension |
| **Vending Machine** | Google, Amazon, Microsoft, Apple, Oracle | ~20% of SDE-1 interviews at product cos; State-heavy |
| **Chess** | Amazon, Adobe, Meta, Microsoft, Games24x7 | Polymorphism/inheritance depth |
| **Tic-Tac-Toe / Connect Four** | Widely used as junior/first-round filter | |
| **Rate Limiter** (token bucket / sliding window) | Stripe, Google, Amazon, Meta, Twitter, Cloudflare, Razorpay, Zomato | Near-universal concurrency follow-up; now often LLD/HLD hybrid |

### Tier 2 — very common (product / e-commerce / fintech)
BookMyShow / movie ticket booking · Logging framework · Library management ·
Notification system (multi-channel) · Meeting-room / calendar scheduler ·
Food delivery (Zomato/Swiggy) · Ride-hailing (Uber/Ola) · Car rental ·
URL shortener (LLD flavor) · Amazon Locker · File system.

### Tier 3 — regular but domain-specific / "hard escalation"
Payment processor/gateway (Stripe, PayPal, Razorpay) · Order matching engine
(Goldman, Morgan Stanley, Coinbase, Robinhood) · Task/job scheduler (DAG) ·
News feed (Meta, Twitter, LinkedIn) · Snake & Ladder · Coupon/discount engine ·
Hotel booking · ATM · Pub-Sub · In-memory SQL/DB · scoreboard.

---

## B. Company-specific formats

**Strict machine-coding** (runnable code, own IDE, 90–120 min) — mostly Indian product/fintech:
- **Flipkart, Uber (India), Swiggy, Ola, Cred, Udaan, Gojek** (per workat.tech).
- **Swiggy**: 5 rounds — OA → machine coding (Splitwise-style) → DSA → LLD (parts of the Swiggy app, e.g. cart) → EM. Hard filter.
- **Razorpay**: 90–120 min; reported problems: in-memory EMI calculator, rate limiter, payment ledger, expense splitter, in-memory SQL DB, in-memory pub-sub, logger with label routing. Graded on SOLID + extensibility.
- **Media.net**: systems/networking-flavored (e.g. UDP echo server + heartbeat in Python), still requires proper OOP structure.
- **Arcesium**: more classic DSA/OA-heavy; LLD is one topic among several.
- **PhonePe, Paytm**: LLD/machine-coding/concurrency now mandatory rounds.

**Whiteboard / discussion OOD** (45–60 min, pseudocode/diagrams, not compiled) — Western Big Tech:
- **Google, Amazon, Meta, Microsoft** — virtual doc/whiteboard, class design + SOLID focus.
- **Amazon** most consistently includes OOD; often "provide the APIs" framing then escalates (sharding, heartbeat, emergencies).
- **Atlassian**: 60-min applied/OOD tied to real product (e.g. "Jira issue permission model for 10K users", "Confluence real-time collab for 50 editors"); adds scale-up mid-round.
- **Fintech/trading** (Goldman, Morgan Stanley, Coinbase, Robinhood): order-matching engine.

**Five recognizable LLD formats** (AlgoMaster): OOD (whiteboard) · Machine Coding (IDE) ·
Concurrency Design · API Design (30–45 min, B2B SaaS) · Schema Design (DB/analytics).

---

## C. How the round runs & how candidates fail

- **Machine coding**: 90–120 min live code (must compile/run, no UI, include a `main`/driver for testability), then a ~30-min code-review discussion. **OOD**: 45–60 min pseudocode/diagrams.
- **Evaluated on**: working code · modularity/readability · separation of concerns · extensibility · SOLID · encapsulation · testability.
- **Universal follow-up escalations**: (1) concurrency/thread-safety — *the* most common; (2) feature extension ("add undo", "multiple floors", "scale to 10K"); (3) failure/edge-case handling.
- **Top reasons candidates fail**: over-engineering (KISS violation) · poor time management (coding before designing, or over-designing) · skipping requirement clarification · silent problem-solving (no trade-off narration) · premature optimization · overusing inheritance · ignoring edge cases.

---

## D. SDE-1 vs SDE-2 bar

- **SDE-1**: can they produce *correct* code at all; hints given freely; learning ability assessed.
- **SDE-2**: independent problem-solving with less hand-holding; **depth of trade-offs and judgment**, not a harder base problem. Scope widens to entity/data modeling + end-to-end flow + API modeling.
- **What raises the bar**: proactive/fluent **concurrency**; **extensibility under live requirement changes**; **driving ambiguity/scope** yourself; **explicit trade-off comparison**; depth over breadth.

---

## E. Trending shifts (2024–2026)

- **AI-assisted coding is an unsettled variable**: Google/Meta piloting AI-allowed formats scored on *how well you use AI*; Amazon/Goldman **ban** unauthorized AI; Canva insists on AI use. Advice: assume banned unless told otherwise in writing; confirm with recruiter.
- **AI-cheating detection** now a real operational issue (large share of live interviews flagged).
- **Rate Limiter** risen from niche to top-recurring; often reframed around LLM/AI infra (RPM/TPM, multi-provider failover, circuit breakers).
- **Concurrency-as-default-escalation** — treated as near-universal for SDE-2+.
- The **canonical problem pool has stabilized** even as companies debate AI-assistance rules.

---

## F. Design patterns — do you need all 23? (No)

Consensus: **5 core** (Strategy, Observer, Factory, Singleton, State) cover most interviews;
**10 secondary**; **8 rare**. See `patterns/README.md` for the full tier list + problem mapping.
Key nuances:
- "Factory" in interviews = **Simple Factory**, not GoF Factory Method.
- **Singleton** widely used but criticized (DI preferred for testability).
- **India** interviews ask patterns *by name* more than the US, which grades design quality.
- **Over-engineering is a named red flag**; "most interview-ready designs use no patterns, or at most one or two."
- Weighted higher than patterns: **SOLID, composition over inheritance, coupling/cohesion, restraint**.

**Concurrency** framing (Hello Interview): every concurrency question is one of —
**correctness** (double-booking race), **coordination** (thread handoff), **scarcity**
(limited resource allocation). Parking-lot fix: **fine-grained per-spot locking**, not a
global lock (which destroys throughput). For SDE-2, correctness is the baseline expectation.

---

## G. How the problem is actually handed to you (UML or not?)

**You are never handed a UML/class/ER diagram to implement** — that would defeat the round,
which exists to test whether *you* can derive the class model. You get a **written or verbal
problem statement** (a paragraph to ~2 pages) and produce the entities/relationships yourself.

**What you're expected to PRODUCE differs by format:**
- **Whiteboard / OOD** (Google, Amazon, Meta, Microsoft; 45–60 min): sketch entities,
  relationships, and an informal class diagram *before* pseudocode. Formal UML notation is
  **not mandatory** — "boxes, arrows, and labels work just fine"; check with the interviewer.
  Flow: clarify scope → use cases → assign responsibilities → model relationships → expose a
  small public API → stress-test with a change request.
- **Machine coding** (Flipkart, Uber, Swiggy, Razorpay; 90–120 min): lighter artifacts, often
  straight to code. Taught trick: **underline the nouns (→ classes) and verbs (→ methods)** on
  a scratchpad. Deliverable is compiled/runnable code with a `main`/driver or unit tests for
  testability. No UI/REST needed — "functional APIs are expected."

**How detailed is the prompt?**
- **Machine coding** gives the *hard constraints that make it codeable* fairly concretely
  upfront (entity types, commands, I/O format) — the clock is tight, so they don't want
  requirements archaeology — while leaving *scope-expanders* (concurrency, multi-floor, new
  split types, scale) for you to ask about or for them to add as escalations.
  - *Splitwise example (near-verbatim):* "Create an expense-sharing application." Users have
    userId/name/email/mobile. Support **EQUAL / EXACT / PERCENT** splits (percent must sum to
    100). Commands: `EXPENSE <payer> <amount> <n> <users> <type> <values>`, `SHOW`,
    `SHOW <user>`. Output `x owes y: amount`, non-zero only, else "No balances". Stretch:
    notes, passbook, debt simplification.
- **Whiteboard / OOD** *inverts* this: the opener is deliberately minimal ("Design a parking
  lot system.") specifically to test your clarifying-question skill.
  - *Parking Lot example:* interviewer says only "Design a parking lot system." You must ask
    "What vehicle types?" → "motorcycles, cars, trucks." "Flat rate or duration-based?" →
    "track entry/exit; duration-based." Scope is built up through *your* questions.

**Starter code?**
- Mostly a **blank IDE** (Indian machine-coding: own laptop, screen-shared). No starter classes.
- Some rounds give a **pre-set repo** to extend (e.g. Uber via HackerRank).
- **No source documented a mandatory required-interface skeleton** for a *classic OOP LLD*
  problem — that pattern belongs to frontend/DSA machine coding. (This repo defines a small
  "test contract" only so the automated tests can call your code — see `HOW_TO_PRACTICE.md`.)

**Tooling:** own IDE + screen-share; CoderPad / HackerRank (some with pre-set repos); Google
Doc (Google, pseudocode); Excalidraw / `whiteboard.facebookrecruiting.com` (Meta); draw.io.
Three phases regardless of tool: **pre-coding** (read + clarify) → **coding** → **post-coding**
walkthrough/demo (~20–30 min).

*Sources:* AlgoMaster (how to answer an LLD problem) · workat.tech (crack machine coding;
Splitwise editorial) · GreatFrontend (machine coding guide) · ByteByteGo (OOD parking lot) ·
Final Round AI (Amazon parking lot) · Excalidraw (hiring use-case) · HackerRank/CoderPad
comparison · Blind (Google Doc; Meta whiteboard threads) · Flipkart interview guide.

---

## Sources

**Problems / formats:** Low Level Design Mastery · CodeZym (2026 guide; 7-day roadmap) ·
AlgoMaster (interview types; concurrency; learn-LLD-from-zero) · Hello Interview
(LLD in-a-hurry; prep guide; patterns; principles; concurrency; rate-limiter breakdown) ·
workat.tech (machine-coding) · Chakresh Tiwari "Ultimate List" (Medium) · Finalround AI
(Swiggy) · techinterview.org (Atlassian) · Media.net interview writeup (Medium) ·
educative.io · "LLD for SDE1/SDE2" (Medium) · getsdeready (SDE-1/2/3) ·
"AI in coding interviews 2026" (Medium).

**Patterns:** Hello Interview (patterns/principles/concurrency) · Educative (frequently-asked
patterns) · CodeZym (4 most-important patterns) · AlgoMaster (roadmap + per-pattern guides:
Chain of Responsibility, Command, Memento, Adapter) · `ashishps1/awesome-low-level-design`
(GitHub) · DEV.to (thread-safe parking lot) · CalibreOS (parking-lot case study) ·
CodeJeet (concurrency patterns) · refactoring.guru.
