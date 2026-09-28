# factbond — user guide

factbond attaches a bond to an ordinary fact: someone says "this is true,
and I lose my bond if it is not", and anyone who disagrees can dispute it
by staking at the odds the claim's confidence sets. Undisputed claims
certify by timeout; only a disputed claim reaches a judge. This guide
shows how to use what is built: the contract, its Python client, the
evidence policy, the adjudicator's procedure, the ledger's views and the
simulation harness. Why it is shaped this way is in
[DESIGN.md](DESIGN.md) and the plans under [plans/](plans/); what comes
next is the [ROADMAP](../ROADMAP.md).

**Status (2026-09-28).** Alpha. The contract described here is the
current source; the deployment on Gnosis (`0xfa6f…bF99`) is the
2026-09-19 version until it is redeployed. Numbers in the shipped policy
are placeholders.

Contents: 1 who does what · 2 the life of a claim · 3 the money ·
4 deploying · 5 the client · 6 writing a consumer · 7 claims about a key ·
8 evidence policy · 9 the adjudicator's procedure · 10 reading the ledger ·
11 the simulation harness · 12 with loopmarket.

## 1. Who does what

| role | does | risks |
|---|---|---|
| **asserter** | posts a claim with a bond and a confidence | the bond, if refuted |
| **challenger** | disputes a live claim within its window | the stake, if the claim is upheld |
| **adjudicator** | the first rung: rules on disputed claims for a fee | its deposit, if the arbiter reverses it |
| **arbiter** | the final rung, named at deployment: rules on appeals and on cases moved up | its reputation; a fee either way |
| **consumer** | a contract told when a claim opens (`hold`) and closes (`resolve`), and acting on the outcome | nothing in factbond |
| **reader** | reads the events: the correction feed, the loss view, the adjudicator view | — |

The contract knows nothing of what a claim means. A claim's `subject` is
a 32-byte hash its consumer (or the asserter) chose, and its `outcome`
is an integer the consumer interprets: a payout for loopmarket's escrow,
1 for a plain true/false claim.

## 2. The life of a claim

```
assert ──► Asserted ──(window closes, nobody disputes)──► Certified
              │                                     (bond back)
              ├─ retract ──► Retracted       (bond back, fee kept)
              │
              └─ dispute ──► Contested ─┬─ concede ──► Refuted (the whole bond to the challenger)
                                        │
                                        ├─ rule ─┬─ no arbiter ──► Certified / Refuted
                                        │        └─ arbiter ─────► Ruled ─┬─ finalize ──► Certified / Refuted
                                        │                                 └─ appeal ───► Appealed ─┬─ ruleAppeal ──► final
                                        │                                                          └─ lapse: finalize, the ruling below stands
                                        │
                                        └─ window lapses ─► escalate ─► Escalated ─┬─ ruleAppeal ──► final
                                            (arbiter only)                         └─ concede
```

- **The challenge window** is how long a dispute may open (the asserter
  chooses it within the deployment's bounds; 0 takes the default).
- **The ruling window** is how long each rung has once the case reaches
  it (the asserter may lengthen it, never shorten it).
- **Only a ruling, or a party's own act, moves money.** If the first rung
  lets its window lapse, anyone calls `escalate` and the case moves up to
  the arbiter with both stakes still held; the arbiter may rule however
  late. Without an arbiter, the adjudicator's ruling is awaited, and the
  deployment's owner may appoint another. Nobody gets their stake back
  for want of a ruling, because parties who do can simply disappear.
- **Concession** is the asserter's own act: before the first ruling, or
  once a lapsed case has moved up, `concede` gives the challenger the
  whole bond, and nobody rules. After a first ruling, its loser gives up
  by waiving the appeal (`finalize`).
- **The appeal window.** With an arbiter, a first ruling's payout waits
  for `appealSeconds`. The loser may appeal in that time; the loser may
  also waive it by calling `finalize` at once.

## 3. The money

**Bond and stake.** The asserter posts the fee plus a bond of at least the
floor. A challenger stakes `max(bond × (1 − c) / c, floor)`, where `c` is
the confidence. A $20 bond:

| confidence | challenger's stake | disputing pays when the claim is false with probability above about |
|---|---|---|
| 0.9 | $2.22 | 13% |
| 0.97 | $0.62 | 4% |
| 0.99 | $0.20 | 1.3% |
| 0.999 | $0.02 | 0.13% |

A higher confidence makes a claim cheaper to attack, so an asserter who
states high confidence and wants disputes to cost something posts a
larger bond: capital at risk grows with stated confidence.

**Fees.** The assertion fee goes to the treasury (the pool, once it
exists) and nothing is ever paid for asserting. A ruling costs the loser
the adjudicator's `rulingFeeWei` and nothing more; the winner takes the
rest of the loser's stake. The fee is at most the floor, so either side's
stake covers it and the adjudicator is paid the same whichever way it
rules. A concession has no fee: nobody ruled.

**Appeal.** The loser of a first ruling appeals by paying double its own
stake plus the arbiter's fee. The arbiter earns its fee either way.
Confirmed, the appellant's appeal stake goes to the other side with the
payout; reversed, the payout goes to the appellant, together with the
first rung's deposit, so the rung that ruled wrongly pays what its ruling
cost. On a case moved up with no ruling below, the arbiter's fee comes out
of the two stakes, whoever wins.

**Deposits.** Where there is an arbiter, the adjudicator must hold
`depositWei` (posted with `postDeposit`) to rule, and cannot withdraw it
while any of its rulings is open to appeal.

## 4. Deploying

```bash
pip install 'factbond[chain]'
FACTBOND_RPC=https://rpc.gnosischain.com FACTBOND_KEY=0x... \
  python scripts/deploy_assertions.py ADJUDICATOR TREASURY FEE_WEI FLOOR_WEI \
    CHALLENGE_S MIN_CHALLENGE_S MAX_CHALLENGE_S RULING_S MAX_RULING_S RULING_FEE_WEI \
    [ARBITER ARBITER_FEE_WEI APPEAL_S DEPOSIT_WEI]
```

The script prints the contract's address. The first ten arguments are the
adjudicator, the treasury, the assertion fee, the floor, the default,
shortest and longest challenge windows, the default (and shortest) and
longest ruling windows, and the ruling fee (at most the floor). The
optional four name the final rung: the arbiter (never the adjudicator),
its fee, the appeal window and the first rung's deposit. Without them
there is one rung, and its ruling pays at once.

After deploying with an arbiter, the adjudicator posts its deposit before
its first ruling:

```python
AssertionsClient(rpc, address, key=ADJUDICATOR_KEY).post_deposit(deposit_wei)
```

To rebuild the shipped contract artifact after changing the Solidity:
`pip install py-solc-x && python scripts/build.py` (solc 0.8.24, via IR,
optimizer 200 runs, so deployed bytecode is reproducible from the source).

## 5. The client

`factbond.AssertionsClient` sends and reads; web3 loads lazily, behind the
`chain` extra. A key signs; reading needs none.

```python
from factbond import AssertionsClient

me = AssertionsClient("https://rpc.gnosischain.com", ADDRESS, key=MY_KEY)
subject = bytes.fromhex(claim_id)             # a 32-byte hash you or your consumer chose
id_, receipt = me.assert_(subject, consumer=None, outcome=1, confidence=990,
                          bond=10 ** 17, window=14 * 86400)

them = AssertionsClient(rpc, ADDRESS, key=CHALLENGER_KEY)
them.dispute(id_)                             # at the stake the confidence sets
me.concede(id_)                               # or wait for the ruling
```

| call | who | what |
|---|---|---|
| `assert_(subject, consumer, outcome, confidence, bond=None, *, window=0, ruling_window=0, about=None)` | asserter | post a claim; returns (id, receipt) |
| `dispute(id, stake=None)` | anyone | dispute within the window |
| `certify(id)` | anyone | an undisputed claim after its window |
| `retract(id)` | asserter | withdraw an undisputed claim |
| `concede(id)` | asserter | give up a contested or moved-up claim |
| `rule(id, upheld)` | adjudicator | the first ruling |
| `appeal(id, value=None)` | the ruling's loser | appeal within the appeal window |
| `finalize(id)` | anyone (the loser at once) | pay out a held ruling, or a lapsed appeal |
| `escalate(id)` | anyone | move a lapsed case up to the arbiter |
| `rule_appeal(id, upheld)` | arbiter | the final ruling |
| `post_deposit(amount)`, `withdraw_deposit(amount)` | adjudicator | its deposit |
| `assertion(id)`, `appeal_state(id)`, `ladder()`, `events(name)` | anyone | reads |

## 6. Writing a consumer

A consumer is a contract that acts on the outcome. It implements two
calls:

```solidity
interface IConsumer {
    function hold(bytes32 subject) external;                    // a claim on your subject has opened
    function resolve(bytes32 subject, uint256 outcome) external; // it closed: the asserted outcome, or 0
}
```

- `hold` may revert, and then the assertion never opens: nobody can open
  a claim on your subject that you did not accept. There is no
  registration step.
- The claim is written before `hold` is called, so `hold` can read it
  (`Assertions(msg.sender).assertions(Assertions(msg.sender).count())`)
  and refuse windows it does not accept, for example a ruling window too
  short for your evidence period.
- `resolve` arrives exactly once: with the outcome on certification or
  an upheld ruling, with 0 on a refutation, concession or retraction.
  Between the two calls your hold persists however long the case takes.

loopmarket's `LoopEscrow` is the worked example: the subject is a
reservation's key, the outcome is what the wanter is paid, and the escrow
holds the reservation until `resolve`.

## 7. Claims about a key

A claim may concern a key: "the holder of key K holds licence L", or a
negation of it. Pass that key as `about`; the contract announces it in a
`Named` event so K's watcher is told. Readers count a claim against a key
only if it named that key, so a negation certified without K ever seeing
it counts for nothing:

```python
from factbond.ledger import claims_about_from_chain
claims_about_from_chain(reader, K)            # the ids of the claims that named K
```

## 8. Evidence policy

A policy document says, for one domain, what a dispute on each type of
claim runs under: who judges it at each rung and how quickly, the notice
and cure periods, the evidence period for a claim the asserter must prove,
the evidence fee, the cap on what a challenger pays, and the finality
window. Its hash is what a claim pins.

```python
from factbond.policy import shipped, load
doc = shipped("credential")                   # the placeholder policy shipped with the package
rule = doc.rule("self-knowable")
rule.ruling_window()                          # the ruling window an assertion of this class needs
doc.policy_ref                                # SHA-256 of the canonical encoding
load(doc.canonical_bytes(), ref=doc.policy_ref) == doc
```

A document that breaks a fixed rule does not load: a class without a
named, bonded final rung, a token vote at any rung, a structural claim
not settled by certificate alone, an evidence period outside the
`self-knowable` class, and the rest listed in `factbond/policy.py`.

## 9. The adjudicator's procedure

`factbond.procedure.decide(case, now)` applies the rules that come before
the merits, so every rung applies them the same way:

- **A label is refused.** A contest must name a claim record the policy
  covers; "fraudster" is not one, and the accused wins.
- **Notice first, for a claim on a reservation.** The claimant cites a
  notice to the giver; the cure deadline must have passed, the notice must
  not have expired, and the giver must not have cured in time. A dispute
  of a live assertion needs no notice: the dispute itself is the notice.
- **Silence counts only after notice.** Where the asserter must prove its
  claim, silence through the evidence period is ruled against it on the
  record; late evidence still goes to the merits.

```python
from factbond.procedure import Accusation, Case, decide, ruling_record
case = Case(doc, Accusation(challenger, asserter, claim.claim_id, disputed_at), claim,
            disputed_claim=claim.claim_id)        # a dispute of a live assertion
d = decide(case, now)
d.kind, d.rule, d.upheld(accuser_is_asserter=False)   # after a silent evidence period: ("ex-parte", "A5", False)
record = ruling_record(case, d, adjudicator=ADJUDICATOR, outcome="refuted", time=now,
                       dispute_ref=f"assertion:{id_}")
```

`d.upheld(...)` is the argument to pass to `rule`. The ruling record
carries the referred fact, the notices, the submissions or their lapse,
the category, the policy version and the rule applied; a record missing
any of these does not load.

## 10. Reading the ledger

The calibration ledger is the contract's events; the views derive from
them, count only negatives, and take a look-back:

```python
from factbond.ledger import loss_view_from_chain, adjudicator_view_from_chain
loss_view_from_chain(reader, now=now, max_loss_age=365 * 86400)
# {asserter: {"losses": [{"id", "subject", "bond", "confidence", "time", "kind"}], "bond_lost": ...}}
adjudicator_view_from_chain(reader)
# {adjudicator: {"reversals": [...], "lapses": [...], "confirmed_on_appeal": [...]}}
```

A dispute the asserter won leaves nothing. A loss's `kind` is `conceded`,
or, given the published ruling records, `refuted`, `silent` or
`procedural` (`ruled` without them). No view ever returns a count of
rulings or a ratio over activity: both can be bought.

## 11. The simulation harness

```bash
python -m factbond.sim run --facts 2000 --ticks 120                  # one cell, ~3 min
python -m factbond.sim run --preset lockers --set cover_rule=cap     # the parcel lockers, under the old cover rule
python -m factbond.sim grid                                          # the parameter grid
python -m factbond.sim curve                                         # the error half-life against consumption
python -m factbond.sim sweeps                                        # volunteers sweeping a district
```

(From a source checkout without installing, prefix `PYTHONPATH=src`.)

A run prints the four panels (the error half-life, the honest
challenger's return, every adversary's return, the pool's solvency), the
calibration anchors and the loss tables, and writes a content-addressed
artifact with `--out`. Every run is exploratory: a scored run
(`--scored`) refuses to start until `preregistration.json` is filled.
`cover_rule="warranty"` (the default) covers a controlled fact only by
its controller's deposit or a surety; `"cap"` is the product before that
rule, kept for comparison.

## 12. With loopmarket

loopmarket's escrow names factbond's contract as the resolver of its
reservations: custody there, adjudication here. How a contested claim on
a deposit runs is sections 2 and 3 above, with the escrow as the consumer
and a notice to the giver first (section 9). loopmarket's own guide
covers the escrow side: `../loopmarket/docs/USER-GUIDE.md` §7.
