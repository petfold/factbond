# factbond — assertion extensions for credentials, cover and long claims

Status: design, 2026-09-23; corrected and decided 2026-09-25; entered
factbond's plan corpus 2026-09-25 from the assurance drafts. Dn, A1–G5
name decisions in `credentials-cover-and-options.md`. Proposed, from Peter's refinements of 2026-09-23
(the harmed are the hunters; a counter-assertion shifts the burden; the
window must be flexible): challenge windows chosen per assertion; the
**burden of proof shifts** to the asserter once challenged for self-knowable
facts; disputes are **specific and refutable**; **self-assertions** about
one's own attributes are first-class; a per-asserter loss view. The standing
mode, the counter-assertion primitive and the loss ledger as a factbond
deliverable were the drafts' extensions; the review found them either
duplicating or contradicting factbond's corpus, and plan D1, D2 and D9
replace them. factbond's scope does not grow: it rejects identity as a
requirement and caps per-fact notionals (`insurance-products.md` §4–§5);
adapters, registers and the insurer's product layer live in the new
assurance repo, which *uses* these assertions.

## 1. Challenge windows

Today `Assertions.sol` sets `challengeSeconds` once, in the constructor, for
every assertion. *(corrected 2026-09-25)* The deployed 1 h is the window
chosen for the loopmarket-escrow contest, not factbond's view of POI facts:
the design has always had per-assertion liveness of days to weeks for cold
claims (`DESIGN.md` §5 "give the world time"; `records-and-anchoring.md`
§2 `ext.factbond.liveness` per assertion record; the simulation's default of
14 ticks). So F1 is not a new idea but the v0 contract catching up with the
record design:

- **per-assertion window**, chosen by the asserter in `assert_`, bounded by
  the contract: a minimum long enough for adjudication to be feasible, a
  maximum, and the deployment's value as the default.

The draft's second item, a **standing mode** inside `Assertions` (an
open-ended window closed only by withdrawal after notice), is withdrawn
*(corrected 2026-09-25)*. factbond decided the standing case on 2026-09-21
(`ontodag-first.md`, "pack claims are standing positions"): a long-lived
bonded fact is *the escrow's deposit shape applied to a claim* — bond posted
and kept, a share **reserved per clearing** that relies on it, released when
that leg settles clean, paid out on a refutation routed from a leg,
withdrawable only with notice and no open reservations. `Assertions.sol` as
built is the one-shot case; the standing case uses the reservation
bookkeeping `LoopEscrow` already has. Plan D1 applies this to self-bonded
credentials. The requirement the draft stated still holds: the bond that
backs "I hold this degree" must still be there when the harm, and the
hunter, arrive; reservations lock it to each reliance for that leg's claim
period, rather than to time.

Why the window matters at all: the informed challenger — the person harmed,
their lawyer or investigator — appears *after* the harm, often months
later. A short window serves a live handover contest; it cannot serve
credentials, warranties or title.

## 2. Burden shift on challenge

For facts the asserter can prove and a challenger may be unable to disprove
(a university confirms a degree only with the graduate's consent):

- a challenge, with its own bond at the stake `mechanism-design.md` sets,
  **obliges the asserter to produce evidence** within an evidence period (the
  document to the adjudicator, a primary-source verification it authorises);
- no evidence in time ⇒ *(corrected 2026-09-25)* the draft said "refuted,
  the asserter's bond to the challenger". That reverses a recorded decision
  (`Assertions.sol` header, 2026-09-19: a dispute with no ruling escalates
  and returns both stakes, "never a default that rewards an absent
  adjudicator or a claimant"). Plan D2 replaces it: no evidence ⇒ the
  statement is **suspended** (it meets nothing at any gate, the bond stays
  locked) until evidence arrives or the relying reservations' claim periods
  end; only a ruling moves money;
- evidence accepted ⇒ the winner's share of the loser's stake as today
  (`winnerBps`; the remainder burns, and the burn is load-bearing against
  self-dispute laundering, THREATS T11 — whole-bond transfers would reopen
  it); the evidence's hash is recorded, and a repeat challenge must bring new
  evidence (no griefing), reconciled with `mechanism-design.md` §6's
  reopenability on evidence that did not exist at ruling time;
- which fact types shift the burden is **evidence policy as data**
  (`evidence-policy.md` §1), not code. *(corrected 2026-09-25)* The policy's
  claim types today are `attribute-matches-source | attribute-matches-world
  | entity-exists`; "self-knowable" is a new class to add there, and under
  the policy's 2026 rulings a scanned document alone is dispute input to a
  staked rung, never sole evidence: the university's confirmation enters as
  digital-proof or an attested document.

*(applied practice review, 2026-09-25)* The clocks, the costs and the
judge, all policy data by fact type unless stated:

- **evidence period** for `self-knowable` claims of the order of 7 to 14
  days; after lapse the adjudicator rules ex parte on the record (plan A5);
- **ruling period** per rung (28 days is the statutory-adjudication
  benchmark, 84 the dispute board's); at lapse the claim moves up
  automatically and the lapsing adjudicator forfeits its fee (A3);
- **the first ruling pays**; reopening within a finality window on
  evidence that did not exist at ruling time, or at any time within the
  window at double the stake with no novelty test; after the window only
  fraud or a contradicting primary source (A4, realigning with
  `mechanism-design.md` §6's own window);
- **rung zero**: a free `notice/` with a cure deadline precedes every
  bonded dispute; nothing is public before it lapses (B1);
- **the challenger's outlay is capped** at a fraction of the reservation a
  claim is routed from, and E returns on any ruling in her favour,
  including a partial one; E also returns when the asserter produces
  evidence only after the notice period lapsed, even if the assertion
  holds (B3, B5);
- **every fact-type class names a final rung**, a bonded, named
  adjudicator or panel, never a token-weighted vote; a class without one
  may not be used in a `requires` gate (C2);
- **the adjudicator is paid per ruling and is in the calibration ledger**
  with a deposit; a reversal at the final rung forfeits the deposit and is
  recorded; the policy names the adjudicator class per category (holders
  of the same credential under the same root, or the register itself).
  **Ruling counts are never a signal**: puppet cases manufacture them for
  the burn slice. The one positive entry allowed is a ruling escalated at
  double stake to the final rung and upheld there (C3);
- **the ruling record** carries the referred fact, the notice timestamps,
  both submissions' hashes or the lapse, the resolver's key, the category
  and the evidence-policy and pack versions applied, and a short reason
  naming the rule; evidence is disclosed to every rung on the path, hashes
  public (C5).

## 3. Disputes, not counter-assertions *(applied plan D2, 2026-09-25)*

A bonded contradiction — "key K does not hold degree N from institution I" —
is not a new primitive. Against a live assertion it is a **dispute**, with
the stake the existing formula sets and, for a self-knowable claim, the
evidence fee of §2. Against a certified (closed) assertion, or a key that
asserted nothing, there is no accused bond to forfeit; what remains is an
ordinary bonded assertion of the negation, which the accused may dispute at
the odds and win by proving the degree. Two rules survive into disputes
generally:

- **specific and refutable**, naming the assertion or a concrete fact; never
  a label ("fraudster"), which cannot be adjudicated and is a defamation
  risk on a permanent public store; the adjudicator refuses a dispute that
  is a label;
- **silence counts only after notice, and only through a ruling**: the
  accused is notified (a consumer hook or the watcher's feed) and given a
  period in days, not hours; unproduced evidence is then grounds for the
  adjudicator to rule against, never a contract default (§2).

The minimum accuser bond the earlier draft left open is answered by the
existing stake formula, since a dispute's stake is set by the asserter's
confidence.

## 4. Self-assertions

The asserter's own attribute as subject: "the holder of key K holds an MSc in
Electrical Engineering from the Technical University of Budapest since 1999,
not revoked as of D" (Peter's example). What makes it usable:

- **the key bound to the person**: a degree number, and the identity binding
  level the relying party requires (assurance); the real holder is the
  best-placed challenger of an impostor;
- **floor set by the relying party**: loopmarket's `requires` ("self-bonded ≥
  B" for this category) — the bond must exceed what lying earns across all
  uses while it stands. *(corrected 2026-09-25)* factbond's reliance term
  (`mechanism-design.md` §3) sizes bonds to *clearing-weighted* reliance
  read from loopmarket's witness feed; out-of-clearing reliance is an open
  problem there (OP-1). For a credential relied on across many trades the
  relying party's floor is therefore the whole mechanism, and plan D1's
  per-leg reservations are what make the reliance measurable;
- **reservation-backed, not standing** *(applied plan D1)*: the statement
  names the deposit that backs it (in v1 the deposit on the maker's own
  offer, possibly another maker's, as a practice for its dentists); each
  relying fill reserves the requirer's floor for its claim period; a
  refutation is a claim on that reservation; **burden shift** (§2) by
  default for this fact type;
- **completeness declarations**: "these are all the licences I hold or have
  held" — refutable by exactly the informed hunters; omitting a banned licence
  is the lie that slashes. The near-term answer to bans recorded under another
  jurisdiction's identifiers.

Suitable for self-knowable, rarely revoked facts at modest stakes. Licences
(often revoked, the asserter motivated to stay silent) need registers; large
harms need insurance — both assurance's.

## 5. Per-asserter loss ledger

*(corrected 2026-09-25)* factbond already has this object: the
**calibration ledger** (`mechanism-design.md` §3 and §6; `domain-choice.md`
§5), a per-asserter, non-transferable, outcome-based record that counts
only resolutions that carried consumption or survived a real dispute, and
into which settlement enters *negatively only* (`loopmarket-coupling.md`
§2: lost disputes, paid claims, slashed bonds, "the events that are
expensive to fake"). The loss ledger this draft proposed is the negative
half of that object, indexed by asserter and issuer category: which
certifiers, attesters and self-asserters were refuted, for what, at what
stake. Two facts about the source: the on-chain `Refuted(id, subject)`
event carries no asserter, bond or stake (those are in `Asserted`), so the
view joins the two on `id`; and the correction *feed* (owner-signed, on
Swarm) is designated but not built ("lands with Phase 1",
`records-and-anchoring.md` §7). It is the input for insurers' pricing. What
it must never be is a ratio: negatives are absolute, and a clean record on
a new key means nothing (THREATS T8; P4 §5 item 5 on association sets).

*(applied practice review, 2026-09-25)* Two rules on the view: it is
queried with a **look-back window** (`max_loss_age`, beside the gate's
`max_root_age`), append-only underneath, so nothing is deleted and nothing
counts forever by default (plan G3); and it is **priceable**: it separates
"refuted" from "did not perform on a ruling", a dispute the asserter wins
leaves no negative entry, and every published ruling names the rule and
fact type applied, so an honest misdescription is not read as fraud (G4).
Adjudicators have entries of their own (C3).

## 6. What the extensions serve

| consumer | uses |
|---|---|
| loopmarket counterparty gate (*self-bonded* and deposit-backed *attested* statements) | §2 (burden shift, suspension), §4 (reservation-backed); no factbond window involved until a claim is asserted |
| assurance attesters and certifiers (bonded statements) | §1, §2, §5 |
| cover (title, "genuine", "not stolen"; plan D3) | §1 per-assertion windows for the *insured's* claim assertion; §5 pricing. No standing window: the insurer never asserts the covered fact at cover time |
| loopmarket escrow claims (existing `hold`/`resolve`) | unchanged. *(corrected 2026-09-25)* The claim period (how long after the window a wanter may still claim) is `LoopEscrow`'s per-reservation `claimSeconds`, loopmarket's parameter and already long-able; factbond's window is how long the giver has to contest once `hold` is called. Lengthening one does not lengthen the other |

## 7. Work packages and gates

| # | Package | Gate |
|---|---|---|
| F1 | per-assertion window with bounds + default | an assertion with a 30-day window is disputable on day 29, certifiable on day 31; out-of-bounds windows refused |
| ~~F2~~ | standing mode with withdrawal notice — **withdrawn** (§1; plan D1: reservation-backed gives on the escrow) | — |
| F3 | burden-shift fact types (policy data: a `self-knowable` class; evidence period, ruling period, evidence fee, challenger cap, finality window per class) | challenged self-assertion without evidence in the period is suspended and meets nothing, then ruled ex parte; with evidence certifies; a repeat challenge needs new evidence or double stake within the finality window, nothing after it but fraud; a claim whose stake plus fee exceeds the cap is refused; E returns on a partial win and on late evidence |
| F4 | dispute rules (§3): specificity; a `notice/` with cure deadline before any dispute; silence counts only through a ruling | a label is refused as a dispute; a dispute without a prior lapsed notice is refused; an unnotified accused cannot lose by silence; a cure within the deadline leaves no public record |
| F5 | asserter-indexed loss view of the calibration ledger (§5), with look-back and the refuted / non-performed split | the view reproduces from `Asserted` and `Refuted` events joined on `id`; an entry older than the look-back is not returned; a won dispute leaves no negative |
| F6 | adjudicators in the ledger: fee per ruling, deposit, reversal entries; the ruling record (§2) | a rung that lapses forfeits its fee and the claim moves up; a reversal at the final rung forfeits the deposit and is recorded; a ruling record missing the referred fact or the notice timestamps is not a ruling |
| F7 | a named, bonded final rung per fact-type class (§2) | a class without a final rung is refused by the gate; the final rung is never a token vote |

F1 is small and unblocks the rest.

## 8. Open

- The evidence period's length per fact type (policy data).
- Who may see sealed evidence. *(corrected 2026-09-25)* Sealed evidence
  sits badly with factbond's "anyone re-derives" (F1, G-REC1); plan D2 makes
  the evidence hash and the ruling public and sends only the document to
  the adjudicator.
- The minimum bond for a bonded negation is answered by the existing stake
  formula once §3 is a dispute (plan D2).

Decided in `credentials-cover-and-options.md` and **applied here on 2026-09-25**: D1
(§1, §4), D2 (§2, §3), D9 (§5, §6), D10 (a per-fact-type escalation value
in the policy before any long-lived boolean use, since the stand-in reads a
boolean outcome as 0). Also factbond's, from D9: pooled cover as the geared
reserve applied to cover gives, a mutual as the first form, and negligence
claims as a mutual's discretionary product outside the ladder (D10).

The practice review's amendments (`../../../loopmarket/docs/plans/commercial-practice-review.md`, decided
2026-09-25) are applied in §2 (A3–A5, B1, B3, B5, C2, C3, C5), §5 (G3, G4)
and §7 (F3–F7). factbond also receives the mutual's rules F1–F8 (plan D9)
with the geared reserve, since the mutual is factbond's.
