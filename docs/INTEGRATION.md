# How factbond composes with ontodag, recordstore/Swarm, and loopmarket

Status: analysis, 2026-08-01 (from the ontodag strategy discussion, Peter +
Claude). This document records *fit*, not commitments: factbond is at design
stage, and every integration below is layered composition under written
contracts — no sister project takes a dependency on factbond, and factbond's
machinery never enters anyone's canonical data.

*(Update 2026-08-07: the commitments this document deliberately does not
make now exist elsewhere — the factbond side in `docs/plans/` (notably
`loopmarket-coupling.md`, `records-and-anchoring.md`), the loopmarket side
in `loopmarket/docs/plans/P3-guarantee-coupling.md`. This file keeps its
charter: composition analysis under the sisters' written contracts.)*

Assumed background: `DESIGN.md` here; ontodag's `docs/CONTRACT.md` (the
guarantees a higher layer may rely on) and `docs/PROVENANCE.md` (attribution
without breaking canonical roots).

## 1. The three answers to "why should I believe this?"

The ontodag stack now offers an escalation of trust, and factbond is its
third leg:

1. **It follows** — structural proofs: Merkle inclusion/absence proofs from
   recordstore's canonical trie, `is_below` certificates (ontodag
   `CONTRACT.md` §7).
2. **Someone said it** — provenance: signed assertions and endorsements in
   a parallel store (`PROVENANCE.md`).
3. **Someone will pay if it's wrong** — factbond: a bonded assertion whose
   stake is slashed on successful dispute, and an insurance premium that
   prices the claim's reliability.

Leg 1 attests structure, never world-truth (ontodag's limit L1). Leg 2 makes
the trust decision explicit but reputational. Leg 3 makes it economic. The
three compose: a bonded claim *cites* canonical structure (leg 1) and *is*
an attributed speech act (leg 2) with money attached.

## 2. ontodag is a claim layer (DESIGN.md §6, layer 1)

The design says the claim layer is the most underrated part of the system —
disputes are about wording, so claims must be precise, versioned,
machine-interpretable, template-generated. For knowledge-graph claims,
ontodag provides exactly this by construction:

- **Claim identity** = canonical name + pinned root. Semantic canonical
  form means spelling variants of the same denotation cannot fork a claim
  (`weight(3kg)` and `weight(3000000mg)` are one claimId).
- **"Always a versioned pointer, never 'whatever the database says now'"**
  is ontodag's root-pinning, verbatim: a claim's subject is a record (or
  edge) *at a root*.
- **Temporal scope** (asserted-as-of, validity window) is expressible
  inside the canonical name via dimension values (`time(a..b)`).
- The two claim types map cleanly: `attribute-matches-source` — "the store
  at root R says X" — and `attribute-matches-world` — "X correctly
  describes the world."

## 3. Batch bonding: bond a root, dispute a leaf

One of the founding ideas (batching many statements into one bet) gets a
mechanism for free from content addressing: **a root is a batched claim.**
"Every record under root `abc…` matches the world, confidence 0.93" is one
bondable assertion over millions of facts — and a challenger disputes a
*single record*, localized by a Merkle inclusion proof against that root
(recordstore `prove`/`verify`, queued in ontodag's roadmap). Bulk assertion
is one signature; disputes stay surgical. This is the capital-efficiency
shape §2 of the design hunts for, arrived at from the storage side — and it
is how the bond pool's "auto-assert over whole KB slices" policy
(`DESIGN.md` §7) is implemented without per-claim bookkeeping.

## 4. The assertion layer is ontodag's provenance store plus money

Compare the record shapes:

| factbond assertion (`DESIGN.md` §6.2) | ontodag provenance record (`PROVENANCE.md` §3) |
|---|---|
| claimId | subject (edge/node) + basis root |
| asserter | author key + signature |
| confidence | speech-act metadata (`PROVENANCE.md` §6) |
| bondRef | — (the economic extension) |
| livenessWindow, status | — (status is *derived* from records + clock) |

Same shape; the deltas are `bondRef` and the odds-weighting function that
`confidence` acquires. Consequences, both directions:

- ontodag's provenance record formats should stay **forward-compatible with
  bonding** (carry-the-field-from-day-one, the lesson loopmarket already
  encodes in its offer schema) — recorded in `PROVENANCE.md` §7.
- factbond's `status` (`Asserted/Certified/Contested/Refuted`) is
  recomputable from the assertion + dispute records plus a clock — derived,
  local, never merged, introducing no new convergence problem.
- `Refuted` emits a **correction feed, not corrected databases**
  (`DESIGN.md` §7) — which is ontodag's grow-only stance plus
  retraction-as-speech-act, independently reinvented from the economic
  side. The convergence is evidence both designs cut reality at the joint.

## 5. Structural claims adjudicate for free

For claims *about an ontodag store*, the cheapest rung of the adjudication
ladder (`DESIGN.md` §6.4) is a **proof checker**: "the store at root R
contains/entails X" is settled mechanically by an inclusion/absence proof or
an `is_below` certificate — no jurors, no vote, no evidence problem. Only
`attribute-matches-world` claims escalate to the expensive rungs. An
optimistic oracle over knowledge-graph claims therefore has a materially
better cost structure than one over free-world claims: the entire
matches-source half of the dispute space resolves at the price of a hash
computation.

## 6. The graph layer is an ontodag query — and it approaches a known wall

`DESIGN.md` §6.5 names the open research question: a restricted
claim/implication language where worst-case collateral and price propagation
are polynomial. ontodag is a concrete candidate fragment:

- **Implications** between subsumption claims are `is_below` — polynomial,
  monotone (entailments only grow under merge, so netting computed at a
  pinned root stays sound), fail-closed, and certifiable (§5). "Liquidity
  by generalization" — stakes propagating along implication structure — is
  propagation along the cone structure the store already maintains.
- **Exclusions** — what negRisk actually nets against — are *disjointness*
  claims, which in ontodag is a documented wall whose shape is already
  resolved (disjointness assertions merge as ordinary claims; enforcement
  is local; `get(A, B)` non-empty *is* the violation check). factbond is
  the second independent consumer to approach that wall (the first being
  agent-written stores needing pollution detection), which is exactly the
  evidence shape ontodag's tripwire discipline waits for.

The publishable bridge, stated once: **subsumption-plus-exact-dimensions is
a tractable, canonically-identified, monotone claim/implication fragment for
knowledge-base collateral netting.** Nobody has worked out this fragment for
KB verification specifically (the transcript's own assessment).

## 7. Agents: the shared first customer

`DESIGN.md` §5.5 concludes the natural first customers are AI agents —
consuming thousands of facts per plan, pricing each, filing evidence-backed
disputes at zero psychological cost. ontodag reached the same customer from
the opposite direction (agents-first decision, 2026-08-01: canonical,
addressable, verifiable, attributable knowledge is what agent ecosystems
lack). The composition point is the agent-facing read surface: an ontodag
MCP answer already cites its root, later its certificate — and can
eventually carry **guarantee status** per fact (asserted/certified/
contested, confidence, capital standing behind it), making "how much is this
answer insured for?" a field, not a research project. Machine-to-machine
information insurance and the agents-first knowledge substrate are one
product surface seen from two sides.

## 8. loopmarket: the first structured consumer

loopmarket's roadmap has reserved the slot since P0: `bond`, `oracle`,
`arbitrator` ride in every offer's canonical encoding (carried, unenforced)
and `Ontology.assert_edge` already takes `bond=` — "bonded assertions,
stakes on ⊑ edges, scaled to centrality" is its P3 line item. **factbond is
the mechanism design for that line item**: bond sizing, odds-weighted
disputes, the shared bond pool, the escalation ladder.

The insurance coupling instantiates with unusual precision there:

- A settling loop *relied on* specific catalogue edges — `satisfies` walked
  them; settlement re-verified them. Those edges are exactly the facts
  whose falsity costs the participants money — i.e. **insurable facts with
  natural consumers**. Settlement can auto-attach information insurance on
  the edges it relied on; a payout auto-files a dispute on the edge that
  lied (`DESIGN.md` §7's coupling). Loop participants become the shared
  catalogue's verification workforce without ever thinking about it.
- The pool's loss experience becomes a **per-edge reliability audit of the
  shared catalogue** — which categories, regions and declarers produce
  disputes — feeding loopmarket's P3 "aggregated risk markets and rate
  premia" directly.
- The proof machinery is shared: loopmarket P2 plans on-chain verification
  of offer inclusion under a pinned book root (since 2026-08-07:
  recordstore's canonical-trie inclusion/absence proofs first, POT
  `ForkPathProof` only if the on-chain verifier demands it —
  `loopmarket/docs/plans/proof-fabric.md`); factbond's dispute layer
  verifies claim subjects the same way. One proof path, two consumers.

*(Concretized 2026-08-07.)* Three details graduated from fit to specified
mechanism: **witness edges** — loopmarket settlement instruments
`satisfies`/`is_below` to emit the exact ⊑ edges each settled loop relied
on, pure telemetry that lands before any bond exists and accumulates the
centrality data bond sizing needs; **reliance as the payout ceiling** — the
settlement root proves which paying transactions pinned an edge, so
information-insurance payouts are capped by provable reliance (invariant
F3), which is what makes insurance-arson structurally unprofitable here
first; and **solver bonds as the pool's second customer** — loopmarket's
P2 solver registration bonds are damage-sized escrow of exactly the shape
the bond pool underwrites, so one bond machinery serves both consumers and
the loss experience stays in one place.

## 9. recordstore and Swarm: evidence, roots, feeds

- **Evidence storage** (`DESIGN.md` §6.4): content-addressed, hash-on-chain,
  must remain retrievable for the life of a dispute — Swarm's postage-stamp
  model gives evidence an explicit funded lifetime, and stamp TTL has a
  natural counterpart in dispute windows.
- **Claim subjects**: recordstore roots are the versioned pointers of §2;
  the canonical trie's inclusion *and absence* proofs are the dispute
  layer's rung zero (§5). Swarm's BMT addressing is keccak-based — the
  EVM's native hash — so on-chain verification is mostly existing pieces.
- **The correction feed** (`DESIGN.md` §7) wants to be a signed Swarm feed:
  an owner-signed, followable address carrying `Refuted` events — the same
  primitive ontodag already uses for "latest root," pointed at corrections
  instead.
- **Anchored time is factbond's to build** (ontodag's `PROVENANCE.md`
  assigns it explicitly): liveness windows and dispute deadlines need a
  time source better than local clocks — feed index vs on-chain anchor is
  the open choice, decided in `docs/plans/records-and-anchoring.md`, which
  also owns the `annotations.factbond` schema (status, confidence, capital
  standing) that ontodag's answer envelopes reserved.

## 10. Boundaries (the part that keeps everyone honest)

The composition discipline mirrors ontodag's B1/B2:

- **factbond state never enters canonical knowledge.** Bonds, confidence,
  status, premiums live beside the data (the provenance-store pattern),
  never in it — two stores with identical knowledge and different bonding
  must keep identical roots, or agreement-by-fingerprint dies.
- **One-directional composition.** factbond consumes ontodag's public
  contract (`CONTRACT.md`) like any higher layer; ontodag, recordstore and
  loopmarket never import factbond. loopmarket's P3 *uses* factbond's
  mechanisms; its core model must keep running with no guarantee fabric
  present.
- **Status is derived; only speech acts are shared.** Assertions, disputes,
  endorsements and rulings are signed records that merge by union;
  everything else (status, prices, reserves' views) is recomputable local
  state.

## 11. Worked example: bounties on the science packs (Peter, 2026-09-03)

ontodag-core's four science packs (physics, mathematics, chemistry, biology
— about 1,900 edges as of 2026-09-03) are a ready-made first case, because
the day they were finished a spot check found the error structure that
factbond prices:

- **The claims are already canonical and finite.** Every pack edge is a
  `sub ⊑ sup` pair of canonical names, and the pack is a store with a
  golden root — so §3 applies verbatim: *bond the pack root, dispute a
  leaf*. One signature covers the whole pack; a challenger names one edge
  and localizes it with an inclusion proof.
- **The base rate is measured, and it is stratified.** A random sample of
  50 edges read by a non-expert found no error. A second reading of the
  1,109 edges carried by a *single* independent source rejected 40 (about
  3.6%). Edges carried by two or more independent sources (WordNet + SUMO,
  Wikidata + OpenCyc) were not where the errors were. Each edge's witness
  set is recorded in `build/evidence.tsv`, so **bond size can follow
  evidence class**: a single-source edge is worth a larger bounty than a
  two-source one, and a ruling-only edge (`claude-ruling`) larger still.
  This is the reliance/evidence term of the bond-sizing rule with the
  evidence already in hand, not estimated.
- **The kinds of error are known, so the challenge is bounded work.**
  Sense drift (`indicator ⊑ sign` for a chemical indicator), label
  collision (`clique ⊑ subclass` via the taxonomic rank), a source's own
  slip (`heterozygote ⊑ zygote`, `covariance ⊑ variance`), a coarse ruling
  that is wrong rather than coarse (`chemical-chain ⊑ concept`). A
  challenger knows what to look for; the reward is for looking.
- **Adjudication has a written evidence standard.** An edge is accepted
  when two independent sources entail it and none entails the reverse, or
  when a named ruling accepts it (`UPPER.md` §1, §6). A dispute therefore
  has a mechanical half — *show the sources do not say this*, checkable
  against the extracted views — and a judgement half — *the sources are
  wrong* — which escalates to a ruling. That is the adjudication ladder of
  `DESIGN.md` §6.4 with the cheap rung genuinely cheap.
- **The correction is a speech act, never an edit.** A refuted edge is
  recorded as a `reject` line in the pack's review files, which the next
  build honours; published edges are sticky by construction (`UPPER.md`
  §1), so the refutation reaches readers as the next pack version plus a
  correction record — §4's "correction feed, not corrected databases",
  already how the packs work.

What it would cost to run: a bond per pack root, a bounty schedule keyed
to witness class, and the ruling role (today Peter, or the two-source
rule) as the top of the ladder. What it would buy: a review of ~1,900
edges by people who each know one field, paid per real mistake, with the
whole dispute history merging by union like everything else. The packs
are small enough that the experiment is cheap and large enough that the
3.6% matters — roughly forty wrong edges are still in them by the
measured rate, and the sample says they hide among the single-source ones.
