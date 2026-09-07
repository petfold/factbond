# factbond: threat register

Status: design, 2026-08-07; dated edit 2026-08-21 (T14, aggregator
omission & centralization, mirrored from the primary register — added
there at owner direction; T10–T13 were imported into the primary register
the same day). Decided at 2026-08-07: the shared IDs T1–T9 adopted
frozen from the primary register, factbond-primary depth on T4–T6 and T9,
the factbond-native entries T10–T13 appended under the mirror's new-IDs
rule, initial tripwire thresholds pre-registered and changeable only by
dated edit, and the invariant ↔ threat coverage matrix with its honesty
row. Open here: the odds-weighted equilibrium as a threat surface, the
top rung's existence at F4 scale, the systemic adjudicator-failure
loading, the fabrication-cost curve E(t), cap-griefing via farmed
reliance, insurable interest without identity, semantic drift.

This is factbond's half of the register both repos gate on; the primary
copy and format definition is loopmarket's
`../../../loopmarket/docs/plans/THREATS.md`. Every entry carries the same
columns — attack, economics with researched numbers, by-construction
defense naming invariant and owning document, residual, tripwire that
pages a human, owning work package and phase — condensed pairwise here
for length. **Content-sync rule:** T4–T6 and T9 are primary *here*;
T1–T3, T7 and T8 are primary in loopmarket's copy and carried below in
full but condensed; T10–T13 are factbond-native, primary here, entering
the mirror on its next dated edit. Edits land primary-first; secondary
copies carry the full columns plus a cross-reference; divergence beyond
primary/secondary marking blocks both registers' phase gates (G4). The
adversary playbooks exercising every factbond-owned entry are
`phase0-simulation.md` §7.

## 0. Register discipline

**Why young-system ordering.** A mature system fears capture and drift; a
young one dies of its own incentive budget (FCoin was insolvent within 20
months of inventing fee-mining). T1–T3 attack the earliest surfaces,
T4–T6 the guarantee fabric — factbond's own layers — and T7–T9 are
chronic. IDs are **frozen: never renumber**; T10–T13 carry the append
rule's new IDs and ride after T9 by ID, not rank (T10 belongs with T1's
class, live the day assertion fees exist; T11/T13 with the fabric; T12 is
chronic). Re-rankings re-sort presentation by dated edit (G5).

**The structural fact, from factbond's side.** A legitimate loop is a
self-financing cycle (Victor & Weintraud, WWW'21), so loop-shaped traffic
proves nothing: bond-sizing centrality and the calibration ledger count
only cleared fee-paid loops (loopmarket's planned U12 —
"reward/reputation statistics count cleared fee-paid loops only"), and
every defense below is by construction, never shape policing. The ten
fee/bond rules compressing that design law live in the primary register;
rules 7–9 (indemnity cap, two-part bond sizing, soulbound stake) are
factbond's to enforce.

**Maintenance rule.** No factbond phase goes green while any entry lacks
an owning work package or, once its surface is live, an instrumented
tripwire. Phase 1 blocks on T4/T10/T11 (bonds, disputes, fees go live);
Phase 2 on T5/T9/T12/T13 (insurance and the reserve); T6's constitutional
clauses gate Phase 1 entry (G-M3).

## T1 — Rebate/reward-farmed wash loops — primary: `loopmarket/docs/plans/THREATS.md`

**Attack & economics.** A sybil ring posts matched ask/bid pairs, a
ring-run solver "finds" the loop, the ring farms any volume-linked
subsidy; the loop consumed nothing. LooksRare: a measured **1.34% daily
return** on wash capital ($6.2M rewards vs $3.7M fees in one day); FCoin:
insolvent in 20 months, $130M shortfall; Chainalysis found only 110
*profitable* NFT wash traders — a real fee floor prices attackers out.

**Defense & residual.** loopmarket's planned U13 — "wash-loop
budget-balance by construction, fees external-asset only" — with U12;
here F9 — "no volume-linked emissions anywhere" — the same law on the
sister system, audited continuously (G-M6): the pool, custodian of solver
bonds, never mints the subsidy that would flip U13's sign. Residual:
off-protocol budgets (grants, airdrop scores) re-fund from outside.

**Tripwire & work package.** Per funding cluster, Σ(rewards + rebates) /
Σ(external-asset fees) > 0.8 over 7 days, or one cluster > 10% of cleared
volume, pages (mirrored). loopmarket `P2-batch-auction.md` §9 (P2); the
self-dealing playbook in `phase0-simulation.md` §7 (Phase 0).

## T2 — Sybil offer spam & statistics pollution — primary: `loopmarket/docs/plans/THREATS.md`

**Attack & economics.** Personal tokens are free identities: flood the
book to pollute indexes, statistics and cohorts — factbond-side, the
witness telemetry and loss tables every bond and premium is sized from.
Marginal wallet ≈ gas + postage; LayerZero filtered **803,093 addresses**,
Linea ~517k of 1.3M claimants (**~40% sybils**); rented World IDs at
~$30–80 restore sybil capacity — a rate limiter, never a trust root.

**Defense & residual.** A cost curve, not detection (loopmarket
`P1-federated-book.md` §6/§8): postage as the offer's rent, U8's
two-layer authenticity. The Circles property bounds damage — no sybil
enters a *cleared* loop without a real counterparty on every leg — so U12
routes every consequential statistic through the cleared fee-paid ledger,
the only feed factbond's centrality and calibration ledger consume.
Residual: anything not clearing-weighted; the witness-replay sampling
rate that bounds poisoning at acceptable cost (`loopmarket-coupling.md`).

**Tripwire & work package.** Never-cleared offer share per funding
cluster: pages when any cluster exceeds 10% of the live book or any
`idx/` prefix (mirrored). loopmarket `P1-federated-book.md` §8 (P1); here
the witness-sampling open problem.

## T3 — Solver collusion in batch auctions — primary: `loopmarket/docs/plans/THREATS.md`

**Attack & economics.** A solver ring rotates lowball wins, shifts
surplus between orders it controls, or games the fairness filter (the
CIP-67 vectors). CoW's record: strategy prevented by mechanism shape, not
punishment — its only real slashes were operational negligence cured at
exact damages, **$166,182.97** (CIP-22) and **$76,783** (CIP-55), with a
72-hour cure window.

**Defense & residual.** loopmarket's: the deterministic baseline as
permanent reserve bid (preconditioned on the ExchangeGraph recall gap —
loopmarket `docs/plans/P2-loop-selection.md` §6; until that passes, the
reserve-bid collusion argument may not be cited as a defense), sealed
proposals, the fairness filter, U14 —
"numeraire-free scoring". factbond's part is custody and law: solver
registration bonds route through the bond pool — one loss ledger
(`loopmarket-coupling.md` §3; decided 2026-08, lands with Phase 1,
activates with loopmarket's P2 auction) — and F9 binds both customer
classes: solver-emission farming and assertion-mining are the same FCoin,
one pool refuses both. Residual: off-chain side payments cannot be
designed away (impossibility results) — resistance, priced, never proof.

**Tripwire & work package.** Median (winning − reserve) margin per beat
pages when < 5% of reserve score for 100 consecutive beats (mirrored);
win-share Herfindahl, rotation autocorrelation. loopmarket
`P2-batch-auction.md` §8/§10 (P2); bond custody here.

## T4 — Adjudication capture & dispute griefing

**Attack & economics.** Three shapes, one root. *Capture*: buy the
ladder's final rung when downstream reliance exceeds its capture cost —
the profit sits in positions outside the oracle game; p+ε bribery
(Buterin 2015) makes vote-buying free on success, paying bribed voters
only if the attack loses. *Griefing*: spam cheap disputes to freeze
claims (`Contested` freezes everything priced on the status) and exhaust
the pool's auto-funding. *Wearing-down*: honest disputers lose bonds to a
captured or conformist tribunal and learn to stop disputing. The record:
Polymarket/UMA, March 2025 — one whale cast 5M UMA across 3 accounts,
**~25% of the DVM vote**, flipping a **$7M** market gated by a **$750**
proposer bond, notional/bond ≈ 10⁴; the Zelenskyy-suit market ($160–237M
volume) resolved NO twice against the photographic record and slashed
honest disputers both times — a conformity cascade that incoherence
slashing amplifies; UMA's patch (UMIP-189: 37 whitelisted proposers)
retreats to partial permissioning with the DVM rung still capturable.

**Defense (by construction).** The revised sizing doctrine
(`mechanism-design.md` §2, amending `../DESIGN.md` §3; decided 2026-08,
lands with Phase 1): bond = max(adjudication-cost floor, k ×
clearing-weighted reliance/centrality); final-rung integrity cost ≥
aggregate open reliance, dispute-market open interest included; and F4 —
"reliance-bounded adjudication + fail-closed caps" — halts
reliance-bearing sales with no override (Nexus Mutual's stake > 5× claim
quorum is the production precedent). F5 — "tribunal independence +
soulbound stake": the top rung is an *independent* arbitrator (the
reality.eth → Kleros composition), never a same-token DVM; per-round
stake-base growth (Kleros's 2n+1) makes p+ε liability outrun the doubling
bond ladder; soulbound stake leaves no bribe market to price capture. The
constitution precedes the first dispute (G-M3): no incoherence-only
slashing (the cascade counter), retroactive refunds on reversal,
reopenability on new evidence, conduct and removal rules for every rung
and the demotion authority. Griefing is priced, not policed: the
challenger floor `D_rung` covers the invoked rung's cost plus the delay
externality, checked grid-wide in Phase 0. Wearing-down is answered
structurally (`mechanism-design.md` §6; lands with Phase 2): payouts
auto-fund the sibling dispute and the pool pays appeal fees up the ladder
— a capitalized repeat player no attack exhausts one bond at a time. F8
shrinks the surface first: matches-source disputes settle by certificate
and never reach a capturable rung.

**Residual.** The correlated bad-ruling tail is T12's — a captured rung
fails every claim it terminates at once and poisons the loss tables;
soulbound stake raises capture cost, it does not zero it; the fast path's
track-record gate is a milder whitelist and still a target — disputes
stay permissionless forever; and the top rung's existence at F4 scale is
open (Kleros: low thousands of cases in eight years, largest ~£6,400) —
fail-closed caps bound the system's size until the rung matures.

**Tripwire & work package.** Top-principal share of final-rung power vs
aggregate open reliance per subject; per-claim cap utilization pages at
80%, before the fail-closed stop (mirrored); honest-disputer attrition
(repeat disputers who lose and exit) trending up; challenger-population
survival after an unjust ruling below the G-M5 threshold (initial).
`mechanism-design.md` §2/§4/§5/§6 (the constitution, Phase 1; pool
funding Phase 2) + `phase0-simulation.md` §6/§7 (capture replay,
wearing-down variant); loopmarket side: `P3-guarantee-coupling.md`.

## T5 — Insurance arson

**Attack & economics.** Buy insurance on a fact, then make it wrong or
corrupt its adjudication — the assassination-politics generalization: a
market paying on an adverse event is a purse for causing it. Variants,
each a scripted Phase-0 playbook: the single arsonist; *aggregation* —
many small legit-looking policies across sybil buyers on one breakable
fact (T2 × T5); *reliance inflation* — real cleared loops run through an
edge to raise its indemnity ceiling before breaking it; *fabrication-fed
arson* — the payout event manufactured as evidence (T13's economics in
T5's service). Profit = payout − premium − corruption cost, unbounded
exactly when payout is unlinked to real loss; the corruption input is
cheap where evidence is — a $100 payout is a $100 bounty on a fabricated
photo, and the honest-looking fraudulent claimant scales as thousands of
small independent attacks, no single expensive rung to buy.

**Defense (by construction).** F3 — "indemnity (payout ≤ provable
reliance; payout-cap proxy where unprovable)" — kills arson at the
pricing desk, not in the courtroom. In the loopmarket coupling reliance
is provable for free: clearing roots pin which cleared legs walked the
insured edge, so breaking an edge you insured returns at most what you
provably had at stake, minus premium (`loopmarket-coupling.md` §3;
decided 2026-08, ships per its two-gate sequencing). In the agents-first
wedge the proxy is hard micro-scale payout caps sized so arson cannot pay
even on wholly fabricated reliance (`insurance-products.md` §2; lands
with Phase 2). Around F3: the controls-source exclusion; F4's per-fact
and per-cluster aggregate caps failing closed — sales stop when open
interest approaches the final rung's capture cost, closing the
aggregation variant; the fabrication-bound gate (no class backs a sold
hedge unless its sourced fabrication-cost estimate exceeds its payout
cap); and adverse selection priced, not screened — demand concentration
raises the quote, tightens the cap, triggers a pre-emptive dispute.

**Residual.** Reliance inflation costs real external-asset fees (U13) and
only cleared fee-paid loops count (U12), so the ceiling is bought at fee
price — but it is buyable. Cap-griefing inverts the defense: farmed
reliance can freeze insurance sales on a rival's edge — the designed
failure mode as denial-of-service (open problem). Insurable interest
without identity remains a heuristic (OP-2).

**Tripwire & work package.** Per-fact (per-edge in the coupling)
open-insurance / final-rung-integrity-cost ratio pages at 80%, before the
fail-closed stop (mirrored); payouts where the buyer's funding cluster
intersects the fact's asserter/disputer cluster; demand-concentration
spikes; pre-launch, the Phase-0 arson-ROI surface stays negative in every
grid cell — one profitable cell is a no-go, not an outlier.
`insurance-products.md` §2/§4/§5 (Phase 2) + `phase0-simulation.md`
§1/§7; `evidence-policy.md` §4; loopmarket: `P3-guarantee-coupling.md` §3.

## T6 — Catalogue governance capture

**Attack & economics.** Patient accumulation of assertion and
adjudication power over hub subjects; bribe markets for edge disputes;
re-meaning categories under cleared offers; capture of the maintainer
surfaces factbond adds — the evidence-class demotion authority, the
pool's auto-assertion policy, the emergency brake; complexity attacks
(structure-adding axioms taxing everyone's netting). Croatian Wikipedia:
**~10 admins held the project for 9 years**, and the comparative CSCW
study (TeBlunthuis et al., CSCW 2024) attributes capture to missing
*rules about rulers*, not content rules. Curve wars: a liquid governance
token spawned an industrial bribe market — Convex over a third of veCRV,
Votium industrializing the vote-buying, the Mochi attack stopped only by
an ad hoc nine-member Emergency DAO. A hub subject underwrites vastly
more cleared value than a leaf — and the contested edges will be
value-laden category placements (organic, halal, refurbished), the
Wikidata pattern of edit wars on identity-adjacent properties.

**Defense (by construction).** Bonds scale with **clearing-weighted
centrality** — realized reliance from the witness feed, never static
degree, which costs only postage to farm (`mechanism-design.md` §2;
`loopmarket-coupling.md` §2). F5 keeps adjudication stake soulbound: no
transferable token for a Votium to price. F2 — "bonds attach to claim
subjects" — a re-routing catalogue commit cannot orphan or shed a hub
bond. F6 — "factbond state never enters canonical knowledge" — bounds the
blast radius: capturing factbond corrupts prices and payouts, never the
catalogue's roots. No always-on voting anywhere (`mechanism-design.md`
§3; the TCR post-mortem — AdChain died of mercenary voters with no shared
judging criteria; here paid loss experience generates the signal, nothing
is voted on in the happy path). Structure is where capture concentrates,
so structure is where bonds concentrate: complexity-priced axioms
(`netting-and-reserves.md` §6, the SciCast rule; decided 2026-08, lands
with Phase 3). The constitution (G-M3, before the first dispute) covers
every rung *and* the demotion authority: demotions are signed
attributable speech acts, wrongful demotion is triable, removal paths
never need the incumbent's cooperation. Catalogue-side norms are
loopmarket's (`catalogue-bootstrap.md`: schema gated and bonded, offers
permissionless, never re-mean a category).

**Residual.** Slow semantic drift inside accepted vocabulary that never
trips a dispute leaves no loss experience to audit — the standing signal
is silent exactly here; the emergency brake and the demotion authority
are constituted, not capture-proof; cultural capture of the seed imports;
and the horizon problem — the Croatian-Wikipedia timescale is years, so
Phase 0 instruments tripwires but cannot simulate the attack to its end.

**Tripwire & work package.** Single-principal bonded share over the top
decile of clearing-weighted subjects pages at > 25% (mirrored; the
offer-side stuffing and schema-merge tripwires ride in the mirror);
assertion-power concentration over hub subjects, instrumented from
Phase 0; demotion/promotion actions per maintainer key against the
triable conduct record; refusal-to-quote share drifting on value-laden
edges — the refusal signal doubling as a drift detector.
`mechanism-design.md` §3/§4 (Phase 1 entry) + `netting-and-reserves.md`
§6 (Phase 3); loopmarket side: `catalogue-bootstrap.md`.

## T7 — Lemons routing — primary: `loopmarket/docs/plans/THREATS.md`

**Attack & economics.** No attacker required: the solver selects the
cheapest leg that type-checks — the lemons leg; the catalogue guarantees
type conformance, never quality. Ripple precedent ("Mind Your Credit",
WWW'18): **~$13M at risk** from misconfigured rippling; as few as 10
highly connected gateway wallets could isolate much of the user base.
loopmarket avoids the hub half structurally; the lemons half remains.

**Defense & residual.** Risk-priced routing (loopmarket
`P3-guarantee-coupling.md` §5; decided 2026-08, lands with loopmarket
P3): solver edge weight = rate × (1 − expected-loss premium), the premium
supplied by factbond's per-edge/per-maker loss tables — the reliability
audit — published as the premium feed (`insurance-products.md` §3),
consumed strictly solver-side. The pricing discipline is law here:
silence is thin data, never safe edges; premiums start wide and narrow
only on cleared history; never priced off asserter confidence alone.
Residual: cold start taxes honest newcomers exactly as hard as lemons;
the feed's inputs are T2-attackable until volume exists.

**Tripwire & work package.** Realized loss/dispute rate of
cheapest-decile legs vs the book median pages at > 3× (mirrored);
acceptance-limit saturation on new makers. loopmarket
`P3-guarantee-coupling.md` §5 (P3); the loss tables here (Phase 2).

## T8 — Reputation gaming — primary: `loopmarket/docs/plans/THREATS.md`

**Attack & economics.** Inflate delivered history via wash loops;
suppress complaints; split identities to farm standing. eBay: **0.3%** of
transactions rated negative while P(negative | partner rated negative)
> **37%** — retaliation suppressed truthful feedback; cheap ratings
inflate toward uselessness ("Reputation Inflation", EC'18).

**Defense & residual.** U12 (quoted in §0) — history inflation costs real
fees (U13). factbond's instantiation is the calibration ledger
(`mechanism-design.md` §3): a certified-by-timeout track record nobody
watched is free to manufacture, so the ledger counts only resolutions
that carried consumption or survived a real dispute; loss experience
comes only from bonded, adjudicated events; an undisputed edge is priced
unknown, never good — silence is uninformative. Residual: collusion among
real people; history farmed at fee price is still history.

**Tripwire & work package.** Per-maker history growth per unit fee paid;
standing-relevant history > 50% common-funder counterparties pages
(mirrored); certified-by-timeout share rides with T10's. loopmarket
`P3-guarantee-coupling.md` §5 (P3); the ledger here (Phase 1).

## T9 — Basis-risk disputes

**Attack & economics.** An erosion, not an attacker: the insured loss is
real but the record is technically "true", or the trigger pays when
nothing was lost. The index-insurance literature is unambiguous that
**basis risk, not fraud, is the #1 uptake killer** at commercial
premiums; parametric products show near-zero measured claims fraud (the
CEGA photo-based indemnity study found none measurable), displacing
failure into trigger–loss mismatch. Every deployed system pays the same
tax through wording — Augur's invalid markets, Proof-of-Humanity's
photo-angle literalism, the Zelenskyy suit — ambiguity is the cheapest
attack surface of all. Each wrong-feeling resolution burns the whole
product class ($160–237M of credibility in the Zelenskyy case) and
teaches honest disputers to exit (T4's wear-down through wording); a
product with latent basis risk is a product nobody renews.

**Defense (by construction).** Identity first: `claimId` includes
`claim_type` and `policy_ref` (`records-and-anchoring.md` §1), so "the
record is wrong" and "the world deviated today" are different claims with
different resolution procedures — conflating them is how basis-risk
disputes are manufactured, and here they cannot share an id. The
two-product split makes the distinction commercial
(`insurance-products.md` §1; decided 2026-08, lands with Phase 2):
parametric convenience hedge (pays on the experienced outcome, no
epistemic claim) vs verification bet (pays on the record adjudicated
wrong), the premium gap between them a published signal — neither buyer
discovers at claim time that they held the other product. F8 —
"structural claims settle by certificate only" — closes the structural
half outright: index and insured object coincide by construction on that
half, lower basis risk than any rainfall index achieved. The worldly half
is fought at wording time: hash-pinned per-domain policies
(`evidence-policy.md` §2 — the policy hash *is* the contract);
parametric-first wherever a canonical feed exists (the Etherisc pattern);
the ambiguity red-team gate (≥20 adversarial fixtures, two independent
panels ruling identically on all 20 before real stakes); F7 — "'certified
≠ true' on every surface" — on every quote.

**Residual.** Semantic edges — suitable-for-X, quality and fitness
categories — keep interpretive basis risk no certificate or wording
closes; quoted wider or declined, the refusal itself published (OP-3).
The premium gap, once published, is a manipulable surface (OP-4).

**Tripwire & work package.** Per policy hash: share of disputes ending
"policy technically satisfied, consumer claims loss" (or the inverse)
pages at > 10% over a rolling quarter (mirrored) and forces a policy
rewrite with a version bump, never an in-place edit; premium-gap
anomalies per fact-type; declined-quote share per edge class.
`evidence-policy.md` §2/§3 + `insurance-products.md` §1/§7 (Phase 2);
loopmarket side: `P3-guarantee-coupling.md` §4.

## T10 — Assertion-mining & assertion spam

**Attack & economics.** Farm any reward proportional to assertion volume
by asserting garbage at scale; failing that, spam assertions to
manufacture a calibration track record from certified-by-timeout claims
nobody watched, or to bury the claims that matter. The precedents are
terminal: FCoin's trans-fee mining reached, with copycats, ~40% of global
reported exchange volume before insolvency inside 20 months; LooksRare's
volume-linked emissions returned a measured 1.34%/day on wash capital.
Assertion-mining would be the FCoin of facts — and the farm's statistics
would poison the one dataset the system exists to produce.

**Defense (by construction).** F9 — "no volume-linked emissions anywhere"
— held by construction: an asserter's income paths are exactly yield on
pool stake, a share of assertion fees as an LP, slash winnings, and the
underwriting business — nothing else exists to farm
(`mechanism-design.md` §3; fees land with Phase 1). Assertions cost a fee
accruing to the pool — the spam price. The calibration ledger counts only
resolutions that carried consumption or survived a real dispute (the U12
shape applied to reputation), so a manufactured record buys nothing.

**Residual.** Off-protocol subsidies re-fund the farm from outside —
T1's residual wearing factbond's mask; a future token would add the
reflexive surface `../DESIGN.md` §9 refuses, revisitable only after
modelling the FCoin scenario.

**Tripwire & work package.** Assertions per principal never touching
consumption or dispute; certified-by-timeout share per asserter funding
cluster; the G-M6 audit finding any volume-proportional path pages
immediately, no threshold. `mechanism-design.md` §3 (Phase 1) +
`phase0-simulation.md` §5 (the F9 check, kept forever).

## T11 — Self-dispute laundering

**Attack & economics.** Dispute your own assertion from a second identity
and wash stake through the winner's share — manufacturing dispute
history, farming the calibration ledger's dispute-survival gate, or
laundering through a dispute-triggered market. The winner takes the
majority of the loser's stake; without a burn, one principal on both
sides recycles its capital at ~zero cost while printing fake track record
and fake loss experience — corrupting T7's feed and T8's ledger at once.

**Defense (by construction).** The slash-split's burned slice
(`../DESIGN.md` §8: majority of the loser's stake to the winner, a slice
burned or to the adjudication treasury; decided 2026-08, lands with
Phase 1): the launderer pays the burn on every cycle, making the loop
strictly negative — loopmarket's wash-loop inequality, applied to
disputes. **The burn is load-bearing**: any future split change must
re-verify the inequality (`mechanism-design.md` §3). Dispute-market size
caps bound the channel's throughput (§5); the ledger's consumption gate
keeps even a paid-for history thin.

**Residual.** The general asserter–challenger collusion form is open
(`mechanism-design.md` §8, question 4); the burn size is a parameter, not
a law — UMA's production analog burns half the loser's bond; the right
slice here is a Phase-0 output.

**Tripwire & work package.** Asserter/challenger funding-cluster
intersection on resolved disputes (the hildobby common-funder shape,
analytics only, never enforcement); dispute-win share within
common-funder clusters; the scripted Phase-0 laundering playbook stays
strictly negative across the grid. `mechanism-design.md` §3/§8 (Phase 1)
+ `phase0-simulation.md` §7.

## T12 — Correlated adjudicator failure as reserve shock

**Attack & economics.** Not an actor but the tail T4 leaves: every claim
whose escalation path ends at the same final rung fails together if that
rung is captured or conformist — the failure respects no DAG structure,
so the min-cut cluster term cannot see it; the pool asserting and the
reserve insuring the same slice fail together too. This is the reserve's
systemic tail term: the Lundberg arm of the v0 formula — u = max(worst
correlated claim cluster, ln(1/ε)/R) — dies under correlation (Poisson
independence is the whole assumption), and heavy tails void the bound
unless per-fact notional caps force a finite MGF. Nexus Mutual's
collapsed model is the production shape: MCR = Total Active Cover / 4.8,
calibrated to Solvency II's 99.5% one-year survival, ~20% concentration
cap per listing.

**Defense (by construction).** The shock enters the reserve as an
explicit cluster — all open exposure sharing a final rung — with its own
loading (`netting-and-reserves.md` §7; decided 2026-08, reserve v0 lands
with Phase 2). Per-fact notional caps enforce the model's assumptions
rather than hoping for them, and they are F4's per-claim arm: at the cap
the pool stops selling — it does not re-price and carry on. Dispute
provisioning carries the correlated bad-ruling shock at reserve level,
never per-policy (`insurance-products.md` §3); upstream, F4's final-rung
condition caps what any single rung is asked to defend, and reopenability
plus retroactive refunds make a reversed capture recoverable. Panel 4 of
the go/no-go demands ≥ 99.5% solvency under scripted cluster shocks.

**Residual.** The loading's size is the registered open problem: if it
dominates at realistic ladder concentration, adjudicator *diversity*
becomes a capital requirement, not a governance nicety. A captured rung
also poisons the loss tables: the audit fails with the payouts, and no
reserve line item restores a corrupted dataset.

**Tripwire & work package.** Share of open exposure terminating at any
single final rung; ruin runs under the capture scenarios re-run at every
reserve or ladder change (the permanence gate); a loss-table divergence
review forced after any final-rung reversal. `netting-and-reserves.md` §7
(Phase 2) + `mechanism-design.md` (shared open problem) +
`phase0-simulation.md` §7 (cluster shocks).

## T13 — Evidence-class rot

**Attack & economics.** The fabrication cost of an admissible evidence
class decays — continuously under generative media, discontinuously on a
per-model exploit that is expensive to find and ~zero to reuse until
revoked. The design precedent: September 2025, an AI-generated image
injected via multiple-exposure mode into a validly signed Nikon Z6III
NEF; Nikon revoked **all** Z6III certificates and suspended its
Authenticity Service — one exploit, a fleet's evidentiary standing gone,
and until the demotion lands every open claim and policy admitting the
class is simultaneously attackable: a correlated evidence shock, T5's
cheapest input. A $100 payout is a $100 bounty on fabricating one
admissible artifact, and fabrication scales as thousands of small
independent attacks (`../DESIGN.md` §5.2); bare C2PA fabrication is near
zero and falling (stripping is any re-encode; the analog hole is
unsolved) — **revocation latency is the binding parameter**.

**Defense (by construction).** Admissibility is data, not code
(`evidence-policy.md` §1; classes land with Phase 1): a demotion is a
signed catalogue edit binding every ruling not yet issued the moment it
publishes — demote fast, promote slow, fail closed. Policies pin *rules*
naming *live inputs* ("valid and unrevoked at ruling time" — the X.509
shape), so a claim pinned to policy v1 stops admitting Z6III photos
without its hash changing. Closed rulings never rebind (F1 — "status
derived never merged"), but a fleet revocation is exactly evidence that
did not exist at ruling time, so the reopening path applies. The reserve
treats a demotion as a correlated shock: the affected cluster is capped
immediately — F4 failing closed at fleet scale. The fabrication-bound
gate (Phase 2) keeps every sole-evidence class's sourced, dated
fabrication-cost estimate above its payout cap or drops it to
corroboration-only; the review cadence is tied to generative-media
capability jumps as a scheduled decision, not a reaction.

**Residual.** Revocation latency itself; the demotion authority is a
T6-adjacent capture vector; E(t) has no defensible empirical anchor — the
sim sweeps it and treats fragility as a gate, but the arms race is
carried, not closed.

**Tripwire & work package.** Revocation-to-demotion propagation time
across open adjudications; per-class realized loss vs the class's dated
fabrication-cost estimate (paying out above it pages); red-team bounty
claim rate per class (the candidate measurement instrument); the Phase-0
mass-revocation drill must show the ladder degrading, never certifying
garbage. `evidence-policy.md` §4/§5 (Phase 1; fabrication-bound gate
Phase 2) + `phase0-simulation.md` §7; reopening: `mechanism-design.md` §4.

## T14 — Aggregator omission & centralization — primary: `loopmarket/docs/plans/THREATS.md`

*(Mirrored 2026-08-21, added at owner direction with the loopmarket
agenda-#5 sign-off; condensed, substance complete.)*

**Attack & economics.** A loopmarket aggregator silently omits or delays
makers/offers from its fold; its manifest is the book most solvers read,
so omission is market exclusion. Admission-by-reference (T2's spam
defense) *is* censorship capability — the same discretionary power — and
with one aggregator worth reading it becomes unilateral market shaping.
Omission is free at the margin and yields a perfectly valid `book_root`;
running a competitor costs a full pinning Bee node, so the market
concentrates by default. factbond exposure: the pool's loss experience,
premium feeds and clearing-weighted reliance measures are computed
over what the fold shows — a censoring aggregator skews the dataset
factbond prices from.

**Defense (by construction).** The fold is pure and commutative:
same inputs ⇒ byte-identical `book_root`s, so manifest divergence is
evidence. Omission is provable: registry-event announcements are the
censorship-resistant ground truth, maker books are public feeds, and
recordstore absence proofs demonstrate absence from a pinned root
mechanically. Fold decisions are attributed in `provenance_root`; entry
is permissionless; solvers can always fold maker feeds directly.

**Residual.** Neutrality-by-auditability is only as real as the number
of independent aggregators running. **Owner directive (2026-08-21):
several independent aggregators are the deployment floor; a
single-aggregator steady state is a failure condition; read-path
decentralization is a mandated investigation before P1 completes.** The
P1 clearing-instance chokepoint stands until P2.

**Tripwire & work package.** Count of independently-operated manifests
(pages below two); unexplained `book_root` divergence; a planted-offer
inclusion probe across watched manifests. loopmarket
`P1-federated-book.md` §2/§8 + `adoption-and-thickness.md` §9;
clearing half: `P2-batch-auction.md`.

## The invariant ↔ threat coverage matrix

"Blocks" means the attack's profit inequality is negative by
construction; "bounds" means damage is capped or localized, never
eliminated.

| invariant | blocks | bounds |
|---|---|---|
| F1 status derived never merged | — | T4 (no stored status to corrupt — only attributable, reopenable rulings); T13 (demotions compose without rebinding history); keeps tripwires G3-computable |
| F2 bonds attach to claim subjects | T6's orphaned-bond variant (a re-routing commit cannot shed a hub bond) | — |
| F3 indemnity (payout ≤ provable reliance; payout-cap proxy where unprovable) | T5 where reliance is provable (the coupling) | T5's wedge variant (caps bound arson, do not eliminate it) |
| F4 reliance-bounded adjudication + fail-closed caps | T4's notional/bond mismatch; T5's aggregation variant | T12, T13 (correlated clusters capped, sales stop) |
| F5 tribunal independence + soulbound stake | T4's bribe-market pricing; T6's Votium path | capture at any price (cost raised, not zeroed) |
| F6 factbond state never enters canonical knowledge | — | T6 (captured factbond never rewrites catalogue roots); T2 (pollution stays out of roots) |
| F7 'certified ≠ true' on every surface | — | T9's mis-selling half; every consumer surface |
| F8 structural claims settle by certificate only | T9's structural half; the matches-source share of T4's surface | — |
| F9 no volume-linked emissions anywhere | T10; T1's factbond-side re-funding | — |

**What no invariant blocks — the honesty row.** T3 is blocked
loopmarket-side by mechanism shape and U12/U13/U14, not by any F-law —
factbond only refuses to re-fund it (F9). T7 and T8 are *priced*, not
blocked: premiums, acceptance limits and the ledger are policy under
invariant discipline, and their cold-start blindness is irreducible. T11
is blocked by a parameter — the burned slice — not an invariant: a split
change can silently break it, hence the re-verification rule. T12 is
survived by capital, not blocked by law. And the erosion halves of T6
(semantic drift), T9 (interpretive basis risk) and T13 (E(t) decay) are
arms races no invariant closes: priced, instrumented, and said out loud.

## Gates

- **G1 — full assignment.** Every entry has an owning work package and,
  per live surface, an instrumented tripwire with a pre-registered
  threshold recorded by dated edit. Phase 1 blocks on T4/T10/T11; Phase 2
  on T5/T9/T12/T13; T6's constitutional clauses gate Phase 1 entry.
- **G2 — adversary coverage.** Every factbond-primary and factbond-native
  entry runs as a scripted attacker with a budget and a stop rule against
  every Phase-0 grid cell; no entry enters this register without its
  playbook (`phase0-simulation.md` §7).
- **G3 — tripwires are derivation-clean.** Every tripwire is computable
  from signed speech-act records, anchor readings, pinned roots and the
  cleared fee-paid ledger alone (F1; U12) — a tripwire fed by pollutable
  statistics is itself a T2/T10 target.
- **G4 — mirror sync.** Diff against loopmarket's register empty modulo
  primary/secondary marking, checked at every phase gate; edits land
  primary-first; T10–T13 propagate to the mirror on its next dated edit.
- **G5 — re-ranking cadence.** The damage ordering is reviewed at every
  phase gate and after any tripwire page; re-rankings are dated edits
  that re-sort presentation without renumbering.

## Open problems

- **The odds-weighted equilibrium as a threat surface** (T4/T10;
  `mechanism-design.md` §8). Until G-M1 passes, every stake schedule
  above is a hypothesis with a flat-bond fallback; assert-at-0.999
  griefing and capital-cost pooling are its named failure shapes.
- **The top rung's existence** (T4; `mechanism-design.md` §4). F4 demands
  a final rung whose integrity cost can exceed aggregate open reliance;
  deployed candidates are small. Fail-closed caps bound the system's size
  until the rung matures — the honest interim, not a solution.
- **The systemic loading** (T12; `netting-and-reserves.md` §7). Size
  unknown; if it dominates at realistic ladder concentration, adjudicator
  diversity becomes a capital requirement.
- **The fabrication-cost curve E(t)** (T13; `evidence-policy.md`). No
  defensible empirical anchor; candidate instrument: standing red-team
  bounties whose claim rate *is* the estimate; fragility on E(t) is a
  gate.
- **Cap-griefing via farmed reliance** (T5; `loopmarket-coupling.md`).
  F4's designed failure mode as denial-of-service — paying real fees to
  freeze a rival's insurance sales; whether U13's floor prices it out is
  open.
- **Insurable interest without identity** (T5; `insurance-products.md`
  OP-2). Controls-source is a heuristic; a principled pseudonymous test —
  or a proof that caps are the best attainable — is open.
- **Reliance denomination under U14** (T5; shared with loopmarket).
  Indemnity needs a value for legs priced in personal tokens; declared
  coverage plus caps is the v1 proxy, incentive-compatibility unproven.
- **Semantic drift inside accepted vocabulary** (T6; shared with
  loopmarket's `catalogue-bootstrap.md`). Capture that never trips a
  dispute leaves no loss experience; the refusal signal is a candidate
  detector, uncalibrated.
- **Threshold calibration** (register-wide, mirrored). Every threshold
  above is an initial pre-registration — honestly, a guess; recalibration
  is by dated edit under G5, never silent.

## What this document does not promise

- **The register is not exhaustive.** T1–T13 are the attacks with
  researched precedent; new entries get new IDs. It governs what is
  listed, not what exists.
- **Tripwires detect; they do not prevent.** Prevention is by
  construction in the owning documents; a page is a human's problem
  arriving late, by design.
- **The matrix maps coverage, not proof.** "Blocks" means a profit
  inequality holds under the modeled valuation, not that the attack is
  impossible; the honesty row is part of the matrix, not a footnote.
- **The researched numbers are other systems' history** — the $750/$7M
  ratio, the 1.34%/day, ~10 admins/9 years, MCR/4.8 — cited exactly,
  never forecasts of factbond's own surface; Phase 0 exists to replace
  them, and a green Phase 0 certifies nothing about model risk.
- **What green does not mean:** certified ≠ true (F7 — "nobody found it
  profitable to dispute this, under this adjudication procedure, at these
  bond and subsidy levels", `../DESIGN.md` §12, verbatim on every
  surface); premium ≠ probability (a price under capital constraints and
  attack); a stopped market is the mechanism working (F4's fail-closed
  halt is designed, never an outage); an admissible evidence bundle ≠
  ground truth.
- **The ordering is a 2026-08 judgment**, not a law; G5 exists because it
  will be wrong in some direction. Only the IDs are promised stable.
