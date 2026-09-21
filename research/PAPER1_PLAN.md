# Paper 1 plan — structure-preserving synthesis over atomless Boolean algebras

**Working title:** Structure-Preserving Reactive Synthesis over Atomless Boolean Algebras

**Status:** research manuscript plan. The theorem chain is derived in repository notes; novelty verification, direct Tau benchmarking, formal proof completion, and patent-boundary review remain before submission.

## 1. Paper thesis

The paper should **not** claim novelty for atomless-Boolean-algebra quantifier elimination by the standard cofactor recurrence. IDNI's granted U.S. patent US 12,254,082 includes essentially the mixed equation/disequation cofactor condition, and Asor's public work already develops the associated Boolean-algebra QE machinery.

The candidate contribution begins after that layer:

> complete-type synthesis over ABA can be represented and solved through the geometry of active Boolean minterm cells, yielding a finite cell game, an exact greatest-response principle for upward targets, a collapse from two-player synthesis to environment-only modal model checking on a positive fragment, and a structural complexity taxonomy with both tractable and hard subclasses.

This is the theorem spine to defend.

## 2. Main theorem chain

### Theorem A — support presentation of complete ABA types

For pure ABA, complete k-types are nonempty supports on the `2^k` Boolean minterm cells:

`|T_k| = 2^(2^k)-1`.

With a finite interpreted-constant set C and constant-partition rank `rho(C)`,

`|T_k(C)| = (2^(2^k)-1)^rho(C)`.

This is baseline structure, not the main novelty claim.

### Theorem B — cell-game factorization for conjunctive Step/Safe

For d state BA coordinates, e environment coordinates and d next/output coordinates, define state/partial/full cell universes

`V, P, U`

with

`|V| = rho(C) 2^d`,
`|P| = rho(C) 2^(d+e)`,
`|U| = rho(C) 2^(2d+e)`.

For conjunctive ABA equations/disequations, complete state types are nonempty subsets of V, but the zero/equation safety dynamics are governed by a finite alternating game on individual cells.

The cell controllable predecessor is

`Pre(A) = { v : for every partial cell p over v, there exists Step-allowed full cell u over p with next(u) in A }`.

Positive disequations are robust target-hit obligations on V.

### Theorem C — canonical upward-support representation

Inside a fixed allowed cell arena A, every upward-closed family of nonempty supports is represented canonically by an inclusion-antichain H of hit obligations:

`Phi_H = { S != empty : S subseteq A and for every h in H, S intersect h != empty }`.

Equivalent dual form: minimal winning supports `M = Tr(H)` via hypergraph blocker/transversal duality.

### Theorem D — greatest response / extremal synthesis

For an observed environment partial support P, let `Max(P)` contain every zero-safe Step-allowed full cell over P.

For every upward target W:

`exists legal Q over P with next(Q) in W`

iff

`Max(P) is legal and next(Max(P)) in W`.

Thus one greatest response type witnesses every successful existential system choice.

### Theorem E — CPre collapses to a box modality

On upward target sets:

`CPre(W) = Box_max(W)`,

where `Box_max` is the universal predecessor in the environment-only transition system induced by the canonical maximal response.

Consequences:

- CPre preserves arbitrary intersections;
- prime hit obligations propagate independently;
- the system's type-level response strategy is objective-independent within the positive fragment.

### Theorem F — positive modal mu-calculus closure

Upward atoms, AND, OR, CPre, least fixed points and greatest fixed points all remain in the canonical antichain lattice.

Hence upward reachability, Büchi, and the corresponding positive modal mu-calculus fragment can be evaluated without complete-type enumeration.

Bounded differential validation currently includes explicit complete-type comparison for reachability and Büchi at d=e=1, including intermediate approximants.

### Theorem G — constructive strategy

Under Asor's effective-presentation/witness assumption, the maximal response complete type can be realized as concrete BA output data. The repository also includes an explicit dyadic-interval ABA reference model for constructive witnesses.

### Theorem H — exact symmetry quotient

If a packed d-coordinate specification is invariant under diagonal `S_d`, state/partial/full cell orbits are histograms and have sizes

`d+1`,
`binom(d+3,3)`,
`binom(d+7,7)`.

The cell predecessor and invariant objectives descend exactly to this quotient.

### Theorem I — affine/XOR-linear tractability

For an equation-only cell transition

`A_s s + A_i i + A_n n = c`

over GF(2), and affine target `Bn=b`, the predecessor is affine or empty.

Let

`M_n = [ A_n ; B ]`

and let L span the left nullspace of `M_n`. Then predecessor existence for all environment inputs is characterized by

`L A_i = 0`

and

`L A_s s = L [ c ; b ]`.

Equation-only affine safety therefore has at most d+1 strict nonempty affine decreases.

### Theorem J — hardness / expressive lower bounds

The cell predecessor can realize arbitrary bottom/top-preserving monotone Boolean dynamics with sufficient environment structure.

Consequences include:

- periodic orbits are antichains;
- Sperner-scale periods are possible as a function of cell width;
- compact XOR/LFSR source formulas already force `2^d-1` strict prime-obligation strengthenings;
- support OBDDs can be exponentially large even for simple disequation CNFs.

This establishes that the good algorithms are structural, not universal.

## 3. Strong narrative

The conceptual story should be:

1. **Type explosion.** ABA has `2^(2^d)-1` complete d-types.
2. **Change representation.** A type is merely a nonempty set of `2^d` Venn cells.
3. **Factor the game.** Equations govern individual cell transitions; disequations become hit obligations.
4. **Find the extremum.** Upward objectives admit one greatest system response.
5. **Collapse synthesis.** `forall environment exists system` becomes environment-only `Box_max`.
6. **Compile the temporal logic.** The upward positive mu-calculus lives in a finite antichain lattice.
7. **Classify structure.** Symmetry and affine structure can collapse complexity; monotone-network universality and LFSRs show genuine lower bounds.

This is a substantially stronger thesis than "binary encode the complete types" or "use BDDs".

## 4. Material that belongs in background / implementation, not novelty claims

Do not sell the following as new mathematical contributions:

- standard ABA quantifier elimination;
- the one-variable equation/disequation cofactor recurrence in the form claimed/published by IDNI/Asor;
- generic binary coding of finite type sets;
- abstract left/right adjoints of substitution;
- generic BDD symbolic model checking;
- general hypergraph transversal duality;
- classical Sperner bounds for monotone map cycles;
- generic CSP polymorphism theory.

They remain important ingredients and comparisons.

## 5. Likely paper sections

1. Introduction and contribution boundary
2. ABA complete-type support geometry
3. Reactive cell games
4. Canonical upward support properties
5. Greatest-response theorem
6. Synthesis-to-model-checking collapse
7. Positive mu-calculus algorithms
8. Strategy realization
9. Structural tractability: symmetry and affine systems
10. Structural hardness: monotone dynamics, OBDD lower bounds, compact LFSR family
11. Experiments / differential validation
12. Relation to ocLTL, Tau, infinite-data synthesis and CSP/polymorphism theory
13. Limitations and patent/IP disclaimer

## 6. Required promotion work

Before submission:

1. complete novelty search theorem-by-theorem;
2. formalize the representation-independent extremal lemmas and at least the finite support/cell layer;
3. obtain a working direct Tau differential benchmark;
4. construct deterministic benchmark families rather than rely on random checks;
5. separate claims that are mathematically novel from implementation improvements to Tau;
6. obtain expert review of the main proofs;
7. state the IDNI patent relationship neutrally and accurately.

## 7. Candidate venues

Choose only after the theorem chain is stabilized. Natural families include formal methods / logic in computer science, automated reasoning, and theoretical CS venues concerned with reactive synthesis, symbolic algorithms, and infinite-domain reasoning.

The submission should be positioned as a theory-specific structural synthesis result, not as a Tau product paper.
