# Knowledge compilation for canonical response families

**Status:** DERIVED reduction + application of established knowledge-compilation theorems. The compilation theorems are literature; OrbitSynthesis contributes the response-conflict reduction and synthesis interpretation.

`HENSON_RESPONSE_WIDTH.md` proves that the canonical maximal-response antichain may be exponential even when the legal response family has a tiny factorized description. Therefore the next backend should represent the **whole legal response relation**, not enumerate its maximal models.

## 1. Response bits

Let a response be a subset

`N subseteq V`

encoded by Boolean variables

`x_v = 1 iff v in N`.

Suppose legality is specified by a conflict hypergraph C: no conflict edge may be fully selected.

Then legality is the CNF

`Legal_C(x) = AND_{F in C} OR_{v in F} NOT x_v`.

An upward target represented by hit obligations H is

`Target_H(x) = AND_{h in H} OR_{v in h} x_v`.

Thus the one-step response existence query is exactly SAT of

`Legal_C(x) AND Target_H(x)`.

No maximal-response enumeration is required.

## 2. Henson K_n-free specialization

For a finite old K_n-free graph G, let C consist of all `(n-1)`-cliques of G.

A fresh response neighborhood N is legal iff it does not contain any C in full.

Hence

`Legal_Henson(x)
 = AND_{C in Cliques_(n-1)(G)} OR_{v in C} NOT x_v`.

The clause width is fixed at n-1 for fixed Henson theory H_n.

Upward adjacency objectives add positive clauses.

Therefore Henson fresh-response synthesis becomes a structured CNF/QBF problem over the old-vertex neighborhood bits.

## 3. Incidence treewidth parameter

Build the incidence graph of the combined response formula:

- one vertex for each response variable x_v;
- one vertex for each conflict/target clause;
- incidence edges connecting variables to clauses that mention them.

Let its treewidth be t.

Established knowledge-compilation results compile bounded-treewidth CNF into deterministic decomposable NNF with size/time fixed-parameter tractable in t.

More recent results extend singly-exponential incidence-treewidth compilation beyond CNF to constraint languages including parity/XOR and bounded-threshold cardinality constraints.

This is directly relevant to Tau/OrbitSynthesis because source terms may contain XOR structure that should not be destroyed by CNF expansion.

## 4. Quantifier projection

Structured d-DNNF / bounded-width knowledge-compilation frameworks support existential and universal projection of variable blocks, with width blowup controlled by the representation width.

Thus a response compiler can perform:

`exists system-response bits. [Legal AND Target]`

symbolically.

For a one-step reactive predecessor containing a fixed `forall environment / exists system` alternation, bounded-width quantified-formula results give a fixed-parameter route in the structural width (with the known nontrivial dependence on quantifier alternation).

This should be treated as an application of existing parameterized QBF/KC theory, not as a new generic complexity theorem.

## 5. Why this matters after the Henson lower bound

For

`G_m = m K_(n-1)`,

there are `(n-1)^m` maximal response neighborhoods, but the legality formula is only m independent clauses:

`AND_{j=1}^m OR_{v in C_j} NOT x_v`.

Its incidence graph is a forest of stars, hence has constant treewidth.

So:

- flat canonical-action enumeration is exponential;
- response-CNF size is linear;
- structural width is constant;
- knowledge compilation is compact.

This is the exact kind of representation separation OrbitSynthesis needs to exploit.

## 6. Backend hierarchy refined

### Unique greatest response

Use one extremal action; eliminate the system player.

### Small maximal-response antichain

Enumerate canonical maximal actions.

### Exponential antichain but low-width conflict formula

Compile the whole response relation to d-DNNF/SDD/ZDD or solve by tree-decomposition dynamic programming.

### High-width but symmetric conflict structure

Quotient by automorphisms before compilation.

### General hypergraph

Use hypergraph dualization / SAT / general finite type-game fallback.

## 7. Interaction with hypergraph duality

The two descriptions are dual:

- conflict CNF encodes all legal responses compactly;
- minimal transversals encode complements of maximal legal responses.

Knowledge compilation avoids explicitly materializing the transversal hypergraph when it is exponentially larger than the original conflicts.

Conversely, if the transversal side is much smaller, `ABA_HYPERGRAPH_DUALITY.md` suggests switching representations.

Thus the correct object is not one canonical data structure but a **dual representation portfolio**.

## 8. Source-level structure

The same principle applies to ABA cell-label synthesis:

- Tau Boolean terms directly define Boolean circuits over cell-label bits;
- affine/XOR fragments should use linear algebra or XOR-aware compilation;
- bounded-incidence-width mixed constraints can use structured KC;
- only dense/high-width formulas should fall back to explicit support/type representations.

The compiler should measure width before expanding terms to minterms or CNF.

## 9. Literature anchors

Relevant established results include:

- Capelli & Mengel, *Knowledge Compilation, Width and Quantification* (2018): structured deterministic-DNNF width and quantified projection; bounded-treewidth quantified CNF with bounded alternation is FPT.
- de Colnet, Szeider & Zhang, *Compilation and Fast Model Counting beyond CNF* (2025): FPT d-DNNF compilation parameterized by incidence treewidth for constraint classes including parity and bounded-threshold cardinality constraints.

These are algorithmic ingredients, not OrbitSynthesis novelty claims.

## 10. Next theorem/engineering targets

1. Prove a formal reduction from Henson fresh-response CPre to bounded-width QBF on the response incidence graph.
2. Benchmark conflict-CNF versus maximal-response enumeration on `m K_(n-1)` and random K_n-free bases.
3. Add XOR-aware compilation for ABA affine transition formulas and compare with direct Gaussian elimination.
4. Measure treewidth before and after naive minterm/CNF expansion to quantify the cost of losing source structure.
5. Combine symmetry quotienting with tree decomposition: quotient first, compile second.
