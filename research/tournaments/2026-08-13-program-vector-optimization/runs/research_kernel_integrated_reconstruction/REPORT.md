# Evidence graph for the integrated reconstruction

Date: 2026-08-15  
Status: **PASS**

## Promoted claims

The validator binds the committed semantic receipts and promotes exactly:

```text
OPV_EXACT
BRIDGE_BOUNDED_SEMANTICS
BRIDGE_34
BRIDGE_15
BRIDGE_113_8
BRIDGE_49_5
```

These correspond to:

1. the exact sibling-shared order-pair theorem from PR #15;
2. the bounded complete-DAG selector-table reconstructions;
3. the explicit all-arity compiler with constant 34;
4. the fixed-schedule constant below 15;
5. the adaptive constant below `113/8`; and
6. the two-stage residual compiler below `49/5`.

The strongest promoted construction preserves depth

```text
r+4*ceil(log_2 r)+9
```

and has construction-specific normalized limsup exactly `9`.

## Deliberately unpromoted claims

```text
BYTE_EXACT_LOCAL_EQUIVALENCE  UNKNOWN
PUBLICATION_NOVELTY           UNKNOWN
EXTERNAL_REFEREE              UNKNOWN
HOSTED_CI                     BLOCKED_INFRASTRUCTURE
```

The reconstruction is not asserted to be byte-identical to the local packet `01ddf456…`. The evidence graph makes no novelty or freedom-to-operate finding and records that a fresh external human referee has not yet reviewed the current integrated reconstruction.

GitHub-hosted workflow jobs have continued to receive no runner and execute zero steps because of the repository account's existing Actions billing/spending restriction. This does not change the local deterministic receipts, but it prevents a remote-execution claim.

## Bound receipts

```text
order-pair theorem
  schema orbit-synthesis/order-pair-program-vector/v1
  semantic bc2378444813857cb3943fff3b45164e21a486fc588b89c9125e6fbdbc2fd83d

explicit compiler bridge
  schema orbit-synthesis/order-pair-integrated-compiler/v1
  semantic b0dec4c34465d5b25e5aa35e59ac6016452afcb9df1307bbb6b52b5399b81e23

constant below 15
  schema orbit-synthesis/order-pair-integrated-constant-15/v1
  semantic ad37969af91fee138674e66151ed1c55c6b4428f5786dce56a44e78744c25193

adaptive constant below 113/8
  schema orbit-synthesis/order-pair-adaptive-113-over-8/v1
  semantic fb4bb1f1cac137e8bbe22a47070b733858009d60d6f3d2ddc755951ff1380142

hierarchical constant below 49/5
  schema orbit-synthesis/order-pair-hierarchical-49-over-5/v1
  semantic ea6d5cf35755fd04cc69b040af1152ae3f72e8a6c4d41a65cc0256551929c520
```

## Evidence receipt

```text
schema orbit-synthesis/research-kernel-integrated-reconstruction/v1
semantic 548e78f2baef1c4c0ad8d7444b8fe5116499bcd4d7415230cc25c25c9f9d0894
atoms 10
edges 9
```

Normal and optimized validator outputs are byte-identical.

## Reproduction

```bash
bash research/tournaments/2026-08-13-program-vector-optimization/runs/research_kernel_integrated_reconstruction/check.sh
```
