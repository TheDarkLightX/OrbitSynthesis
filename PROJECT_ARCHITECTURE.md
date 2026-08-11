# OrbitSynthesis project architecture

**Purpose:** maximize mathematical depth, publication freedom, engineering optionality, and later commercial choices while respecting the current Tau software license and treating patent freedom-to-operate as a separate question.

**Not legal advice.** The operative rights are the executed agreements and applicable patent claims. This file is an engineering/research boundary document.

## 1. OrbitSynthesis Core

A clean, independently authored research/codebase containing no copied Tau source.

### Own mathematical objects

- finite extension-type posets/semilattices;
- ABA Venn-support geometry;
- cell games;
- maximal-response antichains;
- conflict hypergraphs;
- hypergraph blocker/transversal representations;
- positive-mu-calculus antichains;
- symmetry quotients;
- affine/GF(2) solvers;
- knowledge-compilation adapters;
- generic finite game/fixed-point algorithms;
- theorem/proof library;
- benchmark generators.

### Own interfaces

Define theory plugins abstractly:

- `encode_partial_type`;
- `response_extension_geometry`;
- `legal_response_constraints`;
- `greatest_response` if available;
- `maximal_response_representation`;
- `exists_project` / `forall_project`;
- `realize_response_witness`;
- symmetry/width metadata.

No Tau classes/types should be required by the mathematical core.

## 2. Theory plugins

### ABA plugin

Implements the independently derived support/cell representation and algorithms.

Research use can compare against Tau as an oracle, but the plugin should remain source-independent.

Patent-sensitive methods must be labeled separately from mathematical novelty. In particular, do not present IDNI/Asor's claimed Boolean-algebra cofactor QE method as an OrbitSynthesis invention.

### Equality plugin

Star extension semilattice; freshness-positive fragment.

### DLO plugin

Finite cut-chain extension geometry; extremal upward/downward response fragments.

### Rado graph plugin

Fresh-neighborhood Boolean cube / union semilattice.

### Henson plugin

Clique-conflict hypergraph and maximal-response / knowledge-compilation backend.

These plugins establish that OrbitSynthesis is a general infinite-structure synthesis research platform rather than a Tau derivative.

## 3. Tau adapter

A narrow optional integration layer.

Responsibilities:

1. accept or invoke a user-provided Tau installation;
2. parse/export Tau formulas through a documented interface, CLI, or intentionally authored adapter;
3. classify the BA/theory and eligible fragment;
4. translate eligible formulas into OrbitSynthesis Core IR;
5. optionally ask Tau for normalization/QE results as differential oracle;
6. translate OrbitSynthesis strategies/results back to a form usable by the caller.

### Distribution rule

Do **not** bundle or redistribute Tau binaries/source/components under the public-license assumption.

If a public OrbitSynthesis adapter is distributed, its documentation should state that Tau is separately licensed/obtained and any execution using Tau is governed by Tau's license.

## 4. Tau Net product mode

The current public Tau license expressly includes certain commercial Tau-Net-related uses, including applications/specifications solely for deployment/execution over Tau Net and integration with Tau Net.

A potential commercial product architecture is therefore:

`OrbitSynthesis Core -> Tau adapter -> Tau Net deployment`

provided the actual use remains inside the license's Tau-Net-related scope and Tau itself is not redistributed contrary to the license.

Exact product plans should be checked against the then-current license and any separate agreement.

## 5. Standalone commercial mode

A standalone commercial/SaaS product using Tau outside the listed public-license exceptions should be treated as requiring an additional IDNI software license.

Separately, IDNI/Asor patent claims may cover methods relevant to Boolean-algebra specification, quantifier elimination, recurrence/fixed-point synthesis, or related implementation paths.

Therefore standalone commercialization requires a claim-by-claim freedom-to-operate review and, where appropriate, explicit patent rights from IDNI.

Do not infer patent freedom merely because OrbitSynthesis code was independently authored.

## 6. Upstream Tau contributions

The current public Tau license states that contributions proposed through the Product's public repositories transfer associated rights/title/interest to IDNI.

Therefore:

- keep OrbitSynthesis Core independent;
- contribute upstream only intentionally;
- isolate a small patch when we deliberately want Tau itself to gain an optimization;
- do not upstream the whole research engine by default.

A possible model is:

`OrbitSynthesis research theorem + independent reference implementation`

then optionally

`small Tau fast-path contribution`

with the ownership consequence understood.

## 7. Publication mode

Mathematical papers should be written independently of Tau source-code ownership.

Each theorem should distinguish:

- classical/known background;
- Asor/IDNI prior results;
- patent-sensitive known methods;
- OrbitSynthesis-derived theorem;
- bounded computational evidence;
- formal proof status;
- conjecture.

Publication novelty and patent freedom-to-operate are separate questions.

## 8. Clean-room discipline

For any potentially standalone implementation:

1. specify algorithms mathematically in OrbitSynthesis notes/papers;
2. implement from those specifications rather than copying Tau source;
3. preserve source/provenance records;
4. use Tau outputs only for differential testing when license permits;
5. avoid importing Tau headers/code into Core;
6. maintain independent tests/oracles.

This discipline addresses copyright/source independence. It does **not** by itself answer patent infringement questions.

## 9. Patent-sensitive boundary map

Maintain a separate claim map with buckets:

### Background / likely patent-proximate

- first-order ABA QE/cofactor elimination as claimed/described by IDNI;
- Tau-specific software-specification machinery;
- recurrence/fixed-point mechanisms explicitly appearing in patent claims/applications.

### OrbitSynthesis candidate research frontier

- Venn-support complete-type geometry as a synthesis representation;
- complete-type -> cell-game factorization;
- maximal-response/dominant-strategy theorem;
- positive-mu-calculus synthesis-to-model-checking collapse;
- extension-semiltattice classification across theories;
- one-point obstruction incidence width;
- monotone graph-class classification;
- maximal-response conflict hypergraphs;
- Henson response-width lower bounds;
- structure-aware representation portfolio;
- affine/symmetry synthesis subclasses.

These are **candidate novelty areas**, not assertions of patent non-coverage.

## 10. Repository separation

Recommended repositories/modules:

### `OrbitSynthesis`

Research, math, proofs, generic implementation, theory plugins.

### `OrbitSynthesis-Tau`

Optional adapter only if/when we want a separately distributed integration layer.

### `OrbitSynthesis-TauNet`

Deployment/application layer for Tau-Net-specific product work.

### private `ip/`

Executed licenses, correspondence, claim charts, attorney notes. Do not put confidential agreements in the public research repository.

## 11. Commercial-license request checklist

If negotiating broader rights with IDNI, ask the written agreement to address explicitly:

- standalone commercial use;
- SaaS/cloud service;
- modification rights;
- redistribution/deployment model;
- patent family coverage including continuations/divisionals/international counterparts as applicable;
- end-user/sublicense rights;
- ownership of independently developed improvements;
- publication rights;
- interoperability/clean implementation rights;
- survival/version rights after license changes or termination;
- treatment of upstream contributions separately from independent work.

## 12. Strategic principle

Do the deepest mathematics **outside** the dependency boundary.

Use Tau as:

- motivating theory;
- benchmark;
- oracle;
- integration target;
- Tau Net deployment backend where licensed.

Do not make Tau's source license the intellectual boundary of OrbitSynthesis.
