# Dominant fresh-response classification for edge-monotone homogeneous graphs

**Status:** DERIVED corollary combining the classical Lachlan-Woodrow classification of countable ultrahomogeneous graphs with `MONOTONE_GRAPH_EXTENSION_CLASSIFICATION.md`. The homogeneous-graph classification is not OrbitSynthesis work.

## 1. Classical classification input

Lachlan and Woodrow classified the countably infinite ultrahomogeneous undirected graphs. Modern summaries describe the list, up to complementation, as:

- the countable random/Rado graph;
- infinite disjoint unions of finite complete graphs K_n;
- the homogeneous K_n-free (Henson) graphs;
- finite unions of countably infinite complete graphs;
- complementary families.

## 2. Add the edge-monotone age hypothesis

Say the age is **edge-monotone** if every finite graph in the age remains in the age after deleting arbitrary edges while keeping its vertices.

### Rado graph

Its age is all finite graphs, hence edge-monotone.

### Henson K_n-free graph

Its age is all finite K_n-free graphs. Deleting edges cannot create K_n, so the age is edge-monotone.

### Edgeless graph

The age consists of finite edgeless graphs and is trivially edge-monotone.

### Disjoint-union-of-cliques families

For any nontrivial clique size, deleting one edge inside a clique produces a connected component that is no longer a clique, so the resulting graph leaves the age.

### Finite unions of infinite cliques

The same edge-deletion obstruction applies to finite subgraphs containing a clique of size at least 3 (and analogous non-cluster shapes for smaller cases).

### Complementary families

The corresponding ages are not generally closed under deleting edges; edge deletion can introduce forbidden nonedge patterns. The complete-graph extreme is also not edge-monotone.

Therefore the edge-monotone ultrahomogeneous cases reduce to:

1. Rado/random graph;
2. edgeless graph;
3. Henson K_n-free graphs, n>=3.

## 3. Apply the monotone graph extension theorem

`MONOTONE_GRAPH_EXTENSION_CLASSIFICATION.md` states that every fresh neighborhood family is union-closed / has a unique greatest legal response iff every minimal forbidden graph has maximum degree at most 1.

### Rado

No forbidden finite graph. Every fresh neighborhood is legal. Greatest response is adjacency to every old vertex.

### Edgeless

Minimal forbidden graph is K_2, maximum degree 1. Greatest legal response is the empty neighborhood.

### Henson K_n-free

Minimal forbidden graph is K_n, maximum degree n-1>=2. Greatest response fails over an old K_(n-1).

## 4. Corollary

### Theorem

Let M be a countably infinite ultrahomogeneous undirected graph whose age is edge-monotone.

For the fresh-vertex adjacency-inclusion positive response fragment, the following are equivalent:

1. every finite base type has a greatest legal fresh response neighborhood;
2. positive system existential response collapses to that dominant neighborhood over every finite base;
3. M is isomorphic to either the Rado graph or the countably infinite edgeless graph.

Every Henson K_n-free graph is the obstruction family.

## 5. Why this matters

This is a genuine **structure classification**, not only an algorithm for one theory.

Inside a standard model-theoretic universe (countable homogeneous graphs with monotone ages), the dominant-response synthesis property has an exact boundary:

`Rado / edgeless  |  Henson`.

The boundary is controlled by one-point forbidden incidence interaction rather than by omega-categoricity or free amalgamation alone.

## 6. Important scope

The theorem is for:

- undirected countable ultrahomogeneous graphs;
- edge-monotone ages;
- fresh response vertices;
- upward adjacency targets.

It does not classify:

- arbitrary reducts;
- colored/directed graphs;
- induced-forbidden classes that are not edge-monotone;
- equality-to-old-vertex response branches;
- non-upward objectives.

These extensions should be handled separately.

## 7. Next classification targets

1. Countable homogeneous bipartite/multipartite graphs: colored sides may produce coordinatewise Boolean-cube response fibers.
2. Homogeneous directed graphs: define signed incidence orders and obstruction width.
3. Random k-uniform hypergraphs versus Henson-style forbidden hypergraphs.
4. Reducts of Rado/Henson structures: determine which reducts preserve a useful response semilattice.
5. Compare dominant-response classification with polymorphism clone data for the same structures.
