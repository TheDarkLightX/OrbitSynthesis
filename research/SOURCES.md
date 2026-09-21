# Source ledger

Sources are grouped by what claim they support. Prefer primary sources.

## Tau / Ohad Asor

1. Ohad Asor, **ocLTL: LTL Realizability and Synthesis Modulo omega-Categorical Structures** (2026). arXiv:2605.12539.  
   https://arxiv.org/abs/2605.12539

   Used for: complete-type reduction, effective presentation, bounded lookback, §5.2 avoidance of full `T_3`, orbit/type identity, fixed-point direction, stated IP caveat.

2. Ohad Asor, **Theories and Applications of Boolean Algebras**, version 0.29 (dated 2024-12-27).  
   https://tau.net/wp-content/uploads/2026/03/Theories-and-Applications-of-Boolean-Algebras-0.29.pdf

   Used for: Boolean minterms, atomless Boolean algebras, quantifier-elimination/decision-procedure context, GSSOTC/Tau background.

3. Ohad Asor, **Guarded Successor: A Novel Temporal Logic**. arXiv:2407.06214.  
   https://arxiv.org/abs/2407.06214

   Used for: the published GS presentation of Boolean-algebra quantifier elimination, in particular the DNF-first existential-elimination route against which support-level symbolic projection should be compared.

4. IDNI, **tau-lang** source repository.  
   https://github.com/IDNI/tau-lang

   Used for: implementation orientation and later differential testing. Do not infer theoretical limitations from a code search without reproducing them against a pinned commit.

## Infinite-data synthesis

5. Nino Dauvier, Emmanuel Filiot, Pierre-Alain Reynier, **Register-Bounded Synthesis from Constraint LTL**, CSL 2026, LIPIcs 363:8. DOI: 10.4230/LIPIcs.CSL.2026.8.  
   https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CSL.2026.8

   Used for: effective omega-regular satisfiability, completion, omega-regular approximability, 2ExpTime results for equality, `(Q,<)`, `(N,<)`, and partial observation.

6. Léo Exibard, Emmanuel Filiot, Ayrat Khalimov, **A Generic Solution to Register-bounded Synthesis with an Application to Discrete Orders**. arXiv:2205.01952.  
   https://arxiv.org/abs/2205.01952

   Used for: earlier generic register-bounded synthesis / regular-approximability line and discrete-order context.

## Infinite-alphabet automata / minimization

7. Mrudula Balachander, Emmanuel Filiot, Raffaella Gentilini, Nikos Tzevelekos, **Register Automata with Permutations**, MFCS 2025.  
   https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.MFCS.2025.14

   Used for: canonical/minimal permutation register automata, Myhill-Nerode-style equivalence, minimization/equivalence complexity. This source motivates but does not prove a synthesis analogue.

## Generalized group testing / Boolean OR codes

8. Mira Gonen, Michael Langberg, Alex Sprintson, **Group Testing on General Set-Systems**. arXiv:2202.04988 (2022).  
   https://arxiv.org/abs/2202.04988

   Used for: exact identification of a candidate set by empty/nonempty intersection tests, general NP-hardness of optimizing such test families, and structural parameters that permit smaller test sets. Atomic ABA zero/nonzero equations reduce exactly to this model after minterm expansion.

9. Nikita Goshkoder, Nikita Polyanskii, Ilya Vorobyev, **Efficient Combinatorial Group Testing: Bridging the Gap between Union-Free and Disjunctive Codes**. arXiv:2401.16540 (2024).  
   https://arxiv.org/abs/2401.16540

   Used for: separable / union-free code viewpoint in which a support's test outcome is the coordinatewise Boolean OR of the codewords of its elements.

## Symbolic fixed-point computation

10. Jerry R. Burch, Edmund M. Clarke, Kenneth L. McMillan, David L. Dill, L. James Hwang, **Symbolic model checking: 10^20 states and beyond**, LICS 1990.  
    https://lics.siglog.org/1990/BurchClarkeMcMillan-Symbolicmodelchecki.html

    Used for: the classical architecture of representing state sets/relations symbolically with BDDs and computing temporal fixed points without explicit state enumeration. OrbitSynthesis is testing whether ABA support Booleanization gives an especially compact symbolic relation for infinite-data synthesis.

## Problem-solving technique sources actually used

11. Terence Tao, **245A: Problem solving strategies** (2010).  
    https://terrytao.wordpress.com/2010/10/21/245a-problem-solving-strategies/

    Used methodologically for: simpler cases, counterexample construction, abstraction, symmetry reduction, generators/closure, and deliberately changing the problem representation when the original formulation hides the mechanism.

12. Timothy Gowers, **Dimension arguments in combinatorics** (2008).  
    https://gowers.wordpress.com/2008/07/31/dimension-arguments-in-combinatorics/

    Used methodologically for: recasting set systems as algebraic/vector-like objects and screening whether a dimension/rank argument is genuinely appropriate. In the current co-atom lower bound it was rejected in favor of the stronger local forcing proof.

## Model-theoretic / orbit-growth context

13. Pierre Simon, **On omega-categorical structures with few finite substructures**, European Journal of Combinatorics 132 (2026) / earlier arXiv version.  
    https://arxiv.org/abs/1810.06531

    Used for: orbit-growth landscape and the fact that omega-categorical structures can have very different orbit-growth behavior.

## Lean infrastructure checked during bootstrap

14. Mathlib model theory / definability documentation.  
    https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Definability.html

15. Mathlib complete-type infrastructure.  
    https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Types.html

16. Mathlib finite powersets.  
    https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/Finset/Powerset.html

These show relevant infrastructure exists; they do **not** establish that ABA quantifier elimination is already formalized in mathlib.

## Search-tool provenance for bootstrap / current tranche

- Consensus: attempted, but monthly search quota was exhausted; no claim relies on an unseen Consensus result.
- Kurate: direct public fetch timed out in the bootstrap session; no claim is attributed to Kurate.
- The Research Kernel / Morph / LEAP connectors were not exposed in the current tool surface. Previously recorded tactics were applied explicitly and cross-checked against primary public expository sources rather than falsely attributing results to an unavailable connector.
