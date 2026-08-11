# Negative knowledge

This file prevents attractive but unsupported ideas from silently becoming project assumptions.

## NK-001 — "Orbit-Nerode is the frontier"

**Status:** REJECTED AS CURRENT CLAIM.

Recent register-automata work makes Myhill-Nerode-style minimization an interesting analogy, but we have not proved that a corresponding canonical/minimal object exists for reactive synthesis. Keep it as conjecture C6 only.

## NK-002 — "independently checkable certificates are demanded by the Tau/Asor frontier"

**Status:** REJECTED.

Certificates may later be useful engineering, but they did not emerge from the literature frontier analyzed here and are not part of the mathematical thesis.

## NK-003 — "omega-categoricity is the general reason infinite-data synthesis is decidable"

**Status:** REFUTED AS A NECESSITY CLAIM.

CSL 2026 obtains register-bounded synthesis for `(N,<)` and other domains through effective omega-regular satisfiability/approximability. `(N,<)` is not omega-categorical. Therefore omega-categoricity is one sufficient finiteness mechanism, not the unique one.

## NK-004 — "type enumeration can always be avoided"

**Status:** REFUTED IN WORST CASE BY THE SOURCE CONSTRUCTION.

Asor's ocLTL §5.2 explicitly notes that the data predicates can generate the full Boolean algebra of `T_3`; in that worst case the complete type distinctions are genuinely present. Research should seek structural/parameterized improvements, not promise universal compression.

## NK-005 — "fixed-point elimination implies efficient fixed-point computation"

**Status:** FALSE IMPLICATION.

Omega-categoricity gives a finite semantic lattice and therefore termination/FO definability. Formula substitution plus quantifier elimination can still cause severe expression blowup. Efficiency must be measured/proved separately.

## NK-006 — "the ABA type-count formula is novel"

**Status:** NOT CLAIMED.

`|T_k|=2^(2^k)-1` is a baseline derivation from standard minterm structure plus quantifier elimination. Its value here is that it makes the ocLTL type space explicit and yields exact restriction/extension combinatorics.

## NK-007 — "feature quotient = globally minimal synthesis quotient"

**Status:** NOT ESTABLISHED.

The feature map built from input restriction, successor-memory type, and Delta truth vector is intended to capture the information used by Asor's specific reduction. Even if sufficient there, it does not establish global minimality among all implementations or strategies.

## NK-008 — "finite computational agreement is a proof"

**Status:** REJECTED.

Exhaustive search is authoritative only for the finite domain actually exhausted. It may falsify universal conjectures by counterexample and can prove explicitly finite statements, but agreement on small k does not prove an all-k model-theoretic theorem.

## NK-009 — tool availability during bootstrap

Consensus search quota was exhausted and Kurate timed out in the bootstrap session. Lean, Julia, ESSO, and LEAP executables were not present in the execution container. No result is labeled as coming from those tools, and no theorem is called machine-checked.

## NK-010 — "the 79-state ABA ocLTL fiber needs only seven ordinary equation predicates"

**Status:** REFUTED.

Seven is only the unrestricted information-theoretic threshold for **arbitrary definable predicates**. An atomic Boolean equation/inequation is structurally constrained: after minterm expansion its truth bit is an empty/nonempty intersection test on the unknown support.

The 79-state hardest fiber contains the full 8-cell support `U` and every co-atom `U\{v}`. Distinguishing `U` from `U\{v}` by an intersection query forces the singleton query `{v}`. Therefore all eight singleton tests are individually necessary, even adaptively.

Correct statement:

- arbitrary definable predicates: 7 bits are necessary and sufficient in principle;
- atomic BA zero/nonzero equations: exactly 8 tests are necessary and sufficient.

## NK-011 — "projection information should reduce the number of atomic tests needed to recover a full fine type"

**Status:** REFUTED FOR EVERY NONDEGENERATE ABA PROJECTION FIBER.

For a projection fiber with block-support sizes `r_1,...,r_b`, if at least two `r_i>1`, the fiber contains the complete multipartite edge set and every one-edge deletion. Hence every fine-cell singleton test is forced.

Exact atomic-test complexity is `product_i r_i`, the number of fine cells.

## NK-012 — "NP-hard generalized group testing makes the ABA special case hopeless"

**Status:** REJECTED.

Minimum atomic-predicate selection for arbitrary candidate families inherits NP-hardness from generalized group testing. ABA restriction/extension fibers are structured enough to admit exact theorems. Exploit Tau-generated structure instead of solving arbitrary test-cover instances.

## NK-013 — "a compact BDD for the ABA extension relation means symbolic QE is efficient"

**Status:** FALSE IMPLICATION.

The ABA extension relation has an exceptionally compact ROBDD under a natural ordering. Arbitrary specification/fixed-point functions may still have exponential BDD size. Quantifier abstraction can still blow up. Efficiency remains class- and representation-dependent.

## NK-014 — "the raw number of interpreted constants is the right complexity parameter"

**Status:** REJECTED.

The relevant semantic parameter is `rho(C)`, the number of nonzero regions in the finite Boolean subalgebra generated by the constants actually used. It can be exponentially smaller than `2^|C|` for nested/disjoint/partition-like constants.

## NK-015 — "support Booleanization only works for the pure ABA signature"

**Status:** REFUTED BY DERIVATION.

Refine support cells by the finite constant partition. Atomic Boolean functions with interpreted coefficients still reduce to support-bit conditions and the extension geometry remains local. The remaining issue is the cost of constructing/representing that partition.

## NK-016 — "Tau does not already use BDD/Boole decomposition"

**Status:** REFUTED BY SOURCE INSPECTION.

At inspected Tau commit `fd137e860b60083b36f9159ec8090cb1a3c3cb5a`, the anti-prenex quantifier-elimination path explicitly performs Boole/Shannon decomposition and describes whole atomic formulas as BDD variables, with multiple fast paths and fallback handling.

Therefore "use BDDs in Tau" is not a research contribution. The support proposal is different only if it exploits the **lower-level ABA Venn-support coordinates and exact extension geometry** before generic formula-atom splitting.

## NK-017 — "one inequation preserves the equation-only principal-ideal winning regions"

**Status:** REFUTED BY MINIMAL COUNTEREXAMPLE.

For one BA state variable, static safety condition `s!=0` accepts supports `{1}` and `{0,1}` but rejects `{0}`. No region of the form `Supp(s) subseteq A` has this behavior.

The correct carrier is an allowed set plus hit constraints / an upward-closed support family.

## NK-018 — "inclusion-minimal hit sets alone are a canonical representation"

**Status:** FALSE WITHOUT THE NONEMPTY-SUPPORT CONVENTION.

Whole-fixed-point differential testing found the case `H=A`: hitting the whole allowed set is tautological because complete ABA supports are never empty. Retaining it preserves semantics but breaks structural canonical equality.

Correct canonicalization must also delete `H=A`. Standard hypergraph blocker duality can be recovered by adding A back only as an **implicit nonemptiness edge** during the dualization operation.

This bug was found before paper promotion; repository notes and checker were corrected.

## NK-019 — "few inequations imply a small hypergraph fixed point"

**Status:** REFUTED STRONGLY.

There are normalized ABA safety games with **one transition inequation** whose canonical hit family reaches a maximum Sperner antichain of size

`binom(n,floor(n/2))`, `n=2^k`,

and the descending fixed-point sequence has that many strict refinements.

The construction realizes a monotone predecessor that cycles every middle-layer subset. Hence bounded inequation count alone gives no useful worst-case bound.

## NK-020 — "deterministic or input-free dynamics make one inequation easy"

**Status:** REFUTED.

For an input-free deterministic transition given by a permutation delta, hit propagation is `H -> delta^(-1)(H)`. Choosing delta of maximal permutation order and one hit set with full orbit forces Landau-function-many incomparable temporal obligations.

Thus even deterministic, input-free, one-inequation games can have superpolynomial orbit/fixed-point growth. The meaningful parameter is the eventual period/cycle structure, not the words "deterministic" or "input-free".

## NK-021 — "a primitive/mixing deterministic input graph helps preserve nontrivial inequation safety"

**Status:** THE OPPOSITE IS TRUE.

For deterministic outputs with adversarial inputs, hit propagation is the complement of exact-length reachability in the union transition graph. In a primitive strongly connected graph, sufficiently long exact paths connect every state to every state. Consequently every proper persistent hit set eventually propagates to the empty set, making the ABA safety game unrealizable.

Mixing is algorithmically simple here because it **destroys** persistent nontrivial support-witness obligations.

## NK-022 — "the direct clause backend is a worst-case complexity improvement over complete types"

**Status:** REJECTED.

The Sperner construction yields

`binom(2^k,2^(k-1)) = 2^(2^k-k/2+O(1))`

strict refinements, essentially the same double-exponential scale as the `2^(2^k)-1` complete ABA types up to a polynomial factor in the support-bit dimension.

The clause backend's defensible value is:

- exact semantic structure;
- direct strategy/witness extraction;
- parameterization by antichain/orbit/graph structure;
- avoiding unnecessary type enumeration on favorable instances.

Do not market it as a universal asymptotic collapse.
