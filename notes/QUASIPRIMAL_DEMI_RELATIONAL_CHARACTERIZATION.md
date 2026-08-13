# Demi-semi-primality exactly characterizes greatest-region safety for groupoid-invariant relations

**Status:** DERIVED general theorem for finite quasi-primal algebras and internal-isomorphism-invariant finite safety relations. This is stronger than the earlier 27-algebra calibration but weaker than the still-open equation-defined characterization. The universal-algebraic term-function and demi extension theorems are classical; the reactive characterization remains under prior-art review. Not Lean-checked.

## 1. Why split the conjecture

`THREE_ELEMENT_DEMI_BOUNDARY.md` suggested:

> among finite quasi-primal algebras, the demi-semi-primal extension property may be exactly the boundary for universal existence of a greatest original-signature term-winning region.

The previous negative witnesses were equation-defined. For a general quasi-primal algebra, forcing the negative gadget into one equation introduces an extra definability problem unrelated to the controller patching mechanism.

So separate two levels.

### Relation-level question

Allow any finite safety relation that respects every internal isomorphism of the controller algebra.

### Equation-level question

Require the safety relation itself to be given by one or more equations of original-signature terms.

The relation-level problem now has an exact answer.

## 2. Internal-isomorphism-invariant safety

Let Q be a finite quasi-primal algebra.

A local safety relation

`R subseteq Q^k x Q^m x Q^k`

is **groupoid-invariant** when every internal isomorphism

`psi:D -> E`

between subalgebras preserves R on tuples lying in D:

if

`R(a,u,v)`

and every coordinate of `(a,u,v)` lies in D, then

`R(psi(a),psi(u),psi(v))`.

Because internal isomorphisms are invertible and their inverses are also internal isomorphisms, this is equivalently invariance on every internal-isomorphism orbit of complete transition tuples.

Every equation-defined relation between Q-terms has this property, but the converse is not asserted here.

## 3. Positive side: demi-semi-primality

Assume Q is demi-semi-primal.

Then every internal isomorphism between nontrivial subalgebras extends to a global automorphism. As derived in `DEMI_SEMIPRIMAL_TERM_SAFETY.md`, term operations are exactly the functions that:

1. preserve generated subalgebras; and
2. are equivariant under `G=Aut(Q)`.

Any groupoid-invariant R is in particular G-invariant.

Therefore the orbit/stabilizer predecessor `DPre` is monotone on G-invariant state sets and its greatest fixed point is exactly the greatest term-winning region.

So demi-semi-primality implies universal greatest-region behavior for the relation-level class.

## 4. Negative side: start from a genuinely partial symmetry

Now suppose Q is quasi-primal but **not** demi-semi-primal.

Then there exists an isomorphism

`phi:S -> T`

between nontrivial subalgebras S,T of Q that does not extend to any automorphism of Q.

In particular `|S|=|T|>=2`.

Let

`S={s_1,...,s_r}`

and fix the ordered enumeration

`a=(s_1,...,s_r) in S^r`.

Put

`b=phi(a) in T^r`.

### Lemma 1 -- the tags are globally separated

No global automorphism g of Q satisfies

`g(a)=b`.

### Proof

If g(a)=b coordinatewise, then

`g(s_i)=phi(s_i)`

for every element of S. Hence `g|S=phi`, contradicting nonextendability. QED.

This ordered enumeration is the key tag used below.

## 5. Create enough paired state labels

Choose three distinct codewords

`c_0,c_1,c_2 in S^2`.

They exist because `|S|>=2` and therefore `|S^2|>=4`.

Define source-tag states of arity

`k=r+2`

by

`A_i=(a,c_i) in S^k`, `i=0,1,2`.

Define their phi-images

`B_i=phi(A_i)=(b,phi(c_i)) in T^k`.

Because `a != b`, source-tag states and target-tag states are disjoint.

The enumeration prefix also rigidifies each source code under global automorphisms:

### Lemma 2 -- code-state orbit separation

No global automorphism maps `A_i` to `A_j` for `i!=j`, nor `B_i` to `B_j` for `i!=j`, and no global automorphism maps any `A_i` to any `B_j`.

### Proof

If `g(A_i)=A_j`, the first r coordinates give `g(a)=a`. Since a lists every element of S, g fixes S pointwise, hence fixes c_i, so i=j.

The same argument applies on T.

If `g(A_i)=B_j`, then the first r coordinates give `g(a)=b`, contradicting Lemma 1. QED.

## 6. Inputs: one partial-symmetry probe and one global-isolation probe

Take input arity

`m=|Q|`.

### Special input

Choose a tuple

`e in S^m`

that contains every element of S at least once and pads the remaining coordinates by repetition.

Let

`e'=phi(e) in T^m`.

Define the paired special observations

`z_A=(A_0,e)`

and

`z_B=(B_0,e')=phi(z_A)`.

### Global generator input

Let

`g_Q in Q^m`

be an ordering of every element of Q exactly once.

Any internal isomorphism whose domain contains all coordinates of `g_Q` has domain Q itself, hence is a global automorphism.

This tuple will isolate dead-state gadgets from proper partial symmetries.

## 7. Special observation orbit

Consider the full internal-isomorphism groupoid orbit O of `z_A`.

For an observation `psi(z_A)` in O, where psi is any internal isomorphism applicable to S, declare exactly two outputs safe:

`psi(A_1)` and `psi(A_2)`.

### Lemma 3 -- this prescription is well-defined

If two internal isomorphisms `psi_1,psi_2` satisfy

`psi_1(z_A)=psi_2(z_A)`,

then

`psi_1(A_i)=psi_2(A_i)` for i=1,2.

### Proof

The state prefix of z_A contains the ordered enumeration a of all elements of S. Equality of the mapped observations therefore forces `psi_1|S=psi_2|S`. Since A_1,A_2 use only values from S, their images agree. QED.

Thus the two-output restriction is invariant under every internal isomorphism.

At the two distinguished observations this says:

- at z_A, the only safe outputs are `A_1,A_2`;
- at z_B, the only safe outputs are `B_1,B_2`.

The pairings are

`A_1 <-> B_1`

and

`A_2 <-> B_2`.

## 8. Dead states

Make two state/input observations completely dead:

`(A_2,g_Q)`

and

`(B_1,g_Q)`.

For groupoid invariance, make every global-automorphism image of those observations dead as well.

This is sufficient because any internal isomorphism applicable to an observation containing `g_Q` must be a global automorphism.

By Lemma 2 these dead-state automorphism orbits are disjoint from

`A_0,A_1,B_0,B_2`.

They are also disjoint from the special observation orbit because the special input uses only values from the proper subalgebra S (or one of its isomorphic images), whereas `g_Q` contains all |Q| distinct values. A nonextendable internal isomorphism cannot have S=Q, so `|S|<|Q|`.

## 9. Complete safety relation

Define R as follows.

1. On the special observation groupoid orbit O, allow exactly the transported pair of outputs described in section 7.
2. On the two dead global-automorphism observation orbits, allow no output.
3. At every other observation, allow every output.

### Lemma 4

R is groupoid-invariant.

### Proof

The special restriction is defined orbitwise and is well-defined by Lemma 3.

The dead observations form complete global-automorphism orbits, and no proper internal isomorphism applies to the full-carrier input tuple.

Every remaining observation lies outside both exceptional orbit families. If an internal isomorphism mapped such an observation into an exceptional orbit, its inverse would map the exceptional observation back, proving the original observation belonged to the same orbit after all. Thus generic observations map only to generic observations, where every output is safe. QED.

## 10. First winning domain

Let

`W_1={A_0,A_1}`.

Define a total controller table sigma_1 by:

- on the special groupoid orbit, map `psi(z_A)` to `psi(A_1)`;
- everywhere else, use the state projection as the next state.

The table preserves every internal isomorphism:

- the special branch is defined equivariantly;
- the state projection is equivariant;
- the branch condition itself is a groupoid orbit.

Because Q is quasi-primal, each output coordinate of sigma_1 is therefore a Q-term.

On W_1:

- z_A goes safely to A_1;
- no W_1 state lies in a dead orbit;
- every other required observation uses the safe self-loop/state projection.

Hence W_1 is term-winning.

## 11. Second winning domain

Let

`W_2={B_0,B_2}`.

Define sigma_2 by:

- on the special groupoid orbit, map `psi(z_A)` to `psi(A_2)`;
- everywhere else, use the state projection.

At z_B this chooses B_2.

The same equivariance argument makes sigma_2 a Q-term controller, and W_2 is safe and invariant.

## 12. No common winning superset

Let W be any domain containing both W_1 and W_2.

Then both special observations z_A and z_B are active.

At z_A, R allows only A_1 or A_2.

### Case 1: controller chooses A_1 at z_A

Term preservation of phi forces output B_1 at z_B.

Forward invariance therefore requires

`B_1 in W`.

But B_1 is dead at input g_Q, so no winning domain can contain it.

Contradiction.

### Case 2: controller chooses A_2 at z_A

Forward invariance already requires

`A_2 in W`.

But A_2 is dead at input g_Q.

Contradiction.

Those are the only safe choices at z_A.

Therefore no term-winning W can contain both W_1 and W_2.

## 13. Characterization theorem

### Theorem 5 -- exact relation-level boundary

For a finite quasi-primal algebra Q, the following are equivalent:

1. Q is demi-semi-primal;
2. for every finite state arity k, input arity m, and groupoid-invariant safety relation R, the family of original-signature positional term-winning state domains has a greatest element.

### Proof

`1 -> 2` is the orbit/stabilizer greatest-fixed-point theorem from `DEMI_SEMIPRIMAL_TERM_SAFETY.md`, since groupoid invariance implies automorphism invariance.

For `2 -> 1`, contrapose. If Q is not demi-semi-primal, sections 4--12 construct a groupoid-invariant finite safety game with two term-winning domains W_1,W_2 having no common term-winning superset. Hence no greatest domain exists. QED.

## 14. Noether-style inner ground

The boundary is not the vocabulary "demi" versus "quasi".

It is **patchability of partial symmetries**.

When every internal symmetry extends globally:

- strategy choices live on global automorphism orbits;
- a representative choice can be propagated consistently;
- winning domains patch and a greatest fixed point survives.

When a symmetry is genuinely partial:

- one domain may activate only one side of the partial-symmetry constraint;
- another domain may activate only the other side;
- combining the domains activates both ends of one globally coupled controller-table equation;
- the forced image can be routed through a dead state.

The ordered subalgebra enumeration is what converts nonextendability into a concrete separation of global state orbits.

The full-carrier input is what prevents proper partial symmetries from contaminating the dead-state gadget.

## 15. Concrete calibration

`experiments/quasiprimal_general_relation_template.py` instantiates the general construction on the three-element Quackenbush algebra.

It checks:

- the special state tags and phi-pairings;
- all 2^11=2048 binary transition tuples for phi-invariance of R;
- phi-equivariance/subalgebra preservation of the two explicit controller tables on all binary observations;
- safety and invariance of W_1 and W_2 across all 27 inputs.

The checker is a calibration of the template, not the proof of Theorem 5.

## 16. What remains open

The original stronger conjecture now reduces to a definability question:

> if Q is finite quasi-primal and not demi-semi-primal, can the groupoid-invariant relation constructed above always be replaced by an **equation-defined** safety relation while preserving the obstruction?

For the 27 three-element discriminator+unary family the answer is yes by `THREE_ELEMENT_DEMI_BOUNDARY.md`, using an explicit single term equation.

For arbitrary Q this is not yet proved.

The obstacle is real: groupoid invariance of a relation does not by itself imply that the relation is the zero/equality set of one original-signature term equation.

Possible routes:

1. use Pixley/Baker-Pixley interpolation to build a term-valued discriminator for the exceptional transition orbits;
2. allow a finite conjunction of equations first, then compress with the discriminator term if possible;
3. characterize which groupoid-invariant relations of a quasi-primal algebra are quantifier-free/equationally definable;
4. weaken the theorem statement to compatible/subpower safety relations and determine whether the construction can be made a subpower.

## 17. Prior-art boundary

Classical ingredients:

- Pixley's characterization of term functions of quasi-primal algebras by preservation of internal isomorphisms;
- Quackenbush's demi-semi-primal extension condition;
- standard orbit/stabilizer equivariance facts.

Derived here:

- the ordered-subalgebra-tag construction;
- the full-carrier dead-state isolation trick;
- the equivalence between demi-semi-primality and universal greatest-region behavior for groupoid-invariant finite safety games.

Current searches have found work on dominant/permissive reactive strategies and extensive universal-algebra interpolation theory, but no source for this exact restricted-term-controller characterization. This is a bounded search statement, not a publication novelty conclusion.
