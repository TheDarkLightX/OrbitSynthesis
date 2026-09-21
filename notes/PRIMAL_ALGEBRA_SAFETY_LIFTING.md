# Causal equational safety synthesis in primal varieties

**Status:** DERIVED theorem from classical Foster Boolean-power representation + finite safety-game memorylessness + primal term completeness. The universal-algebra ingredients are classical. A targeted literature search found primal-algebra representation/unification work but no direct reactive-synthesis statement; **novelty is not yet established**.

This note generalizes `EQUATIONAL_SAFETY_CUBE_GAME.md`. The two-element Boolean algebra is only the smallest primal algebra.

## 1. Classical universal-algebra background

Let P be a finite nontrivial algebra.

P is **primal** if every finitary function

`P^m -> P`

is represented by a term operation of P (including constant functions in the standard primal setting).

The two-element Boolean algebra is the basic example: every Boolean truth function is term-definable.

Foster's theorem for finite primal algebras states that every algebra

`A in V(P)=HSP(P)`

is isomorphic to a Boolean power of P. Concretely, for some Boolean algebra / Stone space X,

`A ~= C(X,P)`,

the algebra of continuous functions from X to the finite discrete algebra P, with all fundamental operations evaluated pointwise.

Equivalently, an element of A is a finite clopen partition of X labeled by elements of P.

None of this representation theory is new here.

## 2. Local finite safety game

Fix:

- k state variables;
- p environment-input variables;
- k controller-output variables, also used as next state.

Let the safety condition be any finite conjunction of equations in the algebraic signature,

`E(s,x,y)`.

Evaluating those equations in the finite generator P gives a finite safe-transition relation

`R_E subseteq P^k x P^p x P^k`.

For `W subseteq P^k`, define the ordinary finite safety predecessor

`Pre_P(W)
 := { a in P^k : for every u in P^p,
        exists v in W with (a,u,v) in R_E }.`

Let

`W_* = nu W . Pre_P(W)`

be the greatest winning set of this finite perfect-information safety game.

Because P is finite, the game has a positional winning strategy on W_*.

## 3. Pointwise support/image of an A-state

Represent A as `C(X,P)`.

For an A-state tuple

`s in A^k`,

define its local image/support

`Img(s) := { s(xi) in P^k : xi in X }`.

Because s is continuous and P^k is finite discrete, each fiber

`X_a := {xi : s(xi)=a}`

is clopen, and only finitely many are nonempty.

For `W subseteq P^k`, define

`Lift_A(W) := {s in A^k : Img(s) subseteq W}`.

## 4. One-step commutation theorem

### Theorem 1

For every algebra `A in V(P)` and every `W subseteq P^k`,

`CPre_A(Lift_A(W)) = Lift_A(Pre_P(W)).`

Here `CPre_A` uses the causal round order:

1. current A-state s is fixed;
2. environment chooses current A-input x;
3. controller observes x and chooses A-output/next state y;
4. E(s,x,y) must hold and y must lie in the target region.

### Sufficiency

Assume

`Img(s) subseteq Pre_P(W)`.

For every finite local state/input pair

`(a,u) in Pre_P(W) x P^p`,

choose a response

`sigma(a,u) in W`

with

`(a,u,sigma(a,u)) in R_E`.

Extend sigma arbitrarily to a total function

`P^(k+p) -> P^k`.

Because P is primal, every coordinate `sigma_j` is represented by a term

`t_j(s,x)`.

For an arbitrary actual A-input x, define

`y_j := t_j^A(s,x)`.

Operations in the Boolean power are pointwise, so at every Stone point xi,

`y(xi)=sigma(s(xi),x(xi))`.

Since `s(xi)` lies in `Pre_P(W)`, the local transition is safe and the local next state lies in W. Hence all equations E hold pointwise and therefore in A, while `Img(y) subseteq W`.

So s is a controllable predecessor of `Lift_A(W)`.

### Necessity

Assume `Img(s)` contains

`a notin Pre_P(W)`.

Then there is a local environment input

`u in P^p`

such that no `v in W` gives a safe transition from `(a,u)`.

The fiber

`X_a={xi:s(xi)=a}`

is a nonempty clopen subset of X.

Choose an A-input function x that equals u on X_a and is any fixed value outside X_a. Such a piecewise-constant function belongs to the Boolean power A.

If a controller output y were safe and in `Lift_A(W)`, then for every xi in X_a we would have

`y(xi) in W`

while `(a,u,y(xi))` would have to satisfy the finite equations—contradicting the choice of u.

Therefore s is not a controllable predecessor.

## 5. Greatest-fixed-point lifting

Since `Lift_A(P^k)=A^k`, iterating Theorem 1 from the top gives:

### Theorem 2

The infinite-algebra safety winning region is exactly

`Win_A = Lift_A(W_*)`.

Thus causal equational safety synthesis over every algebra in the primal variety V(P) is completely determined by the finite safety game on `|P|^k` local state labels.

The descending chain has at most

`|P|^k`

strict local-state removals.

## 6. Winning region is itself equational

Primality makes every characteristic function term-definable.

Choose distinct constants `c0,c1 in P`. For an arbitrary finite set `W subseteq P^k`, define a function

`chi_W : P^k -> P`

by

- `chi_W(a)=c0` if `a in W`;
- `chi_W(a)=c1` otherwise.

Primality yields a term `q_W(s)` representing chi_W.

Then in every Boolean power A,

`q_W(s)=c0`

holds iff `Img(s) subseteq W`.

### Corollary 3

Every lifted finite winning region is definable by a **single equation**.

Therefore the equational safety fragment is closed under controllable predecessor and greatest fixed point throughout every primal variety.

## 7. Positional term-controller theorem

Finite safety games admit a positional winning strategy

`sigma : W_* x P^p -> W_*`.

Extend it arbitrarily to all of `P^(k+p)`. By primality, each output coordinate is a term.

### Theorem 4

Every realizable causal equational safety game over `A in V(P)` has a **memoryless controller given by algebraic terms of the current A-state and current A-input**.

The same finite tuple of terms works uniformly for every algebra A in the variety V(P).

This uniformity is stronger than merely deciding each Boolean power separately.

## 8. Expressive completeness of equational local transitions

Because P is primal, every finite relation

`R subseteq P^k x P^p x P^k`

can be represented by one equation over P and therefore pointwise over every Boolean power.

Choose a characteristic function of R taking c0 on R and c1 outside R, represent it by a term h, and use equation

`h(s,x,y)=c0`.

### Corollary 5

Causal equational safety games in a primal variety are, at the local-label level, exactly arbitrary finite perfect-information safety games on P-valued state/input/output coordinates.

The infinite algebra adds a Boolean-power spatial decomposition, but no new equation-only strategic complexity beyond the finite generator game.

## 9. Boolean algebra as P=2

Take P to be the two-element Boolean algebra.

Foster's Boolean-power representation becomes Stone representation of Boolean algebras, and

`|P|^k=2^k`.

Theorems 1–4 specialize exactly to `EQUATIONAL_SAFETY_CUBE_GAME.md`.

This reframes that result:

> the Boolean theorem is the two-valued member of a primal-variety safety-lifting principle.

## 10. Support geometry in the atomless Boolean power

Let B be the countable atomless Boolean algebra and consider the countable atomless Boolean power

`P[B]`.

A k-tuple determines a nonempty local support

`S subseteq P^k`.

Every nonempty S is realizable: partition 1 into |S| nonzero Boolean regions and label them by the elements of S.

Thus the number of possible support patterns is

`2^(|P|^k)-1`.

The obvious support code uses exactly

`|P|^k`

bits and is information-theoretically minimum-width because

`ceil(log2(2^(|P|^k)-1)) = |P|^k`.

## 11. Extension geometry generalization

Suppose a k-tuple has support size s and add r new P-valued algebra elements.

Inside each active old region, the r new elements may realize any nonempty subset of

`P^r`.

Hence the exact number of support extensions is

`(2^(|P|^r)-1)^s`.

The complete extension relation on support bits is local:

`z_a <-> OR_{b in P^r} w_(a,b)`

for each old local label `a in P^k`.

Under a block-local ROBDD order, the same proof as `ABA_EXTENSION_ROBDD.md` gives exact relation size

`|P|^k * (1 + 2|P|^r)`

nonterminal nodes.

So the 'huge explicit branching / tiny extension relation' phenomenon is a **primal Boolean-power phenomenon**, not specifically a two-valued Boolean one.

## 12. Relationship to n-valued Boolean-like algebras

Modern work on Boolean-like algebras of finite dimension (nBAs) shows that finite primal algebras are captured by this generalized if-then-else / Boolean-power framework and gives a modern proof of Foster's theorem.

This makes n-valued/primal data domains a concrete candidate extension of Tau-style symbolic synthesis:

- local finite truth domain P;
- infinite Boolean-power data algebra;
- equation-only safety solved on P^k;
- support-symbolic quantification inherited from the same partition geometry.

This is a research direction, not a claim that current Tau already supports arbitrary primal signatures.

## 13. Historical/prior-art guard

The following ingredients are classical and must be cited, not claimed:

- Foster's primal-algebra / Boolean-power theorem;
- primal term completeness;
- finite safety-game positionality;
- Wang / Even–Meyer sequential Boolean equation synthesis in the two-valued setting;
- Boolean equation elimination and Stone/Boolean-power pointwise semantics.

The candidate contribution is their synthesis-theoretic combination:

1. exact causal predecessor commutation across the entire primal variety;
2. uniform term-strategy lifting;
3. support/extension complexity consequences for infinite Boolean powers;
4. use as a direct backend for Tau-like infinite-data synthesis.

A deeper literature search is still required before using 'new' in a paper title or abstract.

## 14. Falsification boundaries

Primality is doing real work.

If P is not primal, a finite winning strategy function may not be term-definable, so it may fail to lift to a controller internal to every algebra in V(P).

If algebras are not Boolean powers / sufficiently separated by the finite local factors, pointwise correctness may not characterize equations in the needed way.

If inequations or other existential support properties are added, local points cease to be independent and the simple `Lift(W)` carrier need not be closed—exactly as `s!=0` already shows for Boolean algebras.

These boundaries should be attacked next rather than silently generalized away.

## 15. Next theorem targets

1. Determine the weakest universal-algebraic hypothesis replacing primality: quasi-primal / semi-primal / discriminator plus a strategy-preservation condition.
2. Characterize which finite strategies over a semi-primal generator are term-liftable.
3. Extend the ABA inequation hypergraph recurrence to Boolean powers of finite primal P; the support universe becomes `P^k` and the same hit-set semantics should apply for suitable non-equality predicates.
4. Check whether ocLTL's omega-categorical machinery recognizes these countable atomless Boolean powers uniformly.
5. Build a prototype for a small nBA/primal example with |P|=3 to validate the finite-game lifting and support extension formulas independently of the Boolean special case.
