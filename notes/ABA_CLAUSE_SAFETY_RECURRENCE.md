# Direct fixed-point recurrence for ABA clause safety games

**Status:** DERIVED from `ABA_CLAUSE_SAFETY_HYPERGRAPH.md`; one-step and end-to-end bounded differential checks completed; Lean pending; literature novelty under review.

## 1. Finite transition data

Let

- `S={0,1}^k` be Boolean state-cell labels;
- `I={0,1}^p` be Boolean input labels;
- `V={0,1}^k` be output/next-state labels.

A normalized ABA safety transition clause is represented by:

- an allowed triple set `L subseteq S x I x V`, from the transition equation;
- transition hit sets `G_1,...,G_q`, from transition inequations.

A nonempty state-region approximation is represented canonically as `R(A;H)` where:

- `A subseteq S` is the allowed state-cell set;
- H is an inclusion antichain of **proper nonempty** subsets of A;
- support T belongs iff `empty != T subseteq A` and T hits every H in H.

The restriction to proper hits is important: `H=A` is tautological on nonempty supports and is not stored.

## 2. Ordinary cube predecessor P

Define

`P(B) := {a : for every u, exists v in B with (a,u,v) in L}.`

This is the controllable predecessor of the finite Boolean-cube game determined by the transition equation alone. P is monotone.

## 3. Transition-hit injection J_i

For each transition hit G_i define

`J_i(B)
 := {a : for every u,
        exists v in B with (a,u,v) in L intersect G_i}.`

Always

`J_i(B) subseteq P(B)`.

## 4. Target hits propagate by the same P

For a target hit `H subseteq A`, lifting it to the output coordinate and applying the support-hypergraph predecessor produces

`{a : forall u exists v in H . (a,u,v) in L}`,

which is exactly `P(H)`.

Since H⊆A,

`P(H) subseteq P(A)`.

This is the central decoupling.

## 5. Canon operator

For allowed set B and candidate hit family K, define `Canon(B,K)`:

1. replace each K by `K intersect B`;
2. if B is empty or any K is empty, return the empty semantic region;
3. delete every K equal to B (implicit-nonemptiness tautology);
4. remove duplicates;
5. remove every hit that strictly contains another retained hit.

This correction was discovered by whole-fixed-point differential testing: keeping the tautological hit B preserves one-step semantics but breaks structural canonical equality and can delay a fixed-point stopping test.

## 6. Exact predecessor recurrence

### Theorem 1

`CPre(R(A;H))
 = Canon(
     P(A),
     {J_i(A) : 1<=i<=q} union {P(H) : H in H}
   ).`

Thus equations and inequation obligations evolve through one finite monotone transformer P plus q injection maps J_i. No complete ABA type is enumerated.

## 7. Kleene iteration

Initialize

`A_0=S`, `H_0=empty`.

Then

`A_(t+1)=P(A_t)`

and

`(A_(t+1),H_(t+1))
 = Canon(
     P(A_t),
     {J_i(A_t)}_i union {P(H) : H in H_t}
   ).`

Stop when the canonical pair stops changing.

Because the representation is now semantically canonical on the nonempty support domain, pair equality is a sound fixed-point stopping test.

## 8. Allowed cells converge independently

The sequence A_t is independent of all inequations and equals the equation-only finite cube safety iteration.

It reaches its greatest fixed point A_* after at most

`|S|=2^k`

strict cell removals.

Inequations may continue to strengthen the nontrivial hit antichain after A stabilizes, but they do not change which individual Boolean state labels are equation-safe.

## 9. Expanded obligation history

Before canonical subsumption, the time-t candidate hits are

`{ P^(t-1-r)(J_i(A_r)) : 0<=r<t, 1<=i<=q }`.

This follows by induction from the recurrence: each transition inequation injects a new one-step obligation, while every older obligation is transported by P.

Canonicalization can delete:

- empty => whole region empty;
- full allowed set => tautological due nonempty support;
- duplicates;
- supersets of stronger hits.

## 10. Maximal-response controller

Suppose the fixed point is nonempty `(A_*,H_*)`.

For every Boolean state/input label `(a,u)` define

`V_(a,u) := {v in A_* : (a,u,v) in L}.`

For winning state cells a, every V_(a,u) is nonempty because `A_*=P(A_*)`.

### Theorem 2 — maximal response is winning

Inside every nonzero actual `(s,x)` region labeled `(a,u)`, let the controller realize **every** output label in V_(a,u) as a nonzero refinement.

Then the resulting output:

1. satisfies the transition equation;
2. remains inside A_*;
3. satisfies every transition inequation;
4. makes the next support satisfy every H in H_*.

### Proof sketch

For transition inequation i, winning support hits `J_i(A_*)`; on such a state cell, every input label has an allowed G_i-witness v, which maximal response includes.

For target hit H, fixed-point recurrence requires the current support to hit P(H); on such a state cell, every input label has an allowed output in H, which maximal response includes.

Atomlessness realizes all required finite output refinements simultaneously.

## 11. Separation of responsibilities

The maximal response relation depends only on:

- transition equation L;
- final equation-safe set A_*.

Inequations determine **which supports are winning** through H_*, but the controller need not choose a delicate subset of equation-safe output labels: realizing all of them is sufficient.

So structurally:

- equations determine safe local moves;
- inequations determine global support obligations;
- atomlessness lets maximal local moves satisfy all obligations simultaneously.

## 12. Concrete split witness

If V_(a,u) has d labels, an actual nonzero BA region b must be split into d disjoint nonzero pieces whose join is b, one per output label. Atomlessness guarantees every finite such split.

An executable backend therefore needs an effective split-witness routine in addition to the finite hypergraph solver.

## 13. Representation-independent algorithm

For moderate k:

- A and each H are `2^k`-bit masks;
- P/J are `forall input / exists output` projections over the finite Boolean cell relation;
- H is kept as an inclusion antichain.

For larger instances, the same recurrence can use ZDD/ROBDD/SAT-backed set representations. The theorem does not privilege one data structure.

## 14. Worst-case warning

The hit antichain can have Sperner size

`binom(2^k, 2^(k-1))`.

Moreover, coordinate membership in P has positive-CNF form

`a in P(B) iff AND_u OR_{v in B} L(a,u,v)`.

With enough input labels, this is expressive enough that no generic polynomial antichain/orbit bound should be assumed.

## 15. Favorable subclasses

Attack these by exhaustive small-case search before general proof attempts:

1. no inequations;
2. laminar/nested hit families;
3. deterministic/functional equation-safe transitions;
4. input-free systems;
5. bounded transition-inequation count q;
6. P-invariant laminar families;
7. symmetries reducing hit orbits.

## 16. Validation

`experiments/aba_clause_safety_hypergraph.py` now compares the entire canonical recurrence against explicit complete-support safety iteration in the one-state/one-input/one-output-bit universe.

Repository defaults perform:

- 5,000 randomized one-step checks;
- 2,000 randomized whole fixed-point trajectory checks.

A larger private run of 10,000 random trajectories also matched at every iteration after the `H=A` canonicalization correction. Examples with up to four iterations occur in this tiny three-state-support universe.

## 17. Next target

Measure canonical hit growth and P-orbits on generated Tau clauses, then prove bounds for whichever structural subclass actually occurs frequently rather than choosing a fashionable subclass in advance.
