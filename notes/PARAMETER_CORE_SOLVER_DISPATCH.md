# Symmetry-gated solver dispatch for parameter cores

**Status:** DERIVED theorem + exhaustive finite calibration + explicit necessity counterexample. Connects the existing parameter-patchability theorem to the standalone `FiniteSafetyGame` demi-semi-primal solver. Tau-independent. Not Lean-checked.

## 1. Problem

The repository already contains two exact solver architectures:

1. the generic pointed/quasi-primal fixed-domain compiler plus domain-lattice search;
2. the demi-semi-primal automorphism-orbit/stabilizer greatest-fixed-point solver.

`QUASIPRIMAL_PARAMETER_PATCHABILITY.md` proves that naming a good parameter core turns a quasi-primal algebra into a pointed demi-semi-primal algebra. But the public parameter-core API currently does not dispatch to the fixed-point solver: it continues to use exhaustive/nogood/bitset domain search for every core.

There is also an important semantic guard. The demi proof uses symmetry of the safety relation. The generic parameterized API accepts arbitrary extensional safe relations, which need not respect the pointed automorphism group.

This note gives the exact dispatch condition.

## 2. Pointed algebraic data

Let Q be a finite quasi-primal algebra and K a closed parameter core.

Write

`G_K = {g in Aut(Q) : g(k)=k for every k in K}`.

For observation z define

`Sg_K(z)=Sg_Q(K union coordinates(z))`.

The pointed expansion `Q_K` has the internal-isomorphism extension property iff every K-fixing isomorphism between K-containing nontrivial subalgebras extends to an element of `G_K`.

This is exactly the existing `has_pointed_extension_property` predicate when quasi-primality is known externally.

## 3. Symmetry of the safety relation

For state/input/output triple `(s,u,v)` and `g in G_K`, write

`g(s,u,v)=(g s, g u, g v)` coordinatewise.

Call the safe relation R **K-invariant** when

`(s,u,v) in R iff g(s,u,v) in R`

for every `g in G_K`.

Because every g is invertible, it suffices computationally to check closure of R under all g.

Every original-signature or K-parameter equation-defined relation has this invariance automatically. An arbitrary extensional relation supplied through the standalone API need not.

## 4. Pointed demi predecessor

Assume K has the extension property and R is K-invariant.

For observation `z=(s,u)`, let

`Stab_K(z)={g in G_K : g z=z}`.

For a K-invariant target W define `DPre_K(W)` to contain state s iff for every environment input u there exists output v such that

1. `v in W`;
2. `(s,u,v) in R`;
3. every coordinate of v lies in `Sg_K(s,u)`;
4. v is fixed coordinatewise by `Stab_K(s,u)`.

This is exactly the demi-semi-primal predecessor applied to the pointed expansion.

## 5. Generalized greatest-region theorem

The earlier notes state the positive theorem for equation-defined safety games. Equation definability is stronger than necessary.

### Theorem 1 -- invariant extensional safety is enough

Let Q be finite quasi-primal, K a closed core with the pointed extension property, and R any finite **K-invariant** extensional safety relation.

Then:

1. `DPre_K` maps K-invariant state sets to K-invariant state sets;
2. its greatest fixed point from the full state space is exactly the greatest domain from which one positional K-polynomial controller wins the safety game;
3. one winning controller is obtained by choosing one stabilizer-fixed safe output per `G_K`-orbit of winning observations and propagating it equivariantly;
4. every coordinate of the resulting total table is a K-polynomial operation.

### Proof sketch

The pointed extension property plus quasi-primality gives the term-function characterization:

`K-polynomial = K-subalgebra-preserving + G_K-equivariant`.

K-invariance of R transports any safe representative choice across the whole observation orbit. K-invariance of W transports target membership. Generated pointed subalgebras and observation stabilizers transport by conjugacy. Thus one representative action defines a consistent safe orbit action.

Conversely every K-polynomial controller preserves pointed subalgebras and is `G_K`-equivariant. Because R is invariant, its full winning set is K-invariant and is a post-fixed point of `DPre_K`. Greatest-fixed-point maximality gives necessity.

No step uses equation syntax once invariance has been supplied.

## 6. Invariant forbidden arenas

Let A be a K-invariant allowed state arena, equivalently the complement of a K-invariant forbidden set.

Define

`F_A(W)=A intersection DPre_K(W)`

and iterate from `W_0=A`.

### Corollary 2

The greatest fixed point of `F_A` is the greatest K-polynomial term-controllable domain contained in A.

Therefore the parameter API can answer arbitrary required-state queries without domain search whenever:

- K has the pointed extension property;
- R is K-invariant;
- the forbidden-state set is K-invariant.

Compute the greatest allowed domain G and return success exactly when the required states are contained in G.

If the forbidden set is not K-invariant, fall back to the generic pointed-domain solver.

## 7. Why safety invariance is necessary

The extension property alone is insufficient for arbitrary extensional games.

Take the pure discriminator algebra

`Q={0,1,2}`

and name parameter 2. The pointed automorphism group contains the swap

`0 <-> 1`, `2 -> 2`.

Use one state coordinate, no environment input, and the safe relation consisting of exactly

`0 -> 0`,
`1 -> 2`,
`2 -> 2`.

This relation is not invariant under the pointed swap because `0->0` maps to the unsafe transition `1->1`.

The pointed class `{0,1}` has two relevant polynomial seeds:

- the state-like seed maps `0->0` and `1->1`;
- the constant-2 seed maps both states to 2.

Hence:

- domain `{0,2}` is controllable with the state-like seed;
- domain `{1,2}` is controllable with the constant-2 seed;
- their union Q is **not** controllable, because no one seed is safe at both 0 and 1.

A naive local demi predecessor checks the observations independently, sees one local action at 0 and another at 1, and incorrectly keeps all three states.

Thus any automatic use of the current demi predecessor on arbitrary extensional games must first verify safety symmetry or require the caller to provide a trusted proof of it.

## 8. Exhaustive discriminator calibration

Use again the pure discriminator algebra Q and pointed core `{2}`.

Its pointed automorphism group has two elements: identity and the swap `0<->1`.

There are 27 scalar transitions `(s,i,y)` with one state coordinate and one input coordinate. Under the pointed automorphism group they form exactly 14 transition orbits:

- one fixed orbit;
- thirteen two-element orbits.

Therefore there are exactly

`2^14 = 16,384`

K-invariant extensional safety relations.

The state carrier has two pointed automorphism orbits `{0,1}` and `{2}`, hence four invariant allowed arenas.

An exhaustive checker tested all

`16,384 * 4 = 65,536`

pairs `(invariant safety relation, invariant allowed arena)`.

For every pair it independently computed:

1. every domain feasible under the exact pointed seed-table semantics;
2. all inclusion-maximal feasible domains;
3. the pointed demi/stabilizer greatest fixed point.

Results:

- zero mismatches;
- exactly one maximal feasible domain in every case;
- that domain equals the fixed-point result in all 65,536 cases.

For the unrestricted arena, greatest-domain sizes across all 16,384 relations were:

- size 0: 9,360 relations;
- size 1: 2,080;
- size 2: 1,920;
- size 3: 3,024.

This is exhaustive finite evidence for the theorem on the smallest nontrivial pointed-symmetry laboratory; the theorem itself is structural.

## 9. Quackenbush parameter-core phase transition

Consider the existing nine-state Quackenbush benchmark from `experiments/quasiprimal_nogood_domain_search.py`.

The closed parameter cores are

`empty`, `{0,1}`, `Q`.

Exact pointed-domain enumeration gives:

### Parameter-free core

- pointed extension property: false;
- feasible domains: 128;
- maximal domains: two incomparable domains of size 7;
- no greatest domain.

The two maximal domains are

`{00,01,02,12,20,21,22}`

and

`{01,02,11,12,20,21,22}`.

### Core `{0,1}`

- pointed extension property: true;
- pointed automorphism group: trivial;
- hence every extensional safety relation is invariant;
- feasible domains: 160;
- unique greatest domain of size 8:

`Q^2 \ {(1,0)}`.

The pointed-demi predecessor reaches it in one strict removal step.

### Full core Q

- primal controller language;
- feasible domains: 253;
- the same unique greatest size-8 domain;
- ordinary/pointed-demi predecessor again reaches it directly.

The 160 and 253 feasible-domain counts agree with the committed generic-kernel campaign, while the fixed-point solver identifies the unique maximum without enumerating the domain lattice.

This is an exact end-to-end demonstration that crossing the patchability threshold can change not only expressivity but the appropriate solver architecture.

## 10. Dispatch rule

For a quasi-primal parameter core K:

### Fast path

Use the pointed demi fixed-point solver when all hold:

1. `has_pointed_extension_property(Q,K)`;
2. the safety relation is `G_K`-invariant;
3. any forbidden-state arena is `G_K`-invariant.

Then there is at most one maximal domain under the arena constraint, namely the greatest fixed point.

### Fallback

Otherwise use the exact pointed seed/domain backend:

- semantic seed canonicalization/dominance;
- bitset/nogood search;
- or direct SAT/CSP compilation.

The fallback is necessary both below the patchability threshold and for symmetry-breaking extensional constraints.

## 11. Fail-closed API consequence

`FiniteSafetyGame.solve_demi_semi_primal()` currently assumes the caller has justified the mathematical hypotheses.

A safer public surface would expose either:

- `solve_demi_semi_primal(check_invariance=True)` and reject non-invariant relations; or
- a lower-level trusted mode requiring an explicit `assume_invariant=True` flag.

For automatic parameter-core dispatch, invariance should always be checked exactly on the finite table.

This is especially important because the three-transition counterexample shows that silently omitting the check can produce a false winning region.

## 12. Solver hierarchy after this result

For quasi-primal controller synthesis the runtime hierarchy becomes:

1. **primal/full table:** ordinary finite safety fixed point;
2. **pointed demi core + invariant game:** pointed orbit/stabilizer fixed point;
3. **non-demi core or symmetry-breaking game:** pointed groupoid/seed-domain solver;
4. within the generic solver, canonicalize semantic seeds and dispatch width-one classes to reachability where possible.

This is stronger than choosing a backend from carrier size alone: the algebraic parameter core and the symmetry of the actual game determine the correct algorithmic class.

## 13. Next steps

1. Add an exact pointed-safety invariance checker.
2. Add a parameter-core `solver="auto"` dispatch that selects the fixed-point path only under the three verified conditions above.
3. Differentially compare auto dispatch against exhaustive pointed semantics on the complete existing bounded corpus.
4. Add the three-transition non-invariance witness as a regression test that must force fallback.
5. Measure the crossover on larger patchable cores; the benefit should grow with state-lattice size because the fast path never enumerates domains.
6. Formalize the invariant-extensional generalization of the demi theorem in Lean.
