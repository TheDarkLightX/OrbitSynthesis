# Bounded primary-source prior-art map: signed discriminator routers

Date: 2026-08-13

Status: **`NO EXACT MATCH VERIFIED; NOVELTY AND FTO UNKNOWN`**

This is a bounded mathematical-literature search, not a novelty opinion, patent
search, freedom-to-operate analysis, or claim that an uncited construction is
new. A failure to retrieve a paper is not evidence that no paper exists.

## 1. Frozen comparison subject

The subject compared here is the conjunction of two frozen results, not any
single ingredient:

1. Over the Boolean slice of the ternary discriminator
   `d(x,y,z)=z if x=y, else x`, d-only full trees `P_h,N_h` have

   ```text
   q_h                    = 3^(h-1) programmable branch leaves,
   dependency depth       = h,
   programmable controls  = 2q_h,
   discriminator nodes    = (3^h-1)/2,
   ```

   and select either a requested branch or its Boolean complement by signed
   middle-edge polarity.

2. Conditional on that family and the already stated representation bridges,
   the repaired residual-first compiler uses the original signature on
   `Q={0,1,2}`, charges both Boolean planes and all address controls, shares
   controls at a level, decodes once, includes the binary branch and anchor,
   and obtains one circuit DAG with

   ```text
   size  = O(3^r/r),
   depth = r+O(sqrt(r)).
   ```

The literature models below differ in alphabet, basis, constants, fan-in,
single- versus multi-output semantics, uniformity, or complexity measure. Those
differences are not cosmetic; an exact collision requires a translation proof.

## 2. Bottom line

No accessible primary source in this bounded search states the exact combined
package above. That is **not novelty evidence**. Several parts are already
classical or sit directly beside strong prior art:

- The `3^r/r` order is the ternary-shaped analogue of the classical
  Shannon--Lupanov circuit scale. Lupanov's synthesis and local-coding ideas,
  and later basis-sensitive Shannon-function work, make an unqualified claim
  to that size order unsafe.
- Linear worst-case depth for arbitrary functions over finite many-valued
  complete bases is already a theorem shape in Kochergin's work. Whether its
  basis constant or construction subsumes coefficient one for the exact
  no-nullary signature `{d,u}` is unresolved here.
- The discriminator operation and its equivalence to switching terms are
  classical universal algebra. Recursive selection with a discriminator should
  not be presented as a new primitive idea.
- Sharp size and depth results for ordinary multiplexers, programmable
  universal circuits, ternary decision diagrams, shared BDDs, and
  multi-selection circuits occupy all neighboring models.

Accordingly, the only defensible candidate discriminator for later expert
review is the **exact conjunction**: the signed `P_h/N_h` recurrence and counts,
the fixed original signature and no-free-control rules, and a simultaneous
same-DAG `O(3^r/r)` / `r+O(sqrt(r))` compiler after residual-first accounting.

## 3. Theorem-shape comparison table

| Primary source | Verified theorem/model | Overlap with frozen subject | Material mismatch / present verdict |
|---|---|---|---|
| O. B. Lupanov, [“A method of circuit synthesis”](https://radiophysics.unn.ru/issues/1958/1/120), *Izv. VUZ Radiofizika* 1(1), 120--140 (1958), no DOI located | Foundational synthesis of arbitrary Boolean functions by circuits. Later primary accounts attribute the asymptotic finite-basis circuit scale `rho_B 2^n/n` to this line of work. | Local-library decomposition and near-counting-bound circuit size are the closest classical ancestors of the compiler architecture. | Boolean rather than ternary, and this source was not found to state the frozen basis/depth conjunction. **High size-method collision risk.** |
| O. B. Lupanov, [“On the principle of local coding and the realization of functions in a certain class of networks composed of functional elements”](https://www.mathnet.ru/eng/dan25510), *Dokl. Akad. Nauk SSSR* 140(2), 322--325 (1961), no DOI located | A function/operator is encoded so that a short, possibly variable-length local code fragment determines its value on an input; the paper splits synthesis into finding the fragment coordinates, producing the fragment, and decoding it, and derives Shannon-function asymptotics for classes. | Very close conceptual shape to the frozen local library, address-derived program bits, shared selection, and one final decoder. | The inspected theorem is for Boolean operators/classes and does not give the signed discriminator family or frozen joint bound. **Highest method-level collision risk.** |
| S. A. Lozhkin, [“Refined bounds on Shannon's function for complexity of circuits of functional elements”](https://www.mathnet.ru/eng/vmumm4473), *Moscow Univ. Math. Bull.* 77(3), 144--153 (2022), [DOI 10.3103/S002713222203007X](https://doi.org/10.3103/S002713222203007X) | For an arbitrary complete finite Boolean basis `B` with reduced weight `rho_B`, the paper records `L_B^C(n) ~ rho_B 2^n/n` and gives closer upper/lower bounds; its construction explicitly uses a standard multiplexer and shared systems of universal remainder functions. | Confirms that near-Shannon size, local universal libraries, remainder functions, and MUX gluing are established circuit-synthesis machinery. | Boolean alphabet; no fixed ternary discriminator basis, two-plane legality ledger, or simultaneous coefficient-one depth theorem. **Direct size-order and architecture risk, not an exact match.** |
| V. A. Orlov, [“Realization of k-valued functions by circuits of functional elements”](https://www.mathnet.ru/eng/mzm1414), *Math. Notes* 64, 371--376 (1998), [DOI 10.1007/BF02314847](https://doi.org/10.1007/BF02314847) | Studies realization of functions in `P_k` by circuits over arbitrary bases. | The alphabet and arbitrary-basis circuit model are much closer than Boolean Lupanov synthesis. | Full theorem text/model translation was not retrievable in this run. Whether it already supplies the `k^r/r` order or a construction applicable to `{d,u}` is **UNKNOWN and a critical follow-up**. |
| V. A. Orlov, [“Complexity of implementing functions of k-valued logic by circuits and formulas in functionally complete bases”](https://www.sciencedirect.com/science/article/pii/S0166218X02003062), *Discrete Applied Mathematics* 135, 223--233 (2004), [DOI 10.1016/S0166-218X(02)00306-2](https://doi.org/10.1016/S0166-218X(02)00306-2) | Proves strong undecidability phenomena for exact Shannon asymptotics over functionally complete bases, while stating that the coefficient in the Shannon-function formula can be approximated arbitrarily well; also distinguishes circuit and formula constants. | Shows that basis-sensitive many-valued Shannon complexity is established prior art and that the exact basis constant is a substantive issue. | The accessible primary abstract does not expose the formula or coefficient for the frozen basis. The exact `O(3^r/r)` relationship to `{d,u}` remains **UNKNOWN**. |
| A. V. Kochergin, [“On the Depth of k-Valued Logic Functions Over Arbitrary Bases”](https://journals.rcsi.science/1072-3374/article/view/241525), *Journal of Mathematical Sciences* 233(1), 100--102 (2018), [DOI 10.1007/s10958-018-3927-5](https://doi.org/10.1007/s10958-018-3927-5) | For every `k>=3`, establishes asymptotic behavior of the Shannon depth function over arbitrary complete bases: linear for finite bases, and constant or logarithmic for infinite bases. | Directly places linear worst-case depth for arbitrary ternary functions in prior art. | The accessible abstract does not state the finite-basis coefficient `c_B`, exact gate/constant conventions, or a simultaneous near-Shannon-size construction. Whether `c_{d,u}=1` or the paper subsumes the frozen result is **UNKNOWN; highest depth risk**. |
| W. F. McColl and M. S. Paterson, [“The Depth of All Boolean Functions”](https://epubs.siam.org/doi/10.1137/0206026), *SIAM J. Comput.* 6(2), 373--380 (1977), [DOI 10.1137/0206026](https://doi.org/10.1137/0206026) | Every `n`-ary Boolean function has depth `n+1` over the basis of all binary Boolean functions. | An exact leading-one arbitrary-function depth result is classical in a richer Boolean basis. | Different alphabet and a vastly richer basis; the abstract does not impose near-Shannon size. **Coefficient-shape collision, not a fixed-basis collision.** |
| S. A. Lozhkin, [“On the Depth of a Multiplexer Function with a Small Number of Select Lines”](https://www.mathnet.ru/eng/mzm14190), *Math. Notes* 115(5), 748--754 (2024), [Russian DOI 10.4213/mzm14190](https://doi.org/10.4213/mzm14190), [English DOI 10.1134/S0001434624050092](https://doi.org/10.1134/S0001434624050092) | In the standard Boolean basis, exact multiplexer depth is `n+2` for `10<=n<=19`; together with prior results the paper states this for all `n>=10` and `2<=n<=5`. | The frozen router is a programmable selector, so exact MUX-depth work is a close comparator. | A standard MUX has `n` address bits and `2^n` data inputs and uses a different basis; the frozen controls are compiled functions, not free select pins. **Close selector-depth risk.** |
| S. A. Lozhkin and N. V. Vlasov, [“On Multiplexer Function Complexity in the pi-schemes Class”](https://dspace.kpfu.ru/xmlui/handle/net/27195), *Kazan Univ. Proc., Physics and Mathematics Series* 151(2), 98--106 (2009), no DOI located | Gives high-accuracy asymptotics for standard multiplexer complexity in the restricted pi-circuit model: `2^(n+1)+2^n/n +/- O(2^n/(n log n))`. | Sharp MUX size accounting is already a mature individual-synthesis problem. | Restricted Boolean pi-schemes, one fixed MUX function, and no ternary all-function compiler. Exact translation to the frozen DAG model is **UNKNOWN**. |
| P. Klein and M. S. Paterson, [“Asymptotically Optimal Circuit for a Storage Access Function”](https://doi.org/10.1109/TC.1980.1675657), *IEEE Trans. Computers* C-29(8), 737--738 (1980), [DOI 10.1109/TC.1980.1675657](https://doi.org/10.1109/TC.1980.1675657) | Classical asymptotically optimal circuit for the storage-access/multiplexer function. | A direct predecessor class for efficient programmable selection. | Full text was inaccessible, so exact gate basis, constant, and depth tradeoff were not independently extracted. **Relevant but theorem-level comparison UNKNOWN.** |
| L. G. Valiant, [“Universal circuits (Preliminary Report)”](https://doi.org/10.1145/800113.803649), STOC 1976, 196--203, [DOI 10.1145/800113.803649](https://doi.org/10.1145/800113.803649) | Constructs an acyclic Boolean circuit of size `O(s log s)` that simulates any Boolean circuit of size `s` after setting designated control inputs. | Establishes programmable control inputs and globally reusable universal routing as classical ideas. | It universalizes a circuit description of size `s`, not a truth table of an arbitrary ternary function under the frozen basis/size target. **Control-programming prior art, not an exact compiler.** |
| S. A. Cook and H. J. Hoover, [“A Depth-Universal Circuit”](https://epubs.siam.org/doi/10.1137/0214058), *SIAM J. Comput.* 14(4), 833--839 (1985), [DOI 10.1137/0214058](https://doi.org/10.1137/0214058) | `U(n,c,d)` simulates any Boolean size-`c`, depth-`d` circuit with depth `O(d)` and size `O(c^3 d/log c)`. | Closest generic evidence that programmability, size, and depth can be accounted jointly. | Different simulation objective and Boolean gate model; polynomial rather than Shannon-optimal overhead. **Adjacent universal-circuit result.** |
| A. F. Pixley, [“The Ternary Discriminator Function in Universal Algebra”](https://eudml.org/doc/162131), *Mathematische Annalen* 191, 167--180 (1971), [DOI 10.1007/BF01578706](https://doi.org/10.1007/BF01578706); M. Ramalho, [“Bounded lattice structured discriminator varieties”](https://ems.press/content/serial-article-files/44660), *Portugaliae Mathematica* 67(4), 485--509 (2010), [DOI 10.4171/PM/1874](https://doi.org/10.4171/PM/1874) | Pixley develops the ternary discriminator in universal algebra. Ramalho explicitly gives mutual term constructions between the ternary discriminator and a quaternary switching function. | Establishes that discriminator and switching-term theory belong to a long algebraic line. | Neither paper studies the signed `P_h/N_h` routing counts or the frozen size-depth compiler. **Primitive/concept collision; quantitative match not found.** |
| R. D. Berlin, [“Synthesis of N-Valued Switching Circuits”](https://doi.org/10.1109/TEC.1958.5222096), *IRE Trans. Electronic Computers* EC-7(1), 52--56 (1958), [DOI 10.1109/TEC.1958.5222096](https://doi.org/10.1109/TEC.1958.5222096); M. Yoeli and G. Rosenfeld, [“Logical Design of Ternary Switching Circuits”](https://doi.org/10.1109/PGEC.1965.264050), *IEEE Trans. Electronic Computers* EC-14(1), 19--29 (1965), [DOI 10.1109/PGEC.1965.264050](https://doi.org/10.1109/PGEC.1965.264050) | Early functionally complete `N`-valued switching synthesis and systematic ternary switching-circuit design/minimization. | Arbitrary multi-valued/ternary synthesis is not itself new territory. | Hardware/sum-of-products synthesis rather than the frozen asymptotic same-DAG theorem. Full texts were not available in this run. **Broad field prior art.** |
| C. K. Vudadha, A. Surya, S. Agrawal, and M. B. Srinivas, [“Synthesis of Ternary Logic Circuits Using 2:1 Multiplexers”](https://doi.org/10.1109/TCSI.2018.2838258), *IEEE Trans. Circuits and Systems I* 65(12), 4313--4325 (2018), [DOI 10.1109/TCSI.2018.2838258](https://doi.org/10.1109/TCSI.2018.2838258) | Transforms ternary functions into a ternary-transformed decision diagram and synthesizes them with 2:1 MUXes; reports benchmark transistor reductions. | Very close practical ternary decision-DAG/MUX synthesis lane. | Empirical hardware cost on benchmarks, not an all-function `O(3^r/r)` / coefficient-one depth theorem in `{d,u}`. **Practical architecture risk, asymptotic mismatch.** |
| J. Holmgren and R. Rothblum, [“Linear-Size Boolean Circuits for Multiselection”](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2024.11), CCC 2024, 11:1--11:20, [DOI 10.4230/LIPIcs.CCC.2024.11](https://doi.org/10.4230/LIPIcs.CCC.2024.11) | Selects `q` indexed bits from an `n`-bit string with size `O(n+q log^3 n)` and depth `O(log(n+q))`. | Strong same-DAG/multi-output evidence that shared selection can beat independent MUX replication. | Boolean data-routing problem with explicit indices, not arbitrary truth-table synthesis or the fixed discriminator basis. **Shared-routing comparator, not collision.** |

## 4. Chinese-language primary-source lane

The bounded Chinese search used combinations of `三值逻辑`, `多值逻辑`,
`判别函数`, `多路选择器`, `电路综合`, `共享BDD`, `多输出`, `香农函数`, and
`电路深度` across journal sites and indexed CNKI/Wanfang-facing pages. Two
directly relevant primary journal records were accessible:

| Primary source | Verified content | Comparison |
|---|---|---|
| 张会红, 陈治文, 汪鹏君 (Zhang Huihong, Chen Zhiwen, Wang Pengjun), [“二叉决策图映射电路的面积和延时优化 / Area and Delay Optimization of Binary Decision Diagrams Mapped Circuit”](https://jeit.ac.cn/cn/article/2019/3), *电子与信息学报 / Journal of Electronics & Information Technology* 41(3), 725--731 (2019), [DOI 10.11999/JEIT180443](https://doi.org/10.11999/JEIT180443), [official PDF](https://jeit.ac.cn/cn/article/pdf/preview/10.11999/JEIT180443.pdf) | Maps each BDD node to a 2:1 MUX, removes diamond structures, changes control variables through path optimization, and reports benchmark area/delay reductions. | Directly adjacent to selector-DAG sharing and control rewrites, but Boolean and empirical; no universal ternary size-depth theorem. |
| 何新华, 宫云战, 魏道政 (He Xinhua, Gong Yunzhan, Wei Daozheng), [“面向多输出电路的BDD拼接构造 / Multiple Output Circuit-Based BDD Analysis and Design”](https://jeit.ac.cn/article/id/85665992-ae08-49a4-83ca-1381a6d4735f), *电子与信息学报 / Journal of Electronics & Information Technology* 19(3), 356--360 (1997), no DOI shown | Builds BDDs recursively from primary inputs to outputs for multiple-output circuits; its keywords include nodes and sharing. | Prior art for recursive shared multi-output decision structures, but an analysis/verification construction rather than a Shannon-optimal compiler. |

These hits materially weaken any broad claim about shared MUX/BDD synthesis.
They do not establish or refute the exact frozen theorem. CNKI and Wanfang did
not provide complete queryable/full-text coverage in this run, so absence of a
Chinese exact match is **UNKNOWN**, not a negative result.

## 5. Ranked collision risks

1. **Many-valued Shannon complexity (highest).** Orlov's papers directly study
   arbitrary `k`-valued bases. Before any originality claim, their full proofs
   must be translated to the exact `{d,u}` basis and no-nullary convention.
2. **Many-valued depth.** Kochergin already proves linear depth asymptotics for
   finite complete `k`-valued bases. The decisive unresolved question is the
   exact constant and whether size and depth are achieved by the same DAG.
3. **Lupanov local coding.** The frozen program-control/local-library/decode
   architecture is close enough that any paper must clearly isolate what is not
   an instance of local coding or a standard remainder-function construction.
4. **Multiplexer individual synthesis.** Storage-access, pi-scheme, and exact
   depth results make selection-size/depth claims crowded even before ternary
   decision-diagram work is included.
5. **Discriminator and switching equivalence.** The primitive and switching
   interpretation are classical. Only the exact signed recursive capacity and
   charged compiler could potentially distinguish the work.
6. **Programmable and shared routing.** Valiant/Cook--Hoover universal circuits,
   Holmgren--Rothblum multiselection, and Chinese shared-BDD work all preclude a
   broad claim that global controls or same-DAG sharing are new.

## 6. Explicit UNKNOWNs and access gaps

- **Exact many-valued size theorem:** the full text and basis normalization in
  Orlov 1998/2004 were not accessible. It is unknown whether the ternary
  `3^r/r` order, an exact coefficient, or a directly convertible synthesis is
  already proved for a basis equivalent to `{d,u}`.
- **Exact many-valued depth coefficient:** Kochergin's accessible abstract gives
  linearity for finite bases but not `c_B`, the treatment of nullaries/weights,
  or joint size. Applicability with coefficient one is unknown.
- **Lupanov 1965 extension:** the cited monograph-length article “On an approach
  to the synthesis of control systems--the principle of local coding,”
  *Problemy Kibernetiki* 14 (1965), 31--110, was not retrieved in full.
- **Storage-access details:** Klein--Paterson 1980 was bibliographically verified
  but full theorem/model details were inaccessible.
- **Pi-scheme translation:** the Lozhkin--Vlasov primary paper was available,
  but no equivalence proof from pi-schemes to the frozen original-signature DAG
  model was attempted.
- **IEEE ternary sources:** Berlin, Yoeli--Rosenfeld, and Vudadha et al. were
  verified by exact publisher DOI/metadata, but paywall/robot access prevented a
  full theorem-by-theorem comparison.
- **Chinese coverage:** the official JEIT sources were accessible; exhaustive
  CNKI/Wanfang citation-chain and dissertation searching was not. This lane is
  incomplete.
- **Semantic retrieval:** the Research Kernel disclosure gate correctly blocked
  sending the unpublished exact theorem to an external semantic index. Generic
  public-vocabulary searches were low-signal, so an exact semantic-neighbor
  search remains unknown.
- **Formal theorem graph:** no formal-library/Lean theorem endpoint was
  available for this circuit-complexity literature; this does not affect the
  bibliographic map but leaves machine-linked theorem retrieval unknown.
- **Patents and FTO:** intentionally outside this search. Mathematical papers,
  even when close, neither establish nor clear patent claims, license duties,
  or copyright permissions.

## 7. Claim discipline and next checks

On this record, a draft should not claim as new:

- the ternary discriminator operation;
- interpreting a discriminator as a switch;
- recursive MUX/BDD routing;
- local coding, remainder libraries, or one-time decoding in general;
- programmable universal controls or same-DAG sharing;
- the bare `O(3^r/r)` order; or
- bare linear, or even leading-one in a richer basis, arbitrary-function depth.

A narrower mathematical claim might survive only after the following are done:

1. obtain and translate Orlov 1998/2004 and Kochergin 2013/2018, including their
   basis constants and constant/nullary conventions;
2. prove or refute a model-preserving reduction between their bases and
   `Q=({0,1,2};d,u)` with the frozen cost ledger;
3. search forward and backward citations from those papers, Lupanov local
   coding, and the Russian multiplexer series, including dissertations;
4. compare the exact signed recurrence `P_h=d(P,N,P)`, `N_h=d(N,P,N)` and its
   `q_h=3^(h-1)` capacity, rather than generic discriminator identities;
5. ask whether any prior construction achieves the size and coefficient-one
   depth **simultaneously on the same DAG**, with all controls compiled and the
   binary/nonbinary branches charged; and
6. conduct a separate counsel-led patent/FTO search if publication or product
   decisions require it.

Until those checks are complete, the honest prior-art verdict is:

> **No exact match verified in a bounded primary-source search; the component
> ideas and both asymptotic shapes are heavily prefigured, so originality of the
> combined fixed-signature result remains UNKNOWN.**
