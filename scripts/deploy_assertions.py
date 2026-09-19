"""Deploy contracts/Assertions.sol from its compiled artifact.

    pip install 'factbond[chain]'
    FACTBOND_RPC=https://rpc.gnosischain.com FACTBOND_KEY=0x... \\
      python scripts/deploy_assertions.py ADJUDICATOR TREASURY FEE_WEI FLOOR_WEI CHALLENGE_S RULING_S WINNER_BPS ESCALATION_BPS

Prints the contract address. `ADJUDICATOR` rules on contested claims (rung 3
standing in for the ladder), `TREASURY` receives the assertion fees and the
slashing remainder (the pool, later), `FEE_WEI` the assertion fee,
`FLOOR_WEI` the adjudication-cost floor for bond and stake, the two windows
in seconds, `WINNER_BPS` the loser's stake share paid to the winner,
`ESCALATION_BPS` the asserted outcome's share resolved when no ruling comes.
"""
import os
import sys

from web3 import Web3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from factbond.assertions import abi  # noqa: E402


def main() -> None:
    rpc, key = os.environ.get("FACTBOND_RPC"), os.environ.get("FACTBOND_KEY")
    if not rpc or not key or len(sys.argv) < 9:
        sys.exit("set FACTBOND_RPC and FACTBOND_KEY; args: ADJUDICATOR TREASURY FEE_WEI FLOOR_WEI "
                 "CHALLENGE_S RULING_S WINNER_BPS ESCALATION_BPS")
    adjudicator, treasury = Web3.to_checksum_address(sys.argv[1]), Web3.to_checksum_address(sys.argv[2])
    fee, floor, challenge, ruling, winner, escalation = (int(x) for x in sys.argv[3:9])
    w3 = Web3(Web3.HTTPProvider(rpc))
    account = w3.eth.account.from_key(key)
    art = abi()
    contract = w3.eth.contract(abi=art["abi"], bytecode=art["bytecode"])
    tx = contract.constructor(adjudicator, treasury, fee, floor, challenge, ruling, winner, escalation
                              ).build_transaction({"from": account.address,
                                                   "nonce": w3.eth.get_transaction_count(account.address)})
    signed = account.sign_transaction(tx)
    receipt = w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed.raw_transaction))
    print(receipt["contractAddress"])


if __name__ == "__main__":
    main()
