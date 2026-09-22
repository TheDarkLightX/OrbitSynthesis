# Fixed-Q initial safety: NP-completeness and obstruction-parameterized synthesis

Date: 2026-09-22. Base inspected: `0ab3648a724370786ac9ea573bf81ac7ef7db7fb`.

**Status:** DERIVED mathematical proofs below, conditional on the classical
quasi-primal term-interpolation characterization. TESTED on the declared finite
campaign. NOT Lean-verified, independently peer reviewed, or novelty-certified.
The implementation is a standalone research prototype, not a production backend.

This answers the fixed-Quackenbush-algebra initial-safety question explicitly
posed in section 12 of `notes/TERM_SYNTHESIS_COMPLEXITY_BOUNDARIES.md`.
It does not modify the fixed-Q circuit-size/depth review branches or the finite
controller runtime. It contains no Tau source or dependency.

## 1. Model, representation, and known algebraic ingredient

Fix the three-element algebra

```
Q = ({0,1,2}; d,u)
d(x,y,z) = z if x=y, otherwise x
u(0)=1, u(1)=0, u(2)=1.
```

Write `B={0,1}` and `bar` for coordinatewise Boolean complement. The only
nonempty subalgebras are B and Q; the only nonidentity internal isomorphism is
complement on B; Q has no nonidentity automorphism. These facts can be checked
directly from the operation tables and are the example already used in
`QUASIPRIMAL_COUPLING_COUNTEREXAMPLE.md`, attributed there to Quackenbush (1974),
Example 9.2.

The classical quasi-primal interpolation characterization gives, for positive
arity r,

```
f:Q^r -> Q is a term operation
iff f(B^r) is contained in B and f(bar z)=bar f(z) for z in B^r.
```

There is no constraint linking different tuples containing 2: each generates Q,
whose only automorphism is the identity. This characterization is KNOWN
background, not a result claimed here. All controller coordinates are terms
in the original `d/u` signature, without added parameters or arbitrary constants.

A game has states `S=Q^k`, k>=1; one environment input i in Q; successor state
`y in S`; and an extensional safe relation `R subset S x Q x S`. A single total,
time-independent controller `F:Q^(k+1)->Q^k` is required. Every coordinate of F
must be a term operation. A domain W is winning when

```
for all s in W and i in Q:
    (s,i,F(s,i)) in R and F(s,i) in W.
```

The decision problem asks whether some W containing a supplied initial state
exists. Equivalently, a controller must be safe from that state against every
input sequence; its reachable set provides W. The optimization extension permits
required and forbidden states and nonnegative integer state utilities.

**Input-size convention:** all `N=3^k` states and their three rows are explicitly
addressed, with successor lists or bitsets. Polynomial means polynomial in this
explicit representation and utility bit lengths, NOT polynomial in k or an
arbitrary succinct formula. The witness is a semantic table, not a syntactic
term DAG with an asserted size bound.

## 2. Fixed-domain feasibility is simple

Let `A(s,i)` be the locally admissible safe successors: intersect the R-row with
`B^k` when `s in B^k` and `i in B`, and otherwise leave it unchanged.

### Lemma 1 — exact fixed-domain criterion

A domain W admits one total Q-term controller iff:

1. `A(s,i) intersect W` is nonempty for every active observation `(s,i)`;
2. for every complementary state pair `s,bar s` contained in W and each `i in B`,

```
there exists y in A(s,i) intersect W
with bar y in A(bar s,bar i) intersect W.
```

In condition 2 y is Boolean because the observations are Boolean.

**Proof.** Necessity follows from safety, closure, subalgebra preservation and
`F(bar s,bar i)=bar F(s,i)`. For sufficiency, partition the Boolean observations
into complement pairs. If both source states are active, use condition 2 to
choose one seed response and transport its complement. If only one source is
active, use condition 1 there and fill the inactive partner by transport. If
neither is active, choose any Boolean seed. For observations containing 2,
choose any locally safe response when active and any Q^k response otherwise.
All choices are independent across these observation components. The completed
table satisfies the classical characterization coordinatewise. QED.

This is a specialization of the repository's existing internal-groupoid
seed/list factorization, not a new general interpolation theorem.

## 3. Main hardness theorem

### Theorem 2 — fixed-Q initial-state safety is NP-complete

Under the explicit representation above, the problem is NP-complete even with
one required initial state, one Q-valued environment input, and a safety relation
that is semantically definable by one equation in the original signature.

The algebra is fixed once and for all; the number of state coordinates varies.

### NP membership

Guess W and the entire F table. There are 3N observations, and each response has
k coordinates. Check initial membership, every active row's safety and closure,
Boolean output membership, and every Boolean complement-pair identity. These
checks are polynomial in the declared explicit input size. The classical
characterization converts table compatibility to term existence without asking
for a short syntactic term certificate.

### Reduction from 3-SAT

Let a formula have n variables and m clauses. Choose k large enough that

```
2^(k-1) >= n+1
3^k-2^k >= max(1,2m-1).
```

For the complexity reduction choose the least such k. It is `O(log(n+m+2))`,
so the full state space remains polynomial in formula size.

Allocate n+1 distinct complementary Boolean state pairs. One is `(t,bar t)`,
where `t=0^k`. The others are the two literal states `(l_v,bar l_v)` for each
variable. Nonbinary states, which contain a 2, will represent clauses and a
binary selection tree. All unmentioned transition rows are empty.

**Sink pair.** From t, every input leads only to t. From bar t, inputs 0 and 1
lead only to bar t, but input 2 has no safe successor. Thus no winning W can
contain bar t.

**Literal pairs.** For either literal state, inputs 0 and 1 permit exactly
`{t,bar t}`, while input 2 permits only `{t}`. Either literal alone can coexist
with t. Both literals cannot coexist in a term-winning W: at observations
`(l_v,0)` and `(bar l_v,1)` the response must be t on both sides, since bar t
cannot belong to W, but complement equivariance requires opposite responses.
Thus domain membership implements mutual exclusion of positive and negative
literals.

**Clauses.** For each clause allocate a distinct nonbinary state c. Every input
at c permits precisely that clause's literal states. Therefore c in W requires
at least one of those literals in W. An empty clause gives a dead clause state.

**Single initial state.** A binary tree of fresh nonbinary selector states has
the clause states as leaves. At each selector, input 0 forces the left child,
input 1 the right child, and input 2 goes to t. Require just its root. Every
clause is then forced into W. For one clause that clause is the root. For no
clauses, one nonbinary root goes to t on all inputs.

**Forward implication.** A satisfying assignment chooses at most one member of
each literal pair, with every clause having a chosen literal. Include these
literal states, t, and the clause/selector states in W. All local obligations
are satisfied; no complementary pair of active Boolean states remains. Lemma 1
provides a total term controller.

**Reverse implication.** Any winning W containing the root includes every
clause and hence at least one literal per clause. It cannot include bar t or
both literals of any variable. Assign variables consistently with its selected
literals, assigning unselected variables arbitrarily. Every clause is satisfied.

This proves the equivalence. The branching gadgets use only one environment
coordinate, not a growing alphabet. Before the sink, their paths are acyclic;
long temporal memory is not the source of hardness. QED.

### Corollary 3 — one-equation definability

The constructed R is invariant under coordinatewise complement on completely
Boolean flattened transition tuples. The sink rows at Boolean inputs are paired,
and the literal rows each permit both sink values. Clause/selector tuples
contain 2, so do not introduce Boolean complement obligations.

For `z=(s,i,y)` define the projection `p(z)=s_1` and the scalar table

```
g(z) = p(z)               when z is safe
       1-p(z)             when z is unsafe and completely Boolean
       (p(z)+1) mod 3     otherwise.
```

Then g preserves B and Boolean complement, so it is a term operation. Also
`R(z) iff p(z)=g(z)`. This proves semantic one-equation definability.

**Important limit:** this is not a polynomial-size formula-emission theorem.
The reduction emits R as an explicit table. It must not be cited as an
NP-completeness theorem for succinct original-signature equation inputs without
an additional syntactic compilation bound.

## 4. The algorithm: delete an obstruction, then recompute viability

For a current allowed set A, let `L(A)` be the greatest fixed point obtained by
repeatedly deleting each s for which some input has no successor in the current
set under A(s,i). This is the ordinary local safety envelope.

Every term-winning `W subset A` is contained in `L(A)`: a term controller uses
locally admissible successors, and induction on the deletion rounds prevents
any W-state from being deleted.

### Lemma 4 — scoped binary obstruction

Let `V=L(A)`. If two complementary states `s,bar s in V` fail condition 2 of
Lemma 1 for some Boolean input, every term-winning `W subset V` omits s or bar s.

**Proof.** Were both included, their paired responses would be complementary
members of W and hence of V, contradicting the empty paired-response test. QED.

This is a statement inside V, not an unconditional nogood. Adding previously
excluded repair successors can remove a conflict.

### Algorithm

```
search(A):
    V = greatest locally safe invariant contained in A
    if a required state is missing: return infeasible
    if V has no paired-response obstruction:
        complete its total term-compatible table; return V
    choose an obstruction {s,bar s}
    search(V minus {s}) and search(V minus {bar s})
```

For pure existence, stop once a branch has a verified feasible witness. For
nonnegative utility optimization, evaluate all feasible leaves and select the
one with largest total utility (then cardinality and a canonical state-mask tie
break). Begin with every state except the forbidden ones.

### Theorem 5 — completeness and parameter bound

Let d be the number of complementary Boolean state pairs entirely contained in
the initial local envelope. The algorithm is exact, has depth at most d and
visits at most `2^(d+1)-1` nodes. Its runtime is `2^d poly(L)`, where L denotes
the explicit input size including weights.

**Proof.** A required-state rejection is justified by local-envelope dominance.
At a conflict, Lemma 4 covers every feasible W by one of the two children.
Passing to a child's local envelope preserves every feasible W within that
child. If a node has no conflict, Lemma 1 proves V feasible, and V contains every
other feasible domain in that node; with nonnegative utilities none is better.
Consequently every feasible solution is either dominated by a visited feasible
leaf or lies along a child preserved by the branching rule.

Each branch deletes one member of a still-complete complementary pair. Deletion
and local reclosure never reintroduce a state, so that pair can never be branched
on again along that path. At most d splits occur on a path. A binary tree of that
depth has the claimed node bound. Each local fixed point, paired test and table
completion is polynomial in L. QED.

At d=0 the solver is simply one local game computation followed by table
completion. Even large explicit games can have small d.

**Not supported:** signed-utility optimization by this algorithm. A feasible
subset of V can score better than V with negative weights. The implementation
rejects negative utilities; the repository's earlier general signed optimizer
remains the appropriate separate method.

Winning domains are also not downward closed. For example, on Q with transitions
`0 -> 1` and `1 -> 0` for all inputs and no moves from 2, `{0,1}` is term-winning
but `{0}` is not. That is why every deletion requires local reclosure.

## 5. Conditional tightness of the parameter

### Corollary 6 — no subexponential dependence on d under ETH

Assume 3-SAT cannot be decided in `2^o(n) poly(n+m)` time. Then no algorithm for
this fixed-Q problem runs in `2^o(d) poly(L)` time on every explicit input.

**Proof.** In the reduction, t and both literal states of every variable survive
local viability: all have a locally permitted path to t. The dead sink does not
survive; all unused Boolean states have no moves. Consequently the initial
local envelope has exactly the n literal pairs, so `d=n`. Clause or selector
failures cannot delete these self-sustaining literal/sink states. The reduction
is polynomial, so the alleged algorithm would solve 3-SAT in the forbidden
running time. QED.

ETH is a hypothesis, not a proved lower bound. This argument does not exclude
better exponential bases, strong preprocessing, easy instance classes, or faster
practical implementations. It identifies d as a parameter carrying genuine SAT
complexity, not merely an artifact of the chosen solver.

## 6. Executed falsification and replay

The adjacent `research/prototypes/2026-09-22-q-obstruction/` package contains a
bitset implementation, an independently written set/tuple checker importing no
solver code, a deterministic campaign and a caller-bound example certificate.
The two implementations share the stated mathematical characterization, so this
is implementation independence, not an independent proof of Pixley's theorem.

Executed with Python 3.13.5 in normal and optimized (`-O`) modes:

| Check | Exact scope/result |
|---|---|
| Scoped unary coupled kernel | 2,048 games, 4,096 optimization requests, exhaustive 8-domain oracle per game |
| Seeded differential corpus | 660 games at arities 1/2/3; 1,320 optimization requests |
| Total compatible-table oracle | All 972 scalar binary compatible tables on 64 games, 512 domain checks |
| SAT reduction | 917 formulas: 459 satisfiable, 458 unsatisfiable; zero discrepancies |
| Parameter preservation | d equals number of allocated variables on all 917 reductions |
| Equation separator | 40,149 flattened rows checked on the declared selected subcorpus |
| Corruption checks | 15 mutations rejected, including game/objective/required-state bindings, inactive symmetry, false envelopes and omitted branches |
| Other guards | Negative weights rejected; required/forbidden collision certified infeasible; non-heredity example retained |

The 917 formulas include all subsets of the eight nonempty nontautological
clauses on two variables, all subsets of the eight full-width three-variable
clauses, five edge cases, and 400 seeded mixed 3-CNFs. These are bounded tests,
not the proof of the universal reduction.

The scaled calibration uses 2,187 states (`Q^7`), three environment values and
7,202 safe edges. A complete six-variable CNF has 64 clauses and is unsatisfiable.
Live nonbinary padding leaves 2,072 states in the naive local envelope, yet d=6.
The exact solver and separate certificate checker establish infeasibility with
127 search nodes, 63 splits and 64 required-state rejection leaves.

This scaled formula has six literals per clause, not three. No exhaustive
2,187-state domain scan was run. The padding deliberately isolates d; this is
not evidence of superiority to SAT/MaxSAT, the existing repository optimizer,
or mature symbolic game solvers. Timing is diagnostic and kept outside the
semantic receipt.

The normal and optimized semantic outputs are byte-identical. Source and receipt
hashes are in the prototype README. The experiment and proof are additive;
full-repository regression tests and hosted CI were not run in this session.

## 7. Prior art, novelty, and complementary scope

**Known ingredients:** discriminator/quasi-primal interpolation, Quackenbush's
algebra and internal complement, SAT hardness, ordinary safety fixed points,
branching on conflicts, and ETH. The repository already has generic groupoid
seed factorization, two-sided nogoods, signed optimization, and proof trees.
None of those is presented here as a new discovery.

**New within this repository:** the explicit fixed-Q single-initial-state SAT
reduction answering the recorded question; its single-equation semantic
strengthening; the specialized viability-envelope binary-obstruction algorithm;
and the matching conditional dependence on d. Publication novelty remains
unverified. Broader constrained/partial-observation memoryless-strategy hardness
is established prior art and narrows the claim considerably.

Ohad Asor's public ocLTL work reduces synthesis over omega-categorical structures
to finite propositional problems through complete types. Here the input is
already finite and the extra issue is which controller tables can be expressed
in a specified original operation signature. This layer is usable without Tau
and is conceptually downstream/orthogonal to that abstraction, not a replacement
for Asor's logic or quantifier-elimination work.

The comparison concerns inspected public material only. It cannot establish
nonoverlap with unpublished research, patent scope, commercial permission or
freedom to operate. No upstream change or claim on Tau's implementation is made.

### Sources inspected / dependency pointers

- R. W. Quackenbush, *Structure Theory for Equational Classes Generated by
  Quasi-Primal Algebras*, Transactions of the AMS 187 (1974), 127-145, Example
  9.2 as cited in the existing repository counterexample. Metadata/abstract were
  rechecked through Consensus; the complete 1974 paper was not independently
  reread in this session. The term-characterization dependency is explicit.
- `notes/QUASIPRIMAL_COUPLING_COUNTEREXAMPLE.md` and
  `notes/TERM_SYNTHESIS_COMPLEXITY_BOUNDARIES.md` at the pinned base above.
- `research/NOGOOD_DOMAIN_SEARCH_UPDATE_2026_08_13.md`: existing two-sided
  seed-nogood and generic domain-search machinery.
- Ohad Asor, *ocLTL: LTL Realizability and Synthesis Modulo omega-Categorical
  Structures* (2026), arXiv:2605.12539; abstract and HTML inspected.
  https://arxiv.org/html/2605.12539v1
- K. Chatterjee, M. Chmelik and J. Davies, *A Symbolic SAT-based Algorithm for
  Almost-sure Reachability with Small Strategies in POMDPs* (2015),
  arXiv:1511.08456; abstract inspected for adjacent prior art, not a claimed
  equivalence between their model and ours. https://arxiv.org/abs/1511.08456
- R. Impagliazzo and R. Paturi, *On the Complexity of k-SAT*, JCSS 62(2) (2001),
  367-375, DOI 10.1006/jcss.2000.1727; publisher abstract inspected for ETH.
  https://doi.org/10.1006/jcss.2000.1727

## 8. Next frontier, not claimed results

The highest-value extension is to replace complementary pairs by minimal
internal-groupoid obstruction cores in other finite quasi-primal algebras, and
ask for a structural P/NP or parameterized classification. The existing
non-demi-semi-primal no-greatest theorem alone does NOT supply such a dichotomy:
its witnesses need not provide the rigid routing, literal exclusion and
polynomial representation used here.

A separate practical step is to compare this prototype against the existing
signed optimizer and SAT backends on identical non-padded and structured inputs,
then prove a verified original-signature DAG compilation bridge. Neither benchmark
superiority nor that bridge is included in this result. The fixed-point, scoped
branching and total-table completion lemmas are concrete formalization targets.
