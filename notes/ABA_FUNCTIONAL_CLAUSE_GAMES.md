# Input-free deterministic ABA clause games: exact orbit characterization

**Status:** DERIVED; unifies a tractable subclass with the Landau lower bound in `ABA_CLAUSE_WORST_CASES.md`; bounded examples checked computationally; novelty not established.

## 1. Setup

Let S be the n=`2^k` Boolean state-cell labels of k BA state variables.

Assume there is no environment input and the transition equation forces a deterministic next Boolean label

`v = delta(a)`

for a total function

`delta : S -> S`.

Equivalently, the BA transition equation forces

`y = delta(s)`

pointwise on every Stone/Venn region, where delta is represented by ordinary Boolean truth functions.

Let the q transition inequations, after restriction to the deterministic graph of delta, correspond to current-state hit sets

`C_1,...,C_q subseteq S`.

That is, inequation i is witnessed on a state region labeled a exactly when the unique full transition cell `(a,delta(a))` lies in its minterm support.

## 2. Cube predecessor becomes ordinary preimage

For every B subseteq S,

`P(B) = delta^(-1)(B)`.

Because delta is total,

`P(S)=S`,

so the allowed component of the clause recurrence is constant:

`A_t=S` for all t.

The transition-hit injection is simply

`J_i(S)=C_i`.

Therefore the exact hit recurrence is

`H_(t+1)
 = CanonHits(
     S,
     {C_i : 1<=i<=q}
     union {delta^(-1)(H) : H in H_t}
   ).`

## 3. Closed temporal form

Before subsumption, after t rounds the candidate hit family is

`{ delta^(-r)(C_i) : 1<=i<=q, 0<=r<t }`.

### Theorem 1 — winning support characterization

An ABA state support T is winning iff, for every inequation i and every time r>=0,

`T intersects delta^(-r)(C_i) != empty`.

Equivalently,

`delta^r(T) intersects C_i != empty`

for every i and r.

### Proof

Since delta is the unique pointwise next-state map, the support evolves deterministically as

`T_(r+1)=delta(T_r)={delta(a):a in T_r}`.

Inequation i must have at least one nonzero witnessing region at every round, exactly the displayed condition. The hypergraph recurrence is the backward form of the same requirement.

## 4. Functional-graph eventual periodicity

Every finite functional graph consists of directed trees feeding directed cycles.

Let

`d`

be the maximum transient depth: the largest number of steps any state takes to reach its eventual cycle.

Let the directed cycle lengths be

`ell_1,...,ell_m`

and define

`L=lcm(ell_1,...,ell_m)`.

Then, for every state a and every t>=d,

`delta^(t+L)(a)=delta^t(a)`.

Consequently, for every subset C,

`delta^(-(t+L))(C)=delta^(-t)(C)`

for every t>=d.

## 5. Exact finite horizon bound

### Theorem 2

The infinite winning condition in Theorem 1 is equivalent to checking only

`0 <= r < d+L`.

Therefore the fixed point stabilizes no later than round

`d+L`,

and before canonical subsumption there are at most

`q(d+L)`

distinct temporal hit obligations.

### Proof

Every later preimage set repeats one from the window `[d,d+L-1]`. Repeated injection of the C_i plus one-step preimage transport therefore reproduces the same family after all transient and periodic phases have appeared.

Canonicalization can only reduce the number of stored hits or cause earlier stabilization.

## 6. Acyclic-to-fixed-point corollary

Suppose every cycle of delta is a fixed point. Then

`L=1`.

Hence the game stabilizes by

`d+1 <= n`

rounds and has at most

`q(d+1) <= qn`

raw temporal obligations.

This is a genuine polynomial-in-n subclass of the clause backend.

It excludes the permutation lower bound for the exact structural reason that no nontrivial phase cycle exists.

## 7. Bounded-cycle corollary

If the lcm of the cycle lengths is bounded by a parameter lambda, then

- iteration count <= `d+lambda`;
- raw hit count <= `q(d+lambda)`.

Thus the relevant deterministic complexity parameter is not simply "functional" or "input-free" but the **eventual period of the cell dynamics**.

## 8. Landau lower bound is the extremal instance

For a permutation, d=0 and L is exactly the permutation order.

Maximizing L over permutations of n labels gives Landau's function g(n). Therefore `ABA_CLAUSE_WORST_CASES.md` is the extremal case of Theorem 2:

`fixed-point horizon = L = g(n)`

for a suitable one-inequation hit set with full orbit.

Classically,

`log g(n) ~ sqrt(n log n)`.

So the same theorem explains both:

- linear behavior for fixed-point functional graphs;
- superpolynomial/subexponential-in-n orbit growth for maximal-order permutations.

## 9. Controller extraction

No atomless output splitting is needed in this deterministic subclass: every current Venn region has exactly one output label delta(a).

The controller is the Boolean term representation of delta itself.

Atomlessness remains relevant to the semantic treatment of the state inequations, but not to strategy branching.

## 10. Algorithm

1. Compile the deterministic Boolean state map delta.
2. Build its functional graph on n Boolean cell labels (explicitly for moderate n, symbolically otherwise).
3. Compute transient depth d and cycle lengths.
4. For each inequation support C_i, generate preimage iterates until repetition; canonicalize by inclusion as they are generated.
5. The winning ABA supports are exactly the nonempty supports hitting every retained temporal obligation.

For an explicit n-state functional graph, steps 2-4 are polynomial in n plus the output antichain size.

## 11. Next generalization

With environment inputs but deterministic output functions

`delta_u(a)`,

the predecessor becomes

`P(B)={a : forall u, delta_u(a) in B}`.

Now temporal behavior is governed by the transformation semigroup generated by the input-indexed maps rather than one functional graph. This connects naturally to finite automata/semigroup theory and may yield useful parameters such as:

- semigroup size;
- aperiodicity;
- bounded group components;
- synchronization properties.

Do not generalize by analogy alone: first test whether aperiodic transformation semigroups force nested/small hit orbits and search the automata literature for the exact existing theorems.
