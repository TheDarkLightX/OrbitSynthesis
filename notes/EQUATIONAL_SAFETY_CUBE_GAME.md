# Equational safety synthesis over Boolean algebras collapses to a Boolean-cube game

**Status:** DERIVED theorem; one-step and fixed-point behavior checked exhaustively against explicit complete-support games for bounded one-state-bit instances; literature novelty NOT yet established. This theorem is stronger than the ABA-only support results: atomlessness is not required.

## 1. Setup

Let `B` be any nontrivial Boolean algebra.

Let:

- `s=(s_1,...,s_k)` be the current state tuple;
- `x=(x_1,...,x_p)` be environment inputs;
- `y=(y_1,...,y_k)` be controller outputs, also used as the next state.

Let

`F(s,x,y)`

be a Boolean-algebra term built from `0,1,meet,join,complement`.

The safety game requires, at every round,

`F(s,x,y)=0`,

then moves to state `s':=y`.

Conjunctions of equations are included because

`F_1=0 AND ... AND F_m=0`

is equivalent to

`(F_1 OR ... OR F_m)=0`.

## 2. The finite Boolean-cube game

Evaluate the same Boolean term in the two-element Boolean algebra.

Let

`f : {0,1}^k x {0,1}^p x {0,1}^k -> {0,1}`

be the resulting truth function.

Define a finite safety game `G_f`:

- states: `a in {0,1}^k`;
- environment actions: `u in {0,1}^p`;
- controller actions / next states: `v in {0,1}^k`;
- transition `(a,u,v)` is safe iff `f(a,u,v)=0`.

For `A subseteq {0,1}^k`, define

`Pre_f(A)
 := { a : for every u there exists v in A with f(a,u,v)=0 }.`

Let

`A_* = nu A . Pre_f(A)`

be the greatest fixed point / finite safety winning set.

## 3. ABA/BA state supports

For a Boolean-algebra tuple `s`, let

`C_a(s) = AND_j s_j^(a_j)`

be its Venn minterm for label `a in {0,1}^k`, and define

`Supp(s) = { a : C_a(s) != 0 }`.

For any `A subseteq {0,1}^k`, define the equation

`W_A(s) := OR_{a notin A} C_a(s) = 0`.

Then

`W_A(s)` holds iff `Supp(s) subseteq A`.

Thus equation-defined state regions are exactly principal ideals of the support powerset.

## 4. One-step predecessor theorem

### Theorem 1

For every Boolean algebra `B` and every cell set `A`,

`CPre_B(W_A) = W_(Pre_f(A))`.

In words:

> an actual Boolean-algebra state is a controllable predecessor of the equation-defined region `W_A` iff every nonzero state Venn cell has a Boolean label that is a controllable predecessor of `A` in the finite cube game.

### Sufficiency proof

Assume

`Supp(s) subseteq Pre_f(A)`.

For every Boolean state label `a in Pre_f(A)` and every environment label `u`, choose one finite-game response

`sigma(a,u) in A`

with

`f(a,u,sigma(a,u))=0`.

After the environment supplies the actual BA tuple `x`, define controller output coordinate `y_j` by the Boolean term

`y_j
 = OR_{(a,u) : sigma(a,u)_j=1}
     [ C_a(s) AND C_u(x) ].`

The joint `(s,x)` Venn regions form a partition of `1`. On every nonzero region labeled `(a,u)`, this term assigns the entire region the output valuation `sigma(a,u)`.

Therefore:

- `F(s,x,y)=0` region-by-region, because `f(a,u,sigma(a,u))=0`;
- every nonzero y-minterm label is some `sigma(a,u) in A`, so `Supp(y) subseteq A`.

Hence the controller reaches `W_A` safely.

No atomless splitting is used.

### Necessity proof

Suppose `Supp(s)` contains a label

`a notin Pre_f(A)`.

Then there exists an input valuation `u` such that

`f(a,u,v)=1`

for every `v in A`.

The environment can choose its BA input tuple so that, on the nonzero region `C_a(s)`, the input valuation is exactly `u` (what it does on other state cells is irrelevant).

Assume the controller could respond with `y` satisfying both

`F(s,x,y)=0`

and

`Supp(y) subseteq A`.

The nonzero region `C_a(s)` is partitioned by the y-minterms. At least one subregion has some output label `v in Supp(y) subseteq A`. On that subregion the Boolean term F evaluates to

`f(a,u,v)=1`,

contradicting `F=0`.

Therefore no controller response exists and `s` is not in the predecessor.

This proves exact equality.

## 5. Greatest-fixed-point collapse

Start the ordinary safety Kleene iteration from all BA states.

The top region is

`W_(A_0)` with `A_0={0,1}^k`,

because the equation `0=0` allows every support.

By Theorem 1,

`CPre_B(W_(A_n)) = W_(Pre_f(A_n))`.

Therefore, by induction, every BA winning-region approximation is equation-defined and corresponds exactly to the finite cube iteration

`A_(n+1)=Pre_f(A_n)`.

### Theorem 2 — exact winning-region characterization

A Boolean-algebra state `s` is winning in the infinite-data safety game iff

`Supp(s) subseteq A_*`.

Equivalently, the winning region is the single equation

`OR_{a notin A_*} C_a(s) = 0`.

## 6. Fixed-point iteration bound

The cube game has only

`2^k`

states.

The descending safety iteration can remove a Boolean state label at most once, so it stabilizes after at most

`2^k`

strict changes.

For countable ABA, the generic complete-type lattice has

`|T_k| = 2^(2^k)-1`

complete k-types, giving the much larger generic omega-categorical strict-change bound.

Thus the equational safety fragment improves the semantic fixed-point bound from

`2^(2^k)-1`

to

`2^k`.

The reason is not a better enumeration of complete types: the winning regions never leave the principal-ideal sublattice generated by forbidden Venn cells.

## 7. Memoryless Boolean-term strategy theorem

Finite safety games admit memoryless winning strategies. Let

`sigma : A_* x {0,1}^p -> A_*`

be one.

The formula from the sufficiency proof yields a BA controller:

`y_j(s,x)
 = OR_{(a,u) : sigma(a,u)_j=1}
   [C_a(s) AND C_u(x)].`

### Theorem 3

Whenever the equational BA safety game is realizable from `W_(A_*)`, it has a **memoryless controller whose outputs are ordinary Boolean terms of the current BA state and input**.

A direct DNF construction uses at most `2^(k+p)` joint minterms per output coordinate before Boolean minimization.

This is a constructive synthesis theorem, not merely a realizability decision.

## 8. Noether / Stone-duality interpretation

This collapse is the structural reason Boolean algebras are unusually friendly for equational synthesis.

Every Boolean-algebra equation is pointwise: under Stone representation, a BA is represented by clopen sets, and a term equation holds globally iff its two-element Boolean truth function holds at every Stone point.

The safety condition therefore decomposes into independent finite Boolean games at the points/cells.

The controller can glue the pointwise finite strategy back into BA elements because every Boolean truth table is representable by a Boolean term (DNF/CNF).

So the theorem combines two classical facts in a reactive setting:

1. Boolean equations are controlled by the two-element algebra;
2. finite Boolean strategies are term-definable and therefore glue uniformly across BA regions.

## 9. Interpreted constants

Let a finite set of interpreted constants `C` induce `rho(C)` nonzero constant regions.

On each constant region, the constants have one fixed Boolean valuation `c`. Specialize the transition truth function to that valuation:

`f_c(a,u,v)`.

Each constant region therefore has its own finite cube game and winning cell set `A_*^c`.

An actual state is winning iff, in every constant region `c`, all nonzero state minterms have labels in `A_*^c`.

This is again definable by one Boolean-algebra equation with coefficients from the constants.

The total number of `(constant-region,state-cell)` labels is

`rho(C) * 2^k`,

so the region-wise descending iteration has at most that many strict cell removals.

## 10. Relation to Asor's fixed-point direction

Asor's ocLTL conclusion observes that fragments reducible directly to fixed-point operators over omega-categorical structures can avoid explicit complete-type enumeration, because fixed-point operators can be eliminated in that setting.

The theorem here identifies a concrete ABA/BA fragment where the stronger statement can be made explicitly:

- no `T_k` enumeration is needed;
- the fixed-point carrier is the `2^k` Venn-cell cube;
- every iterate is a single equation;
- a winning strategy is extracted as Boolean terms.

This should be tested as a direct Tau backend rather than translated through full ocLTL type tables.

## 11. Relation to first-order safety-game literature

General first-order safety synthesis can require second-order quantifier elimination and abstraction/refinement machinery. The equational BA fragment collapses much further because equations are pointwise and Boolean strategy functions are term-definable.

This does not imply comparable collapse for inequations or arbitrary first-order predicates: `g!=0` is an existential/nonlocal condition over the support and couples the Stone points through a global "somewhere nonzero" requirement.

## 12. Scope boundary: why inequations change the game

For an equation `F=0`, every active Venn region must independently satisfy the two-element safety relation.

For an inequation `G!=0`, it is enough that **one** active region witnesses `G=1`. Different regions are no longer semantically independent, and the principal-ideal winning-region invariant can fail.

Therefore the equation-only boundary is mathematically meaningful, not cosmetic.

A next falsification program should add exactly one inequation and determine the smallest game where the cube-collapse theorem fails.

## 13. Validation completed

A private checker exhaustively compared Theorem 1 with the explicit complete-support game for the bounded case

- one BA state variable;
- one environment BA input;
- one BA output/next-state variable;
- all nonempty state supports;
- explicit enumeration of all `(s,x)` and `(s,x,y)` support extensions;
- random 8-cell Boolean transition terms F;
- every principal-ideal target region `W_A`.

No divergence was found. Fixed-point trajectories were also checked on random F.

A reproducible checker is committed separately.

## 14. Algorithmic consequence

For equational safety specifications, the synthesis pipeline can be:

1. compile F to its ordinary finite Boolean truth function / circuit;
2. solve the finite safety game on `2^k` state valuations using standard symbolic or explicit methods;
3. turn the resulting finite positional strategy into Boolean terms;
4. interpret those terms directly over the target Boolean algebra.

This bypasses:

- complete ABA type enumeration;
- generic first-order fixed-point iteration;
- the ocLTL `T_3` feasibility construction;
- repeated ABA quantifier elimination during game solving.

The remaining engineering question is whether Tau can preserve the Boolean circuit structure of F so the finite cube game is solved without expanding a compact term to a full truth table when k is large.
