# OrbitSynthesis research map — 2026-08-13

**Frozen research base:** recovered active branch `agent/frontier-program-v0` at `521038d3ddd342ca51ea73891255a537dd749ff8`, followed by the explicitly recorded local repairs and research artifacts in this tranche.

**Authority boundary:** this is a research-prioritization map, not a novelty opinion, patent analysis, legal advice, or publication claim.

## 1. Program spine

```text
classical finite algebra
  Pixley / Baker-Pixley / Quackenbush
                |
                v
term-table semantics
  pointed generated-subalgebra factorization
                |
                v
reactive domain selection
  one globally shared controller table
                |
       +--------+---------+
       |                  |
       v                  v
positive boundary      negative geometry
extendable symmetry    partial symmetry
greatest region        no greatest region
                          |
                          v
                exact maximal-domain antichain
                2^(2^(k-1)-2) maxima
                          |
                          v
                initial-set feasibility is NP-complete
                under explicit relation encoding
                          |
                          v
                conservative Q-term fragment
                exact count and order-optimal DAG compiler
                          |
                          v
                algorithms / formal proof / paper thesis
```

The selected lane is not “rediscover quasi-primal interpolation.” It uses that classical machinery to expose a different reactive object: the poset of domains controlled by one shared term table.

## 2. Ranked frontier

| Rank | Lane | Current evidence | Leverage | Main kill condition |
|---:|---|---|---|---|
| 1 | Fixed-`Q` initial-set term-safety complexity | Complete manuscript 3-SAT reduction; 394-formula, 4,086-domain fail-closed calibration; four mutations | Very high: exact NP-completeness boundary for the same fixed algebra and one-equation promise | Encoding/proof audit fails, or prior art already gives the same fixed-clone safety theorem |
| 2 | Exact maximal-domain antichain for fixed quasi-primal `Q` | Complete manuscript proof; fail-closed `k=3,4` calibration; exact `k=3` domain enumeration | High: sharp theorem, clear contrast with ordinary safety games, immediate output-size consequence | Prior art already studies the same term-clone domain poset or proof audit finds a gap |
| 3 | Exact conservative-term enumeration and simultaneous Shannon size/depth for fixed `Q` | Closed form `2^(5*2^(r-1)-5) * 3^(3^r-3*2^r+3)`; an independently reconstructed parameter-free compiler simultaneously gives size `<34*3^r/r` and depth `<=r+4*ceil(log_2 r)+9` for `r>=64`; the local sibling-shared vector has matching `4q/3` leading upper/lower terms in its declared scalar-output model | High: exact fixed-clone census plus simultaneous Shannon-order size and leading-one depth in one original-signature DAG | The specialization is already in closed-class, parallel-prefix, or many-valued synthesis literature, or the Pixley/anchor/vector/compiler audits fail |
| 4 | Symbolic optimization over maximal domains | Antichain family has an exact orientation-vector representation; LEAP refuted an over-coarse dynamic quotient | High: turns a negative theorem into algorithms and a representation result | No nontrivial objective/coupling survives independent choices |
| 5 | General selector/Horn classification after pointed factorization | Fixed-domain clone overhead is factorized exactly; one explicit selector problem is now NP-complete | Very high, high risk: possible dichotomy or parameterized boundary | Encoding collapses completely to known CSP/SMP or partial-information-game results |
| 6 | Demi-semi-primal versus quasi-primal greatest-region boundary | Positive extendable-symmetry theorem and negative nonextendable witnesses already exist | Medium-high: structural classification could unify the paper | Existing Quackenbush amalgamation results already imply the reactive equivalence directly |
| 7 | Boolean-power / sheaf-like lifting | Strong existing local-to-global theorem line | Medium-high but less immediate than lanes 1–2 | Gluing hypotheses become standard Boolean-product folklore |
| 8 | Homogeneous-structure response frontiers | Many repo conjectures and partial objects; little decisive evidence | High originality, low maturity | No finite presentation or falsifiable first theorem appears |
| 9 | ABA support-hypergraph synthesis | Mature exact recurrences and lower bounds | Medium: substantial but closer to Tau/ocLTL stimulus | Novelty collapses to known symbolic model checking or hypergraph dualization |
| 10 | Generic finite-clone/finitely-related synthesis | Broad target, mostly a program rather than a theorem | Potentially very high, presently diffuse | Scope remains too general for a paper-sized result |

## 3. Selected paper candidate

### Working thesis

For ordinary finite safety games, statewise action choices yield a greatest winning region. Requiring all choices to arise from one original-signature term controller couples observations through internal isomorphisms. For a fixed three-element quasi-primal algebra, this can produce exactly

`2^(2^(k-1)-2)`

incomparable maximal safe invariant domains at state arity `k`. Under an explicit safety-relation encoding, deciding whether any such domain contains a required initial set is NP-complete, even on a family defined by one constructible original-signature equation.

### Proposed contribution stack

1. Define clone-constrained safety domains and separate them from per-state existential winning.
2. Use classical quasi-primal preservation only as the semantic interface.
3. Prove the exact antichain construction and output-size corollary.
4. Prove NP-completeness of required-initial feasibility for the same fixed algebra.
5. Count the conservative fixed-`Q` term fragment exactly and prove one parameter-free compiler simultaneously attains `O(3^r/r)` shared-DAG size and `O(r)` depth, with matching order-level Shannon lower bounds, while separating this classical local-coding adaptation from the reactive contribution and from term-only succinct input.
6. Give the orientation-vector symbolic representation and weighted-selection baseline.
7. State the positive extendable-symmetry boundary.
8. Supply deterministic checkers and Lean formalizations.

The antichain and hardness theorems form a stronger joint paper than either reduction alone. The closest located memoryless partial-information-game reduction makes careful comparative positioning essential.

### Explicit nonclaims

- The quasi-primal interpolation theorem is not ours.
- The pointed product factorization may be a direct classical corollary.
- Antichain algorithms for ordinary games are not ours.
- Search non-detection is not proof of novelty.
- No claim is made about Tau's private work, an unsigned license, or patent scope.

## 4. Knowledge and evidence map

| Object | Status | Deterministic evidence | Missing evidence |
|---|---|---|---|
| Fixed-domain pointed factorization | `DERIVED`, classical-corollary risk | Exhaustive Quackenbush and discriminator calibrations | Older-source identification; Lean |
| Two incomparable maxima | `DERIVED` | Exhaustive 512-domain checker | Prior-art closure |
| Exact antichain family | `MANUSCRIPT THEOREM` | Fail-closed `k=3,4`; exhaustive saturated `k=3` | Independent proof review; Lean; prior art |
| Single-equation semantic definability | `DERIVED`, classical-corollary risk | General orbit-selector lemma from Pixley preservation; equality checks | Older-source identification; Lean |
| Concrete selector term compiler | `MANUSCRIPT LEMMA` | Exact emitted DAG/tree/depth formulas; all 129 compatible selectors at arity at most 2; larger full-table evaluations; mutation rejection; direct unsharing cross-check | Independent proof/size audit; Lean |
| Conservative fixed-`Q` term-operation count | `MANUSCRIPT THEOREM` | Direct category census through arity 8; all 33 semantic operations at arities 1 and 2 compiled; two count mutations rejected | Independent universal-algebra review; database-native prior art; Lean |
| Worst-case and almost-all term-DAG size | `MANUSCRIPT THEOREM`: `Theta(3^r/r)` | Exact semantic count; explicit Lupanov-style compiler; all 128 arity-2 selectors; arity-9 reduction `58,331 -> 18,135` nodes with all rows checked; plan arithmetic through arity 64 | Independent circuit-complexity audit; exact coefficient; tree bounds; Lean |
| Worst-case and almost-all term-DAG depth | `MANUSCRIPT THEOREM`: `r-log_3(log r)-O(1) <= Delta_r(Q) <= r+O(log r)`, hence leading coefficient one | Exact signed family and optimized vector audits; independent no-author-import reconstruction of nonbinary and binary compiler branches, substitution, decoder, glue, and integer ledgers through arity 16,384 | External full proof review; optimal additive term; end-to-end Lean DAG; database-native closed-class prior art |
| Output-size obstruction | `DERIVED` from exact count | Arithmetic identity | Precise output model in paper |
| Fixed-`Q` initial-set NP-completeness | `MANUSCRIPT THEOREM` | 394 CNFs; 4,086 candidate domains; four mutation controls | Independent complexity review; Lean; database-native prior art |
| Explicit/term-only encoding boundary | `PROVED FOR CURRENT STATEMENT` | Reduction emits `3N^2` relation bits; a local-coded shared DAG is `O(3^r/r)`, while a separate simple compiler gives an `O(7^r)` expanded tree; all are polynomial in the explicit table | Complexity and certificates for term-only succinct inputs; local-coding tree size |
| Static one-per-pair quotient | `REFUTED` as dynamic exact quotient | LEAP counter-verdict | A refined orientation-aware transition quotient |
| Novelty | `UNKNOWN` | International and Chinese search log | MathSciNet, zbMATH, database-native Chinese search, expert review |
| Patent/FTO | `UNASSESSED` | Tau-deletion design and provenance separation | Qualified legal review if commercialization/publication requires it |

## 5. Tool lanes and authority

- **Research Kernel:** durable question/hypothesis/result/risk graph and frontier scoring. It records evidence; it does not prove the theorem.
- **Morph:** reformulation and falsifier menus. Suggestions are not mathematical authority.
- **ZAG:** deterministic bounded checks and semantic replay hashes.
- **LEAP:** abstraction search and counter-verdicts. Its rejected static quotient is preserved as negative knowledge.
- **Lean:** intended generic proof gate. The pinned toolchain is not locally available in this snapshot, so no machine-proof claim is made.
- **ESSO:** reserved for a precise selector/optimization IR. The generic executable is unavailable and the unrelated repository-specific ESSO model is not reused.
- **Kurate / Consensus:** literature assistance only. Kurate was unavailable and Consensus quota was exhausted in this tranche.
- **ShapeForge:** typed model used to keep one changing axis (`k`) and explicit gaps; it is not a prover.

## 6. Literature map

### Directly relevant international foundations

- Pixley: quasi-primality and preservation of internal isomorphisms.
- Baker–Pixley: polynomial/term interpolation.
- Quackenbush: demi-semi-primal extension hierarchy.
- Lupanov: local coding and asymptotically efficient circuit synthesis.
- Yablonskii and Orlov: functional constructions and Shannon complexity in `k`-valued logic.
- Kochergin: linear Shannon-depth behavior over complete finite `k`-valued bases.
- Safin: depth-versus-complexity parallelization in precomplete multivalued formula classes.
- Lozhkin and Kasim-Zade: simultaneous or basis-relative Boolean Shannon-depth context.
- Safety-game literature: greatest winning regions, permissive strategies, and antichain representations.

### Adjacent but not direct

- universal-algebraic CSP and subpower membership;
- discriminator-clone minor equivalence and conservative near-unanimity clone generation;
- self-dual conservative Boolean operations and general circuit-counting arguments;
- satisfiability of systems of term/polynomial equations over fixed finite algebras;
- memoryless strategies in partial-information games, including an adjacent clause/literal 3-SAT reduction;
- reactive synthesis over infinite or omega-categorical data;
- control-invariant set computation;
- symbolic and antichain game solvers.

### Chinese-journal search

Queries used English and Chinese variants for quasi-primal algebra, discriminator term/function, conservative operation, clone, internal isomorphism, local coding, two-rail encoding, multiplexer, parallel prefix, Shannon function, multivalued circuit complexity and depth, reactive synthesis, safety game, maximal controller, and invariant domain. General web search plus domain-filtered CNKI, Wanfang, SciEngine, Peking University journal, and Chinese mathematics-journal searches found physical multivalued-circuit, ternary FPRM, reversible ternary synthesis, two-rail synthesis, and multivalued model-checking papers, but no direct match for the domain theorems, the fixed-`Q` count, the sibling-shared local `4q/3` theorem, or the integrated `Theta(3^r/r)` / leading-one-depth construction.

This is low-confidence negative evidence because “quasi-primal” has inconsistent Chinese translation/indexing and several databases expose limited metadata to public crawlers. Before publication, repeat inside the native databases with a Chinese-speaking algebraist or research librarian.

## 7. Next bounded campaign

1. Audit the antichain theorem, NP reduction, exact count, size/depth lower bounds, and global-anchor local-coding compiler line by line: Pixley hypotheses, absorber semantics, block-size inequalities, recursive library census, dynamic-name scope, exact depth accounting, soundness/completeness, and encoding/syntax size.
2. Formalize the complement-pair lemmas, SAT equivalence, and antichain family in Lean once the pinned toolchain is available.
3. Compare the hardness construction formally with memoryless partial-information games: isolate the exact embedding and what the fixed term clone adds.
4. Translate the Orlov/Lupanov basis coefficient to the anchored incomplete clone, close the explicit depth-coefficient interval `[1,3/2]` through R10/fused/nonserial techniques, and seek ordinary-tree bounds; separately add an orientation-aware symbolic solver and seek a tractable parameter such as complement-coupling width.
5. Run database-native prior-art searches, including Chinese-language clone terminology, and obtain independent algebra, clone-theory, and complexity reviews.
6. Only then draft an abstract or make a novelty claim.
