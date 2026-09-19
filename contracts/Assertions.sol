// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// The bonded assertion's consumer-facing edge (factbond Phase 1, first
/// step, 2026-09-19; DESIGN.md §3 and §7, mechanism-design.md §1–§4,
/// loopmarket-coupling.md §3b). One party asserts a claim about a
/// `subject` — a bytes32 the consumer chose — backed by a bond and a stated
/// confidence; the world may dispute it within a window by staking at the
/// odds the confidence sets; undisputed claims certify by timeout; only a
/// disputed claim reaches the adjudicator. The contract knows nothing of
/// what a subject means: a `consumer` contract, if named, is told twice —
/// `hold(subject)` when the assertion opens, `resolve(subject, outcome)`
/// when it closes — and `outcome` is an integer the consumer interprets
/// (loopmarket's escrow: the payout of a reservation; a Wikidata guarantee:
/// a corrected value's hash; a boolean claim: 1). No registration: the
/// consumer's acceptance of `hold` is what ties an assertion to a subject,
/// so nobody can pre-empt a subject with a market the consumer never chose.
///
/// What this v0 fixes and what it leaves to the plans:
/// - the confidence buckets {0.9, 0.97, 0.99, 0.999} and the challenger's
///   stake max(B·(1−c)/c, floor) are §1 as written; the asserter's bond has
///   the adjudication-cost floor only — the reliance term is Phase 0's
///   output (§2, gate G-M2);
/// - the assertion fee accrues to `treasury` (the pool, once it exists) and
///   nothing else is ever paid for asserting (F9);
/// - the loser's stake goes mostly to the winner, the rest to the treasury
///   (DESIGN.md §8's slashing split, `winnerBps`);
/// - the ladder (§4) is one rung here — `adjudicator`, the independent
///   arbitrator of rung 3 standing in for rungs 0–2 — and a dispute with no
///   ruling inside `rulingSeconds` *escalates*: v0's stand-in for the next
///   rung returns both stakes and resolves the subject at `escalationBps`
///   of the asserted outcome, so neither side wants to get there (decided
///   with Peter 2026-09-19: escalation after the agreed period, never a
///   default that rewards an absent adjudicator or a claimant);
/// - `Certified` is a process fact, not truth (F7): nobody found it worth
///   disputing, at these stakes, under this procedure.
interface IConsumer {
    function hold(bytes32 subject) external;
    function resolve(bytes32 subject, uint256 outcome) external;
}

contract Assertions {
    enum Status { None, Asserted, Contested, Certified, Refuted, Retracted, Escalated }

    struct Assertion {
        address asserter;
        address challenger;
        address consumer;       // address(0): a plain claim, nobody is told
        bytes32 subject;
        uint256 outcome;        // what the asserter claims, in the consumer's units
        uint16 confidence;      // per mille: 900, 970, 990 or 999
        uint256 bond;           // the asserter's, at risk
        uint256 stake;          // the challenger's, at risk once disputed
        uint64 challengeUntil;  // a dispute may open until here; after, anyone certifies
        uint64 rulingUntil;     // the adjudicator rules until here; after, anyone escalates
        Status status;
    }

    address public owner;
    address public adjudicator;   // rung 3 today; the ladder later
    address public treasury;      // the pool's address once it exists
    uint256 public feeWei;        // the assertion fee (spam price, the pool's revenue)
    uint256 public floorWei;      // the adjudication-cost floor for bond and stake alike
    uint64 public challengeSeconds;
    uint64 public rulingSeconds;
    uint16 public winnerBps;      // of the loser's stake, to the winner; the rest to the treasury
    uint16 public escalationBps;  // of the outcome, resolved when no ruling arrives
    uint256 public count;
    mapping(uint256 => Assertion) public assertions;

    event Asserted(uint256 indexed id, bytes32 indexed subject, address indexed asserter, address consumer,
                   uint256 outcome, uint16 confidence, uint256 bond);
    event Disputed(uint256 indexed id, address indexed challenger, uint256 stake);
    event Certified(uint256 indexed id, bytes32 indexed subject, uint256 outcome, bool ruled);
    event Refuted(uint256 indexed id, bytes32 indexed subject);    // the correction feed's event (DESIGN.md §7)
    event Retracted(uint256 indexed id);
    event Escalated(uint256 indexed id, bytes32 indexed subject, uint256 outcome);

    constructor(address adjudicator_, address treasury_, uint256 feeWei_, uint256 floorWei_,
                uint64 challengeSeconds_, uint64 rulingSeconds_, uint16 winnerBps_, uint16 escalationBps_) {
        require(winnerBps_ <= 10000 && escalationBps_ <= 10000, "bps");
        owner = msg.sender;
        adjudicator = adjudicator_; treasury = treasury_;
        feeWei = feeWei_; floorWei = floorWei_;
        challengeSeconds = challengeSeconds_; rulingSeconds = rulingSeconds_;
        winnerBps = winnerBps_; escalationBps = escalationBps_;
    }

    function setAdjudicator(address adjudicator_) external {
        require(msg.sender == owner, "not the owner");
        adjudicator = adjudicator_;
    }

    function isBucket(uint16 c) public pure returns (bool) {
        return c == 900 || c == 970 || c == 990 || c == 999;
    }

    /// The challenger's stake for an assertion at confidence `c` with bond
    /// `bond`: max(bond × (1000 − c) / c, floor) — §1's odds, pro-rated.
    function stakeFor(uint256 bond, uint16 c) public view returns (uint256) {
        uint256 odds = bond * (1000 - c) / c;
        return odds > floorWei ? odds : floorWei;
    }

    // ---- assert ----------------------------------------------------------------

    /// Post a claim: msg.value is the fee plus the bond (at least the floor).
    /// With a consumer, the consumer is told to hold the subject and may
    /// refuse — an assertion the consumer does not recognise never opens.
    function assert_(bytes32 subject, address consumer, uint256 outcome, uint16 confidence)
            external payable returns (uint256 id) {
        require(isBucket(confidence), "confidence is 0.9, 0.97, 0.99 or 0.999");
        require(msg.value >= feeWei + floorWei, "fee plus a bond at least the floor");
        uint256 bond = msg.value - feeWei;
        id = ++count;
        Assertion storage a = assertions[id];
        a.asserter = msg.sender; a.consumer = consumer; a.subject = subject; a.outcome = outcome;
        a.confidence = confidence; a.bond = bond;
        a.challengeUntil = uint64(block.timestamp) + challengeSeconds;
        a.status = Status.Asserted;
        if (feeWei > 0) _pay(payable(treasury), feeWei);
        if (consumer != address(0)) IConsumer(consumer).hold(subject);
        emit Asserted(id, subject, msg.sender, consumer, outcome, confidence, bond);
    }

    /// An undisputed assertion may be withdrawn: the bond returns, the fee
    /// never does (a capital-free renege would be a free option, §1).
    function retract(uint256 id) external {
        Assertion storage a = assertions[id];
        require(msg.sender == a.asserter, "not the asserter");
        require(a.status == Status.Asserted, "not open");
        a.status = Status.Retracted;
        _pay(payable(a.asserter), a.bond);
        if (a.consumer != address(0)) IConsumer(a.consumer).resolve(a.subject, 0);
        emit Retracted(id);
    }

    // ---- dispute -----------------------------------------------------------------

    function dispute(uint256 id) external payable {
        Assertion storage a = assertions[id];
        require(a.status == Status.Asserted, "not open");
        require(block.timestamp <= a.challengeUntil, "challenge window closed");
        require(msg.value >= stakeFor(a.bond, a.confidence), "stake below the odds");
        a.challenger = msg.sender; a.stake = msg.value;
        a.rulingUntil = uint64(block.timestamp) + rulingSeconds;
        a.status = Status.Contested;
        emit Disputed(id, msg.sender, msg.value);
    }

    /// Undisputed after the window: certified by timeout, the bond returns.
    function certify(uint256 id) external {
        Assertion storage a = assertions[id];
        require(a.status == Status.Asserted, "not open");
        require(block.timestamp > a.challengeUntil, "challenge window open");
        a.status = Status.Certified;
        _pay(payable(a.asserter), a.bond);
        if (a.consumer != address(0)) IConsumer(a.consumer).resolve(a.subject, a.outcome);
        emit Certified(id, a.subject, a.outcome, false);
    }

    /// The adjudicator's ruling on a contested claim: the loser's stake goes
    /// mostly to the winner, the rest to the treasury; the consumer learns
    /// the asserted outcome or nothing of it.
    function rule(uint256 id, bool upheld) external {
        Assertion storage a = assertions[id];
        require(msg.sender == adjudicator, "not the adjudicator");
        require(a.status == Status.Contested, "not contested");
        require(block.timestamp <= a.rulingUntil, "ruling window closed");
        address payable winner = payable(upheld ? a.asserter : a.challenger);
        uint256 own = upheld ? a.bond : a.stake;
        uint256 lost = upheld ? a.stake : a.bond;
        uint256 toWinner = lost * winnerBps / 10000;
        a.status = upheld ? Status.Certified : Status.Refuted;
        _pay(winner, own + toWinner);
        if (lost - toWinner > 0) _pay(payable(treasury), lost - toWinner);
        if (a.consumer != address(0)) IConsumer(a.consumer).resolve(a.subject, upheld ? a.outcome : 0);
        if (upheld) emit Certified(id, a.subject, a.outcome, true);
        else emit Refuted(id, a.subject);
    }

    /// No ruling inside the window: the next rung — v0's stand-in returns
    /// both stakes and resolves at `escalationBps` of the asserted outcome.
    function escalate(uint256 id) external {
        Assertion storage a = assertions[id];
        require(a.status == Status.Contested, "not contested");
        require(block.timestamp > a.rulingUntil, "ruling window open");
        a.status = Status.Escalated;
        uint256 outcome = a.outcome * escalationBps / 10000;
        _pay(payable(a.asserter), a.bond);
        _pay(payable(a.challenger), a.stake);
        if (a.consumer != address(0)) IConsumer(a.consumer).resolve(a.subject, outcome);
        emit Escalated(id, a.subject, outcome);
    }

    function _pay(address payable to, uint256 amount) private {
        (bool ok, ) = to.call{value: amount}("");
        require(ok, "payment failed");
    }
}
