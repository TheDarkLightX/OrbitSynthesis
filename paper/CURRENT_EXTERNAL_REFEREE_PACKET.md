# External referee packet: fixed-Q conservative term complexity

Date: 2026-08-15  
Status: **current fresh-room reconstruction packet**  
Repository: `TheDarkLightX/OrbitSynthesis`  
Stack: PR #15 followed by PR #36

## 1. Referee mandate

Please review the current mathematical construction rather than the superseded internal referee report for the earlier `dddeb98c…`/PR #13 snapshot.

The requested review has three logically separate targets:

1. the exact sibling-shared order-pair/KPG program-vector theorem;
2. the explicit all-arity compiler bridge and its strongest recursive-local/two-stage schedule; and
3. the relationship of those constructions to the base conservative-clone census and Shannon lower bounds.

A positive report should state separately whether each target is correct. Publication novelty is a separate question and should not be inferred from mathematical correctness.

## 2. Main claims under review

### Claim A: exact order-pair vector

For address width `w>=1` and capacity `q=3^w`, the exact ordered projection-control vector for either sign has one constant-free original-signature shared DAG with

```text
depth <=3+ceil(log_2 w),
C_s(w)=(4/3+o(1))q,
2*C_s(w)<=5q-1.
```

For `w>=2`, the exact nonconstant output-function census is

```text
positive root: 4q/3-1,
negative root: 4q/3.
```

Since a single-output operation node computes one function and none of these outputs is a raw ternary address input, the leading constant `4/3` is optimal for this exact ordered output vector.

### Claim B: explicit integrated compiler

For every total complement-invariant coordinate selector

```text
sigma:Q^r->{0,...,r-1}
```

and every `r>=64`, the current recursive-local/two-stage construction builds one parameter-free original-signature `{d,u}` shared DAG computing

```text
x |-> x_(sigma(x))
```

with

```text
size  <(19/2)*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

The graph explicitly includes the global anchor, dynamic names, complete recursive local table library, two residual routing stages, both Boolean planes, one decoder, the complement-relative binary branch, and final glue. No free control ROM or same-DAG substitution premise remains.

### Claim C: conservative operations

The base manuscript proves that every conservative term operation of the fixed algebra admits a complement-invariant coordinate selector. Combining that theorem with Claim B gives the same size and depth bounds for every conservative `r`-ary term operation.

Together with the manuscript’s counting lower bounds:

```text
max_f C_r(f)=Theta(3^r/r)
```

and

```text
r-log_3(log r)-O(1)
 <=Delta_r(Q)
 <=r+4*ceil(log_2 r)+9.
```

### Construction-specific asymptotics

For the declared power-of-three local-block architecture,

```text
limsup_(r->infinity) N(r)r/3^r=9.
```

This is not claimed as a lower bound for arbitrary `{d,u}` circuits.

## 3. Authoritative files

### Base manuscript

```text
paper/FIXED_Q_TERM_COMPLEXITY_DRAFT.md
```

Warning: the prose in its historical compiler section predates the strongest reconstructed bridge. Use it for the algebra, semantic characterization, census, counting lower bounds, anchor, binary branch, and historical context. Use the files below for the current router and integrated upper theorem.

### Exact order-pair theorem — PR #15

```text
research/tournaments/2026-08-13-semantic-router-frontier/lanes/order_pair_program_vector/REPORT.md
research/tournaments/2026-08-13-semantic-router-frontier/lanes/order_pair_program_vector/order_pair_model.py
research/tournaments/2026-08-13-semantic-router-frontier/lanes/order_pair_program_vector/audit_order_pair_program_vector.py
research/tournaments/2026-08-13-semantic-router-frontier/lanes/order_pair_program_vector/OrderPairSemantics.lean
research/tournaments/2026-08-13-semantic-router-frontier/lanes/order_pair_program_vector/OrderPairLedger.lean
research/tournaments/2026-08-13-semantic-router-frontier/lanes/order_pair_program_vector/receipt.json
```

### Explicit integrated bridge

```text
notes/QUASIPRIMAL_CONSERVATIVE_TERM_INTEGRATED_COMPILER_RECONSTRUCTION.md
research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/compiler_bridge_model.py
research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/check_compiler_bridge.py
research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/receipt.json
research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/REPORT.md
```

### Strongest recursive-local/two-stage theorem

```text
notes/QUASIPRIMAL_CONSERVATIVE_TERM_HIERARCHICAL_CONSTANT_49_5.md
notes/QUASIPRIMAL_CONSERVATIVE_TERM_RECURSIVE_LOCAL_CONSTANT_19_2.md
research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/hierarchical_compiler_model.py
research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/recursive_local_compiler_model.py
research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/check_hierarchical_49_5.py
research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/check_recursive_local_19_2.py
research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/receipt_hierarchical_49_5.json
research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/receipt_recursive_local_19_2.json
```

### Evidence graph

```text
research/tournaments/2026-08-13-program-vector-optimization/runs/research_kernel_integrated_reconstruction/atoms.json
research/tournaments/2026-08-13-program-vector-optimization/runs/research_kernel_integrated_reconstruction/edges.json
research/tournaments/2026-08-13-program-vector-optimization/runs/research_kernel_integrated_reconstruction/validate.py
research/tournaments/2026-08-13-program-vector-optimization/runs/research_kernel_integrated_reconstruction/receipt.json
research/tournaments/2026-08-13-program-vector-optimization/runs/research_kernel_integrated_reconstruction/REPORT.md
```

## 4. Reproduction commands

From the repository root:

```bash
python3 experiments/audit_fixed_q_preprint.py

bash \
  research/tournaments/2026-08-13-semantic-router-frontier/lanes/order_pair_program_vector/check.sh

bash \
  research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction/check.sh

bash \
  research/tournaments/2026-08-13-program-vector-optimization/runs/research_kernel_integrated_reconstruction/check.sh
```

Each Python evidence layer is run normally and with `python3 -O`; its outputs must be byte-identical and equal to the committed receipt.

The GitHub-hosted workflow has repeatedly received no runner and executed zero steps because of the repository account’s Actions billing/spending restriction. A referee should run the commands locally rather than treating the red hosted status as a theorem failure.

## 5. Required adversarial checks

### 5.1 Order-pair semantics

- Re-derive the first-decision monoid and both coordinate products.
- Verify the one-digit original-signature terms under the explicit `A=2` premise.
- Verify last-`2` gain sharing and `H_(a1)=G_(a2)` reuse.
- Check the sign-parity counts and exact positive/negative recurrences.
- Recompute the output-function census and all cross-family disjointness claims used by the lower bound.

### 5.2 Shared-DAG accounting

- Confirm that every multi-output vector is adjoined once, not per consumer.
- Confirm that all reachable operation nodes are charged and that raw inputs alone are free.
- Check whether name nodes are omitted or double-counted; overcounting is acceptable, undercounting is not.
- Verify that both Boolean planes run in parallel and that decoding occurs exactly once.

### 5.3 Recursive local library

- Prove by induction that all `3^(3^j)` `Q`-valued tables at level `j` are represented.
- Verify that two width-one signed skeletons cost at most eight nodes per new table pair.
- Check that a single width-one vector is shared across the entire level.
- Verify

  ```text
  L(b)=8*sum_(j=1)^b 3^(3^j)+6b<9*3^(3^b).
  ```

- Check the local depth recurrence without inserting a decoder at each level.

### 5.4 Two-stage residual compiler

- Verify the address order and the semantic roles of the bottom and top blocks.
- Recompute the exact residual count

  ```text
  R_2(n)=3P+2V-1+C_+(a)+C_+(c).
  ```

- Confirm that the bottom vector is shared across all `2V` bottom routers.
- Confirm that the top vector is shared by exactly the two top plane routers.
- Verify the complete depth ledger and the inequality `ceil(log_2 b)+1<=ceil(log_2 r)`.

### 5.5 Binary branch and glue

- Verify that no absolute Boolean constant is used on the binary cube.
- Check residual-first padding and the explicit node/depth upper counts.
- Recheck complement equivariance of every selector admitted by the constructor.
- Substitute all binary and nonbinary cases into the three-node glue term.

### 5.6 All-arity constants

- Recompute the exact finite maximum over `64<=r<1024` using integers.
- Check every transition and nontransition case in the analytic tail.
- Verify the three `1/100` lower-order bounds from arity 1024 onward.
- Check the construction-specific limsup argument in both directions.

### 5.7 Base theorems

- Recheck the exact conservative-operation census.
- Recheck the coordinate-selector representation, including binary complement invariance.
- Recheck the DAG-description counting lower bound and the depth-tree counting lower bound.

## 6. Effective mutations already included

The committed audits reject:

```text
prefix-vector duplication,
serialized Boolean planes,
non-equivariant binary selectors,
unguarded first-gain composition,
incorrect sign-aware root reuse,
normal/optimized semantic drift,
receipt or schema drift.
```

A referee is encouraged to add independent mutations rather than relying only on these.

## 7. Evidence status

The reconstruction evidence graph promotes:

```text
OPV_EXACT
BRIDGE_BOUNDED_SEMANTICS
BRIDGE_34
BRIDGE_15
BRIDGE_113_8
BRIDGE_49_5
BRIDGE_19_2
```

It deliberately does not promote:

```text
byte identity with 01ddf456…,
publication novelty,
freedom to operate,
external peer review,
hosted CI execution.
```

## 8. Publication and authorship boundary

Do not deposit this packet on Zenodo or arXiv until:

1. author names, order, affiliations, and ORCIDs are approved;
2. the byte-exact local `01ddf456…` packet is recovered or its absence is explicitly disclosed;
3. a fresh external referee reviews the current integrated theorem rather than an older snapshot; and
4. the manuscript is editorially compressed so the main theorem is not obscured by the historical tournament record.

## 9. Requested report format

Please return:

```text
A. Exact order-pair theorem: PASS / REPAIR / FAIL
B. Integrated construction semantics: PASS / REPAIR / FAIL
C. Size ledger through 19/2: PASS / REPAIR / FAIL
D. Depth ledger: PASS / REPAIR / FAIL
E. Base census and lower bounds: PASS / REPAIR / FAIL
F. Novelty assessment: MATCH FOUND / NO MATCH FOUND / INCOMPLETE SEARCH
G. Smallest concrete counterexample or first unproved implication, if any
H. Publication recommendation and required revisions
```

The absence of a novelty match must not be reported as proof of novelty.
