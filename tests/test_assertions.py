"""The assertion primitive's consumer edge (2026-09-19): assert with a bond
at a stated confidence, the consumer told to hold; certify by timeout; a
dispute at the odds the confidence sets, the adjudicator's ruling charging
the loser the ruling fee and the winner taking the rest; the asserter's
concession; escalation when no ruling comes; retraction keeps the fee. F1
(2026-09-28): the window is the asserter's within the deployment's bounds;
the escalation value is per assertion, `UNRESOLVED` keeping the consumer's
hold until a ruling; the ruling window is per assertion, never shorter than
the deployment's (F4). Skips without the `evm` extra (py-solc-x, eth-tester,
web3)."""

import importlib.util
import os

import pytest

from factbond import AssertionsClient, BUCKETS, UNRESOLVED

_HAVE_EVM = all(importlib.util.find_spec(m) for m in ("solcx", "eth_tester", "web3"))
pytestmark = pytest.mark.skipif(not _HAVE_EVM, reason="needs the evm extra: pip install 'factbond[evm]'")

HERE = os.path.dirname(__file__)
FEE, FLOOR, CHALLENGE, RULING, RULING_FEE, ESCALATION_BPS = 10 ** 15, 10 ** 16, 100, 100, 4 * 10 ** 15, 5000
MIN_CHALLENGE, MAX_CHALLENGE, MAX_RULING, DAY = 10, 60 * 86400, 90 * 86400, 86400
DEFAULT = (0, ESCALATION_BPS, 0)          # an assertion that names no window, escalation value or ruling window

CONSUMER_SRC = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract Consumer {                       // remembers what it was told, refuses one subject
    mapping(bytes32 => bool) public held;
    mapping(bytes32 => uint256) public outcome;
    mapping(bytes32 => bool) public resolved;
    bytes32 public refused;
    function refuse(bytes32 s) external { refused = s; }
    function hold(bytes32 s) external { require(s != refused, "not my subject"); held[s] = true; }
    function resolve(bytes32 s, uint256 o) external { require(held[s], "never held"); resolved[s] = true; outcome[s] = o; }
}
"""


@pytest.fixture(scope="module")
def compiled():
    import solcx
    solcx.install_solc("0.8.24")
    out = solcx.compile_files([os.path.join(HERE, "..", "contracts", "Assertions.sol")],
                              output_values=["abi", "bin"], solc_version="0.8.24",
                              optimize=True, optimize_runs=200, via_ir=True,
                              allow_paths=os.path.join(HERE, "..", "contracts"))
    return next(v for k, v in out.items() if k.endswith(":Assertions"))


@pytest.fixture(scope="module")
def chain(compiled):
    import solcx
    from web3 import EthereumTesterProvider, Web3
    art = compiled
    c_art = solcx.compile_source(CONSUMER_SRC, output_values=["abi", "bin"], solc_version="0.8.24")["<stdin>:Consumer"]
    w3 = Web3(EthereumTesterProvider())
    acc = w3.eth.accounts
    w3.eth.default_account = acc[0]
    adjudicator, treasury = acc[1], acc[9]
    receipt = w3.eth.wait_for_transaction_receipt(
        w3.eth.contract(abi=art["abi"], bytecode=art["bin"]).constructor(
            adjudicator, treasury, FEE, FLOOR, CHALLENGE, MIN_CHALLENGE, MAX_CHALLENGE, RULING, MAX_RULING,
            RULING_FEE, ESCALATION_BPS).transact())
    assertions = w3.eth.contract(address=receipt["contractAddress"], abi=art["abi"])
    receipt = w3.eth.wait_for_transaction_receipt(
        w3.eth.contract(abi=c_art["abi"], bytecode=c_art["bin"]).constructor().transact())
    consumer = w3.eth.contract(address=receipt["contractAddress"], abi=c_art["abi"])
    return w3, assertions, consumer, adjudicator, treasury


def _reverts(fn, who, value=0):
    from eth_tester.exceptions import TransactionFailed
    try:
        fn.transact({"from": who, "value": value})
    except (TransactionFailed, ValueError) as exc:
        return str(exc)
    raise AssertionError("did not revert")


def _advance(w3, seconds):
    w3.provider.ethereum_tester.time_travel(w3.eth.get_block("latest")["timestamp"] + seconds)
    w3.provider.ethereum_tester.mine_block()


def _balance_delta(w3, who, fn, **tx):
    before = w3.eth.get_balance(who)
    receipt = w3.eth.wait_for_transaction_receipt(fn.transact({"from": who, **tx}))
    gas = receipt["gasUsed"] * w3.eth.get_transaction(receipt["transactionHash"])["gasPrice"]
    return w3.eth.get_balance(who) - before + gas + tx.get("value", 0)


def test_stake_follows_the_stated_odds_with_a_floor(chain):
    w3, a, consumer, adjudicator, treasury = chain
    bond = 10 ** 18
    assert a.functions.stakeFor(bond, 900).call() == bond * 100 // 900
    assert a.functions.stakeFor(bond, 999).call() == max(bond // 999, FLOOR)
    assert a.functions.stakeFor(FLOOR, 999).call() == FLOOR          # the floor prices dispute spam
    assert all(a.functions.isBucket(c).call() for c in BUCKETS) and not a.functions.isBucket(950).call()


def test_undisputed_certifies_by_timeout_and_the_consumer_is_told(chain):
    w3, a, consumer, adjudicator, treasury = chain
    asserter = w3.eth.accounts[2]
    subject = b"\x11" * 32
    assert "confidence is" in _reverts(a.functions.assert_(subject, consumer.address, 7, 950, *DEFAULT), asserter, FEE + FLOOR)
    assert "fee plus a bond" in _reverts(a.functions.assert_(subject, consumer.address, 7, 990, *DEFAULT), asserter, FEE)
    fee_before = w3.eth.get_balance(treasury)
    a.functions.assert_(subject, consumer.address, 7, 990, *DEFAULT).transact({"from": asserter, "value": FEE + FLOOR})
    assert w3.eth.get_balance(treasury) - fee_before == FEE               # the fee accrues, nothing else (F9)
    assert consumer.functions.held(subject).call() and not consumer.functions.resolved(subject).call()
    id_ = a.functions.count().call()
    assert "challenge window open" in _reverts(a.functions.certify(id_), asserter)
    _advance(w3, CHALLENGE + 1)
    assert "challenge window closed" in _reverts(a.functions.dispute(id_), w3.eth.accounts[3], FLOOR)
    got = _balance_delta(w3, asserter, a.functions.certify(id_))
    assert got == FLOOR                                                    # the bond returns
    assert consumer.functions.resolved(subject).call() and consumer.functions.outcome(subject).call() == 7
    assert a.functions.assertions(id_).call()[10] == 3                    # Certified
    assert "not open" in _reverts(a.functions.certify(id_), asserter)


def test_a_consumer_that_refuses_the_hold_refuses_the_assertion(chain):
    w3, a, consumer, adjudicator, treasury = chain
    subject = b"\x22" * 32
    consumer.functions.refuse(subject).transact()
    assert "not my subject" in _reverts(a.functions.assert_(subject, consumer.address, 1, 990, *DEFAULT), w3.eth.accounts[2], FEE + FLOOR)
    # no consumer: a plain claim, nobody is told
    a.functions.assert_(subject, "0x" + "00" * 20, 1, 990, *DEFAULT).transact({"from": w3.eth.accounts[2], "value": FEE + FLOOR})
    assert not consumer.functions.held(subject).call()


def test_a_dispute_is_ruled_and_the_loser_pays(chain):
    w3, a, consumer, adjudicator, treasury = chain
    asserter, challenger = w3.eth.accounts[2], w3.eth.accounts[3]
    bond = 10 ** 18
    for subject, upheld in ((b"\x33" * 32, True), (b"\x44" * 32, False)):
        a.functions.assert_(subject, consumer.address, 5, 990, *DEFAULT).transact({"from": asserter, "value": FEE + bond})
        id_ = a.functions.count().call()
        stake = a.functions.stakeFor(bond, 990).call()
        assert stake == bond * 10 // 990
        assert "stake below the odds" in _reverts(a.functions.dispute(id_), challenger, stake - 1)
        assert "not the asserter" in _reverts(a.functions.retract(id_), challenger)
        a.functions.dispute(id_).transact({"from": challenger, "value": stake})
        assert "not open" in _reverts(a.functions.retract(id_), asserter)          # locked to the outcome
        assert "not the adjudicator" in _reverts(a.functions.rule(id_, True), challenger)
        assert "ruling window open" in _reverts(a.functions.escalate(id_), challenger)
        t_before = w3.eth.get_balance(treasury)
        winner, loser, lost = (asserter, challenger, stake) if upheld else (challenger, asserter, bond)
        w_before = w3.eth.get_balance(winner)
        got = _balance_delta(w3, adjudicator, a.functions.rule(id_, upheld))
        assert w3.eth.get_balance(winner) - w_before == (bond if upheld else stake) + lost - RULING_FEE
        assert got == RULING_FEE                                            # the cost, and nothing more
        assert w3.eth.get_balance(treasury) == t_before                     # no slice to anyone else
        assert consumer.functions.outcome(subject).call() == (5 if upheld else 0)
        assert a.functions.assertions(id_).call()[10] == (3 if upheld else 4)


def test_no_ruling_escalates_returning_both_stakes(chain):
    w3, a, consumer, adjudicator, treasury = chain
    asserter, challenger = w3.eth.accounts[2], w3.eth.accounts[3]
    subject = b"\x55" * 32
    a.functions.assert_(subject, consumer.address, 1000, 900, *DEFAULT).transact({"from": asserter, "value": FEE + FLOOR})
    id_ = a.functions.count().call()
    stake = a.functions.stakeFor(FLOOR, 900).call()
    a.functions.dispute(id_).transact({"from": challenger, "value": stake})
    _advance(w3, RULING + 1)
    assert "ruling window closed" in _reverts(a.functions.rule(id_, True), adjudicator)
    a_before, c_before = w3.eth.get_balance(asserter), w3.eth.get_balance(challenger)
    a.functions.escalate(id_).transact({"from": w3.eth.accounts[4]})
    assert w3.eth.get_balance(asserter) - a_before == FLOOR and w3.eth.get_balance(challenger) - c_before == stake
    assert consumer.functions.outcome(subject).call() == 1000 * ESCALATION_BPS // 10000
    assert a.functions.assertions(id_).call()[10] == 6


def test_the_window_is_the_asserters_within_the_bounds(chain, compiled):
    """F1's gate: a 30-day assertion is disputable on day 29 and certifiable
    on day 31; out-of-bounds windows are refused; 0 takes the default."""
    w3, a, consumer, adjudicator, treasury = chain
    asserter, challenger = w3.eth.accounts[2], w3.eth.accounts[3]
    for window in (MIN_CHALLENGE - 1, MAX_CHALLENGE + 1):
        assert "window out of bounds" in _reverts(
            a.functions.assert_(b"\x77" * 32, consumer.address, 1, 990, window, ESCALATION_BPS, 0), asserter, FEE + FLOOR)
    ids = []
    for subject in (b"\x78" * 32, b"\x79" * 32):
        receipt = w3.eth.wait_for_transaction_receipt(a.functions.assert_(
            subject, consumer.address, 1, 990, 30 * DAY, ESCALATION_BPS, 0).transact({"from": asserter, "value": FEE + FLOOR}))
        ev = a.events.Asserted().process_receipt(receipt)[0]["args"]
        assert ev["challengeUntil"] == w3.eth.get_block(receipt["blockNumber"])["timestamp"] + 30 * DAY
        ids.append(ev["id"])
    _advance(w3, 29 * DAY)
    assert "challenge window open" in _reverts(a.functions.certify(ids[1]), asserter)
    a.functions.dispute(ids[0]).transact({"from": challenger, "value": a.functions.stakeFor(FLOOR, 990).call()})
    assert a.functions.assertions(ids[0]).call()[10] == 2                  # Contested on day 29
    _advance(w3, 2 * DAY)
    assert "challenge window closed" in _reverts(a.functions.dispute(ids[1]), challenger, FLOOR)
    a.functions.certify(ids[1]).transact({"from": w3.eth.accounts[4]})
    assert a.functions.assertions(ids[1]).call()[10] == 3                  # Certified on day 31
    # window 0 is the deployment's default
    receipt = w3.eth.wait_for_transaction_receipt(a.functions.assert_(
        b"\x7a" * 32, consumer.address, 1, 990, *DEFAULT).transact({"from": asserter, "value": FEE + FLOOR}))
    ev = a.events.Asserted().process_receipt(receipt)[0]["args"]
    assert ev["challengeUntil"] == w3.eth.get_block(receipt["blockNumber"])["timestamp"] + CHALLENGE
    # a deployment whose default falls outside its own bounds never exists
    for lo, default, hi in ((0, CHALLENGE, MAX_CHALLENGE), (CHALLENGE + 1, CHALLENGE, MAX_CHALLENGE),
                            (MIN_CHALLENGE, CHALLENGE, CHALLENGE - 1)):
        assert "window bounds" in _reverts(w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bin"]).constructor(
            adjudicator, treasury, FEE, FLOOR, default, lo, hi, RULING, MAX_RULING, RULING_FEE, ESCALATION_BPS),
            w3.eth.accounts[0])


def test_an_unresolved_escalation_keeps_the_hold_until_a_ruling(chain):
    """D10's gate: a boolean claim escalated with no ruling reads as
    unresolved, not 0 — the stakes return, the consumer is not told, and a
    later ruling is what resolves it, moving only the record and the
    consumer. A share above the deployment's is refused; a lower one holds."""
    w3, a, consumer, adjudicator, treasury = chain
    asserter, challenger = w3.eth.accounts[2], w3.eth.accounts[3]
    assert a.functions.UNRESOLVED().call() == UNRESOLVED
    assert "escalation above" in _reverts(a.functions.assert_(
        b"\x88" * 32, consumer.address, 1, 990, 0, ESCALATION_BPS + 1, 0), asserter, FEE + FLOOR)
    subject = b"\x89" * 32
    a.functions.assert_(subject, consumer.address, 1, 990, 0, UNRESOLVED, 0).transact({"from": asserter, "value": FEE + FLOOR})
    id_ = a.functions.count().call()
    stake = a.functions.stakeFor(FLOOR, 990).call()
    a.functions.dispute(id_).transact({"from": challenger, "value": stake})
    _advance(w3, RULING + 1)
    a_before, c_before = w3.eth.get_balance(asserter), w3.eth.get_balance(challenger)
    receipt = w3.eth.wait_for_transaction_receipt(a.functions.escalate(id_).transact({"from": w3.eth.accounts[4]}))
    assert w3.eth.get_balance(asserter) - a_before == FLOOR and w3.eth.get_balance(challenger) - c_before == stake
    from web3.logs import DISCARD
    assert a.events.Unresolved().process_receipt(receipt) and not a.events.Escalated().process_receipt(receipt, errors=DISCARD)
    assert a.functions.assertions(id_).call()[10] == 7                     # Unresolved
    assert consumer.functions.held(subject).call() and not consumer.functions.resolved(subject).call()
    assert "not the adjudicator" in _reverts(a.functions.rule(id_, False), challenger)
    assert "not contested" in _reverts(a.functions.escalate(id_), challenger)
    _advance(w3, 10 * RULING)                                              # the next rung has no clock here
    before = [w3.eth.get_balance(x) for x in (asserter, challenger, treasury)]
    receipt = w3.eth.wait_for_transaction_receipt(a.functions.rule(id_, False).transact({"from": adjudicator}))
    assert [w3.eth.get_balance(x) for x in (asserter, challenger, treasury)] == before  # nothing left to move
    assert a.events.Refuted().process_receipt(receipt)
    assert consumer.functions.resolved(subject).call() and consumer.functions.outcome(subject).call() == 0
    assert a.functions.assertions(id_).call()[10] == 4
    assert "not contested" in _reverts(a.functions.rule(id_, True), adjudicator)
    # a share below the deployment's: the asserter's to lower, never to raise
    subject = b"\x8a" * 32
    a.functions.assert_(subject, consumer.address, 1000, 990, 0, 2500, 0).transact({"from": asserter, "value": FEE + FLOOR})
    id_ = a.functions.count().call()
    a.functions.dispute(id_).transact({"from": challenger, "value": stake})
    _advance(w3, RULING + 1)
    a.functions.escalate(id_).transact({"from": w3.eth.accounts[4]})
    assert consumer.functions.outcome(subject).call() == 250 and a.functions.assertions(id_).call()[10] == 6


def test_the_ruling_window_is_the_asserters_only_ever_longer(chain, compiled):
    """F4's clock on chain: an asserter who carries the burden names a ruling
    window long enough for its evidence period and the rung's ruling period,
    so the adjudicator can rule on its silence before the dispute escalates;
    a window shorter than the deployment's, or beyond its bound, is refused."""
    w3, a, consumer, adjudicator, treasury = chain
    asserter, challenger = w3.eth.accounts[2], w3.eth.accounts[3]
    for ruling in (RULING - 1, MAX_RULING + 1):
        assert "ruling window out of bounds" in _reverts(a.functions.assert_(
            b"\x90" * 32, consumer.address, 1, 990, 0, UNRESOLVED, ruling), asserter, FEE + FLOOR)
    subject = b"\x91" * 32
    receipt = w3.eth.wait_for_transaction_receipt(a.functions.assert_(
        subject, consumer.address, 1, 990, 0, UNRESOLVED, 42 * DAY).transact({"from": asserter, "value": FEE + FLOOR}))
    id_ = a.events.Asserted().process_receipt(receipt)[0]["args"]["id"]
    assert a.events.Asserted().process_receipt(receipt)[0]["args"]["rulingWindow"] == 42 * DAY
    receipt = w3.eth.wait_for_transaction_receipt(a.functions.dispute(id_).transact(
        {"from": challenger, "value": a.functions.stakeFor(FLOOR, 990).call()}))
    disputed_at = w3.eth.get_block(receipt["blockNumber"])["timestamp"]
    assert a.functions.assertions(id_).call()[9] == disputed_at + 42 * DAY
    _advance(w3, 41 * DAY)
    assert "ruling window open" in _reverts(a.functions.escalate(id_), challenger)
    a.functions.rule(id_, False).transact({"from": adjudicator})          # on day 41 the rung can still rule
    assert a.functions.assertions(id_).call()[10] == 4
    assert "ruling bounds" in _reverts(w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bin"]).constructor(
        adjudicator, treasury, FEE, FLOOR, CHALLENGE, MIN_CHALLENGE, MAX_CHALLENGE, RULING, RULING - 1,
        RULING_FEE, ESCALATION_BPS), w3.eth.accounts[0])


def test_the_adjudicator_path_carries_the_procedure_to_chain(chain):
    """F4 end to end: a self-knowable claim asserted with its policy's
    ruling window; the challenger disputes on chain at once (a dispute of a
    live assertion takes no notice: it is the notice), the asserter produces
    nothing in the evidence period, and the rung's ex parte ruling refutes it
    inside the ruling window. A label on a second assertion is refused, and
    the asserter keeps its bond."""
    from factbond.policy import shipped
    from factbond.procedure import Accusation, Case, decide
    from factbond.sim.records import Claim
    w3, a, consumer, adjudicator, treasury = chain
    asserter, challenger = w3.eth.accounts[5], w3.eth.accounts[6]
    policy = shipped("credential")
    rule = policy.rule("self-knowable")
    now = lambda: w3.eth.get_block("latest")["timestamp"]  # noqa: E731
    ids = []
    for n in (1, 2):
        claim = Claim(f"cred/{asserter}/licence-{n}", "root:register@1", "self-knowable", policy.policy_ref)
        a.functions.assert_(bytes.fromhex(claim.claim_id), "0x" + "00" * 20, 1, 990, 30 * DAY, rule.escalation_arg(),
                            rule.ruling_window()).transact({"from": asserter, "value": FEE + FLOOR})
        ids.append((a.functions.count().call(), claim))
    assert rule.ruling_window_fits(rule.ruling_window()) and not rule.ruling_window_fits(RULING)
    (id_, claim), (id_label, _) = ids
    _advance(w3, DAY)
    stake = a.functions.stakeFor(FLOOR, 990).call()
    for i in (id_, id_label):
        a.functions.dispute(i).transact({"from": challenger, "value": stake})
    acc = Accusation(challenger, asserter, claim.claim_id, now())
    case = Case(policy, acc, claim, disputed_claim=claim.claim_id)
    assert decide(case, now()).kind == "pending"                           # the evidence period runs
    label = Case(policy, Accusation(challenger, asserter, "label:unlicensed quack", now()), None)
    d_label = decide(label, now())
    assert d_label.kind == "refused" and d_label.upheld(accuser_is_asserter=False) is True
    a.functions.rule(id_label, d_label.upheld(accuser_is_asserter=False)).transact({"from": adjudicator})
    assert a.functions.assertions(id_label).call()[10] == 3                # the asserter's claim stands
    _advance(w3, rule.evidence_period + DAY)
    d = decide(case, now())
    assert d.kind == "ex-parte" and d.upheld(accuser_is_asserter=False) is False
    before = w3.eth.get_balance(challenger)
    a.functions.rule(id_, d.upheld(accuser_is_asserter=False)).transact({"from": adjudicator})
    assert a.functions.assertions(id_).call()[10] == 4                     # Refuted, inside its ruling window
    assert w3.eth.get_balance(challenger) - before == stake + FLOOR - RULING_FEE


def test_the_asserter_concedes_and_nobody_rules(chain, compiled):
    """Concession, the loser's own act: the challenger takes the whole bond
    and its stake back, no fee is due, the correction feed fires with
    `ruled` false, and the consumer learns nothing of the outcome. Only the
    asserter concedes, and only a contested claim. A floor that would not
    cover the ruling fee never deploys."""
    w3, a, consumer, adjudicator, treasury = chain
    asserter, challenger = w3.eth.accounts[2], w3.eth.accounts[3]
    subject, bond = b"\x92" * 32, 10 ** 17
    a.functions.assert_(subject, consumer.address, 24, 970, *DEFAULT).transact({"from": asserter, "value": FEE + bond})
    id_ = a.functions.count().call()
    assert "not contested" in _reverts(a.functions.concede(id_), asserter)
    stake = a.functions.stakeFor(bond, 970).call()
    a.functions.dispute(id_).transact({"from": challenger, "value": stake})
    assert "not the asserter" in _reverts(a.functions.concede(id_), challenger)
    before = [w3.eth.get_balance(x) for x in (challenger, adjudicator, treasury)]
    receipt = w3.eth.wait_for_transaction_receipt(a.functions.concede(id_).transact({"from": asserter}))
    after = [w3.eth.get_balance(x) for x in (challenger, adjudicator, treasury)]
    assert after[0] - before[0] == stake + bond and after[1:] == before[1:]
    assert a.events.Refuted().process_receipt(receipt)[0]["args"]["ruled"] is False
    assert a.functions.assertions(id_).call()[10] == 4
    assert consumer.functions.resolved(subject).call() and consumer.functions.outcome(subject).call() == 0
    assert "not contested" in _reverts(a.functions.rule(id_, True), adjudicator)
    assert "the floor covers the ruling fee" in _reverts(w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bin"]).constructor(
        adjudicator, treasury, FEE, FLOOR, CHALLENGE, MIN_CHALLENGE, MAX_CHALLENGE, RULING, MAX_RULING, FLOOR + 1,
        ESCALATION_BPS), w3.eth.accounts[0])


def test_retraction_returns_the_bond_and_keeps_the_fee(chain):
    w3, a, consumer, adjudicator, treasury = chain
    asserter = w3.eth.accounts[2]
    subject = b"\x66" * 32
    a.functions.assert_(subject, consumer.address, 9, 970, *DEFAULT).transact({"from": asserter, "value": FEE + FLOOR})
    id_ = a.functions.count().call()
    assert _balance_delta(w3, asserter, a.functions.retract(id_)) == FLOOR
    assert consumer.functions.resolved(subject).call() and consumer.functions.outcome(subject).call() == 0


def test_client_and_shipped_artifact(chain):
    from factbond.assertions import abi
    w3, a, consumer, adjudicator, treasury = chain
    client = AssertionsClient("", a.address, client=w3)
    assert client.fee() == FEE and client.floor() == FLOOR and client.stake_for(10 ** 18, 900) == 10 ** 18 // 9
    assert client.window_bounds() == (MIN_CHALLENGE, CHALLENGE, MAX_CHALLENGE) and client.escalation_bps() == ESCALATION_BPS
    assert client.ruling_bounds() == (RULING, MAX_RULING) and client.ruling_fee() == RULING_FEE
    last = client.assertion(client.count())
    assert last["status"] == "retracted" and last["confidence"] == 970 and last["consumer"] == consumer.address
    assert last["escalation"] == ESCALATION_BPS and last["ruling_window"] == RULING
    names = {e["name"] for e in abi()["abi"] if e["type"] == "function"}
    assert {"assert_", "dispute", "certify", "rule", "escalate", "retract", "concede", "stakeFor", "UNRESOLVED",
            "minChallengeSeconds", "maxChallengeSeconds", "maxRulingSeconds"} <= names
    shipped = next(e for e in abi()["abi"] if e.get("name") == "assert_")
    assert [i["name"] for i in shipped["inputs"]][-3:] == ["window", "escalation", "rulingWindow"]  # rebuilt
    with pytest.raises(ValueError):
        client.assert_(b"\x00" * 32, None, 1, 990)
