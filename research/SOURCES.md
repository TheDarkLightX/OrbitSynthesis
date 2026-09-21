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

## Quasi-primal interpolation and discriminator algebras

17. Alden F. Pixley, **The Ternary Discriminator Function in Universal Algebra**, *Mathematische Annalen* 191 (1971), 167–180.
    https://eudml.org/doc/162131

    Used for: the classical discriminator/quasi-primal characterization underlying semantic term existence. OrbitSynthesis does not claim this theorem.

18. Alden F. Pixley, **Functionally Complete Algebras Generating Distributive and Permutable Classes**, *Mathematische Zeitschrift* 114 (1970), 361–372.
    https://eudml.org/doc/171324

    Used for: the classical functional-completeness and quasi-primal background.

19. Kirby A. Baker and Alden F. Pixley, **Polynomial Interpolation and the Chinese Remainder Theorem for Algebraic Systems**, *Mathematische Zeitschrift* 143 (1975), 165–174.
    https://eudml.org/doc/172222

    Used for: the classical finite-algebra interpolation boundary. A fixed-domain interpolation corollary is not treated as publication novelty.

20. Robert W. Quackenbusch, **Demi-Semi-Primal Algebras and Mal'cev-Type Conditions**, *Mathematische Zeitschrift* 122 (1971), 166–176.
    https://eudml.org/doc/171592

    Used for: the extendable-internal-isomorphism hierarchy and the positive/negative structural boundary. The spelling follows the bibliographic record.

21. Wolfgang Poiger, **Semi-Primal Varieties: A View through the Lens of Duality Theory** (doctoral thesis, University of Luxembourg, 2024).
    https://orbilu.uni.lu/bitstream/10993/61640/1/Wolfgang_Poiger_Thesis.pdf

    Used for: a current source map and precise modern statements of quasi-primal, semi-primal, and discriminator results; not a substitute for the original sources above.

## Safety games, permissiveness, and antichains

22. Julien Bernet, David Janin, Igor Walukiewicz, **Permissive Strategies: From Parity Games to Safety Games**, *RAIRO – Theoretical Informatics and Applications* 36(3) (2002), 261–275.
    https://eudml.org/doc/244731

    Used for: the strategy-permissiveness comparison and the fact that “one strategy subsuming all behavior” is a distinct issue. It does not study term-clone-constrained domains.

23. Gilles Geeraerts, Joël Goossens, Amélie Stainer, **Synthesising Succinct Strategies in Safety Games with an Application to Real-Time Scheduling**, *Theoretical Computer Science* 735 (2018), 24–49. DOI: 10.1016/j.tcs.2017.06.004.
    https://doi.org/10.1016/j.tcs.2017.06.004

    Used for: established antichain/succinct-strategy techniques in ordinary safety games. These are adjacent prior art, not the claimed new object.

24. Stanly Samuel, Deepak D'Souza, Raghavan Komondoor, **GenSys: A Scalable Fixed-Point Engine for Maximal Controller Synthesis over Infinite State Spaces**, ESEC/FSE 2021 Demonstrations. DOI: 10.1145/3468264.3473126.
    https://doi.org/10.1145/3468264.3473126

    Used for: the conventional greatest-fixed-point/maximal-controller baseline in logically specified safety games.

## Complexity of constrained strategies and algebraic equations

25. Yackolley Amoussou-Guenou, Souheib Baarir, Maria Potop-Butucaru, Nathalie Sznajder, Léo Tible, Sébastien Tixeuil, **On the Encoding and Solving of Partial Information Games**, *Networked Systems*, LNCS 12635 (2021), 60–76. DOI: 10.1007/978-3-030-67087-0_5.
    https://doi.org/10.1007/978-3-030-67087-0_5

    Used for: the closest located game-synthesis hardness analogue. It proves NP-completeness for memoryless strategies in partial-information reachability games using a 3-SAT clause/literal construction. OrbitSynthesis's fixed-quasi-primal safety proof must be positioned as a distinct algebraic embedding/adaptation, not as invention of the clause/literal pattern.

26. Peter Mayr, **On the Complexity Dichotomy for the Satisfiability of Systems of Term Equations over Finite Algebras**, MFCS 2023, LIPIcs 272:66. DOI: 10.4230/LIPIcs.MFCS.2023.66.
    https://doi.org/10.4230/LIPIcs.MFCS.2023.66

    Used for: the modern fixed-algebra `SysTerm(A)` complexity boundary. Its variables range over algebra elements in supplied term equations; it is adjacent to, but different from, synthesizing a term operation and invariant domain.

27. László Zádori, **On solvability of systems of polynomial equations**, *Algebra Universalis* 65 (2011), 277–283. DOI: 10.1007/s00012-011-0128-1.
    https://doi.org/10.1007/s00012-011-0128-1

    Used for: fixed-finite-algebra `SysPol(A)` dichotomy context. Polynomial-equation satisfiability should not be conflated with term-controller synthesis.

## Conservative operations, discriminator clones, and circuit counting

28. Erkko Lehtonen and Ágnes Szendrei, **Equivalence of operations with respect to discriminator clones**, *Discrete Mathematics* 309 (2009), 673–685. DOI: 10.1016/j.disc.2008.01.003.
    https://arxiv.org/abs/0706.0195

    Used for: modern discriminator-clone structure and minor-equivalence context. It does not state the fixed-`Q` conservative-operation count or the OrbitSynthesis compiler bound in its abstract; a full-text comparison remains required.

29. Johannes Greiner, **Generating clones with conservative near-unanimity operation** (2015 preprint; later journal publication).
    https://arxiv.org/abs/1503.07986

    Used for: adjacent conservative-clone generation and Baker–Pixley arity-bound context. It asks how high an arity is needed to generate a clone containing a conservative near-unanimity operation, not how many conservative operations occur in this fixed discriminator algebra.

30. Erhard Aichinger, Mike Behrisch, and Bernardo Rossi, **On when the union of two algebraic sets is algebraic**, *Aequationes Mathematicae* (2024/2025). DOI: 10.1007/s00010-024-01041-9.
    https://arxiv.org/abs/2309.00478

    Used for: current term-equation geometry on two- and three-element algebras and nearby Boolean clone terminology. It is contextual prior art, not evidence for the fixed-`Q` counting formula.

31. Claude E. Shannon, **The Synthesis of Two-Terminal Switching Circuits**, *Bell System Technical Journal* 28 (1949).
    https://www.nokia.com/bell-labs/publications-and-media/publications/the-synthesis-of-two-terminal-switching-circuits/

    Used for: classical counting-versus-synthesis methodology. The OrbitSynthesis DAG lower bound is not claimed as a new counting paradigm.

## Local coding and multivalued Shannon complexity

32. O. B. Lupanov, **On the principle of local coding and the realization of functions in a certain class of networks composed of functional elements**, *Doklady Akademii Nauk SSSR* 140(2) (1961), 322–325.
    https://www.mathnet.ru/eng/dan25510

    Used for: primary provenance of the local-coding principle. The block-library idea in the fixed-`Q` compiler is explicitly treated as a classical Lupanov-style specialization, not a new synthesis paradigm.

33. O. B. Lupanov, **Asymptotic Estimates of the Complexity of Control Systems**, 2nd ed., Moscow University Press (2024; first edition 1984), ISBN 978-5-19-011976-3.
    https://msupress.com/en/catalogue/books/book/asimptoticheskie-otsenki-slozhnosti-upravlyayushchikh-sistem/

    Used for: a modern publisher-confirmed map of Shannon synthesis, asymptotically best methods, cascade methods, and examples of local coding. It does not establish that the present fixed conservative clone specialization is new.

34. S. V. Yablonskii, **Functional constructions in a k-valued logic**, *Trudy Matematicheskogo Instituta imeni V. A. Steklova* 51 (1958), 5–142.
    https://www.mathnet.ru/eng/tm1275

    Used for: foundational `k`-valued functional-construction context. Any publication must compare the fixed-`Q` fragment against this literature rather than presenting multivalued synthesis as a new setting.

35. V. A. Orlov, **Complexity of implementing functions of k-valued logic by circuits and formulas in functionally complete bases**, *Discrete Applied Mathematics* 135(1–3) (2004), 223–233. DOI: 10.1016/S0166-218X(02)00306-2.
    https://doi.org/10.1016/S0166-218X(02)00306-2

    Used for: directly adjacent multivalued Shannon-function and circuit/formula complexity. Its stated scope is functionally complete bases; the parameter-free `Q` basis studied here preserves `{0,1}` and is not functionally complete. Full-text comparison is still required because the fixed-fragment theorem may be an expected specialization of broader methods.

36. A. V. Kochergin, **On the Depth of k-Valued Logic Functions Over Arbitrary Bases**, *Journal of Mathematical Sciences* 233(1) (2018), 100–102. DOI: 10.1007/s10958-018-3927-5.
    https://doi.org/10.1007/s10958-018-3927-5

    Used for: direct prior-art pressure on the depth lane. The paper establishes linear asymptotic Shannon depth for `k`-valued functions over arbitrary complete finite bases. OrbitSynthesis's parameter-free basis is incomplete, so applicability is not automatic; nevertheless, linear depth itself must not be framed as a new general phenomenon.

37. A. D. Korshunov, **Computational complexity of Boolean functions**, *Russian Mathematical Surveys* 67(1) (2012), 93–165. DOI: 10.1070/RM2012v067n01ABEH004777.
    https://www.mathnet.ru/eng/rm9459

    Used for: a primary survey map of Lupanov local coding, minimal reduced weight, Shannon effects, partial functions, formulas, and circuit depth. It confirms that exact leading coefficients and simultaneous synthesis questions belong to a mature basis-sensitive literature.

38. R. F. Safin, **On a relation between depth and complexity in precomplete classes of k-valued logic**, *Mathematical Problems of Cybernetics* 13 (2004), 223–278 [Russian].
    https://keldysh.ru/papers/2004/mvk/mvk2004_223.pdf

    Used for: directly adjacent multivalued formula parallelization inside precomplete classes. It raises the prior-art bar for depth-versus-size claims but does not, from the inspected public statement, give the fixed parameter-free `Q` term-DAG construction or its same-DAG `4r` accounting.

39. S. A. Lozhkin, **On synthesis of formulas whose complexity and depth do not exceed asymptotically best estimates of high accuracy**, *Moscow University Mathematics Bulletin* 62(3) (2007), 93–100.
    https://www.mathnet.ru/eng/vmumm1048

    Used for: Boolean prior art on simultaneously approaching the relevant Shannon functions for size and depth. The model is the standard complete Boolean basis, not the incomplete conservative clone studied here.

40. O. M. Kasim-Zade, **On the depth of Boolean functions realized by circuits over an arbitrary basis**, *Moscow University Mathematics Bulletin* 62(1) (2007), 15–18.
    https://www.mathnet.ru/eng/vmumm1019

    Used for: the general Boolean depth-order trichotomy and the fact that finite bases have linear Shannon-depth order. It is methodology and prior-art pressure, not direct support for the local coefficient.

## Chinese public-index adjacency

41. 纪堉超, 常胜, 王豪, 何进, 黄启俊, **基于隧穿二极管的集约三值全加器设计**, *微纳电子技术* 53(6) (2016), 353–359. DOI: 10.13250/j.cnki.wndz.2016.06.001.
    https://bdtq.cbpt.cnki.net/portal/journal/portal/client/paper/77f77209a3deca86831eda4c0cdf20a5

    Used for: a Chinese-indexed physical ternary-circuit adjacency returned by the multivalued-complexity search. It optimizes a concrete RTD full adder and is not a fixed-clone Shannon-complexity result.

42. 凌灿红, 常亮, 周洁, 潘海玉, **多值交互时序逻辑的模型检验研究**, *郑州大学学报（理学版）* 57(2), 78–84. DOI: 10.13705/j.issn.1671-6841.2023192.
    https://zzdz.cbpt.cnki.net/portal/journal/portal/client/paper/e7532d60e1d26b3c36a2d1f2726e2c49

    Used for: Chinese-indexed multivalued reactive/model-checking adjacency. It studies polynomial-time model checking, not original-signature term-DAG synthesis or the conservative `Q` fragment.

## Multiplexer and ternary-synthesis depth adjacency

43. S. A. Lozhkin, **On the Depth of a Multiplexer Function with a Small Number of Select Lines**, *Mathematical Notes* 115(5) (2024), 748–754. DOI: 10.1134/S0001434624050092; Russian original DOI: 10.4213/mzm14190.
    https://www.mathnet.ru/eng/mzm14190

    Used for: direct evidence that exact multiplexer formula depth is a mature, basis-sensitive topic. The paper works in the standard Boolean basis and does not establish the branch-scoped `Q`-router identity or the incomplete-clone coefficient-three compiler.

44. 吴训威, 陈偕雄, **具有三轨输出的三值触发器及其在三值时序电路中的应用**, *中国科学 A辑* 1985(7), 643–653.
    https://www.sciengine.com/doi/pdf/39cfd4607c82435d895d35165b3b28c0

    Used for: Chinese-language ternary functional-decomposition adjacency. Its displayed variable-by-variable expansion uses closure, min, and max operations for a different ternary algebra and physical-circuit objective; it is not the fixed `Q=(Q;d,u)` construction.

45. 徐明强, 管致锦, 张海豹, **基于最小混乱度的三值可逆逻辑综合算法**, *电子学报* 41(7) (2013), 1352–1357. DOI: 10.3969/j.issn.0372-2112.2013.07.017.
    https://sns.wanfangdata.com.cn/sns/perio/dianzixb/?isSync=0&issueNum=07&page=2&publishYear=2013&tabId=article

    Used for: Chinese-indexed ternary synthesis adjacency. It optimizes reversible gate networks using truth-table disorder measures; its gate model, reversibility constraint, and cost objective differ from parameter-free conservative `Q`-term DAG depth.

46. Nagisa Ishiura, **Synthesis of Multilevel Logic Circuits from Binary Decision Diagrams**, *IEICE Transactions on Information* E76-D(9) (1993), 1085–1092.
    https://globals.ieice.org/en_transactions/information/10.1587/e76-d_9_1085/_p

    Used for: primary two-rail logic-synthesis adjacency. It constructs two-rail-input/two-rail-output circuits from BDDs under a different basis, semantic class, and depth objective. It prevents treating parallel rail representation as a new general technique but does not establish the fixed-`Q` R9 theorem.

47. John Backes, **Algorithms and Data Structures for Logic Synthesis and Verification**, Ph.D. dissertation, University of Minnesota (2013).
    https://loonwerks.com/publications/pdf/backes2013phd.pdf

    Used for: primary dissertation evidence that dual-rail encodings of ternary semantic values occur in circuit transformation and verification. The encoding convention and objective differ from the anchored `Q`-term compiler; it is adjacency, not theorem support or novelty refutation.

48. Zhaoliang Lu, Wei Fan, and Wenyao Yang, **Optimization of Ternary FPRM Circuit Synthesis Based on IWBA Algorithm**, *Journal of East China University of Science and Technology (Natural Science Edition)*, DOI 10.14135/j.cnki.1006-3080.20170204001.
    https://journal.ecust.edu.cn/article/doi/10.14135/j.cnki.1006-3080.20170204001

    Used for: Chinese-journal ternary circuit-synthesis adjacency returned by the refreshed search. It optimizes FPRM delay and area after converting binary benchmarks to ternary circuits, not parameter-free discriminator-term DAGs or their Shannon depth.

## Search-tool provenance for bootstrap / current tranche

- Research Kernel, Morph, and LEAP were exposed and used in the 2026-08-13 tranche. Their run/candidate identifiers are recorded in the theorem note. They organize hypotheses, propose reformulations, or falsify abstractions; none is treated as proof authority.
- Consensus: attempted, but the monthly search quota was exhausted; no claim relies on an unseen Consensus result.
- Kurate: requests failed remotely; no claim is attributed to Kurate.
- Chinese-language search: English and Chinese query variants were run through public web indexes with CNKI, Wanfang, SciEngine, `mathjournals.cn`, CQVIP, Peking University journal pages, and terms including `保守运算`, `判别函数`, `克隆`, `拟素代数`, `项运算`, `多值逻辑`, `二进制编码`, `多路选择器`, `电路复杂度`, `Shannon函数`, `深度`, and `局部编码`. Results 41–42, 44–48 are representative adjacent hits; no direct match was retrieved for the fixed-`Q` count, `Theta(3^r/r)` compiler, R9 router, or coefficient-`3/2` theorem. This is incomplete negative evidence because native-database coverage and terminology remain unresolved.
- TheoremSearch retrieval-only attempts for the count/compiler failed locally with network errors. A proposed external query containing the unpublished theorem shape was rejected at the approval boundary and was not retried. Failure receipts are preserved under `runs/theoremsearch_conservative_q_terms/`; earlier initial-safety retrieval receipts remain under `runs/theoremsearch_q_term_initial_safety/`. None is theorem or novelty evidence.
- Research Kernel retrieval exposed the existing Pixley source atom and earlier local hypotheses, but the durable graph predates the optimized compiler, exact count, and local-coding result. A generic public-literature retrieval on 2026-08-13 found no direct Lupanov atom in that graph. No write was attempted after the approval boundary had rejected publishing unpublished theorem-shaped payloads to that service; current local receipts and notes remain authoritative for this tranche.
