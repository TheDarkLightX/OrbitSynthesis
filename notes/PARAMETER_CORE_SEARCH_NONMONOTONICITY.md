# Parameter cores: monotone expressivity, nonmonotone search structure

**Status:** DERIVED theorem + exact three-element counterexample + finite calibration. The parameter-closure lattice and polynomial-clone inclusion are established in `QUASIPRIMAL_PARAMETER_CLOSURE_LATTICE.md`. This note adds the reactive/compiler separation: enlarging a closed parameter core monotonically enlarges the controller language and feasible-domain family, but the semantic seed/switch structure of the pointed compiler need not become simpler or more complex monotonically. Tau-independent. Not Lean-checked.

## 1. Semantic monotonicity theorem

Let `Q` be a finite algebra and let `K subseteq L` be closed parameter cores. Then every positive-arity `K`-polynomial operation is also an `L`-polynomial operation:

`Pol_K(Q) subseteq Pol_L(Q)`.

Fix any finite safety game over Q and any candidate state domain W.

### Theorem 1

If W admits one positional controller whose coordinates belong to `Pol_K(Q)`, then W admits such a controller over `Pol_L(Q)`.

### Proof

Use the same controller table. Every coordinate operation available over K remains available over L. Safety and invariance are properties of the unchanged game/table/domain, so they are preserved. QED.

### Corollaries

For fixed game R:

`Feas_K(R) subseteq Feas_L(R)`.

Hence:

- realizability from any fixed initial set is monotone in the parameter core;
- maximum achievable winning-domain cardinality is nondecreasing;
- if greatest winning domains exist at both cores, then `G_K subseteq G_L`.

This is the semantic sense in which more named parameters can only help.

## 2. The compiler metric is different

For a pointed class E, compile each representative seed to a domain-validity family. Quotient semantically equivalent seeds and delete every seed dominated by another seed, as in `SEED_RULE_SEMANTIC_KERNEL.md`.

Define

`sw_K(E)`

as the number of remaining incomparable semantic seeds of E.

Define the **multi-seed class count**

`M_K = |{E : sw_K(E) > 1}|`

and maximum semantic width

`W_K = max_E sw_K(E)`.

These are properties of the compiled search representation, not of controller expressivity itself.

There is no monotonicity theorem for them under `K subseteq L`.

## 3. Exact counterexample on the pure three-element discriminator algebra

Let

`Q={0,1,2}`

with only the ternary discriminator operation

`d(x,y,z)=z if x=y, else x`.

Every nonempty subset is a subalgebra and every bijection between subalgebras is an isomorphism. Parameter-free definable constants are absent, so closed parameter cores are simply subsets of Q.

Use one state coordinate s, one environment input i, and one next-state/output coordinate y.

Define safety by

`Safe(s,i,y) iff NOT (s != i AND s=2 AND y=s)`.

In words:

> every transition is safe except self-output `y=2` from state 2 when the input is different from 2.

We compare the chain

`K0=empty subset K1={2} subset K2=Q`.

## 4. Parameter-free core: one genuine global switch

With no named constants there are two pointed observation classes:

1. equal pairs `(s,s)`;
2. distinct pairs `(s,i)` with `s!=i`.

On the distinct-pair class the generated subalgebra of representative `(0,1)` is `{0,1}`, so there are two seeds.

### State-projection seed

Transporting seed 0 returns the state coordinate everywhere.

It is unsafe exactly at distinct observations whose state is 2. Therefore its valid domains are all subsets of `{0,1}`.

### Input-projection seed

Transporting seed 1 returns the input coordinate everywhere.

It is always safe on distinct observations. Closure requires that if any state is active, both other states are also active. Hence its valid domains are exactly

`empty` and `Q`.

The two validity families are incomparable:

- `{0}` is valid for state projection but not input projection;
- `Q` is valid for input projection but not state projection.

Therefore the distinct class has semantic width two.

The equal class has width one.

Thus

`M_empty=1`, `W_empty=2`.

## 5. Naming only 2 removes every switch

Now let `K={2}`.

Pointed internal isomorphisms must fix 2. The observation orbit partition refines to five classes:

- `(0,0) <-> (1,1)`;
- `(0,1) <-> (1,0)`;
- `(0,2) <-> (1,2)`;
- `(2,0) <-> (2,1)`;
- `(2,2)`.

Exact semantic dominance on the compiled seed rules leaves **one** seed in every class.

In particular, on `(0,1)<->(1,0)` the three raw seeds are 0,1,2, but seed 0 is dominated and the remaining validity families are nested; the semantic antichain has width one for the game above.

Therefore

`M_{2}=0`, `W_{2}=1`.

The pointed kernel has crossed from a switched-search regime to pure graph closure.

## 6. Naming all carrier values reintroduces switches

At the full core `K=Q`, every observation is its own pointed class and every scalar output value is available as a seed because the expansion is primal.

For observations `(2,0)` and `(2,1)`, output 2 is unsafe. The two safe alternatives 0 and 1 impose incomparable successor requirements

`2 -> 0`

and

`2 -> 1`.

Neither semantic seed dominates the other:

- domain `{0,2}` validates the first but not the second;
- domain `{1,2}` validates the second but not the first.

Thus two singleton observation classes have width two.

Therefore

`M_Q=2`, `W_Q=2`.

The switch-count profile is exactly

`1 -> 0 -> 2`,

and maximum semantic width is

`2 -> 1 -> 2`.

## 7. Feasible domains still move only upward

Despite the nonmonotone compiler structure, the feasible-domain families are:

### K=empty

`empty, {0}, {1}, {0,1}, Q`.

### K={2}

Exactly the same five domains.

### K=Q

`empty, {0}, {1}, {0,1}, {0,2}, {1,2}, Q`.

So

`Feas_empty = Feas_{2} proper_subset Feas_Q`.

This exactly matches Theorem 1 while refuting any claim that seed/switch complexity must track semantic expressivity monotonically.

## 8. Full finite profile

The exact checker also evaluates all eight closed cores of the pure discriminator algebra on this game.

For the core-size chain the raw pointed representation grows sharply as symmetry is broken. Representative values are:

- `K=empty`: 2 pointed classes, 3 raw seeds, semantic switch count 1;
- any singleton core: 5 pointed classes, 10 raw seeds; for `{2}` the switch count is 0 in this witness;
- any two-element core: 9 pointed classes, 23 raw seeds;
- `K=Q`: 9 pointed classes, 27 raw seeds, switch count 2.

The exact semantic widths depend on which constant is named because the safety relation singles out state 2.

## 9. Inner ground

Three different effects of parameters were previously being conflated.

### Expressivity expansion

Naming constants enlarges the polynomial clone. This is monotone.

### Symmetry refinement

Naming constants forces pointed isomorphisms to fix more values. Observation orbits split. This usually increases the number of independently selectable local controller pieces.

### Seed dominance

After orbit splitting, some locally available seeds can become semantically redundant because one seed's closure obligations entail another's on the smaller class. This can reduce switch width.

These effects compete.

In the witness:

- no parameters: one global symmetry class couples all distinct observations, leaving one binary switch;
- name 2: the orbit splits in exactly a way that makes every class semantically deterministic after dominance;
- name everything: symmetry is completely removed, and the two safe alternatives at state 2 become independent local switches.

So "more symmetry" and "more freedom" are not ordered by one scalar difficulty measure.

## 10. Research/product consequence: parameter selection is bicriteria

A parameter core should not be scored only by

- parameter budget; or
- controller expressivity / winning-domain size.

It also has a **compiled search cost**.

A first compiler-aware objective is the Pareto tuple

`(parameter rank, semantic switch count, maximum semantic width, winning-domain objective)`.

An intermediate core may be computationally preferable to both the smallest and largest language.

This creates a new independent OrbitSynthesis capability:

> choose the controller language itself as part of synthesis, balancing semantic power against the structure of the resulting exact solver.

The existing parameter-core lattice makes the language choices finite and canonical for finite quasi-primal algebras.

## 11. Relation to CSP constant expansions

Classical finite-CSP theory has a superficially opposite-looking fact: for a finite **core** constraint language, adding all singleton unary relations can be done without increasing the polynomial-time complexity of the CSP. This is commonly used to pass to idempotent polymorphisms.

That result concerns adding constants/relations to the **instance language** while preserving CSP complexity up to reduction.

Here constants enlarge the **controller operation language**, and we inspect the internal structure of an exact synthesis compiler. The two statements are therefore compatible.

Do not present the counterexample as contradicting CSP idempotent reduction.

## 12. Exact bounded calibration

A standalone exhaustive checker enumerated the pointed classes, unique pointed transports, raw seeds, all eight state domains, semantic seed-validity families, equivalence classes, and dominance antichains for every core of Q.

For the chain `empty -> {2} -> Q` it verified:

- multi-seed semantic classes: `1,0,2`;
- maximum semantic widths: `2,1,2`;
- feasible-domain counts: `5,5,7`;
- exact feasible-domain inclusion along the core chain.

The computation is a falsification certificate for the explicit witness, not the proof of semantic monotonicity.

## 13. Next frontier

1. Add compiler-cost metrics to the parameter-core frontier API.
2. Determine whether minimizing semantic switch count over cores under a required winning-domain constraint is NP-hard.
3. Relate switch count to `kappa_patch`: patchability and solver simplicity are distinct objectives and may conflict.
4. Search for algebraic conditions forcing a width-one core to exist below full primalization.
5. Test whether semantic core selection can materially outperform both parameter-free and full-core synthesis on larger quasi-primal benchmarks.
6. Formalize Theorem 1 and the explicit three-element witness in Lean once the current formal files compile.
