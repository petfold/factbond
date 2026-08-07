# factbond: evidence policy — admissibility as data

Status: design, 2026-08-07. Decided here: evidence classes live in a
versioned catalogue with weights and revocation status — admissibility
changes are data edits, never code releases; per-domain hash-pinned policy
documents, referenced from every claim's resolution procedure and every
loopmarket offer's `oracle` field; the five-slot oracle roster with its
2026 rulings; demote-fast / promote-slow; a policy bump never rebinds old
claims. Open here: weight semantics, the demotion authority's constitution,
fabrication-cost measurement, the countersign audit rate, per-source
curation for zkTLS.

`DESIGN.md` §11.1 named the evidence-admissibility spec as one of the two
hardest open problems and prescribed its shape — "a versioned, per-domain
*policy document*, not code." This is that work package. Companions:
`mechanism-design.md` (the adjudication constitution these policies
escalate into), `insurance-products.md` (the products these classes gate),
`records-and-anchoring.md` (where evidence bytes live, and for how long),
`phase0-simulation.md` (consumes §4's fabrication table), `THREATS.md`
(T4 adjudication capture & dispute griefing, T5 insurance arson, T9
basis-risk disputes — all primary here). This document is the **primary
home of the oracle roster**; loopmarket's
`docs/plans/P3-guarantee-coupling.md` consumes it and mirrors nothing
without naming this owner.

## 1. The principle: admissibility is data, not code

Evidence quality is a moving target — a timestamped shopfront photo was
evidence in 2020 and is nearly worthless in 2026 (`DESIGN.md` §5.2) — and
encoding admissibility in adjudicator code means a code release per camera
exploit. The opposite failure is juror discretion without a text: Kleros's
record shows jurors converge on the *letter of the referenced policy*
(Proof-of-Humanity rejected the Gitcoin founder's profile over camera
angle), so discretion without a precise policy converges on pedantry over
whatever text exists. Both point the same way:

**Evidence classes form an ontology — catalogue data with weights and
revocation status** (decided 2026-08, lands with Phase 1). Each class is a
node carrying its trust root (signer allowlist, operator identity,
proof-system version), its admissibility weight, its revocation state, and
its corroboration rules. The Nikon-style downgrade (§5) and the zkTLS-style
upgrade become catalogue edits published as pinned roots — the shape
ontodag already uses for unit packs (mergeable graph data, per-release
roots). The catalogue is factbond data, never canonical knowledge: its own
store, its own root (F6 — "factbond state never enters canonical
knowledge"; ontodag's O1 derived-artifact discipline). And **evidence-class
reliability is itself insurable and bondable**: "attested-capture
certificates of fleet X have a loss rate below y" is an ordinary bonded
assertion — the system prices its own instruments, and per-class loss
experience (§4) becomes the weight-setting data. The catalogue's first
pinned root is the oracles-evidence survey's 2026 robustness ranking, whose
verdicts §3 and §4 carry in full.

One class sits outside the catalogue because it needs no weight:
**structural certificates**. F8 — "structural (matches-source) claims
settle by certificate/inclusion-proof only." ontodag's `is_below`
certificates and recordstore's trie inclusion/absence proofs are shipped
and pin their `REGISTRY_VERSION`; the entire matches-source half of the
dispute space settles at hash-computation cost (`INTEGRATION.md` §5), no
trust root beyond the pinned root itself. Certificates are rung zero of
every escalation path below; the roster serves the matches-world half.

## 2. The policy hash is the contract

The empirical record is unambiguous about the cheapest attack on any
adjudication system: **resolution-criteria ambiguity**. Augur's chronic tax
was the "invalid market"; Kleros's was photo-angle literalism; UMA's was
the $160–237M Zelenskyy "wearing a suit" market, resolved NO twice against
the photographic record, YES-side disputers slashed both times. None of
these was an evidence-quality failure — the evidence was fine; the *text*
was contested. The policy document is the real contract, and it gets
contract discipline:

- **Per-domain policy documents, hash-pinned** (decided 2026-08, lands with
  Phase 1). A policy names, for one claim domain: the admissible evidence
  classes by catalogue reference, the weight each carries at each
  escalation rung, the live inputs consulted at ruling time (revocation
  lists, allowlists — §5), and the escalation path with its terminal rung.
  Policy bytes share evidence bytes' storage discipline
  (`records-and-anchoring.md`: stamp TTL ≥ dispute window).
- **Every claim's resolution procedure references (domain, policy hash).**
  `DESIGN.md` §6.1 reserves the slot; this fills it. v1's template-only
  claim admission is the same defense from the claim side.
- **Every loopmarket offer's `oracle` field carries the policy hash**
  (decided 2026-08; the field enforcement lands with loopmarket's v2
  record bump, the fabric behind it with P3 — loopmarket's
  `docs/plans/P3-guarantee-coupling.md`). The field has ridden in the
  offer's canonical encoding since P0 precisely so this lands without
  churning offer ids. An offer naming a policy hash has agreed, at
  publication time, on what will count as proof of its own performance —
  the ambiguity attack closes before the leg settles.

The first instance is the Phase 1 pilot domain: OSM `opening_hours` in one
city (`DESIGN.md` §10) — high error base rate, cheap physical verification,
crisp evidence, and small enough that the ambiguity red-team gate (§Gates)
is affordable before any stake moves.

## 3. The oracle roster

Order and rulings follow the oracles-evidence survey's recommendation:
countersign → locker → digital-proof → attested-photo → location. Each type
is a resolution procedure over catalogue evidence classes; the table is the
normative summary, the subsections carry the why.

| type | witness | 2026 ruling | fails to |
|---|---|---|---|
| countersign | both counterparties, staked | default; optimistic; value-bounded; audited | collusion (bounded), coercion |
| locker | operator-signed IoT event | admit via zkTLS over tracking APIs; no partnership | operator error/corruption |
| digital-proof | zkTLS / signed feeds | parametric-first where a canonical feed exists | source-site falsehood |
| attested-photo | attested capture device | Truepic-class required; bare C2PA corroboration-only | per-model exploits until revoked |
| location | PoL networks | slot carried, **not implemented 2026** | everything, today |

**Countersign — the default.** The optimistic pattern in miniature: both
parties silent past the liveness window = confirmed; a disagreement — not a
vote — opens the dispute path. It inherits the happy path that makes
optimistic systems cheap (~99% of UMA assertions since 2021 settle
undisputed) and is generative-AI-irrelevant: no media, only signatures. Its
one failure mode is collusion, and the defense is structural: **a
countersigned event never unlocks more value than both parties have at
risk** (escrow and bonds), so a fabricated handover is at best a transfer
between the fabricators, minus fees — the by-construction shape of
loopmarket's wash-loop inequality (U13's spirit). Pool-funded random audits
price the residual; the audit rate is a Phase 0 parameter (§Open problems).

**Locker — operator-signed IoT events.** Parcel-locker networks emit
timestamped lifecycle events — InPost's ShipX API and webhooks carry
creation, deposit-in-locker, and collection confirmed by a unique
QR/collection code; Amazon Hub, DHL Packstation and Quadient expose
equivalent streams. The locker is a centralized but *disinterested* machine
witness: deposit ≈ maker performed, code redemption ≈ taker accepted.
Ruling: admit via **zkTLS over the operator's tracking API or page, no
business partnership needed** — the cheapest machine witness that exists
today. Limits stated in the policy text, not discovered in disputes: the
operator can lie or err (wrong parcel in the cell), and the event attests
*handover*, never contents or quality — the contents residue routes to
countersign or attested-photo.

**Digital-proof — zkTLS, signed feeds, parametric-first.** zkTLS is the one
class with production SDKs in 2026: Reclaim (proxy-witness, 2–4s mobile
proofs, 889 data sources, a claimed break probability of 10⁻⁴⁰ in its own
security analysis), zkPass (hybrid proxy+MPC), Opacity, TLSNotary. The
transport is strong; the caveat is inherited honesty — a zkTLS proof
establishes *what a website said* — so admissibility is granted **per
source, not per protocol**: each domain policy carries a source allowlist.
Where the source is canonical for the claim — flight status, parcel
tracking, on-chain state — the doctrine is **parametric-first**: settle
automatically on the feed with no dispute layer, the Etherisc flight-delay
pattern (Chainlink-fed FlightStats, ≥45-minute trigger, policies in USDC on
Gnosis Chain — the chain loopmarket P2 targets). Parametric triggers
eliminate adjudication but concentrate all risk in the data pipeline; the
trade is taken only where the feed is canonical — the reason
`insurance-products.md`'s parametric convenience product exists separately,
with no epistemic claim.

**Attested-photo — attested capture required.** The 2020 photograph is dead
as standalone evidence. C2PA in 2026: version 2.1 is ISO-ratified, hardware
signing ships broadly (Leica, Sony, Nikon, Canon flagships; Google Pixel
signs every native-camera photo by default; Apple announced for iOS 20,
fall 2026) — and the trust root is *revocable in fleets*: in September 2025
an AI-generated image was injected via multiple-exposure mode into a
validly signed Nikon Z6III NEF, and Nikon revoked **all** Z6III
certificates and suspended its Authenticity Service. Stripping is trivial
(any re-encode), strip-and-re-sign attacks exist, the analog hole is
unsolved; Microsoft's February 2026 media-integrity report concedes
stripping cannot be prevented. Ruling: **bare C2PA is corroboration only**,
under a signer allowlist with live revocation checking, never sufficient
alone. The bar for a photo *oracle* is **Truepic-class attested capture** —
device attestation before capture, hardware-keystore signing,
secure-enclave timestamps, sensor-noise fingerprints binding photo to
device — already sold commercially for insurance virtual inspections. Even
that is per-model breakable (the Nikon precedent), which is why live
revocation is load-bearing and §5 exists.

**Location — the slot is carried, not implemented.** No 2026
proof-of-location network is person-grade: Witness Chain triangulates
signed-UDP round-trip times into city-level confidence regions for DePIN
*servers*; GEODNET's ~3,000+ GNSS reference stations sell positioning
correction, not identity-bound presence; FOAM's zone-anchor Presence Claims
are the strongest cryptographically and cover about a dozen zones. Phone
GPS is trivially spoofable, inadmissible alone. The roster carries the slot
the way loopmarket has carried `bond`/`oracle`/`arbitrator` since P0 — in
the schema, unenforced — with a named tripwire: revisit when a network
offers identity-bound, tamper-resistant presence at useful coverage.

## 4. Fabrication economics

The attack to model first is not tribunal capture but the
**honest-looking fraudulent claimant** (`DESIGN.md` §5.2): it scales as
thousands of small independent attacks, and **a $100 payout is a $100
bounty on fabricating evidence**. The policy's job is to keep every class's
fabrication cost above the payout it can unlock; F3 — "indemnity — payout ≤
provable reliance, payout-cap proxy where reliance is unprovable" — caps
the bounty, and F4 — "reliance-bounded adjudication — final rung integrity
cost ≥ aggregate open reliance, per-claim insurance caps fail closed" —
makes the caps fail closed when the inequality cannot be shown.

| class | fabrication route | 2026 marginal cost | trend | policy consequence |
|---|---|---|---|---|
| countersignature | corrupt the counterparty | ≥ counterparty's at-risk stake + audit slashing | stable (no media) | sole evidence up to the escrow bound |
| operator IoT event | operator insider / compromise | high, concentrated in one operator | stable | sole evidence below per-operator caps |
| zkTLS transcript | break proof system, or corrupt source | proof break ~nil (Reclaim claims 10⁻⁴⁰); source corruption varies | per-source | sole evidence per allowlisted source |
| attested capture | per-device-model exploit | expensive to find; ~zero to reuse until revoked | revocation latency is the binding parameter | sole evidence with live attestation + revocation check |
| bare C2PA manifest | strip-and-re-sign; injection; analog hole | near zero | falling | corroboration only |
| unattested media, unstaked testimony | generative tooling | ~zero | falling | dispute *input* to a staked rung only |

The quantitative population of this table — cost estimates with sources and
dates — is a Phase 0 deliverable: `phase0-simulation.md`'s adversary
playbooks consume per-class fabrication cost as a declining curve over
time, and the policy review cadence is tied to generative-media capability
jumps as a **scheduled decision, not a reaction**. A green cell today says
nothing about next year; that is the whole reason admissibility is data.

## 5. The downgrade path

The Nikon incident is the design precedent: one exploit, one act, an entire
fleet's certificates gone. The machinery must absorb that shape without a
code release and without rebinding history.

- **Who demotes.** Each domain policy names its maintainer key(s); a
  demotion is a signed catalogue edit setting the class's revocation or
  downgrade status. Maintainer appointment, removal, and abuse handling
  belong to the adjudication constitution (`mechanism-design.md`) — written
  before the first dispute; capture of the demotion authority is a
  T6-adjacent risk logged in `THREATS.md`.
- **Demote fast, promote slow.** A demotion binds every ruling not yet
  issued — including open disputes — the moment it is published: fail
  closed. A promotion waits out a review window during which it is
  challengeable as an ordinary bonded assertion. A wrong demotion costs
  convenience; a wrong promotion is an open fabrication bounty.
- **Live inputs resolve the mid-dispute tension.** A policy pins *rules*,
  and the rules name *live inputs*: "admissible if the capture certificate
  is valid and unrevoked **at ruling time**" is stable policy text over
  changing revocation data — the X.509 shape (stable policy, live CRL). A
  claim pinned to policy v1 does not keep admitting Z6III photos after the
  fleet revocation, though its policy hash never changes.
- **Closed rulings never rebound — but they can reopen.** A past
  certification whose evidence class is later demoted keeps its status (F1
  — "status derived from signed speech acts plus a clock, never
  stored-and-merged"). The fleet revocation is, however, exactly "evidence
  that did not exist at ruling time," so it qualifies for the reopening
  path (`mechanism-design.md`; precedent: Nexus Mutual's bZx claim, first
  denied, then reversed and paid ~$31K after the post-mortem).
- **The reserve treats a demotion as a correlated shock.** Every open
  insurance position whose certification relied on the demoted class is one
  exposure cluster; per-cluster caps (`DESIGN.md` §8,
  `netting-and-reserves.md`) stop new sales into the cluster immediately —
  F4's fail-closed clause at fleet scale.

## 6. Versioning

- **Policy documents are content-addressed.** A version *is* a hash;
  "current" is a signed pointer (the same Swarm-feed primitive as the
  correction feed, `INTEGRATION.md` §9); the change history is the feed's.
- **Claims pin the policy version.** A claim's resolution procedure names
  (domain, policy hash) at creation; adjudication runs under that hash plus
  the live inputs it names (§5), forever.
- **A policy bump never rebinds old claims.** New claims reference the new
  hash; old claims resolve under theirs. Nothing else is compatible with
  bonded assertion — an asserter priced their bond against a specific
  contract, and moving the contract under an open bond is expropriation.
- **Policy edits are speech acts.** Signed, attributed, merged by union,
  acceptance as reader policy — factbond's provenance discipline applied to
  the policy layer itself.

## Gates

- **Policy lint (Phase 1, blocks pilot launch).** The OSM `opening_hours`
  pilot policy machine-checks clean: every claim type has a terminating
  escalation path; every referenced evidence class exists in the catalogue
  with a status; no rung both admits and refuses a class; every live input
  is named with its source.
- **Ambiguity red-team (Phase 1, blocks real stakes).** ≥20 adversarial
  fixtures against the pilot policy (Augur-invalid-shaped,
  photo-angle-shaped, wearing-a-suit-shaped); two independent adjudication
  panels rule identically on **all 20**. A divergence fixes the text and
  reruns the full set — the threshold never moves.
- **Fabrication-bound check (Phase 2, blocks insurance sales).** For every
  class admissible as sole evidence, a sourced, dated fabrication-cost
  estimate exceeds the class's per-claim payout cap; a failing class drops
  to corroboration-only. No failing policy backs a sold hedge.
- **Revocation drill (Phase 2).** A simulated Nikon-shaped fleet revocation
  runs end-to-end in the Phase 0 harness: demotion reaches all open
  adjudications before their rulings; the affected exposure cluster is
  identified and capped; at least one prior ruling traverses the reopening
  path.
- **Roster sync (continuous).** loopmarket's `P3-guarantee-coupling.md`
  mirror of the roster carries full columns and names this document as
  primary owner; divergence between the copies blocks release of either.

## Open problems

**Weight semantics** (this work package, Phase 0→1). Are class weights
ordinal ranks (sole-evidence / corroboration / dispute-input) or cardinal
multipliers feeding the reserve's premium math? Cardinal invites false
precision — the reason confidence buckets are coarse (`DESIGN.md` §8) —
but the reserve's correlated-shock model may need more than three levels.
Start ordinal; revisit with real per-class loss data.

**The demotion authority's constitution** (`mechanism-design.md`). Who may
demote, how maintainers are removed, and how an emergency demotion is kept
from becoming a censorship lever — the emergency brake is itself a capture
vector, and it must be constituted with written removal rules before the
first dispute, not improvised during one.

**Fabrication-cost measurement** (`phase0-simulation.md`). The §4 numbers
decay continuously; a measurement instrument is needed — candidate:
standing red-team bounties per class, whose claim rate *is* the estimate.
Until one exists the table is expert judgment with dates on it.

**The countersign audit rate** (`phase0-simulation.md`). The random-audit
frequency that keeps collusive countersigning unprofitable at a given
escrow bound is a simulation output, not a guess; it interacts with T5
(arson via fabricated legs) and must be set before countersign backs
insured claims.

**Per-source curation for zkTLS** (per-domain policy documents). zkTLS
admissibility is per-source, so someone curates each domain's source
allowlist — the same authority problem as demotion, one level down.
Whether source entries should themselves carry bonds ("this feed is
canonical for flight status") is open.

## What this document does not promise

F7 — "certified ≠ true on every surface" — and this is a surface. An
admissible evidence bundle bounds dispute outcomes *under a pinned policy
version*; it is not ground truth, and every policy document carries that
sentence on its face. Class weights are not probabilities, and premiums
derived from class loss experience are prices under capital constraints
and attack, not measurements of reality. The §3 rulings are a 2026
snapshot whose robustness claims decay — which is the reason admissibility
is data, not a reason to trust the snapshot. A green revocation drill
certifies the drill's own model of a fleet event, nothing about the next
real one. And rung zero's certificates attest structure, never truth
(ontodag's L1): a flawless inclusion proof of a wrong record proves only
that the record was there.
