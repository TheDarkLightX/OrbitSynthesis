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
