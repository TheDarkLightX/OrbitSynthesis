# Three-state reactive term safety is NP-hard over F3

**Status:** DERIVED NP-completeness theorem for a sparse forbidden-observation representation. Graph 3-colorability NP-completeness is classical. This complements the input-free hardness theorem by moving the growing dimension from state arity to environment-input arity. Tau-independent. Not Lean-checked.

## 1. Why another hardness embedding matters

`F3_ROW_LIST_REACTIVE_HARDNESS.md` proves NP-complete input-free sparse term safety over

`A=(F_3;+,-,0)`,

but its state arity grows with the source SAT instance.

One might hope the hardness is merely caused by the exponentially large ambient state cube.

It is not.

The same fixed algebra has NP-hard controller existence with **one state coordinate**, hence exactly three local states.

The price is that the environment input arity grows.

## 2. Decision problem

Fix

`A=(F_3;+,-,0)`.

An instance gives:

- an environment input arity n;
- a sparse finite set `F subseteq F_3^n` of input vectors that are dangerous when the current state and next state are both 0.

The current state is

`s in F_3`.

The environment chooses

`u in F_3^n`.

The controller chooses the next state/output

`y in F_3`.

Safety is:

`not (s=0 and u in F and y=0)`.

Equivalently:

- at state 0 and a listed dangerous input, y must be nonzero;
- every other transition is safe.

The candidate invariant domain is the full carrier

`W=F_3`,

so every controller output automatically remains in W.

The controller must be one original-signature term

`sigma:F_3^(n+1)->F_3`.

## 3. Term controllers

Every such term has form

`sigma(s,u_1,...,u_n)
 = beta s + alpha_1 u_1 + ... + alpha_n u_n`

for coefficients

`beta,alpha_i in F_3`.

## 4. Reduction from graph 3-colorability

Let

`G=(V,E)`, `V={1,...,n}`.

For each edge `{i,j}` put the dangerous input

`u_(ij)=e_i-e_j`

into F.

No other input is dangerous.

### If G is 3-colorable

Let

`alpha_i in F_3`

be the color of vertex i.

Choose beta arbitrarily, for example beta=0.

At a dangerous observation with current state 0:

`sigma(0,e_i-e_j)=alpha_i-alpha_j`.

Proper coloring makes this nonzero, so every dangerous transition is safe.

Every nonlisted observation is safe by definition.

Hence sigma is a winning term controller on all three states.

### If a winning term controller exists

Take its coefficient vector alpha.

For every edge `{i,j}`, the environment may choose

`s=0, u=e_i-e_j`.

Safety forces

`alpha_i-alpha_j != 0`.

Thus i and j receive different F3 values.

So alpha is a proper 3-coloring of G.

### Theorem 1

Sparse three-state original-signature term safety over `(F_3;+,-,0)` is NP-hard.

## 5. NP membership

The certificate is the coefficient vector

`(beta,alpha_1,...,alpha_n) in F_3^(n+1)`.

Since every unlisted transition is safe, verification only evaluates the term on the explicitly listed dangerous inputs.

Thus the problem is in NP.

### Corollary 2

The problem is NP-complete.

## 6. Strength of the restriction

The hardness holds with:

- one fixed 3-element algebra;
- exactly three local states;
- one scalar next-state/output coordinate;
- no controller memory beyond the current state;
- full state invariant W=F3;
- every dangerous observation forbidding exactly one output value;
- dangerous input vectors of support exactly two;
- a sparse representation containing one dangerous vector per graph edge;
- polynomial-time ordinary SMP for the controller algebra.

Only the environment input arity grows.

## 7. Comparison with the input-free reduction

There are now two incomparable minimal-looking embeddings.

### Input-free hardness

`F3_ROW_LIST_REACTIVE_HARDNESS.md`:

- input arity 0;
- state/output arity grows with n;
- every listed state has at most two safe successors.

### Three-state hardness

This note:

- state/output arity 1;
- exactly three states;
- input arity grows with n;
- each dangerous observation merely forbids output 0.

Together they show the hardness is not tied specifically to large state dimension or to adversarial input. Either dimension can carry the term coefficients that encode the NP search.

## 8. Representation caveat

The safety relation is sparse and implicit:

`all transitions safe except the listed forbidden triples`.

The full input space F3^n is exponential and is not enumerated.

Do not reinterpret the theorem under a full truth-table representation without adjusting the input-size measure.

The relation is also not claimed to be definable by one module equation.

## 9. Exact calibration

`experiments/f3_three_state_reactive_hardness.py` exhausts every labelled simple graph on up to five vertices.

For each graph it compares:

1. brute-force 3-colorability;
2. direct search over all term coefficient vectors `(beta,alpha)` for the three-state safety game.

It checks 1,099 graphs total.

## 10. Product implication

A standalone solver cannot assume that a tiny concrete state carrier makes synthesis easy.

It should track at least:

- concrete state size;
- state arity;
- environment-input arity;
- term-clone/interpolation complexity;
- safety-relation representation;
- row-list/disequality structure.

This is another reason the independent OrbitSynthesis architecture should expose algebraic structure explicitly instead of hiding everything behind one generic finite-state count.
