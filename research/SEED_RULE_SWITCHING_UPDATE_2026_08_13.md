# Frontier update — seed-rule switching boundary, 2026-08-13

**Status:** DERIVED + finite-calibrated. Tau-independent. Not Lean-checked. The NP-hardness is closely adjacent to classical switching-graph results and is not claimed as a new complexity class result.

## S1 — the compiled pointed kernel is a switched reachability object

For a fixed pointed controller core, each class has candidate seeds. A chosen seed contributes a set of forward requirements

`p in W -> q in W`

and an unsafe set that W must avoid.

After choosing one seed per class, union the selected implications into a directed graph E and the active unsafe sets into B. For required states I, the least possible invariant domain is exactly

`Reach_E(I)`.

Therefore a seed selection is feasible iff

`Reach_E(I) intersection B = empty`.

This is the right representation for the generic seed-rule backend: local rules are Horn implications, while classwise seed choice globally switches implication edges on and off.

## S2 — one seed per class has an exact graph algorithm

If every class has one seed, E and B are fixed.

Required-domain feasibility is equivalent to

`Reach_E(I) intersection B = empty`.

The greatest feasible closed domain is

`V \ PreStar_E(B)`,

where `PreStar_E(B)` is the set of states that can reach B.

So width-one seed rules need no domain branch-and-bound: one forward reachability query tests required states and one reverse reachability query gives the greatest feasible domain.

The family of feasible domains is union-closed in this case.

## S3 — two seeds per class are already NP-complete

Define BINARY-SEED DISCONNECTION:

- finite state set V;
- required I and blocked B;
- each class has exactly two seed edge sets;
- choose one seed from every class;
- ask whether the resulting reachability closure of I avoids B.

This problem is in NP.

A direct reduction from 3-SAT proves NP-hardness under a much stronger restriction: the union of **all possible implication edges** is a disjoint union of directed paths of length three.

For clause

`C_j=(l_1 OR l_2 OR l_3)`

create

`c_0 -> c_1 -> c_2 -> c_3`,

require c_0, and block c_3.

For Boolean variable x_i, its two seed choices mean false/true. Put clause edge r into exactly the seed that **falsifies** literal l_r.

Then c_3 is reachable exactly when all three literals are false. Hence all blocked endpoints are unreachable exactly when the 3-CNF formula is satisfiable.

Consequences of the construction:

- exactly two seeds per class suffice;
- all blocked states are fixed independently of seed choice;
- every selected implication graph is acyclic;
- every path has depth at most three;
- hardness comes from one seed choice controlling many literal occurrences, not from graph topology.

## S4 — inner ground: global synchronization is the hard resource

A single seed class is only Horn closure.

The first hard operation is **reusing one binary choice across many otherwise independent Horn paths**.

A satisfying literal cuts one edge of its clause's path to failure. The same variable choice determines which occurrence-edges are cut in every clause containing that variable.

So the complexity source is global synchronization of local implication rules.

This explains why further generic Horn simplification is unlikely to remove the exponential frontier: the remaining disjunction is shared across many observations by controller coherence.

## S5 — classical switching-graph prior-art correction

Groote and Ploeger study switching graphs, where Boolean switch settings select graph branches. Their 2008 paper proves NP-completeness of connection and disconnection problems for one global switch setting and connects the formalism to Boolean equation systems, modal mu-calculus model checking, and parity games.

Sources:

- J. F. Groote and B. Ploeger, *Switching Graphs*, Electronic Notes in Theoretical Computer Science 223 (2008), 119–135, DOI `10.1016/j.entcs.2008.12.035`.
- expanded journal version, International Journal of Foundations of Computer Science 20(5) (2009), 869–886, DOI `10.1142/S0129054109006930`.

Therefore OrbitSynthesis should **not** claim binary switched disconnection NP-completeness itself as novel.

The useful result is the exact derivation

`pointed algebraic controller classes -> seed rules -> switched implication graph`,

which lets us import switching-graph algorithms/lower bounds while retaining algebraic controller reconstruction and replayable nogood certificates.

## S6 — exact bounded validation

A standalone checker was run before this update.

### One-seed calibration

On a three-state universe it exhausts:

- all `2^9=512` directed edge sets;
- all 8 blocked sets;
- all 8 required sets.

Total: `32,768` cases.

For every case, brute domain enumeration agrees with:

- required feasibility by forward reachability;
- greatest domain by complement of reverse reachability to blocked states.

### Binary-seed calibration

The checker compares brute SAT with switched seed-rule feasibility for:

- all 256 subsets of the eight sign-pattern clauses on `(x1,x2,x3)`;
- 1,600 deterministic random 3-CNF instances with 1–8 variables.

Zero mismatches.

Deterministic receipt:

`9c8f45de43b0c7e24b349494bb48b2d53b520f78b9f854ab17a2559e99767a73`.

These computations calibrate the proofs; they are not the proofs.

## S7 — solver dispatch consequence

The compiled domain solver should expose at least:

- number of multi-seed classes;
- maximum seed width;
- class/implication-component incidence structure;
- number of switch-controlled edges;
- fixed implication SCC structure.

Dispatch:

1. **all width one:** graph reachability/SCC solver;
2. **s multi-seed classes:** exact enumeration is `product_i |C_i|` graph closures, binary `2^s poly(input)`;
3. **general switched case:** current nogood/bitset search or SAT/CSP backend.

Raw seed width is not enough for a useful dichotomy because width two is already hard.

## S8 — new frontier: interaction width

The next promising structural parameter is an incidence graph linking

- multi-seed classes, and
- implication components / state obligations they can modify.

High-value questions:

1. Is binary seed-rule feasibility polynomial when this incidence graph is a forest?
2. Is it FPT for bounded incidence treewidth?
3. Can learned domain nogoods be interpreted as switched-path cut certificates and reused via graph separators?
4. Can stronger parameter cores provably collapse enough classes to width one to cross from switched search to pure graph closure?
5. Which abstract switched seed-rule instances are actually realizable by pointed quasi-primal controller kernels?

The last question is essential: abstract seed-rule hardness does not by itself prove the same lower bound for every algebraically generated instance family.

## Tool/literature receipt

- Consensus was queried again on this frontier but the connected account's monthly 30-search quota is exhausted until September 1.
- Kurate public search was used as triage; no candidate was promoted as evidence.
- CNKI's web-indexed international surface returned no directly relevant result for the targeted term-interpolation/switching-graph queries; this is a retrieval limitation, not evidence of absence.
- Morph's abstraction recipe directly motivated the representation shift from disjunctions-of-Horn-rules to globally switched reachability.
- Research Kernel's fail-closed posture is retained: this update labels only the finite-calibrated and directly derived statements; no novelty claim is promoted from negative searches.
