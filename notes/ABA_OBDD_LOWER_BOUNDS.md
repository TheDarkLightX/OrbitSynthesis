# OBDD lower bounds already occur in very simple ABA disequation clauses

**Status:** DERIVED reduction from the Bova–Slivovsky lower-bound family; source theorem is established literature, not novel. This note is negative knowledge for backend design.

## 1. The source lower bound

Bova and Slivovsky, *On Compiling Structured CNFs to OBDDs* (Theory of Computing Systems 61, 2017; arXiv:1411.5494), prove a family of positive graph CNFs with exponentially large OBDDs.

Their strong syntactic form is important:

- every clause contains exactly two positive literals;
- every variable occurs in at most three clauses;
- nevertheless every OBDD for the family has size `2^{Omega(size(F))}`.

The proof uses bounded-degree expander graphs and a subfunction-width argument.

Primary sources:

- https://arxiv.org/abs/1411.5494
- https://doi.org/10.1007/s00224-016-9715-z

## 2. Embed a positive graph CNF into ABA

Take `k` Boolean-algebra variables, giving

`N=2^k`

Venn/minterm support coordinates. For every cell `v in {0,1}^k`, let `C_v(x)` denote its Boolean minterm and let

`z_v = 1 iff C_v(x)!=0`.

Choose an injective map from the variables of a positive graph CNF F into distinct support cells. If F has more than a power-of-two convenience requires, choose `k=ceil(log2 n)` and leave unused support cells irrelevant.

For every graph edge `{u,v}`, replace the propositional clause

`z_u OR z_v`

by the single ABA disequation

`C_u(x) OR C_v(x) != 0`.

Because distinct minterm cells are disjoint,

`(C_u OR C_v)!=0`

holds exactly when

`z_u OR z_v`.

Thus the conjunction of these ABA disequations has exactly the same support Boolean function as the graph CNF on the embedded support coordinates.

## 3. Valid-support constraint does not remove the lower bound

A genuine complete ABA type cannot have the all-zero support vector.

For a nonempty positive graph CNF, however, the all-zero assignment already falsifies every positive two-literal clause. Therefore

`F -> OR_v z_v`.

Conjoining the ABA valid-support condition does not change F as a Boolean function:

`F AND Valid = F`.

Unused support coordinates can be set to zero when restricting any candidate OBDD back to the embedded graph-CNF variables. Hence padding to a power-of-two support width cannot make the original function easier than the source lower bound.

## Theorem 1 — exponential OBDD family inside ABA disequation clauses

There is an infinite family of pure-ABA formulas of the form

`AND_{e={u,v} in E} (C_u OR C_v != 0)`

such that:

1. every atomic disequation contains the join of exactly two ABA minterms;
2. every support coordinate/minterm occurs in at most three disequations;
3. every OBDD for the induced support Boolean function has size exponential in the number of participating support coordinates.

### Proof

Take the bounded-degree expander graph-CNF family of Bova–Slivovsky and apply the exact embedding above. Any OBDD for the ABA support function restricts, by fixing unused coordinates to zero, to an OBDD for the original graph CNF. The source theorem supplies the exponential lower bound.

## 4. Source-formula size caveat

One ABA minterm on k source BA variables has term syntax size `Theta(k)` if written explicitly. A bounded-degree n-variable graph CNF therefore becomes a straightforward Tau/ABA syntax tree of size `O(n log n)` when `k=ceil(log2 n)`.

The OBDD lower bound is `2^{Omega(n)}`. So in terms of the unshared source syntax this is at least

`2^{Omega(L/log L)}`

for source length L, and it is exponential in the compiled support-CNF size.

With term sharing / named minterms the representation accounting changes, but the semantic OBDD lower bound in support width n remains unchanged.

Do not state `2^{Omega(source syntax size)}` without specifying the source representation.

## 5. Consequence: ROBDD cannot be the canonical representation for the clause fragment

`ABA_CLAUSE_PROJECTION.md` represents a conjunction by:

- one forbidden-cell mask Z;
- a list of positive hit masks `G_1,...,G_q`.

The expander-derived formulas have a **linear-size mask/hypergraph representation** while every OBDD is exponential.

Therefore the backend architecture should be representation-polymorphic:

- clause mask / hypergraph representation for conjunctions;
- ROBDD only when a width/cost predictor indicates compactness;
- ZDD/CNF/SAT-style representations where appropriate;
- existing Tau path as fallback/oracle.

The point of support Booleanization is not "everything becomes a BDD." It is that all these representations operate over the same exact support semantics.

## 6. Match with the positive width theorem

`SUPPORT_OBDD_WIDTH.md` gives, for a chosen variable order sigma,

`OBDDsize <= n 2^{c(sigma)}`

where c(sigma) is the maximum number of positive obligations crossing a cut.

Expander graph CNFs are precisely the kind of incidence geometry where no ordering can keep enough independent crossing obligations small; Bova–Slivovsky formalize this through subfunction width and derive the exponential lower bound.

So the upper- and lower-bound stories are consistent:

- low cut/subterm width -> compact OBDD;
- expander-like incidence -> exponentially many residual subfunctions.

## 7. Tao/Gowers-style lesson

This is the adversarial/extremal counterpart to our earlier compact examples.

A handful of random ocLTL feasibility benchmarks staying small is not evidence for a universal compactness theorem. Expander constructions deliberately remove the separators that a good variable ordering would exploit.

The correct theorem program is therefore a **classification by structure**, not a universal BDD claim.

## 8. Next questions

1. Can Tau source syntax generate expander-like support incidence naturally, or is it mostly a worst-case adversarial family?
2. Can crossing/subfunction width be estimated from BA term syntax without expanding all minterms?
3. Which real Tau formula classes yield variable-convex, bounded-pathwidth, beta-acyclic, or otherwise compilation-friendly support CNFs?
4. Does direct clause-mask fixed-point computation avoid the OBDD lower bound for useful safety fragments?
5. Can an adaptive backend switch representations during fixed-point iteration based on measured width growth?
