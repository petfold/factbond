"""The assertion primitive's consumer edge (2026-09-19): assert with a bond
at a stated confidence, the consumer told to hold; certify by timeout; a
dispute at the odds the confidence sets, the adjudicator's ruling slashing
the loser; escalation when no ruling comes; retraction keeps the fee. Skips
without the `evm` extra (py-solc-x, eth-tester, web3)."""

import importlib.util
import os

import pytest

from factbond import AssertionsClient, BUCKETS

_HAVE_EVM = all(importlib.util.find_spec(m) for m in ("solcx", "eth_tester", "web3"))
pytestmark = pytest.mark.skipif(not _HAVE_EVM, reason="needs the evm extra: pip install 'factbond[evm]'")

HERE = os.path.dirname(__file__)
FEE, FLOOR, CHALLENGE, RULING, WINNER_BPS, ESCALATION_BPS = 10 ** 15, 10 ** 16, 100, 100, 7500, 5000

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
def chain():
    import solcx
    from web3 import EthereumTesterProvider, Web3
    solcx.install_solc("0.8.24")
    compiled = solcx.compile_files([os.path.join(HERE, "..", "contracts", "Assertions.sol")],
                                   output_values=["abi", "bin"], solc_version="0.8.24",
                                   optimize=True, optimize_runs=200, via_ir=True,
                                   allow_paths=os.path.join(HERE, "..", "contracts"))
    art = next(v for k, v in compiled.items() if k.endswith(":Assertions"))
    c_art = solcx.compile_source(CONSUMER_SRC, output_values=["abi", "bin"], solc_version="0.8.24")["<stdin>:Consumer"]
    w3 = Web3(EthereumTesterProvider())
    acc = w3.eth.accounts
    w3.eth.default_account = acc[0]
    adjudicator, treasury = acc[1], acc[9]
    receipt = w3.eth.wait_for_transaction_receipt(
        w3.eth.contract(abi=art["abi"], bytecode=art["bin"]).constructor(
            adjudicator, treasury, FEE, FLOOR, CHALLENGE, RULING, WINNER_BPS, ESCALATION_BPS).transact())
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
    assert "confidence is" in _reverts(a.functions.assert_(subject, consumer.address, 7, 950), asserter, FEE + FLOOR)
    assert "fee plus a bond" in _reverts(a.functions.assert_(subject, consumer.address, 7, 990), asserter, FEE)
    fee_before = w3.eth.get_balance(treasury)
    a.functions.assert_(subject, consumer.address, 7, 990).transact({"from": asserter, "value": FEE + FLOOR})
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
    assert "not my subject" in _reverts(a.functions.assert_(subject, consumer.address, 1, 990), w3.eth.accounts[2], FEE + FLOOR)
    # no consumer: a plain claim, nobody is told
    a.functions.assert_(subject, "0x" + "00" * 20, 1, 990).transact({"from": w3.eth.accounts[2], "value": FEE + FLOOR})
    assert not consumer.functions.held(subject).call()


def test_a_dispute_is_ruled_and_the_loser_is_slashed(chain):
    w3, a, consumer, adjudicator, treasury = chain
    asserter, challenger = w3.eth.accounts[2], w3.eth.accounts[3]
    bond = 10 ** 18
    for subject, upheld in ((b"\x33" * 32, True), (b"\x44" * 32, False)):
        a.functions.assert_(subject, consumer.address, 5, 990).transact({"from": asserter, "value": FEE + bond})
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
        a.functions.rule(id_, upheld).transact({"from": adjudicator})
        assert w3.eth.get_balance(winner) - w_before == (bond if upheld else stake) + lost * WINNER_BPS // 10000
        assert w3.eth.get_balance(treasury) - t_before == lost - lost * WINNER_BPS // 10000
        assert consumer.functions.outcome(subject).call() == (5 if upheld else 0)
        assert a.functions.assertions(id_).call()[10] == (3 if upheld else 4)


def test_no_ruling_escalates_returning_both_stakes(chain):
    w3, a, consumer, adjudicator, treasury = chain
    asserter, challenger = w3.eth.accounts[2], w3.eth.accounts[3]
    subject = b"\x55" * 32
    a.functions.assert_(subject, consumer.address, 1000, 900).transact({"from": asserter, "value": FEE + FLOOR})
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


def test_retraction_returns_the_bond_and_keeps_the_fee(chain):
    w3, a, consumer, adjudicator, treasury = chain
    asserter = w3.eth.accounts[2]
    subject = b"\x66" * 32
    a.functions.assert_(subject, consumer.address, 9, 970).transact({"from": asserter, "value": FEE + FLOOR})
    id_ = a.functions.count().call()
    assert _balance_delta(w3, asserter, a.functions.retract(id_)) == FLOOR
    assert consumer.functions.resolved(subject).call() and consumer.functions.outcome(subject).call() == 0


def test_client_and_shipped_artifact(chain):
    from factbond.assertions import abi
    w3, a, consumer, adjudicator, treasury = chain
    client = AssertionsClient("", a.address, client=w3)
    assert client.fee() == FEE and client.floor() == FLOOR and client.stake_for(10 ** 18, 900) == 10 ** 18 // 9
    last = client.assertion(client.count())
    assert last["status"] == "retracted" and last["confidence"] == 970 and last["consumer"] == consumer.address
    names = {e["name"] for e in abi()["abi"] if e["type"] == "function"}
    assert {"assert_", "dispute", "certify", "rule", "escalate", "retract", "stakeFor"} <= names
    with pytest.raises(ValueError):
        client.assert_(b"\x00" * 32, None, 1, 990)
