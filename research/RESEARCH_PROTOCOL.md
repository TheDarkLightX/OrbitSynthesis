# OrbitSynthesis systematic research protocol

This protocol is mandatory for major theorem/algorithm directions. Its purpose is to prevent fashionable-word drift, rediscovery, weak novelty claims, and opaque proof accumulation.

## 1. Source the problem from the actual frontier

Every direction must begin with one of:

- a precise limitation/open question in a primary source;
- a concrete complexity bottleneck in Tau/Asor's implementation/theorems;
- a falsified conjecture whose failure exposes new structure;
- a mathematically natural generalization whose assumptions can be stated independently of project vocabulary.

Do not create directions by combining unrelated project memories or buzzwords.

## 2. Representation-first rule (Morph/Noether discipline)

Before strengthening a theorem, search for a representation in which the mechanism is natural.

Examples already successful here:

- complete ABA type -> nonzero Venn support;
- restriction fiber -> spanning multipartite hypergraph;
- atomic equation -> set-intersection/group test;
- family of support constraints -> monotone CNF / hit hypergraph;
- Boolean-power tuple -> locally constant finite-label partition;
- quasi-primal term strategy -> internal-isomorphism-equivariant finite table.

Ask explicitly:

> What are the degrees of freedom? Which are representation artifacts? Which coordinates are invariant under the relevant symmetries?

## 3. Emmy Noether / inner-ground requirement

A proof is exposition-ready only when it explains *why* the result is true structurally.

Examples:

- ABA extension count: each nonzero old region independently chooses a nonempty refined support;
- co-atom lower bound: each missing cell requires a private observation;
- clause hypergraph recurrence: equations remove allowed cells, inequations are global hit obligations, atomlessness permits maximal simultaneous witnesses;
- Boolean-power lifting: equations are pointwise and clopen patchwork glues finite local responses.

A mechanical derivation may certify truth but is not the final understanding proof.

## 4. Tao: basic-example calibration

At every quantitative theorem or complexity conjecture, test the claimed exponents/scales on deliberately simple families that isolate one parameter.

Following Tao's "Use basic examples to calibrate exponents": choose examples with trivial behavior in every feature except the exponent/parameter being tested, and include expected saturating examples whenever possible.

Required calibration families for this program include:

### Support/type counts

- one active Venn cell;
- full support;
- half-density/random support;
- nested constant partitions;
- generic independent constant partitions.

### Hypergraph fixed-point width

- no inequations;
- one singleton hit;
- nested/laminar hits;
- maximum Sperner antichain;
- random hit families.

### Transition dynamics

- identity map;
- constant map;
- directed path to a fixed point;
- one directed cycle;
- disjoint cycles of coprime lengths (Landau calibration);
- primitive strongly connected graph;
- random directed graph.

### Finite-algebra clone constraints

- primal (all functions);
- semi-primal with a proper subalgebra;
- demi-semi-primal with nontrivial global automorphisms;
- quasi-primal with a nonextendable internal isomorphism (Quackenbush counterexample).

A proposed asymptotic exponent/bound that gives the wrong behavior on one of its supposed extremal/basic examples is rejected before proof work.

## 5. Tao: counterexample before proof

For every nontrivial universal conjecture:

1. try the smallest arity/cardinality;
2. search near-extreme pairs (full/co-atom, empty/full, deterministic/permutation, etc.);
3. brute-force the first finite domains when feasible;
4. search for a construction violating the strongest form;
5. preserve the minimized falsifier.

Only after surviving this phase should proof construction dominate effort.

## 6. Symmetry reduction

Before exhaustive search, quotient by obvious automorphisms whenever this preserves the question.

Relevant symmetries:

- Venn-cell coordinate permutations/complements;
- row/column permutations in projection fibers;
- automorphism groups of finite local algebras;
- internal-isomorphism groupoids for quasi-primal term tables;
- SCC/cyclic-class symmetries of transition graphs.

But do not quotient by a symmetry that is not actually respected by the specification.

## 7. Fields-medalist / top-mathematician transfer rule

When a problem is hard, search for a structurally similar solved problem and extract the *method*, not the prestige label.

Techniques already screened/applied:

- Gowers-style algebraization/dimension check;
- Tao representation change and basic-example calibration;
- extremal constructions / near-equality tests;
- orbit/symmetry reduction;
- finite-to-structural proof promotion;
- duality (prime hits vs maximal losers vs minimal transversals);
- graph-period / matrix-power reduction;
- universal-algebra clone/Pol-Inv thinking.

If a technique adds no explanatory or proof power, record it as screened out rather than forcing it into the argument.

## 8. Literature-frontier protocol

For each theorem candidate:

1. search the exact statement vocabulary;
2. search the structural mechanism in adjacent fields;
3. search older terminology (not only modern terminology);
4. inspect references of the closest paper;
5. distinguish "known ingredient" from "known combination";
6. record prior art that narrows the claim.

Older-source checks are mandatory. This program already found crucial prior art in Wang (1959), Even-Meyer (1968/69), Marriott-Odersky (1996), Foster/Pixley/Quackenbush, and symbolic model checking.

## 9. Kurate usage

Kurate may be used as a **discovery/ranking signal**, not novelty authority. Its methodology uses AI pairwise ranking of current arXiv papers; its own materials caution against treating rankings as sole academic judgment.

Use it to:

- discover current papers/categories;
- identify clusters worth primary-source inspection;
- find recent frontier terminology.

Every mathematical claim must still be grounded in the primary paper/source.

## 10. Consensus usage

Use Consensus for peer-reviewed-literature retrieval when quota/tool access exists.

Current tool state (Aug 11 2026 session): monthly search quota is exhausted. Do not claim a result came from Consensus until search access returns and the returned paper is fetched/inspected.

## 11. Research Kernel / Morph / LEAP provenance

If these private connectors are exposed in a session, use them for the roles the user designed them for:

- Research Kernel: source graph, theorem dependency/frontier retrieval, tactic archive;
- Morph: reusable representation/proof tactics and negative knowledge;
- LEAP: concrete research/workflow use cases where its capabilities apply.

Current Aug 11 2026 tool surface exposes no installed plugin matching Research Kernel, Morph, LEAP, or Kurate. Therefore this branch must not falsely attribute results to those tools.

The reusable tactics previously retrieved from the user's private workflow are still applied explicitly, but tool provenance is recorded honestly.

## 12. Three-certificate rule

For a publishable theorem/algorithm, seek three distinct forms of support:

1. **truth certificate** — rigorous proof / formal proof where feasible;
2. **understanding certificate** — Noether-style structural explanation;
3. **falsification certificate** — adversarial finite search / extremal tests / minimized failed generalizations.

A computation alone is not a universal proof; a formal proof alone may still hide the mechanism; intuition alone is insufficient.

## 13. Formalization discipline

Lean or another prover should formalize mature dependencies, not conceal missing mathematics behind axioms.

Separate:

- finite combinatorial layer;
- universal-algebra/model-theory layer;
- algorithm correctness layer;
- implementation equivalence to Tau.

If Lean is unavailable in the runtime, label formalization pending rather than inventing validation.

## 14. Differential-testing discipline

When an executable alternative to Tau is proposed:

- keep Tau's current behavior as one oracle, not unquestioned authority;
- keep an independent bounded semantic oracle where possible;
- on divergence, minimize the input and prove which semantics is correct;
- preserve every real defect/counterexample.

## 15. Complexity discipline

Never infer algorithmic efficiency from decidability, finite orbit count, compact transition relation, or small proposition count.

Track separately:

- semantic state/type count;
- minimum information width;
- representation DAG size;
- transition/extension representation size;
- fixed-point iteration length;
- antichain width;
- witness reconstruction cost;
- preprocessing cost (e.g. constant partition rank).

Use Tao-style examples to calibrate every claimed dependence.

## 16. Novelty/IP gate before promotion

Before calling a result a contribution:

1. search old and new prior art;
2. compare against Ohad/Tau papers;
3. compare against relevant patent claims as a separate issue from academic novelty;
4. mark the result as:
   - KNOWN / REPACKAGED;
   - NEW COMBINATION CANDIDATE;
   - THEOREM CANDIDATE, NOVELTY UNVERIFIED;
   - NOVELTY-SUPPORTED AFTER SEARCH;
5. do not make freedom-to-operate claims without legal review.

See `research/IP_BOUNDARY.md`.

## 17. Promotion/kill rule

Every conjecture needs:

- assumptions;
- strongest version;
- simplest falsifier sought;
- finite test domain;
- prior-art target;
- promotion criterion;
- kill condition.

If a conjecture dies, preserve the counterexample and ask what structure its failure reveals. Several of the best theorems in this program arose exactly this way.
