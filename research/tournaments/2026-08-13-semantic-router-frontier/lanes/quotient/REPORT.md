# Exact positive-polarity depth-three capacity

Date: 2026-08-13

Status: **solver-certified lane result, awaiting the tournament's independent
audit/promotion wave**.

## Result

Let `P_pos,d(3)` be the largest `q` for which a Boolean programmable router of
dependency depth at most three can be built using only

`d(x,y,z) = z if x=y, else x`,

with one fixed skeleton, target-specific address-only Boolean controls, and
every occurrence of every routed branch under an even number of second-child
edges. Trees and DAGs are both allowed; the DAG statement uses the unsharing
transfer proved below.

The exact result in this declared grammar is

`P_pos,d(3) = 9`.

The lower bound is the frozen exact `R9`. The upper bound is an exact complete
full-tree `R10` SMT instance: Z3 4.15.4 returns `UNSAT`, cvc5 1.1.2
independently returns `unsat`, and cvc5 also returns `unsat` with internal proof
checking enabled. Thus the best depth-three rate in this grammar is
`log(9)/3`, equivalently compiler depth coefficient
`3*log_9(3) = 3/2`. The would-be `R10` coefficient
`3*log_10(3) = 1.431363764...` is excluded only in this grammar.

## The initially proposed quotient is false

On `{0,1}` the repository discriminator is not ordinary majority:

`d(x,y,z) = majority(x,1-y,z)`.

The checker exhausts all eight rows. There are four disagreements with
`majority(x,y,z)` and none with the twisted-majority identity.

Consequently the unrestricted two-extreme proposal is false. The minimal
frozen counterexample is

`F(x0,x1) = d(x0,x1,0)`.

For target `x0`, `F(0,1)=0` and `F(1,0)=1`, so the proposed two tests pass, but
`F(1,1)=0 != 1`. No arbitrary-leaf conclusion is drawn from the pair
quotient.

## Corrected polarity theorem

### Lemma 1: path polarity

On Boolean inputs, `d` is nondecreasing in its first and third arguments and
nonincreasing in its second argument. Give a leaf occurrence sign

`(-1)^(number of second-child edges on its root path)`.

If every occurrence of a branch variable has positive sign, then the whole
term is nondecreasing in that branch variable.

Proof: induct over the tree. First- and third-child composition preserves the
inductive sign; second-child composition reverses it because `d` is antitone
there. When several occurrences meet, every incoming dependence has the same
nondecreasing direction, so the parent remains nondecreasing. Controls are
fixed while the branch variable varies. At depth three, the 14 positive leaves
are

`0,2,4,6,8,10,12,14,16,18,20,22,24,26`,

and the 13 negative leaves are the odd positions.

A consistently negative branch cannot be routed as itself: a nonincreasing
Boolean function of `x_i` cannot equal the nonconstant increasing projection
`x_i`. Therefore any exact router in the consistent-unate d-only grammar must
put every branch occurrence at positive polarity. The solver grammar is thus
complete for consistent-unate routers, not merely a selected positive case.

### Lemma 2: two extremes are exact for monotone terms

For a Boolean function `F` nondecreasing in every branch variable,

`F = x_i`

if and only if

`F(x_i=0, all other branches=1)=0`, and

`F(x_i=1, all other branches=0)=1`.

The forward implication is immediate. Conversely, for any assignment `y` of
the other branches, monotonicity gives

`F(0,y) <= F(0,1,...,1) = 0`,

and

`1 = F(1,0,...,0) <= F(1,y)`.

Hence `F(0,y)=0` and `F(1,y)=1`. As a calibration independent of the tree
encoding, `check_extreme_lemma.py` exhausts all 256 ternary Boolean functions,
finds the expected 20 monotone functions, and checks the equivalence for all
60 function/target pairs.

### Lemma 3: exact four-state pair semantics

For target `i`, attach one two-bit state to each leaf:

- target branch `x_i`: `01`;
- every other branch: `10`;
- a programmed control bit `c`: `cc`, hence `00` or `11`.

Evaluate `d` componentwise. The two components are exactly the two valuations
in Lemma 2; no abstract transition is used. Root state `01` is therefore
equivalent to both extreme equations. Lemma 1 supplies monotonicity, and Lemma
2 lifts the pair result to every one of the `2^q` valuations. Conversely, any
router satisfies both extremes, so the quotient loses no witness.

The controls are target-specific but are identical in both components. They
therefore depend only on the address/target, never on a payload valuation.

## Complete R10 instance

`solve_positive_pair_r10.py` encodes a complete depth-three d-tree with 27
leaf-label integers:

- label `0` means a private programmable Boolean control;
- labels `1..q` mean branch variables;
- every branch label must occur at least once;
- labels may repeat arbitrarily;
- all 14 positive-polarity leaves may be controls or branches;
- all 13 negative-polarity leaves are controls;
- every control leaf has an independent target-specific bit.

For each target, the actual Boolean `d` is evaluated in both pair components
and the root is constrained to `01`. Branch-first-occurrence ordering removes
only branch-name permutations. It is no-loss: rename branches in order of
their first leaf occurrence and apply the same permutation to the target
program rows.

The frozen q=10 instance is
`positive_pair_r10.smt2`, SHA-256
`48c81acb99af1644c5bcaacd3477ce2cc94b602501900754d55be28ddc72ff65`.

Results:

- Z3 normal mode: `UNSAT` (the checker intentionally exits 2 for UNSAT).
- Z3 optimized Python mode: identical `UNSAT` JSON bytes.
- cvc5 independent replay: `unsat`, exit 0.
- cvc5 with `--produce-proofs --check-proofs`: `unsat`, exit 0. The proof was
  checked internally; no standalone proof object is claimed or stored.
- q=9 positive control through the same solver: `SAT_EXACT`, followed by all
  `9*2^9 = 4608` concrete projection checks and an effective control-bit
  mutation for every target.

## Exact R9 lower bound

`check_positive_r9_lower.py` independently loads the frozen predecessor bytes,
checks their required SHA-256, and confirms that its nine branch occurrences
are at positions

`2,4,6,10,12,16,20,22,26`.

Every position has positive path polarity. Normal and optimized runs replay all
4,608 Boolean identities and find a control flip that breaks each target. The
two receipt files are byte-identical. This establishes `P_pos,d(3) >= 9`
without relying on the pair quotient.

## Transfers from the complete tree

### Full-tree padding

Every positive-polarity d-only formula of depth at most three embeds in the
complete depth-three tree without changing its function or branch polarities.
Recursively pad each child to the required remaining height. When a whole term
needs one more level, use

`d(c,c,t) = t`

and put `t` in the third child. Fill a constant-control subtree with equal
control bits, since `d(c,c,c)=c`. The third-child edge is positive, so this
wrapper preserves every old branch polarity. The solver permits separate
private controls to be programmed equal, so the padding is legal.

Therefore full-tree R10 UNSAT excludes every shallower positive-polarity
d-only formula, not just syntactically full trees.

### DAG unsharing

Unfold a dependency-depth-at-most-three d-only DAG at every shared use. The
result is a tree of the same dependency depth and computes the same function.
Each unfolded branch occurrence inherits its original root-to-use path, so an
all-positive DAG stays all-positive. Duplicate controls receive the same
target-specific bit as the shared control; independent controls in the tree
grammar permit this equality. Pad the unfolded tree as above.

Thus the upper bound transfers to positive-polarity d-only DAGs of dependency
depth at most three. It does not transfer to DAGs with a mixed-polarity branch
path, `u`, signed leaves, or greater depth.

### Arity monotonicity

If an `Rq` with `q>10` existed in this grammar, retain any ten branches and
relabel every omitted branch occurrence as a control fixed, for example, to
zero. The original projection identities hold for every valuation of the
omitted branches, so they still hold after fixing them. This would produce an
R10, contradicting the exact instance. Hence q=10 UNSAT excludes every q>=10
and, with R9, gives the stated exact capacity.

## Reproduction

Run from this lane directory. Python is 3.12.3, Z3 is 4.15.4, and cvc5 is
1.1.2.

```text
python3 check_extreme_lemma.py --out extreme_lemma.json
python3 -O check_extreme_lemma.py --out extreme_lemma_optimized.json

python3 check_positive_r9_lower.py --out positive_r9_lower.json
python3 -O check_positive_r9_lower.py --out positive_r9_lower_optimized.json

python3 solve_positive_pair_r10.py --q 9 --timeout-ms 120000 \
  --out positive_pair_q9_solver_control.json

python3 solve_positive_pair_r10.py --q 10 --timeout-ms 120000 \
  --out positive_pair_r10.json --dump-smt2 positive_pair_r10.smt2
python3 -O solve_positive_pair_r10.py --q 10 --timeout-ms 120000 \
  --out positive_pair_r10_optimized.json

cvc5 --lang smt2 positive_pair_r10.smt2
cvc5 --lang smt2 --produce-proofs --check-proofs --tlimit-per=120000 \
  positive_pair_r10.smt2
```

The two q=10 Python commands are expected to exit 2 after writing an `UNSAT`
receipt. cvc5 warns that the Z3-emitted file lacks `set-logic`, then selects all
theories and returns `unsat`; the warning does not change the result.

The complete machine-readable command/result/hash record is
`solver_receipt.json`, SHA-256
`c9a0d0cf118395bc45e38100336c4135e1329e368d74f7d2329269d2755bb47e`.

## Falsifiers and boundaries

- **F-input:** the R9 checker rejects any predecessor-byte hash drift.
- **F-grammar:** all 27 leaf labels and all 13 actual d nodes are encoded;
  branch repetitions and controls at positive leaves are included.
- **F-control:** a control has one target-specific bit shared by both extreme
  valuations; no payload-dependent program is representable.
- **F-polarity:** the ordinary-majority premise is explicitly refuted; the
  path-parity census and negative counterexample are frozen.
- **F-quotient:** componentwise evaluation gives coverage/no-loss, and the
  monotonicity theorem supplies the full-truth-table lift.
- **F-tree:** padding and unsharing are one-way reductions into the solved
  grammar and preserve depth, function, controls, and polarity.
- **F-degenerate:** repeated labels, unused positive slots, arbitrary controls,
  all targets, q=9 SAT, full R9 replay, and effective mutations are covered.
- **F-boundary:** this is not arbitrary d-only R10 UNSAT. A branch with both
  positive and negative occurrences can evade the monotone quotient.

No claim is made about mixed-polarity d-only terms, signed/complement leaves,
charged `u` terms, depth four or six fused routers, direct-Q routing, generic
optimality, novelty, copyright, patents, freedom to operate, the offered Tau
development license, or Tau relevance. The highest-leverage next exact target
is a canonical mixed-polarity semantic quotient (full truth-table/BDD or SAT
miter), followed separately by a correctly charged signed-leaf overapproximation.
