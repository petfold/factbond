# factbond on ontodag: the obvious structural consumer (Peter, 2026-09-20)

Status: direction, one paragraph from Peter at the end of the 2026-09-19
session; not started. Companion to `domain-choice.md` (POI liveness for the
matches-world rung) — this is the matches-source rung's first domain.

## Why it is obvious

- **The assertion layer already exists.** ontodag's provenance store is
  factbond's record set minus money (`INTEGRATION.md` §4;
  `records-and-anchoring.md` §2 adopts its shapes verbatim, adding
  `ext.factbond = {claim_ref, confidence, bond_ref, liveness}`).
- **Disputes settle by certificate.** A claim `X ⊑ A` at a pinned root is
  decided by `is_below` — rung 0, F8, cents to adjudicate, no evidence
  problem, no discretion (`INTEGRATION.md` §5). The expensive half of the
  ladder is never invoked.
- **The base rate is measured, not guessed.** ontodag-core's second
  reading rejected ~3.0 % of the single-source edges across the domain
  packs (`ontodag/docs/CORE.md`; ontodag-core `UPPER.md` §9). That is a
  planted-error prior with real provenance — the one number the Phase-0
  plan (§3) says must be measured at snapshot time, already measured.
- **The subjects are adversary-computable.** A pack version's root pins
  every edge; the claim record of `records-and-anchoring.md` §1 (subject,
  basis root, claim type `attribute-matches-source`, policy) hashes the
  same for everyone.
- **Bonds attach to claim subjects, never edges (F2)**, and ontodag's
  transitive reduction is exactly why: an asserted edge can vanish while
  its claim stays entailed. `Ontology.assert_edge(bond=)` in loopmarket
  must resolve to the claim subject.

## The shape

1. **Batch root-claims, disputed at the leaf** (`records-and-anchoring.md`
   §5): one assertion per pack version — "every edge under root R holds"
   — with one bond, at a confidence the pack's reading history earns
   (v6 packs with two readings higher than v2 packs with one); a dispute
   names a leaf with its inclusion proof and an `is_below` certificate.
   Per-edge assertions would cost 3,649 × (fee + bond) on chain for the
   economics pack alone; one root-claim costs one.
2. **The pool as asserter over packs, the readings as the refusal
   record**: what a second reading rejected is what the pool declines to
   cover, and refusal is signal.
3. **The consumer edge is loopmarket's clearing**: a cleared loop relied
   on the edges `satisfies` walked; the coupling's reliance proof
   (`loopmarket-coupling.md` §3) is exactly this claim family, so bonding
   pack roots is the first half of clearing-attached insurance.
4. **The harness cell**: `attribute-matches-source` facts with the 3 %
   prior, verification cost ~0 (a certificate), adjudication cost ~0
   (rung 0), drift ~0 (a pinned root does not rot; a *new* root is a new
   claim) — the degenerate cell where every panel should pass trivially
   and the calibration anchor (~1–2 % disputes) is the interesting number.
5. **The editor's own bond**: `domain-choice.md` §5 thread 3 (the
   reputation-first plugin) applies here first — an ontodag contributor
   asserting an edge at a confidence, scored on the calibration ledger,
   sponsored by the pool until they hold stakes.

## First concrete step (next session)

`factbond.claims`: the claim record for an ontodag edge at a root and for
a pack root (content-addressed as §1 says), a script that asserts a pack
root on `Assertions` (deployed at `0xfa6f…BF99`; consumer `0`, a plain
claim), and a dispute path that takes a leaf, checks `is_below` locally
and — the rung-0 verifier being the missing contract — rules through the
adjudicator key for now. Then the harness cell above.

## Bonded packs (Peter, 2026-09-20): makers insured against the catalogue

Peter's extension the same morning: if anyone can publish a pack, nobody
controls what goes into it, so the pack's author must have something at
stake, and **no pack may be used to match bonded offers without a bond**.
The rules this yields, with two corrections to the section above:

1. **One claim per edge or scope — the semantic one** (corrected
   2026-09-21 on Peter's doubt; "two claims per pack" withdrawn). An
   edge's *presence* under a root is a content-addressed fact with an
   inclusion proof; a proof is evidence, not an assertion, and nobody
   bonds what nobody can be wrong about. `attribute-matches-source` is
   for a record against a *separate* source (a statement against the
   paper it cites, recorded hours against the shop's site); a pack edge's
   source is the pack. What a maker is insured against is the edge being
   *wrong* (a Vespa under `bicycle`) — `attribute-matches-world` on a
   definition, decided by the ladder's adjudicating rungs with the
   catalogue's documentation as evidence; the ~3 % the second readings
   rejected were such errors, and the pack bond backs that claim. The
   inclusion proof and the `is_below` certificate keep their jobs *inside
   a dispute*: the proof localizes the leaf a root-claim's challenger
   attacks, the certificate confirms what the catalogue at that root
   entails. What does settle by certificate is a different claim kind —
   an **entailment claim**, "the catalogue at R relates these names",
   asserted by whoever *uses* the catalogue (a solver's match, a beat's
   leg), decided by computation: the structural half the beat's verifier
   already checks, arising per use, never per pack edge.
2. **The author's bond and the coverage are different money.** The
   author's bond is process collateral — slashable on a refuted edge,
   sized to the adjudication floor plus the reliance term
   (mechanism-design §2), high enough that cheating loses. What a maker
   is *paid* on a bad clearing is coverage: underwritten by the pool
   against provable reliance (F3; the clearing root is the proof),
   reserved per clearing, capped by reserves (F4). The author deters,
   the pool covers, the slashed bond feeds the pool's loss. If the
   author's bond alone had to cover every bad clearing, no individual
   could publish a pack — reliance on core exceeds any one person's
   capital.
3. **The gate, by declaration.** A wanter's `requires` gains a coverage
   floor: the edges her match relies on must carry standing bonded claims
   with *free* coverage at least her point. At clearing the edges
   `satisfies` walked are known; each covering claim's free coverage is
   checked and a share **reserved per clearing**, exactly as the escrow
   reserves a deposit per fill; a claim whose free coverage is exhausted
   admits no further bonded clearing until more bond is posted — F4
   failing closed. So a pack is usable for bonded offers precisely as far
   as its coverage goes, and unbonded offers may still match through
   unbonded packs (the shallow regime stays alive at launch). "No pack
   without a bond" is therefore a gate the checklist runs, not a policy.
4. **Parts, and the sum above.** A claim on a subtree covers every edge
   under it; a finer claim on a sub-subtree adds to the edges it
   contains; **an edge's coverage is the sum of the free coverage of every
   standing claim whose scope contains it** — the sum above it, as Peter
   put it, with one refinement: a bond backs all edges in its scope at
   once, so two failures in one scope draw on the same bond, and the
   honest worst case is the largest failure cluster (one bad hinge edge
   fails everything derived through it) — `netting-and-reserves.md` §7's
   cluster term, computed, not assumed. Reservations draw on the **most
   specific claim first** (the specialist who knew the subtree) with the
   root claim as the backstop, reinsurance-layer style.
5. **Core is the hub claim.** The hinge set carries the most reliance, so
   it needs the largest coverage and is where F4's final-rung condition
   binds first; the pool bonds it first, and everyone who relies on it
   co-bonds through endorsements (`records-and-anchoring.md` §2) — the
   sum above every edge grows with the reliance on it.
6. **Refusal is signal here too.** A pack or subtree nobody will bond is
   one the gate keeps bonded offers away from — the market's verdict on a
   catalogue, without a governance vote.

What this asks of loopmarket: a coverage floor in `Requires` (v6), the
clearing checklist reserving coverage on the covering claims per cleared
leg (the escrow's `reserve` shape, one call per claim), and `Ontology`
exposing the edges a match walked (`satisfies` already computes them).

## Peter's questions (2026-09-21) and the answers taken into the design

1. **Coverage for a proposed circulation.** A leg's match walked a set of
   edges (`satisfies` computes them); what a bad edge loses is the leg, so
   the exposure is the wanter's point *per leg*, not per edge. Rule: for
   each leg and each edge it walked, the free coverage of every standing
   claim whose scope contains the edge, summed, must reach the wanter's
   point; **one reservation of the point per leg on each claim whose
   scope the leg touches**, drawn on the most specific claim first. The
   sum above an edge is the admissibility test; the per-leg reservation
   is the accounting (a leg fails once). Reservations are records beside
   fills (`coverage/<claim>/<loop>`), so free coverage is derivable from
   the fold like a remainder, and U11's shape applies to them.
2. **Who includes a pack.** A maker proposes by pinning a root that
   contains it; a clearing decides by adopting that root (U3 re-derives
   against the clearing's own catalogue); a pack no clearing adopts is
   unused. Merges commute, so a root is a set of packs. Bonded packs add
   only this: a clearing may adopt unbonded packs, and the coverage gate
   keeps *bonded* offers off their edges.
3. **An apple without OntoDAG.** Exact-name matching is the degenerate
   catalogue (every name a node, no edges): apple meets apple, and fails
   the moment the want says fruit. An exact-name match walks no edges and
   so needs **no coverage** — coverage is owed only for what a match
   relied on, and the shallow regime (no packs, no bonds) is a valid
   corner of the same system, not a different one.
4. **Why publish a pack: the bond is an underwriting position.** Every
   bonded clearing that relies on an edge pays a **coverage premium**
   (priced off the loss table, in the asset, on the wanter's side of the
   leg), and the premium goes to the claims that covered the edge, pro
   rata to their reservations. A true-but-contested pack earns exactly
   when it is relied on and nobody can refute it, and loses only on a
   refuted edge — a prediction market's payoff for being right without
   the counterparty, the notional or the settlement (`DESIGN.md` §3's
   spectrum, from the other end). Consequences:
   - a giver's **own low-level pack** (its products under core's hinges)
     is the intended shape; it bonds its taxonomy, earns on its use, and
     a competitor does the same;
   - **the same claim in two packs** is two co-bonds on one claim subject
     when the names agree (more coverage); different names are different
     claims — ontodag's synonym problem, not factbond's;
   - **disagreement** (one pack files a thing where another would not)
     is a dispute; the refuted side's bond is slashed; no vote;
   - **core is the commons and funds itself by use**: it carries the most
     reliance, so its underwriters earn the most premium; the pool or the
     foundation underwrites it at bootstrap, and co-bonding
     (`records-and-anchoring.md` §2's endorsement) is open to anyone who
     relies on it and wants the premium share.

Open: the premium rule for coverage (a per-clearing charge on the
wanter's point, from the loss table per edge — `insurance-products.md`
§3 applies with the edge as the fact type), and whether a clearing's
adopted root must itself carry a minimum coverage to post beats.

## The coverage market (Peter, 2026-09-21): quoted premiums, covers, verification

1. **A claim quotes a premium.** Beside confidence and bond, a claim on
   a scope carries a **premium rate** — what a wanter pays per unit of
   point reserved per clearing. The bonded assertion, already a limit
   order on the dispute side (mechanism-design §1), becomes an offer to
   insure at a price; anyone may post another claim on the same scope at
   their own rate, and competition drives rates toward the loss rate plus
   capital cost. The going rate per edge is `DESIGN.md` §5's signal.
2. **Scopes are nodes.** A claim's scope is a node of the pinned
   catalogue (a pack root, or any node under it: the subtree), never an
   arbitrary edge set. Scopes are then nested (a laminar family), which
   is what keeps the cover cheap to find.
3. **The walk is fixed; the cover is chosen.** A leg's edges are what
   `satisfies` walked — no route finding. The choice is which claims to
   draw coverage from: for one edge, cheapest free coverage first until
   the point is met (a fractional knapsack); across a leg, a wide claim
   reserves the point *once* for every walked edge in its scope, so one
   wide claim at a higher rate may beat several narrow ones — minimum-
   cost cover of the walked edges by nested scopes, a tree DP, exact and
   linear. Across a circulation the cost is the sum over legs and enters
   each leg's gain on the wanter's side, so `selection.pack` already
   weighs it.
4. **The solver chooses, the clearing verifies validity, never
   optimality** (U3's shape). The proposal names each leg's cover: claim
   refs, reserved amounts, rates. The checklist re-derives the walk,
   checks every walked edge lies in some chosen scope, each chosen claim
   has free coverage ≥ the reservation, the rates are the claims' own,
   the sum is the proposal's — O(edges × chosen claims). A cheaper cover
   is a better proposal; the beat's score rewards it.
5. **On chain, optimistic.** Full verification would need one inclusion
   proof per walked edge (that it lies under the scope's node) at ~1 M
   gas each. The beat pattern applies: the cover is in the loop record,
   reservations are recorded at finalization like fills
   (`coverage/<claim>/<loop>`), and a challenge that an edge lies outside
   every chosen scope or a claim's free coverage was short verifies that
   one fact — one proof, one sum. Free coverage is then derivable by
   anyone from the records plus the chain's reservations.
6. **Who pays, when — the open choice.** By the declaration principle
   (whoever requires, pays) the wanter pays the premium at finalization,
   in the asset, and it stays with the underwriters pro rata when the leg
   settles clean; that needs a wanter-side deposit the v5 record lacks
   (v6). The alternative — the giver's deposit carries it, priced into
   the ask — keeps wanters deposit-free at the cost of the principle.
   Recommendation: the wanter pays.

## Deposits, payers, abuse, aggregation, gas (Peter, 2026-09-21)

- **Why a deposit.** Liability between pseudonymous keys is enforceable
  only as custody; per-fill reservation keeps the idle part small. For
  the premium specifically: it is paid at finalization in someone else's
  transaction while the wanter is offline, and an allowance can be spent
  between clearing and finalization, so the pull could fail after the leg
  cleared — settlement risk in the one step meant to have none. Locked
  funds are what make the pull unable to fail. And the wanter needs a
  deposit regardless: the cancellation ladder is symmetric (§5c), so a
  wanter who cancels owes the giver her ladder — the **v6 wanter
  deposit**, which the premium rides on.
- **Wanter pays** (decided): whoever requires, pays; a floor is chosen
  knowing its price; a wanter without crypto sets the floor to 0. Giver
  pays was rejected: the wanter would choose a cost the giver bears, and
  premiums pulled from the giver's deposit drop it below the declared
  bond so the held gate refuses the giver's next legs — a grief vector.
- **The giver's deposit under attack.** Reservation exhaustion is bounded
  by the bond and is what a give is for; holding a reservation with a
  claim costs the claimant fee plus a floor-sized bond for a bounded
  window and loses the stake if refuted; clearing-and-vanishing requires
  the attacker to give something (a loop needs it), and with the wanter
  deposit her own no-show costs her ladder; the notice period is by
  design. Resistant once the wanter deposit exists; the claim's fee and
  floor are the anti-spam device.
- **Aggregation.** Premiums are never transferred per link: at
  finalization the beat sums them **per underwriter and per asset** and
  credits them in the escrow's ledger (pull payments — one storage write
  each, withdrawn when the underwriter likes, reentrancy-safe);
  reservations aggregate per claim per beat.
- **Gas.** The submitter pays it (the clearing key today) and recovers it
  through the solver's spread leg (`P2-batch-auction.md` §7, the reward
  the fee decision left). On Gnosis: submit ~0.5 M, finalize ~0.3 M, a
  reservation ~0.1 M, a credit ~30 k — small, not zero. It shapes the
  cover: the solver's objective carries a **fixed gas cost per distinct
  claim and per distinct underwriter**, favouring one wide claim over
  several narrow ones at equal premium; the clearing verifies sums, not
  the choice, so nothing in the checklist changes.

## Clarifications (Peter, 2026-09-21): custody, discovery, who is slashed, standing claims

- **"Liability without custody"** meant only this: a key's promise "I pay
  if this link is wrong" is enforceable only if the money is posted. The
  pack bond is that custody, and it is what is slashed.
- **A wrong link is found two ways.** Opportunistically — the pack is
  public and any challenger may dispute `black ⊑ light-colour` with a
  stake at any time, no loop needed (factbond's ordinary dispute). And
  **at settlement, through a leg that relied on it** — the usual way: the
  wanter's *as described* dispute finds the giver delivered what the
  offer declared, and the match held only because of the link; the leg
  dispute is **routed to the link's claim** (insurance-products.md §6's
  sibling-dispute wiring, the leg as the paid claim and the link as the
  record relied on).
- **Who pays, who is slashed.** The wanter is paid from the link's
  coverage; the giver's deposit is untouched (he delivered what he
  declared); the link's **bonder** — the claim's asserter — is slashed
  and the link corrected. Never the clearing that adopted the pack, never
  a maker who merely pinned it, unless they are the bonder. A link with
  no bonder means the wanter bore the risk by requiring no coverage —
  what the gate means.
- **The supermarket** makes two declarations and backs both: "this item
  is what I say" (the give's deposit) and "what I say is filed where I
  put it" (its pack bond). Same party, same principle, two bonds; a wrong
  thing received through its own taxonomy is paid by it either way.
- **Correction — pack claims are standing positions.** An ordinary
  assertion's bond returns at certification (`Assertions.certify`); a
  coverage claim's bond must stay posted while any reliance on it is
  open. So a coverage claim is the escrow's deposit shape applied to a
  claim: bond posted and kept, a share **reserved per clearing** that
  relies on it, released when that leg settles clean, paid out on a
  refutation routed from a leg, withdrawable only with notice and no
  open reservations. `Assertions.sol` as built is the one-shot case; the
  standing case needs the reservation bookkeeping `LoopEscrow` already
  has — the second contract of the ontodag step.

## Superseding note (Peter's question, 2026-09-21): no wanter deposit — the premium is a leg

The "wanter pays at finalization in the asset" choice and the v6 wanter
deposit above are **withdrawn**. Two facts settle it:

- **A wanter is a maker with a give.** In a loop every node gives and
  receives, so her give's v5 deposit is already the custody for her
  performance *and* her cancellation (leaving the loop cancels her give
  and her want together). The symmetric ladder never needed a second
  deposit.
- **Coverage is a give; the premium is its price.** The underwriter is a
  maker: `give coverage(S) … p` — "I cover reliance on edges under scope
  S", backed by a `Bond` on that give exactly as any give is (the payout
  on a refuted link *is* the give's performance). A wanter's coverage
  requirement is satisfied by **composition**: her leg is composed with a
  coverage give the way a transport give moves a thing to her door — the
  coverage give moves the leg from uncovered to covered. The premium is
  the coverage give's price on the underwriter's scale and **cancels in
  the loop**; nothing moves at clearing, nobody pays offline, nothing is
  held for it.

What this reuses (all existing): the underwriter's bond reserved per
fill (bond × taken / quantity — the per-clearing reservation); the
wanter's floor as her `requires` point on that give (the gate); the
standing position as a give open across many fills under the escrow's
notice and reservations; the coverage leg verified as a leg (on chain,
one more leg); the underwriter paid in loop value, or in `xdai` (money is
a thing someone gives). The "second contract" of the previous note is
gone: the escrow already holds a coverage give's deposit. The routed
dispute stands: a wrong link fails the coverage leg, and its deposit pays.

What is new (small): a `coverage` head in the catalogue whose argument is
the scope node (the operator-term machinery); a coverage requirement in
`requires` the solver satisfies by composition; the solver's cover choice
as a choice among coverage gives — cheapest scope-covering set first,
gas per distinct give. Premium aggregation per underwriter is then the
loop's own accounting.

## Who owns what (Peter's question, 2026-09-21)

**ontodag — nothing has to change.** The catalogue stays money-blind:

- claim subjects are names at a pinned root, already canonical; pack
  version roots are canonical; the provenance store's records carry the
  `ext` map factbond writes into (`records-and-anchoring.md` §2);
- **the coverage gate needs no walk.** A match walks upward from the
  give's concept to the want's, so every node on the walk lies under the
  want's concept, and the walk lies within scope S iff the want's concept
  ⊑ S — one `is_below`, which exists. A coverage give `coverage(S)`
  therefore covers a leg iff the want's concept (and the handover terms it
  relied on) sit under S; which pack authored an edge inside S is the
  underwriter's business, not the gate's;
- `coverage(S)` as a term is ontodag #15's role-head-takes-a-node,
  declared by loopmarket's seed like `transport`; ordering by the graph
  exists;
- `is_below` certificates (`ontodag.certificates`, built 2026-08-01)
  cover the dependency closure and settle the structural claim at
  rung 0; edge-under-root is recordstore's inclusion proof.

Two optional asks, neither blocking: a **minimal witness path** query
(the edges one derivation used — for a dispute to name *which* link was
wrong and for the correction to target it; the certificate's closure
contains it but does not single it out), and, in ontodag-core, the
**reading history per pack** as machine-readable pack metadata (readings,
rejections) so an underwriter's confidence can start from data.

**loopmarket** owns: the `coverage` head in its seed (argument: a scope
node), `Requires.coverage` (v6) as the floor, the solver composing a
coverage give into a leg when required (a composed-leg kind beside the
operator's, chosen cheapest-first with gas per distinct give), the
checklist re-deriving it (want's concept ⊑ S; the coverage give's deposit
meets the point — `meets` as today), the received/as-described
countersign split (v6), the box operator's event as a witness type, and
`Ontology.assert_edge(bond=)` retired in favour of coverage gives.
Nothing new in the escrow or the beat: a coverage leg is a leg.

*(Reconciled 2026-09-25, `credentials-cover-and-options.md` D4:)* the
"composed-leg kind beside the operator's" is loopmarket's
**argument-only operator** (`operator-argument`, an operator declared by
its argument with no ends, composed by `check_composition` on
`accepts(thing, terms)` alone), and `Requires.coverage` is one entry of
the general **`requires.legs`** ("the loop must contain a give under
category X whose argument accepts the wanted thing"), the same field
that composes `insure(…)` and `inspect(…)` legs. One v6 bump carries them
all. And the rule above — no pack may be used to match bonded offers
without a bond — applies to the credential vocabulary pack the
counterparty gate reads: it carries a coverage give once bonded offers
match on it.

**factbond** owns: `factbond.claims` (claim records for edges and pack
roots; one-shot root assertions on `Assertions`), the routed dispute (a
leg's *as described* claim resolved against the coverage give's
reservation, and the sibling dispute on the link's claim), the correction
event, loss tables per scope, the calibration ledger, the harness cell
with the packs' measured prior. factbond never learns offers or loops:
its resolver sees a subject and an outcome.

## Remark (Peter's question, 2026-09-21): is the catalogue walk part of the loop search?

In principle yes: makers and catalogue nodes form one graph (a give an
arc maker → concept at its price, an edge X ⊑ A an arc X → A at cost 0
or the coverage premium, a want an arc concept → maker), and a loop is a
cycle through it; Bellman–Ford would find loops and choose covers at
once. But the catalogue part is a DAG, so no cycle closes inside it and
it only ever contributes a path between a give's concept and a want's;
contracting each such path to its cost yields exactly today's match
graph. **The two-stage search is the unified search with its acyclic half
contracted — exact, not an approximation.** Running it as one search
would also be awkward: a match is a conjunction over dimensions (a
hyperedge, not an arc — why a leg is one want and several gives), the
exact gates (units, steps, floors, both-ways handover containment,
declared requirements) are checks rather than weights, and ontodag's one
cone query per want is the pruning a million-node relaxation would
lose. The one genuinely joint part — a coverage give's free capacity
shared across legs — has the structure of a divisible give's remainder
and lives where selection already handles it (`selection.pack`, coverage
gives as gives with capacity). The flow formulation of
`P2-loop-selection.md` §11 can carry catalogue arcs explicitly if a
reason appears; none has.

## What this document does not promise

That a root-claim's on-chain verifier (the `is_below` certificate checked
in Solidity, or a trie inclusion proof of the edge under the root — the
`TrieProofVerifier` loopmarket already has) exists yet; that the pool's
confidence per pack is calibrated by anything but the reading count.
