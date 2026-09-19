"""The bonded assertion on chain (`contracts/Assertions.sol`): assert a
claim about a subject with a bond and a stated confidence; dispute at the
odds the confidence sets; certify by timeout; the adjudicator rules only on
a contested claim; a consumer contract, if named, is told `hold` and
`resolve`. `AssertionsClient` sends and reads; web3 loads lazily behind the
`chain` extra. The contract's own docstring is the design record for what
v0 fixes and what waits for the plans."""

from __future__ import annotations

import json

#: the four confidence buckets, per mille (mechanism-design.md §1)
BUCKETS = (900, 970, 990, 999)

STATUS = ("none", "asserted", "contested", "certified", "refuted", "retracted", "escalated")


def abi() -> dict:
    """The compiled `Assertions` (solc 0.8.24, via IR, optimizer 200 runs),
    shipped as `factbond/contracts/Assertions.json` by `scripts/build.py`."""
    from importlib import resources
    with resources.files("factbond").joinpath("contracts", "Assertions.json").open(encoding="utf-8") as fh:
        return json.load(fh)


class AssertionsClient:
    """`Assertions` at `address` on the chain behind `rpc_url`. `key` signs
    (an asserter's, a challenger's, the adjudicator's); reading needs none.
    `client` may be a web3 instance (tests, embedders)."""

    def __init__(self, rpc_url: str, address: str, *, key: str | None = None, client=None):
        self.rpc_url, self.address, self._key, self._client = rpc_url, address, key, client

    def _web3(self):
        if self._client is None:
            try:
                from web3 import Web3
            except ImportError as exc:
                raise RuntimeError("the chain needs web3: pip install 'factbond[chain]'") from exc
            self._client = Web3(Web3.HTTPProvider(self.rpc_url))
        return self._client

    def contract(self):
        return self._web3().eth.contract(address=self.address, abi=abi()["abi"])

    def account(self):
        if not self._key:
            raise ValueError("a transaction needs a key")
        return self._web3().eth.account.from_key(self._key)

    def _send(self, fn, value: int = 0):
        w3 = self._web3()
        account = self.account()
        tx = {"from": account.address, "nonce": w3.eth.get_transaction_count(account.address), "value": value}
        signed = account.sign_transaction(fn.build_transaction(tx))
        return w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed.raw_transaction))

    # ---- parameters ----------------------------------------------------------

    def fee(self) -> int:
        return self.contract().functions.feeWei().call()

    def floor(self) -> int:
        return self.contract().functions.floorWei().call()

    def stake_for(self, bond: int, confidence: int) -> int:
        return self.contract().functions.stakeFor(bond, confidence).call()

    # ---- the lifecycle -------------------------------------------------------

    def assert_(self, subject: bytes, consumer: str | None, outcome: int, confidence: int,
                bond: int | None = None) -> tuple[int, dict]:
        """Post a claim; the bond defaults to the floor. Returns (id, receipt)."""
        if confidence not in BUCKETS:
            raise ValueError(f"confidence is one of {BUCKETS} per mille")
        c = self.contract()
        bond = self.floor() if bond is None else bond
        receipt = self._send(c.functions.assert_(subject, consumer or "0x" + "00" * 20, outcome, confidence),
                             value=self.fee() + bond)
        return c.events.Asserted().process_receipt(receipt)[0]["args"]["id"], receipt

    def dispute(self, id_: int, stake: int | None = None) -> dict:
        a = self.assertion(id_)
        stake = self.stake_for(a["bond"], a["confidence"]) if stake is None else stake
        return self._send(self.contract().functions.dispute(id_), value=stake)

    def certify(self, id_: int) -> dict:
        return self._send(self.contract().functions.certify(id_))

    def rule(self, id_: int, upheld: bool) -> dict:
        return self._send(self.contract().functions.rule(id_, upheld))

    def escalate(self, id_: int) -> dict:
        return self._send(self.contract().functions.escalate(id_))

    def retract(self, id_: int) -> dict:
        return self._send(self.contract().functions.retract(id_))

    # ---- reads ---------------------------------------------------------------

    def assertion(self, id_: int) -> dict:
        r = self.contract().functions.assertions(id_).call()
        return {"asserter": r[0], "challenger": r[1], "consumer": r[2], "subject": r[3], "outcome": r[4],
                "confidence": r[5], "bond": r[6], "stake": r[7], "challenge_until": r[8],
                "ruling_until": r[9], "status": STATUS[r[10]]}

    def count(self) -> int:
        return self.contract().functions.count().call()
