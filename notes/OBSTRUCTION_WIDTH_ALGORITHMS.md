# Algorithms parameterized by one-point obstruction width

**Status:** DERIVED synthesis reduction + application of established 2024 bounded-VC-dimension transversal enumeration. The hypergraph algorithm is literature; the obstruction-width-to-response-enumeration consequence is the OrbitSynthesis result under investigation.

## 1. Setup

Let K be a **fixed finitely bounded relation-monotone class** over a finite relational signature.

Assume K is described by a fixed finite family of forbidden finite structures

`F={H_1,...,H_t}`

under the monotone substructure notion used in `RELATIONAL_ONE_POINT_OBSTRUCTION_WIDTH.md`.

For a finite old/base structure A in K, build the fresh-response conflict hypergraph

`C_K(A)`

on independently selectable response incidences.

Let

`r = omega_1(K)`

be the maximum number of selectable response incidences involving the distinguished new point in a minimal forbidden configuration.

Because K is fixed and finitely bounded, r is a constant independent of |A|.

## 2. Conflict hypergraph rank is bounded

By the obstruction-width theorem,

`rank(C_K(A)) <= r`.

That is, every minimal response conflict contains at most r selectable incidences.

## 3. Bounded rank implies bounded VC dimension

### Lemma 1

Every hypergraph of rank at most r has VC dimension at most r.

### Proof

If a set S of size r+1 were shattered, the trace family would need to contain S itself. Therefore some hyperedge E would satisfy

`E intersection S = S`,

so E would contain all r+1 vertices of S, contradicting rank <=r.

## 4. Modern transversal enumeration theorem

Mary (2024), *Enumeration of minimal transversals of hypergraphs of bounded VC-dimension*, proves that hypergraphs of bounded VC dimension admit incremental-polynomial enumeration of all minimal transversals.

Therefore fixed response obstruction width gives output-sensitive tractability of the canonical maximal-response antichain.

## 5. Main synthesis corollary

### Theorem 2 — incremental-polynomial maximal-response enumeration

Assume:

1. K is a fixed finitely bounded relation-monotone class;
2. the conflict hypergraph `C_K(A)` can be generated in time polynomial in |A| for the fixed forbidden family;
3. response codes use the positive-incidence representation from the obstruction-width theorem.

Then all inclusion-maximal legal fresh response codes over A can be enumerated in incremental polynomial time.

### Proof

- conflict rank is bounded by constant r;
- hence VC dimension is bounded by r;
- minimal transversals of the conflict hypergraph can be enumerated incremental-polynomially;
- maximal legal responses are complements of minimal transversals by `MAXIMAL_RESPONSE_ANTICHAIN.md`.

The complement operation is linear in the response ground-set size.

## 6. Why conflict generation is polynomial for fixed finite forbiddens

For each fixed forbidden structure H and each choice of distinguished new point v in H:

1. enumerate embeddings of the old part `H-v` into A;
2. read off the response incidences involving v;
3. insert the resulting incidence set as a candidate conflict;
4. remove duplicates/nonminimal candidates.

Since every forbidden H has constant size, the number of embeddings is polynomial in |A| with a theory-dependent fixed exponent.

Thus finitely boundedness supplies an explicit polynomial-size conflict description before transversal enumeration.

## 7. Henson graph corollary

For fixed Henson `K_n`-free theory:

- forbidden structure: K_n;
- one-point obstruction width: `r=n-1`;
- conflict hypergraph: all `(n-1)`-cliques of the old graph G;
- conflict rank: n-1;
- VC dimension: at most n-1.

Therefore maximal legal fresh neighborhoods can be enumerated incremental-polynomially for fixed n.

This remains true even though `HENSON_RESPONSE_WIDTH.md` exhibits bases with exponentially many maximal neighborhoods.

The result is **output-sensitive**: no algorithm can print exponentially many distinct actions in polynomial total time.

## 8. Triangle-free Henson H_3

Conflicts are edges of G.

Minimal transversals are minimal vertex covers; maximal legal responses are maximal independent sets.

Classical specialized algorithms are available here, but the general bounded-VC theorem already supplies the output-sensitive conclusion.

## 9. Fixed obstruction width versus total complete types

The total number of complete response types can still be exponential or worse in the base tuple size.

The theorem shows that for the chosen fresh-incidence fragment, canonical response actions can be generated from a polynomial-size bounded-rank conflict representation without enumerating all complete types first.

This is exactly the kind of structural separation OrbitSynthesis seeks:

`complete type count`

is not the right predictor of response synthesis complexity.

## 10. Stronger circuit route

Enumeration is not always desirable.

If the maximal-response antichain is exponential but the original conflict hypergraph has low incidence treewidth, `RESPONSE_KNOWLEDGE_COMPILATION.md` can keep the response family symbolic instead of enumerating its transversals.

Thus two algorithmic modes coexist:

- **incremental enumeration** from bounded VC dimension / fixed obstruction width;
- **factorized circuit compilation** from low structural width.

## 11. Proposed theory-plugin API consequence

A monotone-relational theory plugin can expose:

- forbidden one-point templates;
- obstruction width r;
- generated conflict hypergraph;
- optional tree decomposition/symmetry metadata;
- incremental maximal-response iterator;
- symbolic response-CNF/circuit.

The synthesis engine then chooses whether to:

- use one greatest response;
- enumerate canonical maximal responses lazily;
- compile them symbolically;
- or fall back to complete types.

## 12. Next questions

1. Obtain explicit polynomial-delay bounds from the bounded-VC algorithm specialized to fixed rank r.
2. Compare with older fixed-rank transversal algorithms in practice/theory.
3. Extend from finite forbidden families to effectively enumerable bounded-obstruction theories.
4. Generalize to signed/induced constraints where legality is not downward closed.
5. Combine incremental response enumeration with on-the-fly parity/Buchi game solving so only actions actually needed by the temporal solver are generated.
