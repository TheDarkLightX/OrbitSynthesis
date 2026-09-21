# Exact fresh-extension classification for monotone graph classes

**Status:** DERIVED theorem. This is a finite graph-combinatorial classification motivated by the extension-semilattice synthesis criterion. It should be checked against existing hereditary/monotone graph-class literature before a novelty claim.

This note sharpens the Rado-versus-Henson comparison.

## 1. Fresh one-point extension family

Let K be a class of finite simple graphs closed under taking (not necessarily induced) subgraphs.

For G in K and a new vertex y, identify a fresh extension by the neighborhood

`N subseteq V(G)`

assigned to y.

Define

`E_K(G) = { N subseteq V(G) : G +_N y belongs to K }`,

where `G +_N y` adds a fresh vertex adjacent exactly to N.

Because K is subgraph-closed, `E_K(G)` is a downward-closed family:

`N in E_K(G), M subseteq N  =>  M in E_K(G)`.

Deleting y-incident edges cannot create a forbidden subgraph.

## 2. Downward + union-closed means a Boolean cube

### Lemma 1

Let `E subseteq P(V)` be finite and downward closed. Then E is union-closed iff

`E = P(U)`

for

`U = union E`.

### Proof

If E is union-closed, the finite union of every member belongs to E, so `U in E`. Downward closure gives `P(U) subseteq E`. By definition every member of E lies in U, so `E subseteq P(U)`.

The converse is immediate.

### Synthesis reading

A monotone graph extension fiber has a greatest fresh response exactly when all individually admissible neighbor choices are jointly compatible. Then the greatest neighborhood is simply U.

There are no genuinely intermediate downward+join-closed geometries: they collapse to a Boolean cube.

## 3. Minimal forbidden subgraphs

Let M(K) be the set of graphs H not in K that are minimal under the subgraph relation: every proper subgraph of H lies in K.

Every graph outside K contains some H in M(K) as a subgraph.

## 4. Classification theorem

### Theorem 2

The following are equivalent:

1. for every G in K, the fresh extension family `E_K(G)` is union-closed;
2. for every G in K, `E_K(G)=P(U_G)` for some `U_G subseteq V(G)`;
3. every minimal forbidden graph `H in M(K)` has maximum degree at most 1.

### Proof: (1) iff (2)

Lemma 1.

### Proof: (1) implies (3)

Assume some minimal forbidden H has a vertex v with degree at least 2.

Let

`G = H - v`.

By minimality, G belongs to K.

Let the neighbors of v in H be

`N_H(v)={u_1,...,u_r}`, with r>=2.

For each j, the extension of G by a fresh y adjacent only to u_j is a proper subgraph of H, so it belongs to K. Hence

`{u_j} in E_K(G)`

for every j.

If `E_K(G)` were union-closed, then

`N_H(v) = union_j {u_j}`

would belong to `E_K(G)`.

But `G +_{N_H(v)} y` is isomorphic to H, which is forbidden. Contradiction.

Therefore every minimal forbidden H must have maximum degree <=1.

### Proof: (3) implies (1)

Assume every minimal forbidden H has maximum degree <=1.

Take G in K and legal fresh neighborhoods N_1,N_2 in E_K(G). Suppose their union N=N_1 union N_2 were illegal.

Then `G +_N y` contains some minimal forbidden H as a subgraph. Since G itself belongs to K, every embedding of H must use the new vertex y.

Because `Delta(H)<=1`, y has at most one incident edge inside that embedded copy of H.

If y has degree 0 in the copy, the same forbidden H would already occur in G, impossible.

So the copy uses exactly one edge `y-u`, where u belongs to N.

Then u belongs to N_1 or N_2. The same embedded copy of H is already present in the corresponding legal extension `G +_{N_i} y`, contradiction.

Hence N_1 union N_2 is legal. Finite induction gives union closure.

## 5. Examples

### All finite graphs / Rado age

There are no forbidden graphs. Every neighborhood is legal:

`E_K(G)=P(V(G))`.

The greatest response is adjacency to every old vertex.

### K_n-free graphs / Henson age

The minimal forbidden graph is K_n, whose maximum degree is n-1>=2.

Therefore union closure fails.

The obstruction constructed in Theorem 2 is exactly the familiar one: over an old K_(n-1), each single adjacency is legal but adjacency to the whole clique is not.

### Edgeless graphs

The minimal forbidden graph is K_2, with maximum degree 1.

For every old G, the only legal fresh neighborhood is empty:

`E_K(G)={empty}=P(empty)`.

The greatest response exists trivially.

### Matching-number bounded classes

If K forbids a matching of m edges as a subgraph, the minimal forbidden graph mK_2 has maximum degree 1. Fresh extension fibers are therefore Boolean cubes, although which old vertices are individually admissible depends on the existing matching structure.

This is a less trivial extremal-response class than the random graph.

## 6. Dominant-response synthesis corollary

Suppose K satisfies Theorem 2 and the corresponding countable homogeneous/universal structure exists for the age under consideration.

For a fresh response over G, let

`U_G = union E_K(G)`.

Then U_G is the greatest legal neighborhood.

For every target predicate upward under neighborhood inclusion,

`exists legal N. Good(N)`

iff

`Good(U_G)`.

Thus the system existential response collapses to one canonical neighborhood exactly as in the ABA/Rado positive fragment.

The temporal positive-mu-calculus collapse then follows once the environment side and effective witness realization are supplied.

## 7. Exact failure certificate

When the classification fails, a minimal forbidden graph H with a vertex v of degree >=2 gives a canonical finite synthesis counterexample:

- base graph `G=H-v`;
- individually legal singleton response neighborhoods `{u}` for neighbors u of v;
- illegal union `N_H(v)`.

This is a small, human-readable certificate that no neighborhood-union dominant response can exist for the full positive adjacency fragment.

For Henson H_3, H=K_3 and G is one edge.

## 8. General relational analogue

The graph proof suggests a higher-arity extension-width invariant.

In a relational class, a one-point forbidden configuration H with distinguished new vertex v may require several positive atomic incidences involving v. If every minimal forbidden configuration can involve v in at most one independently selectable response incidence, union-style response choices cannot interact. If some minimal forbidden configuration requires two or more such incidences, it creates a potential Henson-style incompatibility.

A precise relational theorem must define what counts as independent selectable incidences when relation arity exceeds 2 and when negative relations matter.

Do not promote this analogue until formalized.

## 9. Relation to free amalgamation

Free amalgamation alone is **not** enough for the greatest-neighborhood property.

The age of the Henson K_n-free graph is a standard free-amalgamation class, yet Theorem 2 shows fresh neighborhood union closure fails.

Thus the synthesis criterion detects a different local property: absence of multi-incidence one-point forbidden configurations.

## 10. Next questions

1. Classify finitely bounded monotone relational Fraisse classes by the arity/degree of minimal one-point obstructions.
2. Determine which of the graph classes satisfying Delta(H)<=1 for minimal forbiddens have a countable homogeneous Fraisse limit.
3. Add unary colors / multipartite random graphs and derive colored Boolean-cube extension fibers.
4. Compare the criterion with semilattice polymorphisms of the corresponding relational reducts.
5. Determine whether bounded one-point obstruction degree k yields a useful `k`-choice synthesis algorithm when the greatest-response case k=1 fails.
