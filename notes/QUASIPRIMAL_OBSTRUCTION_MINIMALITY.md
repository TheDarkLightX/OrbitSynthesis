# Minimality of the first quasi-primal no-greatest-region obstruction

**Status:** DERIVED theorem for carrier-size minimality within finite quasi-primal algebras, plus a DERIVED `k=1` union-closure theorem for the concrete three-element Quackenbush algebra. The `k=1,m=1` single-equation calibration is FINITE-VERIFIED by `experiments/quasiprimal_k1_exhaustive.py`. Not Lean-checked.

This note sharpens `QUASIPRIMAL_NO_GREATEST_REGION.md` by asking whether its three-element carrier and two state coordinates are artifacts of the construction.

They are not, in the precise senses below.

## 1. Carrier size two cannot exhibit the quasi-primal/demi boundary

Recall the standard Quackenbush definition used in Burris--Sankappanavar:

> a finite algebra is demi-semi-primal when it is quasi-primal and every isomorphism between nontrivial subalgebras extends to an automorphism of the whole algebra.

Here `nontrivial` excludes one-element algebras.

### Lemma 1

Every two-element quasi-primal algebra is demi-semi-primal.

### Proof

Let A have two elements.

The only nontrivial subalgebra of A is A itself. Therefore every isomorphism between nontrivial subalgebras is simply an isomorphism

`A -> A`,

which by definition is an automorphism of A and hence already extends globally.

Thus the demi-semi-primal extension condition is automatic. QED.

### Consequence

By `DEMI_SEMIPRIMAL_TERM_SAFETY.md`, every equation-defined finite safety game over a two-element quasi-primal controller algebra admits the exact orbit/stabilizer greatest-fixed-point construction.

Hence the no-greatest-region pathology proved in `QUASIPRIMAL_NO_GREATEST_REGION.md` requires at least three carrier elements **within the finite quasi-primal hierarchy**.

The existing three-element example therefore has minimum possible carrier size for that hierarchy.

This is a structural lower bound; no finite search is needed.

## 2. The concrete three-element algebra

Use

`Q=({0,1,2}; d,u)`

with ternary discriminator d and

`u(0)=1, u(1)=0, u(2)=1`.

The only proper nonempty nontrivial subalgebra is

`B={0,1}`,

and its only nonidentity internal automorphism is

`phi(0)=1, phi(1)=0`.

The full algebra has trivial automorphism group.

Thus, by the quasi-primal term-function characterization, a total operation

`f:Q^n -> Q`

is a Q-term exactly when it:

1. maps `B^n` into B; and
2. satisfies `f(phi z)=phi f(z)` on `B^n`.

Outside `B^n`, there is no nontrivial internal-isomorphism coupling.

## 3. One state coordinate always patches

Let the state be a single element

`s in Q`,

let the environment input have arbitrary finite arity m, and let the next state/controller output again be one element of Q.

Let

`R subseteq Q x Q^m x Q`

be any safety relation invariant under the internal isomorphisms of Q. Every relation defined by equations between Q-terms has this invariance.

Call a domain `W subseteq Q` **term-winning** if there is one positional Q-term controller

`sigma:Q^(1+m) -> Q`

that keeps W safe and forward invariant for all inputs.

### Theorem 2 -- k=1 union closure

For this Q, if W and V are term-winning, then

`W union V`

is term-winning.

Therefore the family of term-winning domains is union-closed and has a greatest element.

### Proof

Put `U=W union V`.

We construct one complete controller table for U and then use the quasi-primal term characterization.

Split observations

`z=(s,input)`

into two classes.

### Case A -- z is not in `B^(1+m)`

No nontrivial internal isomorphism constrains this table entry.

If `s in U`, choose the output from any winning controller among W or V whose domain contains s. That output is safe and remains in its source domain, hence in U.

If `s notin U`, postpone the entry to the arbitrary total-table completion.

### Case B -- z lies in `B^(1+m)`

Now s is 0 or 1 and the table must respect the phi-pair

`z <-> phi(z)`.

There are only three possibilities for `U intersect B`.

#### B1. U contains exactly one of 0,1

Suppose it is a.

Any winning controller for a domain whose intersection with B is `{a}` must output a on every all-B observation having state a: subalgebra preservation forces the output into B, while forward invariance forces it into the singleton `{a}`.

Use this value at the required side and define the paired table entry to be `phi(a)`.

The paired state is outside U, so this completion creates no winning obligation there.

#### B2. One source domain already contains both 0 and 1

Use that source controller on the complete phi-paired block. It is already a Q-term, so its values are safe, U-valued, B-preserving, and phi-equivariant.

#### B3. U contains both 0 and 1 but neither W nor V does

After exchanging W and V if needed,

`W intersect B={0}`

and

`V intersect B={1}`.

As in B1, every all-B observation with state 0 is forced by the W controller to output 0, and every all-B observation with state 1 is forced by the V controller to output 1.

Internal-isomorphism invariance of R transports

`(0,input,0)`

to

`(1,phi(input),1)`.

Hence the two singleton choices are automatically safe as a phi-pair.

Define the new controller by those paired values.

### Total completion

On observations whose states lie outside U, complete the remaining table arbitrarily subject to:

- B-valued output on `B^(1+m)`;
- phi-equivariance on each B-observation pair.

Such a completion is immediate: choose one B-value on each unassigned pair representative and propagate it by phi; outside `B^(1+m)` choose arbitrary Q-values.

The resulting total function preserves B and phi, hence is a Q-term. By construction it is safe and U-valued at every observation whose state lies in U.

Thus U is term-winning. QED.

## 4. Greatest region follows

There are only finitely many state domains `W subseteq Q`.

By Theorem 2 the union of any two term-winning domains is term-winning. Iterating finite unions, the union of all term-winning domains is itself term-winning.

Therefore a greatest term-winning domain exists for every internal-isomorphism-invariant `k=1` safety game over this Q.

## 5. Why k=2 changes the geometry

With one state coordinate, the nontrivial subalgebra B supplies only two local next-state labels:

`0 <-> 1`.

If two separately winning domains require opposite sides of this phi-pair, their union contains both labels, so the paired controller choices patch.

With two state coordinates, B^2 has four labels:

`00 <-> 11`

and

`01 <-> 10`.

The no-greatest witness exploits the second orbit as a **third logical role**:

- `00` and `11` are the two special required states;
- `01` is included as the locally required successor;
- its forced image `10` is deliberately excluded and made dead.

That separation is impossible in B itself but possible in B^2.

This is the inner reason state arity two is needed for the current minimal carrier.

## 6. Minimality theorem for the existing witness

Combining Lemma 1, Theorem 2, and `QUASIPRIMAL_NO_GREATEST_REGION.md`:

### Theorem 3

Within the finite quasi-primal term-controller framework:

1. carrier size 2 cannot exhibit failure of a greatest region through the demi/non-demi mechanism;
2. the concrete three-element Quackenbush algebra cannot exhibit such failure with one state coordinate, for any finite input arity and any internal-isomorphism-invariant safety relation;
3. the existing three-element, two-state-coordinate, single-equation game does exhibit failure.

Thus the existing counterexample is simultaneously carrier-minimal and, for its algebra, state-arity-minimal.

Do **not** read item 2 as saying that every three-element quasi-primal algebra is k=1 patchable. It is a theorem about the particular Q above.

## 7. Exact k=1,m=1 calibration

`experiments/quasiprimal_k1_exhaustive.py` independently checks the smallest input-bearing case.

For controller observations `(state,input)`:

- exactly 972 total term-controller tables exist;
- for a single equation `p=g`, equality status on the 27 transition triples has exactly 23 independent bits: four phi-paired binary-transition bits plus 19 unconstrained nonbinary bits;
- the checker computes inclusion-minimal required-safe-bit masks for each of the seven nonempty state domains;
- it then tests every pair of incomparable candidate domains at the hardest safety mask: the union of their two minimal requirement masks.

Why this is exhaustive without iterating all `2^23` masks:

if a pair W,V can win under some safety mask S while no common winning superset exists, let `r_W subseteq S` and `r_V subseteq S` be requirement masks of witnessing controllers. The smaller mask

`S0=r_W union r_V`

still makes W and V win, and deleting safe transitions cannot create a new common winning superset. Therefore a counterexample must already occur at one of these minimal pair masks.

The checker examines 819 such combinations and finds none.

This computation is calibration only; Theorem 2 supplies the arbitrary-input proof.

## 8. Literature boundary

Classical ingredients:

- R. W. Quackenbush, *Demi-Semi-Primal Algebras and Mal'cev-Type Conditions*, Math. Z. 122 (1971), 166--176.
- S. Burris and H. P. Sankappanavar, *A Course in Universal Algebra*, Exercise IV.10.5: demi-semi-primality is stated using extension of isomorphisms between nontrivial subalgebras.
- A. F. Pixley's quasi-primal interpolation theorem / the standard internal-isomorphism characterization of term functions.

The controller-domain minimality theorem above is a derived reactive consequence and remains under prior-art review.

## 9. Next target

The strongest remaining structural conjecture is still:

> for finite quasi-primal Q, universal greatest-region behavior for equation-defined term safety is equivalent to Q being demi-semi-primal.

The minimality result suggests attacking necessity by giving a nonextendable internal isomorphism enough **tuple arity** to create distinct roles analogous to `00,11,01,10`, while using a globally generating input tuple to isolate the dead-state gadget from proper partial symmetries.
