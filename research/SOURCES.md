# Source ledger

Sources are grouped by what claim they support. Prefer primary sources.

## Tau / Ohad Asor

1. Ohad Asor, **ocLTL: LTL Realizability and Synthesis Modulo omega-Categorical Structures** (2026). arXiv:2605.12539.  
   https://arxiv.org/abs/2605.12539

   Used for: complete-type reduction, effective presentation, bounded lookback, §5.2 avoidance of full `T_3`, orbit/type identity, fixed-point direction, stated IP caveat.

2. Ohad Asor, **Theories and Applications of Boolean Algebras**, version 0.29 (dated 2024-12-27).  
   https://tau.net/wp-content/uploads/2026/03/Theories-and-Applications-of-Boolean-Algebras-0.29.pdf

   Used for: Boolean minterms, atomless Boolean algebras, quantifier-elimination/decision-procedure context, GSSOTC/Tau background.

3. IDNI, **tau-lang** source repository.  
   https://github.com/IDNI/tau-lang

   Used for: implementation orientation and later differential testing. Do not infer theoretical limitations from a code search without reproducing them against a pinned commit.

## Infinite-data synthesis

4. Nino Dauvier, Emmanuel Filiot, Pierre-Alain Reynier, **Register-Bounded Synthesis from Constraint LTL**, CSL 2026, LIPIcs 363:8. DOI: 10.4230/LIPIcs.CSL.2026.8.  
   https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CSL.2026.8

   Used for: effective omega-regular satisfiability, completion, omega-regular approximability, 2ExpTime results for equality, `(Q,<)`, `(N,<)`, and partial observation.

5. Léo Exibard, Emmanuel Filiot, Ayrat Khalimov, **A Generic Solution to Register-bounded Synthesis with an Application to Discrete Orders**. arXiv:2205.01952.  
   https://arxiv.org/abs/2205.01952

   Used for: earlier generic register-bounded synthesis / regular-approximability line and discrete-order context.

## Infinite-alphabet automata / minimization

6. Mrudula Balachander, Emmanuel Filiot, Raffaella Gentilini, Nikos Tzevelekos, **Register Automata with Permutations**, MFCS 2025.  
   https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.MFCS.2025.14

   Used for: canonical/minimal permutation register automata, Myhill-Nerode-style equivalence, minimization/equivalence complexity. This source motivates but does not prove a synthesis analogue.

## Model-theoretic / orbit-growth context

7. Pierre Simon, **On omega-categorical structures with few finite substructures**, European Journal of Combinatorics 132 (2026) / earlier arXiv version.  
   https://arxiv.org/abs/1810.06531

   Used for: orbit-growth landscape and the fact that omega-categorical structures can have very different orbit-growth behavior.

## Lean infrastructure checked during bootstrap

8. Mathlib model theory / definability documentation.  
   https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Definability.html

9. Mathlib complete-type infrastructure.  
   https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Types.html

10. Mathlib finite powersets.  
    https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/Finset/Powerset.html

These show relevant infrastructure exists; they do **not** establish that ABA quantifier elimination is already formalized in mathlib.

## Search-tool provenance for bootstrap

- Consensus: attempted, but monthly search quota was exhausted; no bootstrap claim relies on an unseen Consensus result.
- Kurate: direct public fetch timed out in the session; no bootstrap claim is attributed to Kurate.
