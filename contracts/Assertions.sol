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
/// - a ruling costs the loser the adjudicator's `rulingFeeWei` and nothing
///   more; the winner takes the rest of the loser's stake (decided with Peter
///   2026-09-28, replacing DESIGN.md §8's 25% slashing slice to the
///   treasury): deductions are costs, and a margin above cost is a price only
///   competition may set, so it is the adjudicator's to charge within its fee,
///   never the protocol's. The fee is at most the floor, so either side's
///   stake covers it; no ruling, no fee (a lapsing rung forfeits it, A3).
///   Laundering stays a loss on the fees alone, as long as surviving a dispute
///   is never a positive signal (THREATS T11);
/// - the asserter may `concede` a contested claim: the challenger takes the
///   whole bond and its own stake back, no adjudicator is needed and no fee
///   is due. Concession is the loser's own signed act, never silence; silence
///   still goes to the adjudicator (the 2026-09-19 principle);
/// - the ladder (§4) is one rung here — `adjudicator`, the independent
///   arbitrator of rung 3 standing in for rungs 0–2 — and a dispute with no
///   ruling inside its ruling window *escalates*: v0's stand-in for the next
///   rung returns both stakes and resolves the subject at the assertion's
///   escalation value, so neither side wants to get there (decided with
///   Peter 2026-09-19: escalation after the agreed period, never a default
///   that rewards an absent adjudicator or a claimant);
/// - the challenge window is the asserter's, per assertion (F1,
///   2026-09-28; assertion-extensions.md §1): `window` seconds in
///   `assert_`, 0 for the deployment's `challengeSeconds`, within
///   [`minChallengeSeconds`, `maxChallengeSeconds`] — the record design's
///   per-assertion liveness (records-and-anchoring.md §2), for which the
///   one constructor value stood in. The ruling window is the asserter's
///   too (F4, 2026-09-28): `rulingWindow` seconds, 0 for the deployment's
///   `rulingSeconds`, otherwise between that and `maxRulingSeconds` — only
///   ever longer, since a shorter one would let an asserter who expects to
///   lose force the escalation that returns its bond. A self-knowable claim
///   needs its evidence period plus the rung's ruling period here, or the
///   adjudicator cannot rule on the asserter's silence before it escalates
///   (`factbond.policy.ClassRule.ruling_window`);
/// - the escalation value is per assertion too (credentials-cover-and-
///   options.md D10, 2026-09-28): a share of the outcome in bps, at most
///   the deployment's `escalationBps` (a lower share only ever costs the
///   asserter), or `UNRESOLVED` — for a boolean or a hash, where a share
///   reads as 0 or as nothing: the stakes return as at any escalation, the
///   consumer is not told, its hold persists, and the adjudicator's later
///   ruling (the next rung; v0's slot is the owner's to refill) is what
///   resolves it. Which value a fact type takes is the evidence policy's
///   (`factbond.policy`), never this contract's. Both are written before
///   `hold` is called, so a consumer with bounds of its own (a longest
///   window, `UNRESOLVED` for cover claims) reads `assertions(count())`
///   inside `hold` and refuses;
/// - `Certified` is a process fact, not truth (F7): nobody found it worth
///   disputing, at these stakes, under this procedure.
interface IConsumer {
    function hold(bytes32 subject) external;
    function resolve(bytes32 subject, uint256 outcome) external;
}

contract Assertions {
    enum Status { None, Asserted, Contested, Certified, Refuted, Retracted, Escalated, Unresolved }

    /// The escalation value that resolves nothing: the consumer's hold
    /// persists until a ruling.
    uint16 public constant UNRESOLVED = type(uint16).max;

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
        uint16 escalation;      // bps of the outcome resolved when no ruling arrives, or UNRESOLVED
        uint64 rulingWindow;    // seconds from a dispute to `rulingUntil`
    }

    address public owner;
    address public adjudicator;   // rung 3 today; the ladder later
    address public treasury;      // the pool's address once it exists
    uint256 public feeWei;        // the assertion fee (spam price, the pool's revenue)
    uint256 public floorWei;      // the adjudication-cost floor for bond and stake alike
    uint64 public challengeSeconds;     // the window of an assertion that names none
    uint64 public minChallengeSeconds;  // the bounds an asserter's window keeps
    uint64 public maxChallengeSeconds;
    uint64 public rulingSeconds;        // the ruling window of an assertion that names none, and the shortest
    uint64 public maxRulingSeconds;
    uint256 public rulingFeeWei;  // the loser pays it to the adjudicator that ruled; at most the floor
    uint16 public escalationBps;  // the most of the outcome an assertion may resolve at when no ruling arrives
    uint256 public count;
    mapping(uint256 => Assertion) public assertions;

    event Asserted(uint256 indexed id, bytes32 indexed subject, address indexed asserter, address consumer,
                   uint256 outcome, uint16 confidence, uint256 bond, uint64 challengeUntil, uint16 escalation,
                   uint64 rulingWindow);
    event Disputed(uint256 indexed id, address indexed challenger, uint256 stake);
    event Certified(uint256 indexed id, bytes32 indexed subject, uint256 outcome, bool ruled);
    event Refuted(uint256 indexed id, bytes32 indexed subject, bool ruled);  // the correction feed's event (DESIGN.md §7);
                                                                             // ruled false: the asserter conceded
    event Retracted(uint256 indexed id);
    event Escalated(uint256 indexed id, bytes32 indexed subject, uint256 outcome);
    event Unresolved(uint256 indexed id, bytes32 indexed subject);  // escalated, the consumer's hold kept

    constructor(address adjudicator_, address treasury_, uint256 feeWei_, uint256 floorWei_,
                uint64 challengeSeconds_, uint64 minChallengeSeconds_, uint64 maxChallengeSeconds_,
                uint64 rulingSeconds_, uint64 maxRulingSeconds_, uint256 rulingFeeWei_, uint16 escalationBps_) {
        require(escalationBps_ <= 10000, "bps");
        require(rulingFeeWei_ <= floorWei_, "the floor covers the ruling fee");
        require(0 < minChallengeSeconds_ && minChallengeSeconds_ <= challengeSeconds_
                && challengeSeconds_ <= maxChallengeSeconds_, "window bounds");
        require(0 < rulingSeconds_ && rulingSeconds_ <= maxRulingSeconds_, "ruling bounds");
        owner = msg.sender;
        adjudicator = adjudicator_; treasury = treasury_;
        feeWei = feeWei_; floorWei = floorWei_;
        challengeSeconds = challengeSeconds_; rulingSeconds = rulingSeconds_;
        minChallengeSeconds = minChallengeSeconds_; maxChallengeSeconds = maxChallengeSeconds_;
        maxRulingSeconds = maxRulingSeconds_;
        rulingFeeWei = rulingFeeWei_; escalationBps = escalationBps_;
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
    /// `window` is how long a dispute may open, in seconds (0: the default);
    /// `escalation` what the subject resolves at if a dispute gets no ruling
    /// (bps of `outcome`, at most `escalationBps`, or UNRESOLVED);
    /// `rulingWindow` how long the adjudicator has once disputed (0: the
    /// default, never shorter). With a consumer, the consumer is told to hold
    /// the subject and may refuse — an assertion the consumer does not
    /// recognise never opens.
    function assert_(bytes32 subject, address consumer, uint256 outcome, uint16 confidence,
                     uint64 window, uint16 escalation, uint64 rulingWindow)
            external payable returns (uint256 id) {
        require(isBucket(confidence), "confidence is 0.9, 0.97, 0.99 or 0.999");
        require(msg.value >= feeWei + floorWei, "fee plus a bond at least the floor");
        if (window == 0) window = challengeSeconds;
        require(minChallengeSeconds <= window && window <= maxChallengeSeconds, "window out of bounds");
        require(escalation <= escalationBps || escalation == UNRESOLVED, "escalation above the deployment's");
        if (rulingWindow == 0) rulingWindow = rulingSeconds;
        require(rulingSeconds <= rulingWindow && rulingWindow <= maxRulingSeconds, "ruling window out of bounds");
        uint256 bond = msg.value - feeWei;
        id = ++count;
        Assertion storage a = assertions[id];
        a.asserter = msg.sender; a.consumer = consumer; a.subject = subject; a.outcome = outcome;
        a.confidence = confidence; a.bond = bond;
        a.challengeUntil = uint64(block.timestamp) + window;
        a.status = Status.Asserted; a.escalation = escalation; a.rulingWindow = rulingWindow;
        if (feeWei > 0) _pay(payable(treasury), feeWei);
        if (consumer != address(0)) IConsumer(consumer).hold(subject);
        emit Asserted(id, subject, msg.sender, consumer, outcome, confidence, bond, a.challengeUntil, escalation,
                      rulingWindow);
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
        a.rulingUntil = uint64(block.timestamp) + a.rulingWindow;
        a.status = Status.Contested;
        emit Disputed(id, msg.sender, msg.value);
    }

    /// The asserter's concession of a contested claim: the challenger takes
    /// its stake back and the whole bond, and no fee is due since nobody
    /// rules. The consumer learns nothing of the asserted outcome.
    function concede(uint256 id) external {
        Assertion storage a = assertions[id];
        require(msg.sender == a.asserter, "not the asserter");
        require(a.status == Status.Contested, "not contested");
        a.status = Status.Refuted;
        _pay(payable(a.challenger), a.stake + a.bond);
        if (a.consumer != address(0)) IConsumer(a.consumer).resolve(a.subject, 0);
        emit Refuted(id, a.subject, false);
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

    /// The adjudicator's ruling on a contested claim: the loser's stake pays
    /// the ruling fee to the adjudicator and the rest to the winner; the
    /// consumer learns the asserted outcome or nothing of it. An unresolved
    /// claim is ruled with no clock (the next rung's ruling): both stakes
    /// went back at escalation, so only the record and the consumer move, and
    /// the lapsed rung has no fee to collect.
    function rule(uint256 id, bool upheld) external {
        Assertion storage a = assertions[id];
        require(msg.sender == adjudicator, "not the adjudicator");
        if (a.status == Status.Unresolved) {
            a.status = upheld ? Status.Certified : Status.Refuted;
        } else {
            require(a.status == Status.Contested, "not contested");
            require(block.timestamp <= a.rulingUntil, "ruling window closed");
            address payable winner = payable(upheld ? a.asserter : a.challenger);
            uint256 own = upheld ? a.bond : a.stake;
            uint256 lost = upheld ? a.stake : a.bond;
            a.status = upheld ? Status.Certified : Status.Refuted;
            _pay(winner, own + lost - rulingFeeWei);
            if (rulingFeeWei > 0) _pay(payable(msg.sender), rulingFeeWei);
        }
        if (a.consumer != address(0)) IConsumer(a.consumer).resolve(a.subject, upheld ? a.outcome : 0);
        if (upheld) emit Certified(id, a.subject, a.outcome, true);
        else emit Refuted(id, a.subject, true);
    }

    /// No ruling inside the window: the next rung — v0's stand-in returns
    /// both stakes and resolves at the assertion's escalation value of the
    /// asserted outcome; at UNRESOLVED the consumer is not told, so its hold
    /// persists until the adjudicator rules.
    function escalate(uint256 id) external {
        Assertion storage a = assertions[id];
        require(a.status == Status.Contested, "not contested");
        require(block.timestamp > a.rulingUntil, "ruling window open");
        bool unresolved = a.escalation == UNRESOLVED;
        a.status = unresolved ? Status.Unresolved : Status.Escalated;
        _pay(payable(a.asserter), a.bond);
        _pay(payable(a.challenger), a.stake);
        if (unresolved) {
            emit Unresolved(id, a.subject);
            return;
        }
        uint256 outcome = a.outcome * a.escalation / 10000;
        if (a.consumer != address(0)) IConsumer(a.consumer).resolve(a.subject, outcome);
        emit Escalated(id, a.subject, outcome);
    }

    function _pay(address payable to, uint256 amount) private {
        (bool ok, ) = to.call{value: amount}("");
        require(ok, "payment failed");
    }
}
