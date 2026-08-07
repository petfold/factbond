# factbond: records and anchoring

Status: design, 2026-08-07. Decided here: every factbond object is a signed,
mergeable record adopting ontodag `PROVENANCE.md` shapes verbatim, the
economic deltas riding in the namespaced `ext` map (decided 2026-08, lands
with Phase 1); claimId = canonical subject + pinned root, temporal scope
inside the canonical name; status derived from speech acts plus an anchored
clock, never stored-and-merged (**F1**); bonds attach to claim subjects,
never edges (**F2**); bulk assertion = batch root-claims disputed
leaf-by-leaf via inclusion proofs; the correction feed as an owner-signed
Swarm feed of `Refuted` events; the `annotations.factbond` schema. Open
here: the anchored-time mechanism (feed index vs on-chain anchor — deadline
Phase 1), ruling supersession, the payload-subject form, batch slashing
granularity.

This document fixes the data layer under `../DESIGN.md`'s five layers: what
gets written, by whom, signed how, merged how, judged against which clock.
The economics on top — bond sizing, odds, slashing — are
`mechanism-design.md`; what counts as evidence is `evidence-policy.md`; what
the records feed is `insurance-products.md` and `netting-and-reserves.md`;
the shared-anchor consumer on the loopmarket side is
`loopmarket-coupling.md`. Composition constraints: `../INTEGRATION.md`.
Attack coverage: `THREATS.md`.

## 1. Claim records: identity before money

Essentially every real prediction-market dispute is about wording
(`../DESIGN.md` §6.1), so the claim record is the primary defense, and it
must be **adversary-computable**: asserter, challenger, insurer and
adjudicator must derive the same claimId from the same proposition, or
bonds attach to nothing. ontodag gives this for free (`../INTEGRATION.md`
§2): a claim's subject is a canonical name (or `sub ⊑ sup` name pair) **at
a pinned root** — "always a versioned pointer, never 'whatever the database
says now'" — and temporal scope rides *inside* the canonical name as
dimension terms (`time(a..b)`, calendar periods), so validity windows
cannot fork a claim's identity.

A claim record is content, not a speech act: unsigned, deterministic,
content-addressed (decided 2026-08, lands with Phase 1):

| field | meaning |
|---|---|
| `v` | schema version; readers ignore unknown fields |
| `subject` | canonical name / name pair, adversary-computable (`PROVENANCE.md` §3) |
| `basis_root` | the pinned knowledge root the subject is read against |
| `claim_type` | controlled vocabulary: `attribute-matches-source` \| `attribute-matches-world` \| `entity-exists` (`../DESIGN.md` §6.1) |
| `policy_ref` | hash pin of the resolution-procedure document (`evidence-policy.md`) |
| `ext` | namespaced extensions map, empty in v1 |

`claimId` = hash of the canonical encoding of exactly these fields — the
content-address discipline loopmarket uses for `offer_id`. Asserter,
confidence and bond are deliberately *not* in it: one claim, many
assertions. `claim_type` and `policy_ref` *are* in it: the matches-source
and matches-world readings of one subject are different propositions with
different resolution procedures, and conflating them is how basis-risk
disputes are manufactured (T9, `THREATS.md`) — the wording plus its
adjudication procedure is the contract. v1 admits only template-generated
claims over KB entries; free text stays a v2 luxury (`../DESIGN.md` §6.1).

## 2. Assertion, dispute, ruling, endorsement: one format, not two

ontodag's provenance store already is factbond's assertion layer minus
money (`../INTEGRATION.md` §4; `PROVENANCE.md` §7 records the
field-for-field mapping). We adopt those shapes **verbatim** and put the
deltas — `bondRef`, liveness, and the odds-weighting function `confidence`
acquires — in the namespaced `ext` map every provenance record has carried
from day one. Inventing a second format would be pure divergence risk: the
upstream shapes are implemented, signed over content-addressed data
(secp256k1 via the same `bee` package as the feed pointer), keyed
`s/<subject-hash>/<record-hash>` with set semantics, union-merged in the
per-writer deployment shape — "loopmarket's one-book-per-maker shape, same
machinery" (`PROVENANCE.md` §3). The set (decided 2026-08, lands Phase 1):

- **assertion** — `PROVENANCE.md` §3 verbatim: subject, author key, basis
  `knowledge_root`, `origin: asserted|derived`,
  `derived_from: (corpus_root, learner_version)?`, `time?`; plus
  `ext.factbond = {claim_ref, confidence, bond_ref, liveness}`. `claim_ref`
  binds it to a §1 claim (hence to type and policy); `confidence` is
  `PROVENANCE.md` §6's speech-act confidence acquiring its economic
  function — it sets the odds-weighted dispute ratio, in `../DESIGN.md`
  §8's coarse buckets (0.9/0.97/0.99/0.999; game theory:
  `mechanism-design.md`); `bond_ref` points into the shared pool;
  `liveness` is measured against the §4 anchor.
- **dispute** — same envelope discipline, challenger-signed: subject,
  challenger key, basis root, `time?`; `ext.factbond = {assertion_ref,
  bond_ref, leaf?, evidence_refs?}`. `assertion_ref` names the disputed
  assertion by content hash (the odds ratio comes from *that* assertion's
  stated confidence); `leaf = {key, inclusion_proof}` localizes a dispute
  inside a batch root-claim (§5).
- **ruling** — adjudicator-signed: subject, adjudicator key, `dispute_ref`,
  `outcome ∈ {upheld, refuted}`, `rung`, `certificate_ref?` (mandatory at
  the mechanical rung — **F8**), `evidence_refs?`, `supersedes?` (an
  earlier ruling_ref, for reopening on new evidence —
  `mechanism-design.md`'s constitution), `time?`.
- **endorsement** — `PROVENANCE.md` §3 verbatim; with
  `ext.factbond.bond_ref` it becomes co-bonding — capital joining an
  existing assertion (decided 2026-08, lands with Phase 2).
- **retraction** — upstream shape unchanged; factbond's use (withdrawal
  before dispute, and its price) is `mechanism-design.md`'s.

Who signs what: asserters sign assertions, challengers sign disputes,
adjudicators sign rulings; everything merges by union in per-writer stores
under each writer's signed feed, folded by exactly the aggregator loop
loopmarket P1 builds
(`../../../loopmarket/docs/plans/P1-federated-book.md`). Record spam is
admission-by-reference upstream (un-merge the flooder); its economic
pricing — assertion fees — is this system's layer, and sybil statistics
pollution is T2 (primary owner:
`../../../loopmarket/docs/plans/THREATS.md`).

Bonds attach to **claim subjects, never edges** (**F2**). The reason is
upstream and mechanical: ontodag keeps the graph in unique transitive
reduction, so an asserted edge can be pruned while its claim stays entailed
(assert `X⊑A`; `X⊑B, B⊑A` arrives; the edge vanishes, `is_below(X, A)`
stays true — `PROVENANCE.md` §8.1). An edge-attached bond would be orphaned
by a re-routing that changed no knowledge; claim-grain subjects survive
reduction by construction. loopmarket's `Ontology.assert_edge(bond=)` must
therefore resolve its bond to the claim subject, not the stored edge.

None of these records ever enters canonical knowledge (**F6**): identical
knowledge with different bonding must keep identical roots, or
agreement-by-fingerprint dies (`../INTEGRATION.md` §10).

## 3. Status is a derivation, never a column

**F1: "status derived from signed speech acts plus a clock, never
stored-and-merged."** `status(claimId) ∈ {Unasserted, Asserted, Contested,
Certified, Refuted, Expired}` (`../DESIGN.md` §6.2; §7's `Stale` is the
validity-expired case of `Expired`) is a pure function of (the union of
records the reader folded, the anchor reading): no covering assertion →
`Unasserted`; open liveness, no dispute → `Asserted`; liveness expired at
the anchor, no dispute → `Certified`; undecided dispute → `Contested`;
ruling `upheld` → `Certified`, `refuted` → `Refuted`; subject validity
window past the anchor → `Expired`.

Two replicas holding the same records and anchor reading compute the same
status — a conformance test, not a hope (Gate G-REC1). Storing status would
reintroduce the convergence problem the record model just eliminated: only
speech acts merge (by union, order-free); status, prices and reserve views
are recomputable local state (`../INTEGRATION.md` §10). The one genuinely
order-sensitive input is rulings: reopening means several rulings can stand
on one dispute, so derivation totally orders them by (rung, anchor reading,
explicit `supersedes` chain) — a registered open problem below, because
getting it wrong quietly re-creates stored status one level up.

## 4. Anchored time: the decision factbond must make

Every "expired" in §3 needs a clock, and record timestamps cannot be it:
upstream, `time?` is part of the signed claim — "K says it was Tuesday" —
never load-bearing, and `PROVENANCE.md` §3 assigns the upgrade explicitly:
"anchored time (feed index, on-chain anchor) is the upgrade path, and its
natural customer is factbond's liveness windows, so it belongs to that
contract." ontodag will not build it. Two candidates:

- **On-chain anchor (Gnosis).** Windows in block numbers: ~5.15 s blocks,
  gas ~0.2 gwei in xDAI, sub-cent transactions (gnosisscan.io/gastracker;
  https://www.gnosischain.com/). "After" is provable by embedding a recent
  block hash in a signed record; "before" is the dispute transaction's own
  inclusion. The bond pool contract lives on this chain anyway and cannot
  read Swarm feeds, so every window that releases or slashes money is
  enforced by the machine holding the money. Anchoring a root is "32 bytes
  in a contract, keccak-native BMT addressing, waits only on a consumer"
  (ontodag ROADMAP, 'Parked'). Cost: a chain touch per window-crossing
  event, batched by §5's root-claims.
- **Feed-index anchor (Swarm).** An owner-signed heartbeat feed; elapsed
  time = sequence-index delta. Zero gas, chain-free deployments; but the
  feed owner *is* the clock (stalling freezes every liveness expiry — a
  certification denial-of-service, T4-adjacent), feed lookups cost seconds
  (loopmarket's live triangle: ~51 s end-to-end on a Gnosis-mainnet light
  node), feed `compare_and_set` is best-effort, and a feed head is a
  single-owner chunk erasure coding cannot protect — only ~4× neighbourhood
  replication guards it.

What hangs on the choice: liveness expiry (`Asserted → Certified`), dispute
and appeal windows (**F4**'s fail-closed caps need a clock to fail closed
against), insurance validity (`insurance-products.md`), the evidence
stamp-TTL rule (§7), and — the second consumer — loopmarket's offer-expiry
and tombstone judging in the federated book
(`../../../loopmarket/docs/plans/P1-federated-book.md`): one design, two
consumers, one mechanism. Working lean, stated as a lean: money-bearing
windows want the on-chain anchor, because enforcement and clock then share
a trust domain; feed-index survives as advisory ordering. Registered open
problem with a hard deadline: **decided before any Phase 1 stake is live**
(Gate G-REC3).

## 5. Batch root-claims: bond a root, dispute a leaf

Content addressing gives batching for free: **a root is a batched claim**
(`../INTEGRATION.md` §3; ontodag `CONTRACT.md` L1 extension: "bond millions
of facts in one assertion, dispute one record via an inclusion proof").
"Every record under root R with key-prefix P matches the world, confidence
0.93" is one §1 claim whose subject is the coverage pair `(R, P)` — a new
subject form this document owns, sibling to upstream's sketched
`payload(name, content-hash)` form — and one §2 assertion: one signature,
one bond reference. This is how the pool's auto-assertion policy ("all OSM
opening_hours in Prague, confidence 0.93, bond 0.5 DAI each" —
`../DESIGN.md` §7) works without per-claim bookkeeping — the
capital-efficiency shape `../DESIGN.md` §2 hunts for.

Disputes stay surgical: `leaf = {key, inclusion_proof}` localizes one
record under the bonded root. The proof machinery is shipped, not planned:
recordstore v0.16.0 `prove(key)` returns a self-describing envelope
(`{format: "recordstore-trie-proof", version: 1, addressing, root, key,
present, nodes, value}`) and module-level `verify_proof(proof, root)`
checks it with **no store access**; because the trie encoding is canonical
a key has exactly one possible location, so **absence is provable too** — a
dispute claiming the record isn't even under the asserted coverage settles
the same way. Per-leaf status derives from the covering batch assertion
unless leaf-specific records override it: a leaf dispute contests that
leaf, not the root claim's other millions of leaves (Gate G-REC5).

Every `attribute-matches-source` dispute — batch or single — terminates at
the mechanical proof-checker rung (**F8**): an inclusion/absence proof or
an `is_below` certificate, verified by anyone holding 32 bytes; no jurors,
no evidence problem (`../INTEGRATION.md` §5). Only matches-world claims
reach the expensive rungs. How many leaf refutations exhaust a root bond —
per-record density vs whole-root stake — is `mechanism-design.md`'s; the
record shape carries the density field so ids don't churn when it lands.

## 6. The correction feed: an oracle output, never a corrected database

`Refuted` cannot fix Wikidata. It emits an event on the **correction
feed** — an owner-signed Swarm feed (the same primitive ontodag uses for
"latest root", pointed at corrections — `../INTEGRATION.md` §9) carrying
`{v, claimId, subject, basis_root, ruling_ref, adjudicated value?, evidence
hashes, anchor reading}` per event (decided 2026-08, lands with Phase 1).
The system's output is an **authenticated correction feed, not corrected
databases** (`../DESIGN.md` §7); the last mile is social, and every
consumer document must say so.

Two honesty points. The feed is a *cache of derivations*, not an authority:
trust roots in the cited ruling signatures, which consumers re-verify —
anyone can republish a correction feed by folding rulings, and readers
choose feeds as they choose provenance stores to merge. And the payload
should suit ontodag's proposed `reclassify` operation (retraction +
motivating evidence + keep-list in one operation group — EVOLUTION.md §5, a
discussion draft: "the why of a retraction can be certifiable") so KB-side
consumers act mechanically — but that operation **does not exist yet**; we
track it upstream and commit only to evidence hashes plus the adjudicated
value, not to an unbuilt API's argument shape.

Operational fragility, named: a feed head is a single chunk — no erasure
protection, ~4× neighbourhood replication on a thin network (4,270
reachable full nodes in January 2026, staking heavily concentrated in
Finland —
https://blog.ethswarm.org/foundation/2026/state-of-the-network-january-2026/).
Mitigations: a self-hosted pinning node for the feed, and — if §4 resolves
on-chain — anchoring the latest event hash in the transaction that settles
the ruling. Bee 2.7.0 made feed resolution deterministic across
legacy/wrapped formats (`Swarm-Feed-Resolved-Version` response header —
https://blog.ethswarm.org/foundation/2026/bee-2-7-0-release); readers
should tolerate both formats and log the header for audit.

## 7. Evidence storage: retrievability is part of admissibility

Evidence goes to content-addressed storage with only hashes in records and
on chain (`../DESIGN.md` §6.4; `../INTEGRATION.md` §9). Swarm's postage
model gives evidence an explicitly funded lifetime, and that lifetime is a
correctness rule, not an ops detail: **stamp TTL ≥ remaining dispute window
plus appeal allowance, checked at filing; evidence that cannot prove that
much funded lifetime is inadmissible** (decided 2026-08, lands with
Phase 1). When TTL hits zero the data is garbage-collected and gone forever
(https://docs.ethswarm.org/docs/concepts/incentives/postage-stamps/);
evidence expiring mid-appeal is indistinguishable from evidence that never
existed, so the rule fails closed. Batch expiry is visible tooling-side
(Swarm-CLI v3.2.0 surfaces stamp expiration dates — May 2026 dev update).

Who pays: the filer stamps what they file — the party whose money depends
on a blob's persistence funds it; and because **top-up is permissionless**
(anyone with BZZ can top up anyone's batch —
https://blog.ethswarm.org/foundation/2022/the-mechanics-of-swarm-networks-storage-incentives/),
an insurer with open exposure or an appellant can keep adverse evidence
alive without the filer's cooperation. Escalation extends windows, so
whoever escalates tops up. Costs are a nuisance, not a moat: a depth-17
batch (the minimum) runs ≈ 2 xBZZ/year at the 24,000 PLUR/chunk/block
reference price — cents to well under $1/year at 2026 BZZ prices — so
storage-cost griefing is weak; the real griefing surface is adjudicator
attention (T4, `THREATS.md`), and per-policy evidence size caps live in
`evidence-policy.md`. Blobs above chunk size carry erasure coding
(Reed–Solomon per 128-chunk group: Medium 9 parities / 7.6% overhead
tolerating 1% chunk loss; Strong 21 / 19.6% / 5% —
https://docs.ethswarm.org/docs/concepts/DISC/erasure-coding/, theory arXiv
2409.01259; production-usable as of Bee 2.7+); single-chunk objects get no
parity benefit — one more reason evidence *records* are cheap pointers and
the blobs they name are the funded objects. A stamp buys bytes, not
meaning: retrievable evidence can still be fabricated — admissibility
weights, revocation, and the generative-era arms race are entirely
`evidence-policy.md`'s subject.

## 8. Envelopes, pins, and the `annotations.factbond` schema

Certificates and proofs reuse ontodag's envelope policy verbatim:
self-describing JSON `{format, version, root, subject, evidence}`, evidence
as raw hex-encoded blobs, verification by hash-chain recomputation over
those exact bytes, never re-serialization; format-name versioning; unknown
formats ignored; transport opt-in (ontodag `CONTRACT.md` §7). No
factbond-specific proof format exists or is planned — one proof path,
shared with `../../../loopmarket/docs/plans/proof-fabric.md`.

Every factbond record pins its interpretation context:
`ext.factbond.{contract_version, registry_version}` beside the basis root,
because claim subjects are canonical names whose parametric semantics live
in the dimension registry — the registry participates in canonical
reduction, `is_below` certificates already pin `REGISTRY_VERSION`, and a
mismatched verifier refuses. This mirrors loopmarket's planned four-element
pin discipline (**U10**: verifiers refuse on mismatch *or absence*); a
record with absent pins is unverifiable, not grandfathered.

The one agent-facing surface factbond owns is the `annotations.factbond`
namespace in ontodag answer envelopes — reserved upstream from day one
(`CONTRACT.md` §2's worked example is `annotations.factbond = {status,
confidence, capital}`; the map ships empty in v1, "guarantee status rides
here later without reshaping anything" — `AGENT_SURFACE.md` §1, §8).
Schema v1, defined here (decided 2026-08; `status`/`confidence` land with
Phase 1, `capital` lands with Phase 2):

```
annotations.factbond = {
  v: 1,
  status:     Unasserted|Asserted|Contested|Certified|Refuted|Expired,
  confidence: stated odds bucket of the covering assertion (0.9|0.97|0.99|0.999),
  capital:    { bond, insured_open, payout_cap },   # capital standing
  basis:      { provenance_roots, anchor: {kind, reading}, record_refs },
  policy_ref: hash pin of the governing resolution procedure
}
```

The annotation is a cache of a §3 derivation, never a source of truth:
every field is recomputable from `basis` (**F1**), unknown namespaces are
ignored by readers (upstream rule), and no field may be rendered as
"true" — `Certified` is a process fact (**F7**). `capital.payout_cap` is
the fail-closed per-claim cap **F4** requires surfaced to consumers before
they rely; how it is set is `netting-and-reserves.md`'s business.

## Gates

- **G-REC1 (Phase 0/1 exit).** Status derivation is replay-invariant: the
  same record set folded in ≥4 gossip orders, plus one independently
  re-implemented derivation, yield byte-identical status maps at the same
  anchor reading. Divergence blocks release.
- **G-REC2 (Phase 1).** Scorched-earth follower: a fresh client holding
  only the correction-feed owner address and a claimId retrieves a
  `Refuted` event and verifies the full chain — feed signature, ruling
  signature, certificate or evidence hashes — with no other state.
- **G-REC3 (before first live stake).** The §4 anchored-time decision is
  made, written here, and enforced: zero wall-clock reads in status
  derivation (mechanically checkable); every Phase 1 window denominated in
  the chosen anchor.
- **G-REC4 (Phase 1).** The stamp-TTL rule is enforced at filing: evidence
  whose batch TTL < dispute window + appeal allowance is refused; one
  calendar experiment (shared with loopmarket P1's postage-expiry work)
  confirms GC behavior matches the assumed TTL semantics.
- **G-REC5 (Phase 1).** Batch round-trip at scale: bond one root covering
  ≥10⁴ records, dispute one leaf by inclusion proof, verify with
  `verify_proof` and no store access, confirm the other leaves' derived
  status unchanged; repeat with an absence proof.
- **G-REC6 (Phase 1 entry).** Record schema v1 frozen; later changes bump
  `v` with old-record read paths kept — loopmarket's U2 discipline applied
  before the first record is signed.

## Open problems

- **Anchored-time mechanism (this work package; deadline Phase 1; shared
  with loopmarket P1).** Feed-index vs on-chain anchor per §4: cost,
  granularity and trust profiles differ; factbond windows and loopmarket
  offer expiry must land on one mechanism, and the choice decides whether
  window enforcement shares a trust domain with the bond pool. Blocked on
  nothing; blocking every liveness semantics.
- **Ruling supersession under union merge (this work package, with
  `mechanism-design.md`).** Reopenable rulings mean several rulings can
  stand on one dispute after a fold. The derivation's total order — (rung,
  anchor reading, `supersedes` chain) — must be proven confluent, or stored
  status sneaks back in disguised as "the latest ruling."
- **Payload-subject form (this work package, tracked upstream).** Claims
  about record *payloads* (attribute values, not edges) need the
  `payload(name, content-hash)` subject form `PROVENANCE.md` §3 leaves
  sketched-and-unimplemented. Phase 1's narrow domain (OSM opening hours)
  needs at least this form worked; the §5 coverage-pair subject defined
  here must stay consistent with whatever lands upstream.
- **Batch slashing granularity (`mechanism-design.md`).** Whether a root
  bond is per-record density ("0.5 DAI each") or whole-root stake, and how
  many leaf refutations exhaust it, is mechanism economics — but the record
  fields carrying density are fixed here first so batch-claim ids don't
  churn when the mechanism lands.
- **Correction-feed payload vs `reclassify` (this work package, tracked
  upstream).** ontodag's retraction+evidence+keep-list operation is a
  discussion draft; committing the feed payload to its argument shape now
  couples us to an unbuilt API, committing to less than evidence hashes +
  adjudicated value strands mechanical consumers. Revisit at each upstream
  EVOLUTION.md status change.

## What this document does not promise

**Certified ≠ true (F7).** Every status these records derive — including
the one served through `annotations.factbond` — means "nobody found it
profitable to dispute this, under this adjudication procedure, at these
bond and subsidy levels" (`../DESIGN.md` §12), never world-truth.
Confidence buckets are asserter-quoted odds, and premiums are prices under
capital constraints and attack, not probabilities. An anchor reading orders
records against a chain or a feed; it does not timestamp the world — it
bounds when a dispute may be filed, not when a shop actually closed. A
stamp keeps bytes retrievable; it certifies nothing about what the bytes
depict. And a green run of every gate above certifies record-layer
mechanics only — replay-invariance, proof round-trips, TTL enforcement —
not the economic model the records feed: parameter, adversary and model
risk live in `phase0-simulation.md` and `THREATS.md`, and a green
simulation certifies nothing about model risk either.
