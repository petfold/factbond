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

## What this document does not promise

That a root-claim's on-chain verifier (the `is_below` certificate checked
in Solidity, or a trie inclusion proof of the edge under the root — the
`TrieProofVerifier` loopmarket already has) exists yet; that the pool's
confidence per pack is calibrated by anything but the reading count.
