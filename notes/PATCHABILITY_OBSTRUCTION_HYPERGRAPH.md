# Parameter patchability is exactly a hitting-set problem over nonextendable partial symmetries

**Status:** DERIVED exact finite-algebra identity. Hitting set/transversal theory is classical. The new value here is the structural factorization of pointed internal-isomorphism extension into one unpointed obstruction enumeration plus a hypergraph transversal problem, and its controller-language interpretation for quasi-primal algebras. Tau-independent. Not Lean-checked.

## 1. Setup

Let A be any finite algebra; quasi-primality is **not** needed for the structural result.

Consider internal isomorphisms

`phi:S -> T`

between nontrivial subalgebras `|S|,|T|>1`.

Call phi **nonextendable** if no global automorphism of A restricts to phi on S.

Let

`NExt(A)`

be the finite set of all such nonextendable internal isomorphisms.

For phi define its pointwise fixed set

`Fix(phi) = {x in S intersect T : phi(x)=x}`.

Elements outside the domain/codomain are deliberately not counted as fixed.

## 2. When does naming C kill one obstruction?

Let

`C subseteq A`

be a set of named constants.

In the pointed expansion `A_C`, subalgebras must contain C and internal isomorphisms must fix C pointwise.

### Lemma 1 -- survival criterion

An unpointed nonextendable internal isomorphism phi survives as an internal isomorphism of `A_C` iff

`C subseteq Fix(phi)`.

### Proof

For phi to be an internal isomorphism of `A_C`:

1. both its domain S and codomain T must contain every named constant c;
2. phi(c)=c for every c in C.

Those two conditions say exactly that every c belongs to `S intersect T` and is fixed by phi, i.e.

`C subseteq Fix(phi)`.

QED.

Equivalently, C **kills** phi iff

`C not subseteq Fix(phi)`.

## 3. No new nonextendability can appear after naming constants

The pointed problem does not create a second kind of obstruction.

### Lemma 2

Let phi be an internal isomorphism of `A_C`. If phi extends to some unpointed global automorphism g of A, then g automatically fixes C and is therefore an automorphism of `A_C`.

### Proof

Since phi is pointed, `phi(c)=c` for every c in C. Since C is contained in the domain of phi and g extends phi,

`g(c)=phi(c)=c`.

Thus g fixes C pointwise. QED.

Therefore:

> a pointed internal isomorphism fails to extend iff it was already an unpointed nonextendable internal isomorphism that survived the naming of C.

This is the key simplification.

## 4. Obstruction hypergraph

For every nonextendable phi define the hyperedge

`E_phi = A \ Fix(phi)`.

Because an identity map on the whole carrier always extends, every E_phi is nonempty.

Let

`H_patch(A) = {E_phi : phi in NExt(A)}`.

Duplicate edges may be removed.

Further, if

`E_1 subseteq E_2`,

then any set hitting E_1 automatically hits E_2. Hence only inclusion-minimal hyperedges matter for transversals.

Call the resulting antichain

`MinH_patch(A)`.

## 5. Exact hitting-set theorem

### Theorem 3 -- patchability = transversal

For every finite algebra A and parameter set C:

`A_C has the nontrivial internal-isomorphism extension property`

iff

`C is a transversal/hitting set of H_patch(A)`.

Equivalently:

`for every phi in NExt(A), C intersection E_phi != empty`.

### Proof

By Lemma 1, phi survives precisely when

`C subseteq Fix(phi)`.

Negating:

phi is killed precisely when there exists

`c in C` with `c notin Fix(phi)`,

which is exactly

`C intersection (A\Fix(phi)) != empty`.

By Lemma 2 the pointed expansion has the extension property iff every unpointed nonextendable phi is killed.

Thus C is good iff it hits every E_phi. QED.

## 6. Exact parameter-number formula

For the provisional invariant from `QUASIPRIMAL_PARAMETER_PATCHABILITY.md`:

### Corollary 4

`kappa_patch(A) = tau(H_patch(A))`,

where tau is the hypergraph transversal number.

The same minimum is obtained from the inclusion-minimal obstruction antichain:

`kappa_patch(A) = tau(MinH_patch(A))`.

For quasi-primal A, this number is exactly the minimum controller parameter budget restoring universal greatest-region term safety.

## 7. All minimal good parameter sets

The result is stronger than a minimum cardinality formula.

### Corollary 5

The inclusion-minimal parameter sets C for which `A_C` has the extension property are exactly the **minimal transversals** of `H_patch(A)`.

Thus classic hypergraph-duality machinery can enumerate all irredundant parameter choices.

## 8. Why this explains monotonicity

Good parameter sets are upward closed because hitting sets are upward closed.

This recovers Lemma 2 of `QUASIPRIMAL_PARAMETER_PATCHABILITY.md` without a separate extension argument.

## 9. Why naming an element outside an obstruction works

The hyperedge definition may at first look unusual because

`E_phi=A\Fix(phi)`

includes elements outside S or T.

That is intentional.

Naming an element c outside S prevents S from being a subalgebra of the pointed expansion, so phi ceases to be an eligible pointed internal isomorphism.

Thus an anchor may kill a partial symmetry in either of two ways:

1. **domain exclusion:** c is not available on both sides;
2. **motion obstruction:** c lies in both sides but phi(c)!=c.

Both are unified by `c notin Fix(phi)`.

## 10. Six-element star witness compression

For

`u=(0,0,0,3,3,5)`

with discriminator, exact enumeration finds:

- 77 raw nonextendable internal isomorphisms;
- 8 distinct obstruction hyperedges after deduplication;
- only 3 inclusion-minimal hyperedges:

`{3,4,5}`,

`{0,1,2,5}`,

`{0,1,2,3,4}`.

No singleton hits all three, while several pairs do.

Hence

`kappa_patch=2`.

The three-edge kernel is a much smaller certificate than rerunning all pointed subalgebra/isomorphism searches.

## 11. Six-element rigid-chain witness compression

For

`u=(0,1,1,3,3,4)`

with discriminator, exact enumeration finds:

- 45 raw nonextendable internal isomorphisms;
- 7 distinct hyperedges;
- 3 inclusion-minimal hyperedges:

`{0,1,2}`,

`{0,3,4,5}`,

`{1,2,3,4,5}`.

Again the transversal number is 2.

This algebra has trivial global automorphism group, so the hypergraph consists entirely of **latent local symmetries with no global counterpart**.

## 12. Solver architecture

The exact small-carrier reference pipeline should be:

1. enumerate all nontrivial internal isomorphisms once;
2. enumerate global automorphisms once;
3. retain only nonextendable internal isomorphisms;
4. compile each to `E_phi=A\Fix(phi)`;
5. deduplicate and remove nonminimal hyperedges;
6. solve minimum hitting set / enumerate minimal transversals.

This dominates the earlier brute pipeline:

`for each C -> rebuild pointed subalgebras -> rebuild pointed isomorphisms -> retest extension`.

The expensive algebraic work is now performed once.

## 13. Evidence certificate

A compact certificate for `kappa_patch(A)=r` can contain:

### Upper certificate

A concrete parameter set C of size r hitting every minimal obstruction edge.

### Lower certificate

Either:

- the full minimal obstruction hypergraph plus a checked proof that no `(r-1)`-set hits it; or
- a smaller dual packing/lower-bound certificate when available.

For tiny carriers exhaustive `(r-1)`-subset rejection is sufficient.

This fits the Research Kernel/Morph evidence-first style much better than a bare scalar answer.

## 14. Complexity consequence

Once `H_patch(A)` is explicitly available, computing `kappa_patch` is an ordinary Hitting Set instance.

This does **not yet** prove that computing `kappa_patch` from operation tables is NP-hard: the obstruction hypergraph may have special algebraic structure, and enumerating it may itself be expensive.

So separate two complexity questions:

1. **obstruction generation:** compute/compress `H_patch(A)` from the finite algebra;
2. **anchor optimization:** solve transversal on the resulting hypergraph.

A future NP-hardness proof must reduce to the operation-table input, not merely observe that the second stage is generic hitting set.

## 15. Relation to the monounary one-generator speedup

`POINTED_MONOUNARY_ONE_GENERATOR.md` reduces direct pointed verification for nonempty C to one-extra-generated subalgebras.

The obstruction-hypergraph theorem is more general and conceptually cleaner:

- it applies to any finite algebra;
- it eliminates repeated pointed verification entirely once unpointed obstructions are known.

The monounary theorem remains useful for generating or validating the obstruction hypergraph more efficiently in that special family.

## 16. Next questions

1. Can `MinH_patch(A)` be computed without enumerating all internal isomorphisms?
2. Which hypergraphs can occur as patchability obstruction hypergraphs of finite quasi-primal algebras?
3. Does that realization problem yield NP-hardness of computing `kappa_patch` from algebra tables?
4. Can blocker duality produce compact lower certificates for large parameter budgets?
5. Can obstruction edges be learned incrementally from failed controller-patching attempts instead of pre-enumerated?
