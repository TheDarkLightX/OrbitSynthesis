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

Exact atomic-test complexity is

`product_i r_i`,

which is simply the number of fine cells. Projection information may greatly reduce the number of *candidate supports* while giving no worst-case reduction in the number of atomic tests required for complete identification.

This pushes the project away from "encode every complete type with a few atomic predicates" and toward direct symbolic operations on families of supports.

## NK-012 — "NP-hard generalized group testing makes the ABA special case hopeless"

**Status:** REJECTED.

Minimum atomic-predicate selection for an arbitrary explicitly listed candidate family inherits NP-hardness from generalized group testing. But ABA restriction/extension fibers are highly structured hypergraph families, and that structure already gave an exact closed-form optimum. The relevant research problem is to exploit Tau-generated structure, not solve arbitrary test-cover instances.

## NK-013 — "a compact BDD for the ABA extension relation means symbolic QE is efficient"

**Status:** FALSE IMPLICATION.

The one-variable ABA extension relation has an ROBDD of exactly `5*2^k` nonterminal nodes in the pure k-variable case, and `5*rho(C)*2^k` with a finite interpreted-constant partition. This proves the **relation** is compact under a natural ordering.

An arbitrary specification or fixed-point iterate can still have exponential BDD size in the number of support variables. Quantifier abstraction can still trigger blowup. Efficiency remains a formula-class / ordering / workload question.

## NK-014 — "the raw number of interpreted constants is the right complexity parameter"

**Status:** REJECTED.

For a finite set `C` of interpreted constants, the support/type geometry depends on `rho(C)`, the number of nonzero atoms of the finite Boolean subalgebra generated by those constants. `rho(C)` can be `2^|C|` in generic position but only `O(|C|)` for nested, disjoint, or partition-like families.

Any complexity model that ignores Boolean relations among the interpreted constants can overestimate the effective support dimension by an exponential factor.

## NK-015 — "support Booleanization only works for the pure ABA signature"

**Status:** REFUTED BY DERIVATION.

For any finite set of interpreted constants occurring in a formula, refine the support cells by the nonzero regions of the finite subalgebra generated by those constants. Atomic Boolean functions with interpreted coefficients reduce to zero/nonzero conditions on those refined support bits, and the local extension relation is unchanged.

The remaining caveat is computational: obtaining and representing the constant partition itself may be expensive when many independent constants occur.
