# Source-structure width backends for symbolic ABA cell games

**Status:** literature-backed algorithm map plus OrbitSynthesis specialization. No new generic treewidth/QBF theorem is claimed here.

`ABA_CELL_LABEL_SYMBOLIC_GAME.md` reduces the zero/equation ABA problem to a Boolean reactive game whose transition relation is represented directly by Tau Boolean term circuits. This note identifies which existing structural algorithms can be used without first expanding to complete types or Venn-cell tables.

## 1. One predecessor is a fixed-rank QBF/projection problem

For target circuit `G(n)`, one cell-level predecessor is

`Pre_G(s)
 = forall i. exists n.
     R(s,i,n) AND G(n)`

(up to the permanent safety predicate and exact variable grouping).

The state variables s remain free; i and n are projected/quantified.

Thus one predecessor calculation is projected knowledge compilation / QBF with a fixed environment-system quantifier pattern.

## 2. Ordinary treewidth: useful but not magic

Classical parameterized-QBF results show that QBF is fixed-parameter tractable when parameterized jointly by primal treewidth and quantifier rank. The dependence on treewidth is a tower whose height tracks quantifier rank.

Fichte, Hecher, and Pfandler (LICS 2020) prove ETH lower bounds showing that this tower behavior cannot generally be collapsed by a substantially lower tower for arbitrary QBF of the corresponding quantifier rank.

For one OrbitSynthesis predecessor the quantifier rank is fixed/small, so ordinary treewidth can still give an FPT route.

**But:** repeated temporal fixed points can make the target representation G more complicated. Small treewidth of the original Step term alone does not prove that every subsequent symbolic target has small width.

Primary reference:

- Johannes K. Fichte, Markus Hecher, Andreas Pfandler, *Lower Bounds for QBFs of Bounded Treewidth*, LICS 2020, DOI 10.1145/3373718.3394756, arXiv:1910.01047.

## 3. Prefix-sensitive widths are more faithful to synthesis

Ordinary treewidth ignores which variables are:

- state/free;
- universally controlled by the environment;
- existentially controlled by the system.

This is a known weakness for QBF.

Recent work introduces **bilateral treewidth**, combining strategy-style and resolution-style decompositions and giving FPT QBF evaluation for a strictly stronger prefix-sensitive structural parameter.

This is especially relevant to OrbitSynthesis because the input/output distinction is semantically fundamental rather than syntactic noise.

Primary/current reference:

- Robert Ganian, Marlene Gründel, *Bilateral Treewidth for QBF: Where Strategies and Resolution Meet*, SAT 2026, LIPIcs; arXiv:2605.06262.

**Research target:** measure bilateral/dependency-style widths on Tau-generated cell-label predecessor formulas and compare them with ordinary incidence/primal treewidth.

## 4. Structured d-DNNF and quantifier projection

Capelli and Mengel show that bounded-width structured deterministic DNNFs support existential/universal quantifier elimination with blow-up governed by representation width, and obtain FPT results for bounded-treewidth, bounded-alternation QBF via knowledge compilation.

Primary reference:

- Florent Capelli, Stefan Mengel, *Tractable QBF by Knowledge Compilation*, STACS 2019, DOI 10.4230/LIPIcs.STACS.2019.18; related arXiv:1807.04263.

This gives a natural backend candidate:

`Tau term constraints -> structured d-DNNF -> project i/n blocks -> state target circuit`.

The advantage over explicit Venn support is that the representation can remain source-structural.

## 5. Do not destroy XOR/parity structure

Tau uses term-level XOR (`^`) directly; compact affine/LFSR relations are an important example in this repository.

Converting parity constraints to naive CNF can erase the very structure making them compact.

De Colnet, Szeider, and Zhang (IJCAI 2024) prove FPT compilation to d-DNNF for conjunctions of constraint types that have constant-width OBDDs under all variable orders, parameterized by incidence treewidth. Their examples include parity constraints and bounded-threshold cardinality constraints.

Primary reference:

- Alexis de Colnet, Stefan Szeider, Tianwei Zhang, *Compilation and Fast Model Counting beyond CNF*, IJCAI 2024, DOI 10.24963/ijcai.2024/367.

**OrbitSynthesis consequence:** a source profiler should preserve Tau XOR/affine nodes as native constraints and use incidence structure rather than first bit-blasting them into generic clauses.

## 6. Relation to the LFSR lower bound

The LFSR family demonstrates an important distinction:

- one-step transition relation: tiny affine/XOR description;
- cell-label relation: structurally easy to compile;
- temporal obligation orbit: length `2^d-1`;
- prime H-form output: exponentially large;
- dual M-form output: potentially tiny.

Thus low source treewidth / affine structure can make one-step projection cheap without making every temporal representation cheap.

Backend selection must distinguish:

1. one-step compilation cost;
2. fixed-point/orbit dynamics;
3. final representation cost.

## 7. Proposed profiler fields

For every homogeneous ABA block/game, compute or approximate:

### Source circuit

- number of BA coordinates;
- term DAG size;
- XOR/parity constraints retained as native nodes;
- variable incidence graph;
- incidence/primal treewidth estimate;
- pathwidth/order estimate;
- environment/system/free partition;
- dependency/bilateral-width estimate when available.

### Cell dynamics

- deterministic / functional next relation;
- permutation / affine next relation;
- stutter/pin properties;
- coordinate symmetry group / replicated structure;
- zero-safe cell count if enumerated.

### Positive objectives

- H antichain size;
- M antichain size when dualized;
- hypergraph VC dimension estimate;
- transversal rank;
- conformality;
- degree;
- crossing width for an OBDD order.

## 8. Backend decision sketch

Use the cheapest validated route whose preconditions are met:

1. **affine/permutation:** finite-field/permutation solver;
2. **full replicated symmetry:** histogram/orbit quotient;
3. **small prefix-sensitive width:** structured QBF/d-DNNF backend;
4. **small ordinary incidence width + fixed simple constraints:** d-DNNF/OBDD compilation;
5. **small H/M hypergraph structural parameters:** antichain/blocker backend;
6. **small empirical BDD with safe abort threshold:** BDD;
7. **otherwise:** existing Tau normalization/QE/synthesis path as fallback/oracle.

This is a portfolio, not a universal replacement algorithm.

## 9. Falsification targets

1. Find low-treewidth Tau formulas whose repeated positive fixed points produce high-width targets.
2. Find high ordinary treewidth but low bilateral/dependency width examples where prefix-sensitive decomposition wins.
3. Find parity-heavy Tau terms where CNF expansion is catastrophic but native-constraint compilation is small.
4. Compare the LFSR family across generic BDD, structured d-DNNF, affine solver, H-form, and M-form.
5. Measure whether Tau's own demos/tests predominantly fall into one of these protected structural classes.
