# Semantic-router frontier state

Date: 2026-08-13

Status: research-only frozen contract. Search, solver, Morph, and retrieval
outputs are advisory until an explicit witness or certificate is replayed by a
small deterministic checker and independently audited. No paper edit,
publication claim, patent/FTO conclusion, license action, or Tau claim is
authorized in the author lanes.

## Frozen predecessor

- Exact Boolean depth-three `R9` witness:
  `../2026-08-13-router-frontier/lanes/capacity/boolean_q9_r8_radius1.json`,
  SHA-256
  `d3c25e47ce671d8a5d484d6c50cc0b3fccf7f6bb5507097ef8bff6bcbbbe529c`.
- Integrated Boolean-plane compiler checker:
  `../../../experiments/quasiprimal_boolean_r9_routing.py`, SHA-256
  `a586337ed15a31c90ab6051dc1c12c319e0a972ee321075711870a5913a2af4b`.
- Self-binding compiler receipt:
  `../../../runs/quasiprimal_boolean_r9_routing/summary.json`, SHA-256
  `86859eef0d4a73f493ffe95dce97dae65d324b5d6c4fecbb92cf3256dac27e55`.
- Established conditional compiler bound:
  `O(3^r/r)` same-DAG size and `(3/2)r + O(r/log r)` depth.
- Established serial-grammar barrier: serial mixtures of the frozen
  `R6/R7/R8/R9` routers cannot improve the rate `log(9)/3`.
- The predecessor's R10 results are bounded `NO_HIT`/grammar-UNSAT only; no
  global R10 impossibility was established.

## Exact object and candidate quotient (refuted, then repaired)

On the Boolean subalgebra `{0,1}`, the discriminator is actually

`d(x,y,z) = majority(x, 1-y, z)`, not `majority(x,y,z)`.

The initially proposed ordinary-monotone two-extreme equivalence is **refuted**.
For `F=d(x_0,x_1,0)` and target `x_0`, the points
`(x_0,x_1)=(0,1)` and `(1,0)` return `0` and `1`, respectively, but
`F(1,1)=0 != x_0`. Preserve this as negative knowledge; no lane may use the
naive equivalence.

The replacement target is a polarity-aware quotient. Each leaf occurrence has
a path polarity given by the parity of second-child edges (and any charged
`u` nodes). After complementing variables at negative occurrences, a fixed
tree may become unate only when every occurrence of a given branch has a
consistent induced polarity. Under that explicit consistency condition, test
whether an exact two-extreme theorem holds and prove its lift. Mixed-polarity
occurrences require a richer exact semantic relation or the full truth table;
they may not be collapsed by monotonicity.

An exact four-state pair evaluator remains valid for any *chosen pair of
valuations*, but two pair states alone do not certify a projection without the
proved unateness bridge. Otherwise use a complete Boolean truth table, BDD,
SAT miter, or a larger canonical semantic quotient.

## Goal and benchmarks

Primary target: settle exact programmable projection capacity above `R9` by a
different representation.

- Depth 3: an exact Boolean or direct-Q `R10` gives coefficient
  `3*log_10(3) = 1.431363764...`, strictly below `3/2`.
- Depth 4: a router must have at least `19` branches to beat rate `log(9)/3`.
- Depth 6: a fused macro must have at least `82` branches to beat the serial
  `R9 x R9` capacity `81`.
- An exact global `R10` UNSAT certificate for the complete positive depth-three
  discriminator-tree grammar, together with a full-tree/unsharing transfer,
  is a paper-relevant optimality theorem for that declared grammar, not a
  lower bound for arbitrary `{d,u}` terms.

## Lanes

### Semantic quotient and global capacity

First freeze the counterexample to the naive extremal lemma. Then derive and
check a polarity-aware unate theorem, or use exact BDD/SAT-miter semantics to
encode arbitrary branch/control leaf labels (including repeated branches) in
a complete depth-three discriminator tree and solve R10. A SAT result requires
full `10*2^10` replay and effective mutations. An UNSAT result requires a
durable instance, a second solver or proof certificate, and explicit
full-tree/unsharing scope. Free signed leaves are a separate over-approximation
and may not be silently included in the charged positive grammar.

### Direct-Q bit-parallel synthesis

Replace valuation-by-valuation SMT with packed two-bitplane truth tables or an
equivalent exact semantic DP. Starting from the frozen direct-Q `R6`, search
bounded neighborhoods toward direct-Q R7--R10. A timeout is `UNKNOWN`; only a
fully enumerated witness is a construction.

### Fused/nonserial macro

Attack depth-4 R19 or depth-6 R82 using cross-level semantic quotienting,
control borrowing only when it remains address-only, and exact local-to-global
cost accounting. A serial composition or schedule cannot win by the frozen
rate lemma and must be rejected as dominated.

## Common falsifiers

- `F-input`: only public frozen repository inputs are used.
- `F-grammar`: every leaf, `d`, and `u` is legal and its dependency depth is
  charged.
- `F-control`: every program value depends only on address, never payload.
- `F-polarity`: every second-child reversal and charged `u` is tracked; an
  extremal lemma is used only after consistent unateness is proved.
- `F-quotient`: the four-state abstraction has coverage, no-loss, and witness
  lift-back proofs.
- `F-tree`: full-tree padding and DAG unsharing are one-way permissions stated
  exactly; an UNSAT scope cannot be broadened without the transfer proof.
- `F-rate`: all routing, two-plane encoding/decoding, controls, anchors, and
  shared-DAG costs are charged.
- `F-degenerate`: repeated labels, unused controls, constants, complements,
  padding, and every target are tested.
- `F-boundary`: finite or grammar-specific evidence is not a global lower
  bound, novelty result, or FTO opinion.
- `F-prior`: majority-formula restriction/projection capacity and universal
  circuit literature remain prior-art obligations.

## Budget and acceptance

- Three author lanes and one independent audit/reduction wave.
- Bounded local CPU and memory; no installation or large download.
- Preserve all `NO_HIT`, counterexamples, and `UNKNOWN` branches.
- Promotion requires frozen bytes, exact commands, normal/optimized replay,
  mutation or malformed-input controls, and an independent implementation.

Success is either a strictly better all-arity compiler coefficient with all
bridges checked, or an exact major grammar barrier that materially shrinks the
next frontier.
