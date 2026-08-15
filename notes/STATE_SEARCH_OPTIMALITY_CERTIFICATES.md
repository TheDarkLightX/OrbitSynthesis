# Proof-carrying weighted synthesis by state-search certificates

**Status:** exact finite theorem and implementation. The certificate verifier
is independent of the optimizer that produced the claimed controller. The
format can be exponentially large and is not claimed to be a general
polynomial-size MaxSAT proof system.

## 1. Component-domain semantics

Let `S` be the finite state set. The compiled quasi-primal controller model has
components `C`. Each component has a finite set of candidate rules `T_C`.
Every rule `tau` carries:

```text
F_tau subseteq S
E_tau subseteq S x S.
```

A complete domain `D subseteq S` accepts `tau` exactly when

```text
F_tau cap D = empty
```

and

```text
(s,t) in E_tau and s in D  implies  t in D.
```

The domain is term-winning exactly when every component has at least one
accepted candidate rule.

## 2. Partial state assignments

A partial assignment is a disjoint pair `(I,E)`:

```text
I = states already included,
E = states already excluded.
```

Its completion cylinder is

```text
Cyl(I,E)={D subseteq S : I subseteq D and D cap E=empty}.
```

A candidate rule is already impossible at `(I,E)` when either

```text
F_tau cap I != empty,
```

or there is an edge

```text
(s,t) in E_tau
```

with

```text
s in I and t in E.
```

Both violations are monotone under completion.

### Component-conflict lemma

If every candidate rule of one component is impossible at `(I,E)`, then no
`D in Cyl(I,E)` is term-winning.

The proof is immediate: any complete controller must select one candidate in
every component, but the identified component has none.

## 3. Exact signed objective bound

Let `w:S->Z` be the primary state utility. For a partial assignment define

```text
UB(I,E)
 = sum_(s in I) w(s)
 + sum_(s notin I union E) max(0,w(s)).
```

### Bound lemma

For every `D in Cyl(I,E)`,

```text
sum_(s in D) w(s) <= UB(I,E).
```

Each undecided positive state contributes at most its weight, while an
undecided nonpositive state cannot improve the score.

## 4. Certificate tree

A state-search proof is a finite rooted binary tree. Every node denotes one
partial assignment. A node is one of:

### Conflict leaf

Names one component with no viable candidate. The component-conflict lemma
proves every completion infeasible.

### Bound leaf

Records the recomputed value `UB(I,E)` and requires

```text
UB(I,E) <= S_star,
```

where `S_star` is the claimed optimum score.

### Branch node

Chooses one undecided state `s` and has exactly two children:

```text
(I union {s},E)
(I,E union {s}).
```

These cylinders are disjoint and their union is the parent's cylinder.

## 5. Optimality theorem

Assume:

1. the root is the required/forbidden hard-state assignment;
2. every leaf is a valid conflict or bound leaf;
3. every internal node is a valid state branch;
4. one target domain `D_star` satisfies the hard constraints;
5. `D_star` is term-winning;
6. its score is `S_star`.

Then `D_star` is globally optimal for the primary signed objective.

### Proof

Induct from the leaves to the root. A conflict leaf contains no feasible
completion. A bound leaf contains no completion of score above `S_star`. A
branch node is the disjoint union of its two children, so the same statement
holds for the parent. At the root, no feasible hard-constrained domain beats
`S_star`. Since `D_star` is feasible with exactly that score, it is optimal.

## 6. Infeasibility theorem

If no target score is supplied and every leaf is a valid component conflict,
then no hard-constrained term-winning domain exists.

No objective-bound leaf is permitted in an infeasibility proof.

## 7. Verification complexity

Let:

```text
N = number of proof nodes,
R = total candidate-rule representation size.
```

A direct verifier checks each node against the compiled component model. The
simple implementation is polynomial in `N` and `R`. It never repeats the
optimizer's branch-and-bound search; it follows the supplied tree and checks
local obligations.

The proof itself may have exponential size. This is expected: exact weighted
controller synthesis is NP-hard in the explicit relation model, and the format
makes no succinct-certificate claim for arbitrary instances.

## 8. Relation to external MaxSAT

The complete proof-carrying pipeline is

```text
WCNF / MILP search oracle
        |
        v
Boolean assignment
        |
        v
OrbitSynthesis hard-clause and controller replay
        |
        v
feasible domain/controller certificate
        |
        v
state-search optimum or infeasibility certificate
```

The external backend can be HiGHS, RC2, Open-WBO, MaxHS, or another solver.
The final mathematical authority comes from the checked certificate, not from
the backend status string.

## 9. Compression frontier

The uncompressed proof tree suggests several new research problems:

1. hash-cons identical residual subproblems into a proof DAG;
2. replace repeated component conflicts by model-bound learned clauses;
3. add pseudo-Boolean cuts with independently checked arithmetic;
4. translate state conflicts to LRAT or VeriPB proof steps;
5. characterize algebras or game families with polynomial certificate size;
6. exploit the exact orientation geometry of antichain families to emit
   closed-form certificates rather than search trees;
7. reuse certificates under incremental specification changes.

The practical target is a portfolio:

```text
closed-form theorem certificate
or bounded exhaustive authority
or compressed state-search proof
or general proof-producing MaxSAT trace.
```

## 10. Nonclaims

This result does not prove:

- polynomial-time synthesis;
- polynomial-size optimality certificates in general;
- a new general MaxSAT proof system;
- proof-producing HiGHS;
- formal verification in Lean;
- publication novelty.

It gives OrbitSynthesis a precise, independently replayable optimality object
for finite clone-constrained controller synthesis.