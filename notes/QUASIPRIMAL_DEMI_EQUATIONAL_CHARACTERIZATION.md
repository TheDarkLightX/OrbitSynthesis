# Demi-semi-primality exactly characterizes greatest-region single-equation term safety

**Status:** DERIVED general characterization for finite quasi-primal algebras. The positive direction uses the derived demi-semi-primal orbit/stabilizer theorem. The negative direction combines the nonextendable-partial-symmetry reactive construction with the orbit-selector single-equation lemma. Classical Pixley/Quackenbush interpolation machinery is source-bound prior art; the reactive characterization remains under prior-art review. Not Lean-checked.

## 1. Main theorem

Let Q be a finite quasi-primal algebra.

Consider finite perfect-information safety games with:

- state space `Q^k`, `k>=1`;
- environment input space `Q^m`, `m>=0`;
- next-state/controller output in `Q^k`;
- one positional controller whose output coordinates must be original-signature Q-terms;
- safety relation given by a **single equation between Q-terms**.

### Theorem 1 -- exact demi boundary

The following are equivalent:

1. Q is demi-semi-primal;
2. every such single-equation safety game has a greatest original-signature term-winning state domain;
3. every finite equation-defined safety game over Q has a greatest original-signature term-winning state domain.

Since one equation is a special case of an equation-defined relation, `3 -> 2` is immediate. The content is `1 -> 3` and `2 -> 1`.

## 2. Positive direction

Assume Q is demi-semi-primal.

By the classical Quackenbush/Pixley characterization, Q-term operations are exactly the functions that preserve subalgebras and are equivariant under the global automorphism group `G=Aut(Q)`.

Every equation-defined safety relation is G-invariant because term operations commute with automorphisms.

`DEMI_SEMIPRIMAL_TERM_SAFETY.md` derives the exact predecessor

`DPre(W)`

on G-invariant state sets by requiring, at each observation:

- safety;
- next state in W;
- generated-subalgebra membership;
- observation-stabilizer-fixed output.

The greatest fixed point of DPre is exactly the set of states from which one positional Q-term controller wins.

Hence a greatest term-winning region exists for every equation-defined safety game.

This proves `1 -> 3`.

## 3. Contrapositive negative direction

Assume Q is quasi-primal but **not** demi-semi-primal.

Choose a nonextendable internal isomorphism

`phi:S -> T`

between nontrivial subalgebras.

`QUASIPRIMAL_DEMI_RELATIONAL_CHARACTERIZATION.md` constructs, from phi, a finite groupoid-invariant safety game with two term-winning domains

`W_1`

and

`W_2`

that have **no common term-winning superset**.

The construction has explicit arity bounds:

- if `r=|S|`, state arity `k=r+2`;
- input arity `m=|Q|`.

Its mechanism is:

1. order all elements of S in a tuple `a` and tag states by a;
2. use `b=phi(a)` as the paired target tag;
3. nonextendability guarantees no global automorphism maps a to b;
4. add two code coordinates from `S^2` to create several distinct phi-paired state labels;
5. at one special phi-paired observation orbit, allow exactly two paired response choices;
6. make one source-side and one target-side forced image state dead;
7. isolate dead observations with an input tuple enumerating the whole carrier Q.

Then:

- W_1 can activate only the source side of the partial-symmetry constraint;
- W_2 can activate only the target side;
- any common superset activates both sides;
- term preservation of phi forces a response through one of the dead states.

Thus no greatest winning domain exists for that groupoid-invariant relation.

The remaining task is to show that this relation can always be represented by one term equation.

## 4. Why every forbidden tuple in the construction is separable by a coordinate

Flatten a transition

`(state,input,next_state)`

into one tuple `x in Q^N`, where

`N=2k+m`.

Let p denote the first state coordinate.

The constructed relation R has only two kinds of forbidden tuples.

### Special-orbit forbidden tuples

Their observation contains the ordered enumeration of a nontrivial subalgebra (or an internal-isomorphism image of it).

Since that subalgebra has at least two elements, the transition tuple contains a coordinate whose value differs from `x_p`.

### Dead-orbit forbidden tuples

Their input contains an enumeration of the full carrier Q.

Since a non-demi quasi-primal algebra must have at least three elements, and in any case the relevant nonextendable S is proper, the full-carrier input contains a value different from `x_p`.

Therefore every forbidden tuple x satisfies

`exists j: x_j != x_p`.

## 5. Compile the relation to one equation

Apply `QUASIPRIMAL_ORBIT_SELECTOR_EQUATIONS.md`.

Because R is groupoid-invariant and every forbidden groupoid orbit has a coordinate separating it from p, choose one such coordinate index `j(O)` for every forbidden orbit O.

Define a total operation

`g:Q^N -> Q`

by:

- on safe orbits, `g(x)=x_p`;
- on forbidden orbit O, `g(x)=x_(j(O))`.

The operation g always returns one of its coordinates, so it preserves every subalgebra.

The branch partition is by internal-isomorphism orbits and the selected coordinate index is constant on each orbit, so

`g(psi x)=psi g(x)`

for every internal isomorphism psi wherever defined.

By Pixley's quasi-primal term-function characterization, g is represented by an original-signature Q-term.

By construction:

`R(x) iff x_p = g(x)`.

Thus the same no-greatest-region game is defined by the single term equation

`p=g`.

This proves the contrapositive of `2 -> 1`.

## 6. Conclusion

`1 -> 3 -> 2 -> 1`, proving Theorem 1.

So the previously observed primal/semi/demi/quasi algorithmic ladder has an exact semantic boundary:

> **among finite quasi-primal algebras, universal patchability of term-constrained safety winning regions is equivalent to extension of every nontrivial internal isomorphism to a global automorphism.**

## 7. The inner ground

The theorem is best understood as a statement about **local symmetry versus global patchability**.

### Demi-semi-primal side

Every partial algebraic symmetry relevant to term tables is the restriction of a global symmetry.

Controller choices can therefore be made on global observation orbits. Stabilizer-fixed representative actions propagate consistently, and the ordinary greatest-fixed-point logic survives.

### Non-demi quasi-primal side

There is a genuinely partial symmetry phi that no global automorphism realizes.

Two domains can each avoid one endpoint of phi's table constraint. Each therefore admits its own term controller.

Their union activates both endpoints. The shared-controller requirement then exposes an equation between table entries that the two independently chosen controllers never had to satisfy simultaneously.

The dead-state gadget turns that newly activated equality into an impossibility.

This is why the failure is specifically reactive:

`for each domain exists a term controller`

does not patch to

`exists one term controller for the union`.

## 8. Prior-art correction

The ordered-subalgebra enumeration used to separate source and target tags is a classical move, not a new OrbitSynthesis invention.

A standard proof of the Quackenbush characterization starts from a nonextendable

`iota:S->T`,

orders S as sigma and T as `tau=iota(sigma)`, observes that sigma and tau lie in distinct global automorphism orbits, and defines a conservative operation by different coordinate projections on those orbits.

That technique is recorded in connection with Burris--Sankappanavar Exercise IV.10.5 and is structurally the same representation move used here.

The orbit-selector equation lemma is likewise a quasi-primal interpolation application of orbitwise coordinate selection.

Do not claim those universal-algebra ingredients as novel.

The candidate contribution is the **reactive characterization**: extension of partial symmetries is exactly the condition for universal greatest-region patchability of original-signature term controllers.

## 9. Relation to the earlier finite evidence

`THREE_ELEMENT_DEMI_BOUNDARY.md` exhaustively classified the 27 discriminator+unary algebras on a three-element carrier:

- 15 demi;
- 12 non-demi;
- all 12 non-demi admitted a verified single-equation no-greatest witness.

Theorem 1 explains that complete finite observation as one instance of a general mechanism rather than an accident of the chosen family.

`QUASIPRIMAL_OBSTRUCTION_MINIMALITY.md` further proves that the existing three-element Quackenbush example has minimum carrier size within the quasi-primal hierarchy and requires state arity at least two for that concrete algebra.

## 10. Computational calibration

`experiments/quasiprimal_general_relation_template.py` verifies the general reactive template on the three-element Quackenbush algebra.

`experiments/quasiprimal_orbit_selector_equation.py` verifies the equation compiler on the same higher-arity template:

- all `3^11=177147` transition tuples are checked;
- 320 are forbidden;
- they form 306 forbidden internal-isomorphism orbits in that algebra;
- `safe(x) iff x_p=g(x)` holds globally;
- g is checked for phi-equivariance on all `2^11=2048` tuples in the proper binary subalgebra.

These computations are independent calibrations, not the proof of Theorem 1.

## 11. Literature status

Source-bound classical facts include:

- Pixley's characterization of quasi-primal term operations via isomorphisms between subalgebras;
- Quackenbush's demi-semi-primal extension characterization;
- the classical orbit-separation proof technique described above.

Searches also find reactive-synthesis work on dominant/permissive/maximal strategies and universal-algebra work on term interpolation/SMP, but no direct statement of Theorem 1 has yet been located.

That is **not** a novelty conclusion. Before paper promotion, search must still include:

- discriminator-variety and natural-duality literature;
- constrained/permissive strategy literature;
- algebraic automata/control literature;
- theses and older universal-algebra sources that may formulate the same patchability property under different terminology.

## 12. Next research frontier

The theorem closes the first structural classification. The next high-value questions are no longer "is demi the boundary?" but:

1. **complexity:** how hard is variable-domain synthesis on the non-demi side?
2. **subpower formulation:** exploit `SUBPOWER_ROW_LIST_SYNTHESIS.md` to design general term-clone backends;
3. **beyond quasi-primal:** find the analogous patchability criterion for finitely related/Mal'cev/edge-term clones;
4. **controller expressivity:** compare term, polynomial/parameterized, arbitrary local-table, and Boolean-power patchwork controllers;
5. **formalization:** mechanize the finite orbit-selector and no-common-superset theorem in Lean once the theorem statement is frozen.
