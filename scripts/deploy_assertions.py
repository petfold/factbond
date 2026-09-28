"""Deploy contracts/Assertions.sol from its compiled artifact.

    pip install 'factbond[chain]'
    FACTBOND_RPC=https://rpc.gnosischain.com FACTBOND_KEY=0x... \\
      python scripts/deploy_assertions.py ADJUDICATOR TREASURY FEE_WEI FLOOR_WEI \\
        CHALLENGE_S MIN_CHALLENGE_S MAX_CHALLENGE_S RULING_S MAX_RULING_S RULING_FEE_WEI ESCALATION_BPS \\
        [ARBITER ARBITER_FEE_WEI APPEAL_S DEPOSIT_WEI]

Prints the contract address. `ADJUDICATOR` rules on contested claims (rung 3
standing in for the ladder), `TREASURY` receives the assertion fees (the
pool, later), `FEE_WEI` the assertion fee, `FLOOR_WEI` the
adjudication-cost floor for bond and stake; then the default challenge
window and the bounds an asserter's own window keeps, the default (and
shortest) ruling window and the longest, all in seconds; `RULING_FEE_WEI`
what the loser of a ruling pays the adjudicator (at most the floor; the
winner takes the rest); `ESCALATION_BPS` the asserted outcome's share
resolved when no ruling comes (the default, and the most an assertion may
name). The optional last four name the final rung (F6): the arbiter, its
fee (prepaid by an appellant), the appeal window a first ruling is held
through, and the deposit the first rung holds, forfeited on a reversal.
Left out, there is one rung and its ruling pays at once.
"""
import os
import sys

from web3 import Web3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from factbond.assertions import abi  # noqa: E402


def main() -> None:
    rpc, key = os.environ.get("FACTBOND_RPC"), os.environ.get("FACTBOND_KEY")
    if not rpc or not key or len(sys.argv) < 12:
        sys.exit("set FACTBOND_RPC and FACTBOND_KEY; args: ADJUDICATOR TREASURY FEE_WEI FLOOR_WEI "
                 "CHALLENGE_S MIN_CHALLENGE_S MAX_CHALLENGE_S RULING_S MAX_RULING_S RULING_FEE_WEI ESCALATION_BPS")
    adjudicator, treasury = Web3.to_checksum_address(sys.argv[1]), Web3.to_checksum_address(sys.argv[2])
    fee, floor, challenge, lo, hi, ruling, max_ruling, ruling_fee, escalation = (int(x) for x in sys.argv[3:12])
    ladder = ((Web3.to_checksum_address(sys.argv[12]), int(sys.argv[13]), int(sys.argv[14]), int(sys.argv[15]))
              if len(sys.argv) >= 16 else ("0x" + "00" * 20, 0, 0, 0))
    w3 = Web3(Web3.HTTPProvider(rpc))
    account = w3.eth.account.from_key(key)
    art = abi()
    contract = w3.eth.contract(abi=art["abi"], bytecode=art["bytecode"])
    tx = contract.constructor(adjudicator, treasury, fee, floor, challenge, lo, hi, ruling, max_ruling, ruling_fee,
                              escalation, ladder).build_transaction({"from": account.address,
                                                   "nonce": w3.eth.get_transaction_count(account.address)})
    signed = account.sign_transaction(tx)
    receipt = w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed.raw_transaction))
    print(receipt["contractAddress"])


if __name__ == "__main__":
    main()
