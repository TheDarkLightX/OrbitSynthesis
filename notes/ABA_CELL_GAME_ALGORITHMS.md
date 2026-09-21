# Algorithms on the ABA cell game

**Status:** DERIVED specialization of standard finite safety-game algorithms to the ABA cell arena. The queue/counter attractor algorithm is classical; the contribution under investigation is the cell reduction that makes it applicable to Tau/ABA type synthesis without enumerating complete types.

## 1. Cell arena recap

Use the finite arena from `ABA_CELL_GAME.md`:

- V: state cells;
- P: `(state,input)` partial cells;
- U: `(state,input,next)` full cells;
- `state:P->V`;
- `partial:U->P`;
- `next:U->V`.

Let

`Allowed(u) iff u notin Z_T`

for Step's combined zero/equation mask.

Let

`SafeCell(v) iff v notin Z_S`.

A state cell v is zero-winning iff for every environment partial cell p over v, the system has an Allowed full cell u over p whose next cell is zero-winning.

This is an ordinary turn-based safety condition on the finite incidence arena.

## 2. Naive fixed-point iteration

The direct mask iteration is

`A_(n+1)=SafeCells intersect Pre(A_n)`,

starting from `A_0=V`.

It stabilizes in at most |V| strict state-cell removals, but recomputing Pre from scratch can scan all of U on every round.

Worst raw cost:

`O(|V||U|)`

before bitset/parallel improvements.

The standard losing-attractor algorithm is better.

## 3. Counter-based losing attractor

For every partial cell `p in P`, maintain

`live[p]
 = # {u in U : partial(u)=p, Allowed(u), next(u) not currently losing}`.

A partial cell p is **spoiling** iff

`live[p]=0`.

A state cell v is losing iff:

1. v is state-unsafe (`v in Z_S`), or
2. there exists a spoiling partial cell p with `state(p)=v`.

### Initialization

1. Mark every state cell in Z_S losing and enqueue it.
2. Compute the initial live[p] counts from Allowed full cells whose next state is not yet marked losing.
3. Any p with live[p]=0 immediately spoils its state; enqueue any newly losing state.

### Propagation

When state cell w becomes newly losing:

for every Allowed full cell u with

`next(u)=w`,

decrement

`live[partial(u)]`.

If a live counter reaches zero, its partial cell p becomes spoiling. Mark `state(p)` losing if not already marked and enqueue it.

Continue until the queue is empty.

## Theorem 1 — exact zero winning set

At termination, the unmarked state cells are exactly

`A* = nu A. [SafeCells intersect Pre(A)]`.

### Proof sketch

The algorithm is the usual backward attractor for a safety game.

A partial cell becomes spoiling exactly when every currently possible system response leads to an already-known losing state (or is Step-forbidden).

A state becomes losing as soon as the environment has one spoiling refinement.

These are exactly the two quantifier layers

`exists bad environment p . forall system u . bad next`.

The queue computes the least fixed point of the losing operator, whose complement is the greatest safe fixed point.

## 4. Linear incidence complexity

Assume adjacency lists index Allowed full cells by their next-state cell.

Every state cell is enqueued at most once.

Every Allowed full cell causes at most one counter decrement: when its next cell first becomes losing.

Every partial-cell counter reaches zero at most once.

Therefore:

### Theorem 2

The zero attractor is computable in

`O(|V|+|P|+|U_allowed|)`

time and comparable linear incidence storage, after the Allowed transition relation has been generated.

In the explicit pure-ABA packed dimensions:

`|V| = 2^d`,

`|P| = 2^(d+e)`,

`|U| = 2^(2d+e)`.

With interpreted-constant partition rank rho(C), multiply each by rho(C).

This is singly exponential in the BA coordinate dimension and exponentially smaller than enumerating complete support types.

## 5. Equation-only safety synthesis is especially simple

Suppose Step and Safe contain **equations only**, with no disequations.

Then the complete winning type family is simply

`{ nonempty S subseteq A* }`.

No positive antichain phase exists.

Thus:

### Corollary 3 — equation-only ABA safety synthesis

Decide the winning state-type family by one finite cell losing-attractor computation. Represent the result by the allowed-cell mask A*, not by enumerating its

`2^|A*|-1`

winning complete types.

At runtime, for an observed partial support P, the maximal-support strategy selects every Step-allowed full cell over P whose next cell lies in A*, then realizes that target complete type through the effective witness routine.

This is an exact synthesis algorithm, not only a satisfiability test.

## 6. Positive obligation predecessor query

Once A* is fixed, let `U*` be Allowed full cells whose next state lies in A*.

For a target cell mask G, compute

`L(G)
 = {v in A* : every p over v has some u in U* over p with next(u) in G}`.

A direct implementation scans U* and counts, for each partial p, whether it has at least one target transition.

One query costs

`O(|U*|+|P|+|V|)`

with simple bit/counter arrays.

For many obligation-orbit queries, precompute the next-cell sets

`R_p={next(u): u in U*, partial(u)=p}`.

Then

`v in L(G) iff for every p over v, R_p intersects G`.

This is the monotone positive-CNF representation of the cell predecessor from `ABA_MONOTONE_DYNAMICS_UNIVERSALITY.md`.

## 7. Bitset implementation

Represent every R_p and target G as N-bit bitsets.

Then a partial cell is target-live iff

`R_p AND G != 0`.

For each state v, L(G) contains v iff all its partial-cell bit tests succeed.

This makes one L query roughly

`sum_p bitset_intersection_cost(R_p,G)`

plus state aggregation.

For N that fits in one or a few machine words, this is extremely small.

## 8. Sparse versus dense transition storage

Two natural representations:

### Sparse adjacency

Store lists of allowed next cells per p.

Good when Step equations forbid most full cells.

### Dense bitsets

Store one N-bit R_p per partial cell.

Good when transitions are dense and target intersections dominate.

A backend can choose from transition density.

## 9. Symbolic Step compilation

Generating all `|U|` full minterm cells can itself become expensive.

The next compiler layer should compile Step's zero-equation term to one of:

- a BDD over full-cell valuation bits;
- a decision DAG;
- a SAT/circuit evaluator;
- direct term truth-table generation using Gray-code incremental evaluation;
- specialized algebraic transition representation when next variables are explicit functions of state/input.

The cell-game theorem is independent of this choice.

## 10. Deterministic fast path

If normalized Step equations determine exactly one safe next cell for every partial cell, store a function

`delta:P->V`

instead of general R_p bitsets.

Then

`L(G)`

requires only membership tests `delta(p) in G`.

If delta is independent of the environment refinement and induces a state permutation, use the permutation-orbit algorithms from `ABA_EASY_CELL_DYNAMICS.md`.

## 11. Connection to Tau

A practical Tau backend can therefore stage its choices:

1. compile zero/equation atoms to cell transitions;
2. solve zero safety with the linear attractor;
3. if no disequations, stop and synthesize directly;
4. otherwise build the zero-safe R_p relation;
5. classify its dynamics (stutter, pin, deterministic, permutation, general);
6. solve positive obligations using the cheapest matching representation.

This is substantially more specific than "use a BDD for Tau."
