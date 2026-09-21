# Arbitrarily large patchability number with trivial automorphism group

**Status:** DERIVED explicit family. The general notions of automorphism-group base/fixing number and monounary homogeneity are classical. The purpose of this note is to prove that parameter patchability measures genuinely partial symmetry rather than ordinary global symmetry. Tau-independent. Not Lean-checked.

## 1. Goal

`QUASIPRIMAL_PARAMETER_PATCHABILITY.md` defines the provisional invariant

`kappa_patch(Q)`

as the minimum number of named carrier elements needed to make a finite quasi-primal algebra demi-semi-primal.

A natural suspicion is that this is merely another form of automorphism-group base size / graph fixing number.

It is not.

We construct finite quasi-primal algebras with:

`Aut(Q)=1`

but arbitrarily large `kappa_patch(Q)`.

## 2. Rigid chain components

For `m>=1`, let the carrier be the disjoint union

`K_1 + ... + K_m`

where `K_i` is a rooted unary chain of length i:

`x_(i,i-1) -> ... -> x_(i,1) -> r_i -> r_i`.

So `|K_i|=i` and the total carrier size is

`m(m+1)/2`.

Let u be the unary map defined by those arrows.

Add the ternary discriminator d as a basic operation.

Call the resulting finite algebra

`R_m=(Q_m; d,u)`.

Because d is a basic discriminator, R_m is quasi-primal.

## 3. The global automorphism group is trivial

### Lemma 1

`Aut(R_m)=1`.

### Proof

Any automorphism preserves u-components.

The components have pairwise distinct cardinalities 1,...,m, so no automorphism can permute distinct components.

Within one rooted chain K_i:

- r_i is the unique fixed point;
- x_(i,1) is the unique nonfixed point mapping to r_i;
- x_(i,2) is the unique point mapping to x_(i,1);
- and so on.

Thus every element of K_i is individually fixed.

The discriminator is preserved by every bijection, so it introduces no additional automorphisms.

Hence the identity is the only global automorphism. QED.

Therefore the ordinary automorphism-group base size / fixing number is 0.

## 4. Lower bound on parameter patchability

### Lemma 2

Every good parameter set C meets at least m-1 distinct unary components.

### Proof

Suppose two components K_i,K_j are completely untouched by C.

Let `cl(C)` be the unary closure of C.

Then

`S = cl(C) union {r_i,r_j}`

is a C-containing subalgebra.

Inside S both r_i and r_j are simply isolated fixed points of the restricted unary operation. Define a C-fixing internal automorphism phi of S by swapping r_i and r_j and fixing cl(C).

If phi extended globally, it would be a nonidentity automorphism of R_m.

But Lemma 1 says the global automorphism group is trivial.

Therefore phi does not extend.

So C cannot be good while leaving two components untouched. QED.

Since one named element lies in only one component,

`|C|>=m-1`.

## 5. Upper bound

Name the roots of any m-1 components:

`C={r_1,...,r_(m-1)}`.

### Lemma 3

C is good.

### Proof

Take a C-fixing internal isomorphism

`phi:S->T`

between C-containing unary subalgebras.

All named roots are fixed.

If the remaining root r_m occurs in S, its image must be a fixed point of u. The named roots are already occupied by their own fixed images, so injectivity forces

`phi(r_m)=r_m`.

Thus every component root occurring in S is fixed.

A u-invariant subset of one rooted chain containing its root is necessarily a prefix

`{r_i,x_(i,1),...,x_(i,h)}`

for some height h.

Because phi fixes r_i and commutes with u, it must send the unique height-1 point to itself, then the unique height-2 point to itself, and so on.

Hence phi is the identity on every component portion in its domain.

Therefore phi itself is the restriction of the global identity automorphism, which fixes C.

So every pointed internal isomorphism extends. QED.

## 6. Exact separation theorem

### Theorem 4

For every m>=1,

`Aut(R_m)=1`

and

`kappa_patch(R_m)=m-1`.

### Proof

Lemma 1 gives trivial automorphism group. Lemma 2 gives the lower bound `kappa_patch>=m-1`; Lemma 3 gives the matching upper bound. QED.

## 7. Consequence

For every r>=0 there is a finite quasi-primal algebra Q with

- fixing/base number 0;
- `kappa_patch(Q)=r`.

Take `Q=R_(r+1)`.

So no function of ordinary global-symmetry base size can upper-bound parameter patchability.

The inner reason is simple:

> `kappa_patch` measures **nonextendable local symmetries**, including symmetries that do not occur globally at all.

A globally rigid algebra can contain many small subalgebras that look locally identical.

## 8. Smallest exact examples

### r=1

Components of sizes 1 and 2:

`u=(0,1,1)`

on three points.

The algebra is globally rigid but the two roots can be swapped in the two-root subalgebra, so `kappa_patch=1`.

### r=2

Components of sizes 1,2,3:

`u=(0,1,1,3,3,4)`

on six points.

Exact enumeration gives:

- one global automorphism, the identity;
- no good parameter sets of size 0 or 1;
- good parameter pairs exist, e.g. `{0,1}`.

Thus `kappa_patch=2`.

This provides a second six-element pi=2 witness, stronger conceptually than the star witness because global symmetry is already absent.

## 9. Comparison with generating rank

The same family separates `kappa_patch` from algebraic generating rank.

The discriminator is conservative and u only moves points toward the chain root. A non-root chain element cannot be generated from lower points.

To generate the whole disjoint union one needs the top element of every nontrivial chain and the isolated root of K_1, hence at least m generators (indeed exactly m).

So

`kappa_patch(R_m)=m-1`

while the algebraic generating rank is m.

The two are close on this family but conceptually different: one anchors partial symmetries; the other must generate every element.

The star family in `QUASIPRIMAL_PARAMETER_PATCHABILITY.md` gives much larger gaps in the other quantitative direction.

## 10. Relation to monounary homogeneity literature

Recent and classical monounary literature classifies ultrahomogeneity, partial homogeneity, and related extension properties of the **unpointed** unary structure.

The rigid-chain family is intentionally outside ultrahomogeneity: singleton generated subalgebras at distinct roots are isomorphic but cannot be globally interchanged.

Demi-semi-primality ignores those singleton subalgebras, but the same latent root symmetry reappears on a two-root nontrivial subalgebra. Naming constants removes these latent swaps component by component.

So the family is a clean bridge between static unary homogeneity and the pointed controller-language resource studied here.

## 11. Next question

Determine the minimum carrier size

`n(r)=min{|Q| : Q finite quasi-primal and kappa_patch(Q)=r}`.

The rigid-chain family gives

`n(r) <= (r+1)(r+2)/2`.

The complete discriminator+unary campaign proves

- `n(0)=1` trivially;
- `n(1)<=3` and no two-point quasi-primal algebra needs a parameter;
- `n(2)=6` within the complete one-unary discriminator laboratory because all n<=5 maps have kappa<=1 and explicit six-point witnesses have kappa=2.

For r>=3 the exact minimum remains open.
