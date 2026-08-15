# Independent reconstruction: explicit order-pair compiler bridge

Date: 2026-08-15  
Branch: `research/order-pair-integrated-compiler-reconstruction`  
Base: PR #15, `research/order-pair-program-vector` at `5f3093a6…`  
Status: **explicit construction and deterministic audit; not the byte-exact `01ddf456…` packet**

## Verdict

The order-pair/KPG theorem in PR #15 composes into a complete parameter-free compiler. The reconstructed algorithm takes any total complement-invariant selector table

```text
sigma:Q^r->{0,...,r-1}
```

and builds one hash-consed original-signature `{d,u}` DAG computing

```text
x |-> x_(sigma(x)).
```

For every `r>=64`, the generic proof gives

```text
size  <34*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

The construction explicitly instantiates and unions:

1. one balanced global anchor;
2. one local order-pair vector;
3. two signed local routers for every `Q`-valued local table;
4. one prefix order-pair vector;
5. two signed prefix routers;
6. one two-plane decoder;
7. one complement-relative binary branch; and
8. one final binary/nonbinary glue term.

There is no remaining same-DAG substitution hypothesis or free control-ROM premise in the reconstructed theorem.

## Exact semantic reconstruction

`compiler_bridge_model.py` contains a standalone hash-consed `d/u` DAG implementation. It does not import the repository’s compiler implementation.

For bounded differential testing it materializes the entire graph, including the universal local library and all shared vectors. The audit checks:

```text
128  complete compatible arity-two selector tables,
32   deterministic independent arity-three selector tables,
160  total selector tables,
2016 complete input rows.
```

Every row returns the requested coordinate value. The largest bounded materialized graph has 81 reachable operation nodes and depth 17.

The audit independently rebuilds the order-pair vector for both signs through width five and checks:

```text
132,858 target/physical/sign cases.
```

Its exact rows agree with PR #15:

| width | positive nodes | negative nodes | depth |
|---:|---:|---:|---:|
| 1 | 6 | 6 | 3 |
| 2 | 20 | 21 | 4 |
| 3 | 66 | 67 | 5 |
| 4 | 151 | 152 | 5 |
| 5 | 428 | 429 | 6 |

## Generic construction

Let

```text
ell=ceil(log_3(r^2)),
H=r-4-ell,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b).
```

The local block has `M` assignments. Every one of its `3^M` `Q`-valued tables is encoded into two Boolean planes and assigned two positive signed-router roots. Both planes and every local table share one width-`b` order-pair vector.

For each of the `P` prefix assignments, the selector table determines one existing local-table pair. Two prefix routers select those roots and share one width-`r-b` order-pair vector. One decoder recovers the `Q` value.

The binary cube is compiled by the frozen complement-relative residual-first signed-router construction. Its logical controls are address-only; physical Boolean values are represented by `x_0,u(x_0)`. The final three-node glue selects the binary or nonbinary result.

The full construction and proof are in

```text
notes/QUASIPRIMAL_CONSERVATIVE_TERM_INTEGRATED_COMPILER_RECONSTRUCTION.md
```

## Integer ledger

Every integer arity from 64 through 16,384 is checked. The audit performs 228,494 ledger assertions covering:

- exact order-pair vector recurrences;
- local/prefix parameter identities;
- reserve inequalities;
- the local universal library;
- prefix routers and shared vector;
- the explicit binary node and depth upper bounds;
- the total `<34*3^r/r` inequality; and
- the complete depth inequality.

The finite maximum of the audited normalized total is

```text
14.925925925925938
```

at arity 93. This suggests a substantially sharper constant, but only `34` is promoted by this reconstruction because its simple analytic proof is complete for every arity.

## Effective falsifiers

### Per-branch prefix-vector duplication

Replacing the single shared prefix vector by one copy per physical prefix makes the normalized size approximately

```text
4.019310e+29
```

already at arity 64. The theorem therefore depends essentially on the declared multi-output sharing convention.

### Serialized Boolean planes

Running the high and low planes serially gives depth 159 at arity 64, while the theorem target is 97. The planes must run in parallel and decode once.

### Broken binary equivariance

A selector table that assigns different indices to a binary point and its complement is rejected before construction. The binary branch does not silently assume illegal absolute constants.

## Receipt

Normal and optimized Python executions are byte-identical.

```text
compiler_bridge_model.py SHA-256
  e4d8176ce8e4cca977486fb22ac7c4f409890a1167382f178cf98208a07cb9e7

check_compiler_bridge.py SHA-256
  22460971b2ea655ec74d97d8ee7667514053c0786ed351427b24445d3056be69

receipt.json SHA-256
  fbb71cd468db036889871421a6a6df7311bd4a564c56df5e7c91865262c05d32

semantic SHA-256
  b0dec4c34465d5b25e5aa35e59ac6016452afcb9df1307bbb6b52b5399b81e23
```

## Boundary

This is a fresh-room reconstruction of the theorem shape reported for local hash `01ddf456…`. It is not evidence that the uploaded files are byte-identical to that packet, and it does not reproduce the reported 65-source portfolio gate or Research Kernel evidence object.

It establishes neither novelty nor freedom to operate. A fresh external referee should review the eventual byte-exact upload of the local packet and compare it with this independent reconstruction.
