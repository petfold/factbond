# factbond

Bonded assertions and information insurance for factual claims — a mechanism
design for attaching economic guarantees ("someone will pay if this is
wrong") to millions of ordinary facts: opening hours, database entries,
knowledge-graph edges.

**Status: design stage. Nothing is implemented.** This repo currently holds
the design documents; the next concrete step is a simulation (see
`docs/DESIGN.md` §10), not contracts.

## The idea in one paragraph

Prediction markets cannot scale down to millions of mundane, near-certainly-
true statements: every bet needs a matched counterparty, full-notional
collateral locked for the claim's lifetime (the "99-cent problem"), and a
mandatory settlement even when nobody ever disagreed. The right primitive
for that regime is the **bonded assertion** (the optimistic-oracle pattern):
one party posts a claim backed by a bond sized to the *cost of adjudication*,
not the value at stake; the whole world is the latent counterparty during a
challenge window; undisputed claims certify by timeout for free; and the
expensive machinery — evidence, adjudication, real price discovery — spins up
only on the ~1% of claims where someone actually disagrees, which is exactly
where the information value lives. On top of that sits the consumer product,
**information insurance**: the person (or AI agent) about to *act* on a fact
buys a cheap hedge against it being wrong — which couples verification demand
to consumption, pays exactly the right person to discover each error, and
makes the pool's quoted premium a market-priced reliability signal for every
fact, without anyone betting on most of them.

## Documentation

- **[docs/DESIGN.md](docs/DESIGN.md)** — the design: why markets fail at
  this scale, the bonded-assertion primitive, odds-weighted bonds, the
  insurance coupling, the five-layer architecture, the claim lifecycle,
  capital pools, build order, and the two hardest open problems.
- **[docs/INTEGRATION.md](docs/INTEGRATION.md)** — how factbond composes
  with the sister stack: [ontodag](https://github.com/petfold/ontodag) as
  the claim layer and netting fragment,
  [recordstore](https://github.com/petfold/recordstore)/[Swarm](https://www.ethswarm.org/)
  for evidence and proofs, and
  [loopmarket](https://github.com/petfold/loopmarket) as the first
  structured consumer (its P3 "guarantee fabric" is this design).
- **docs/prediction-markets-transcript.pdf** — the founding discussion
  (Peter Földiák with Claude, 2026; also at
  https://claude.ai/share/2d3c2fe8-adfc-4c01-8f36-ff3ab29baf6d), from which
  `DESIGN.md` is distilled. Where the two disagree, the transcript is the
  record of the discussion and `DESIGN.md` is the current position.

## Origin

The starting ideas (bets on facts rather than future events; capital
efficiency; batching; bets embedded in a knowledge graph) are Peter
Földiák's, developed in discussion with Daniel A. Nagy — whose observation
about capital lock-up on near-certain claims (the 99-cent problem) shapes
much of the design — and, following the ETHPrague 2026 prediction-markets
workshop, with Krzysztof Paruch (Token Engineering Labs) and Mark B
Richardson (Bancor). The synthesis and the architecture sketch come from the
transcript above.

## Honest scope

Even a perfect version of this system does not certify *truth*. It certifies
"nobody found it profitable to dispute this, under a specific adjudication
procedure, at current bond and subsidy levels" — which is genuinely more
than most databases offer today, and the design documents are careful to
keep the distinction explicit throughout.
