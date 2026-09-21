# OrbitSynthesis commercial / licensing architecture

**Status:** project-design memo, not legal advice. The public Tau license and the currently identified IDNI patent family impose different constraints. Any standalone commercial launch should be reviewed against the executed license and then-current patent status.

## 1. Design principle

Do not make the mathematical core of OrbitSynthesis a fork of Tau.

Use three layers:

### Layer A — OrbitSynthesis Core

Independent research/software assets:

- finite type/orbit interfaces;
- ABA support and cell representations;
- canonical support clauses / antichains;
- hypergraph duality adapters;
- cell-game algorithms;
- positive-mu-calculus engine;
- symmetry quotient engine;
- affine/XOR solver;
- structure-aware backend selection;
- Lean formalizations;
- independent dyadic ABA reference model;
- generic fiberwise-extremal synthesis interfaces;
- benchmarks and falsification oracles.

This layer should contain no copied Tau code and should be usable with independently supplied logical frontends.

### Layer B — Tau Adapter

An interoperability layer that:

- recognizes eligible Tau formula shapes;
- queries or receives normalized Tau syntax through a supported interface;
- compiles eligible formulas into OrbitSynthesis Core objects;
- compares results with Tau as a differential oracle;
- falls back to Tau for unsupported theories/shapes.

Keep this adapter thin. Do not redistribute the Tau Language Framework unless a separate license explicitly permits it.

### Layer C — deployment product

Possible forms:

1. research/non-commercial OrbitSynthesis;
2. Tau-Net-only commercial application, if it stays within the Tau Net Related Instances of the public license;
3. standalone commercial engine/SaaS, only after obtaining the required additional Tau software license and appropriate patent rights;
4. independent solver for theories and methods outside any applicable Tau/IP claims, after an actual freedom-to-operate analysis.

## 2. Public Tau license implications

The current public `LICENSE.md` permits free use of the Product for:

- education;
- research;
- non-commercial use;
- time-limited 30-day internal evaluation;
- specified Tau Net related commercial/non-commercial instances.

It says software created within those permitted scopes may be licensed/distributed under its creator's terms, but the Additional/Tau-Net instances do **not** permit redistribution of the Product or portions of it.

Uses outside those grants require an additional license from IDNI AG.

Public-repository Contributions transfer their associated rights/title/interest to IDNI AG under section 3. Therefore independently developed OrbitSynthesis mathematics/code should not automatically be contributed upstream if retaining ownership matters.

## 3. Patent boundary currently identified

### Granted patent

US 12,254,082 B1, assigned to IDNI AG, covers a Boolean-algebra formal-language / quantifier-elimination software method. Its claim 1 includes an atomless-BA mixed equation/disequation cofactor construction closely corresponding to the classical recurrence independently rediscovered in this project.

**Project consequence:** use that recurrence as prior/background/implementation material, not as an OrbitSynthesis novelty claim.

### Pending continuation

US 2025/0252179 A1 (application 19/083,375) describes a much broader reactive-software-synthesis recurrence/fixed-point method over a decidable base language having finitely many formula equivalence classes for bounded symbols; the public text includes sliding time windows and alternating input/output quantification.

**Project consequence:** the independent mathematical results can be researched and published, but a standalone commercial implementation should not assume freedom to operate merely because its internal representation or algorithm differs.

Patent scope is determined by issued claims and prosecution history, not by abstracts or this memo.

## 4. Rights to request in a separate IDNI agreement

For maximum commercial optionality, request explicit written rights covering:

1. standalone commercial use of the Tau Language Framework;
2. local, server, cloud and SaaS use;
3. modification and derivative integration;
4. redistribution of any necessary Tau runtime/components, or an approved end-user installation mechanism;
5. use for OrbitSynthesis even when not deployed on Tau Net;
6. a worldwide patent license covering the relevant granted patent, pending continuation, PCT/national family and future continuations/divisionals to the extent needed;
7. sublicensing/end-user execution rights;
8. explicit ownership by the OrbitSynthesis creators of independently developed algorithms, proofs, formalizations and software;
9. no automatic assignment of improvements except code intentionally submitted as an upstream Tau contribution;
10. unrestricted academic publication of independent mathematical results, subject only to genuinely confidential information separately identified;
11. interoperability and clean-room implementation rights;
12. survival/version rights so later public-license changes do not revoke the negotiated commercial rights.

## 5. Development policy until a commercial agreement exists

### Safe/default research mode

- continue mathematical research as deeply as useful;
- publish independent proofs/algorithms when novelty/IP review is satisfactory;
- keep OrbitSynthesis Core clean-room / independently implemented;
- use public Tau code under the research license for reading, comparison and differential benchmarking;
- avoid shipping Tau code in OrbitSynthesis distributions;
- keep patent-adjacent algorithms clearly sourced and labeled.

### Tau upstream contributions

Contribute upstream only deliberately. Because the public Tau license says contributed material transfers its rights/title/interest to IDNI AG, a contribution decision should distinguish:

- generic Tau bug fix worth upstreaming;
- OrbitSynthesis-owned algorithm/research result that should remain independent;
- implementation jointly developed under a separate agreement.

## 6. Recommended product roadmap

### Product R0 — research engine

Independent OrbitSynthesis CLI/library operating on internal ABA/cell-game formats plus benchmark corpus and theorem oracles.

No Tau redistribution.

### Product R1 — Tau research adapter

Parse/export through permitted Tau interfaces or user-supplied Tau installation. Detect the protected fragment and run both Tau and OrbitSynthesis for differential comparison.

### Product R2 — Tau Net synthesis service

If commercially attractive, build a Tau-Net-specific application using the public Tau-Net-related grant, after checking that the intended deployment and distribution model really stays inside that scope.

### Product R3 — licensed standalone engine

After a negotiated agreement, expose OrbitSynthesis + Tau interoperability as standalone desktop/server/SaaS software.

## 7. Mathematical independence strategy

The long-term research should generalize beyond Tau/ABA:

- fiberwise greatest-extension structures;
- semilattice response fibers;
- polymorphism-based sufficient criteria;
- equality/DLO/random-graph/Henson counterexamples and classifications;
- succinct finite hyperdoctrines for omega-categorical structures;
- symbolic reactive synthesis independent of one implementation language.

This makes Tau the first backend/case study rather than the intellectual owner of the whole research direction.

## 8. Decision rule

For every new result, ask separately:

1. **Is the mathematics novel?**
2. **Is the implementation independently written?**
3. **Does using Tau code require a software license for this deployment?**
4. **Could practicing the method fall within an IDNI patent claim in a commercial jurisdiction?**
5. **Who owns the contribution if it is upstreamed?**

Do not collapse these into one yes/no question.
