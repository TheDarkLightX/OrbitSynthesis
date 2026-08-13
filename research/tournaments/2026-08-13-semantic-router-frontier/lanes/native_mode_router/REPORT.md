# Native mode router lane report

Date: 2026-08-13

## Verdict

The theorem survives and admits a strict mathematical refinement.

The old `(equal,gain)` flags encode three reachable outcomes. Naming them `equal`, `gain`, and `loss` reveals a first-non-equal monoid. With the encoding `equal -> 2`, `gain -> 1`, `loss -> 0`, its product is the original discriminator term `d(left,2,right)`.

## Quantitative results

| construction | bound | depth/status |
|---|---:|---|
| reusable `2q` Boolean controls | `<=100q/27 < 4q` | `<=4+ceil(log2 w)` |
| native `q`-root mode vector | `<=17q/9`; `q+O(sqrt q)` | `<=3+ceil(log2 w)` |
| generic complete fused router | `<=35q/9` | `<=w+4+ceil(log2 w)` |
| complement-closed complete router | `<=10q/3`; `(5/2)q+O(sqrt q)` | same signed-router leading depth |
| conditional all-arity ledger | `<16*3^r/r` | `<=r+4 ceil(log2 r)+9` |

The native mode vector is leading-coefficient optimal: its `q` output functions are pairwise distinct, giving a lower bound `q-(w+1)`, while the construction uses `q+O(sqrt q)` nodes.

## Evidence

```text
checker SHA-256: 41d0f2b0d08b651d9e2e3158192eaab8728f956a2c577b76bf183fd6dcb505ed
receipt SHA-256: b08c3e4de3bf42a662c8597b4ffb20ee77a07a7e87cd38d3536a13cf932718d7
semantic SHA-256: 2acaa8c187bb2bd530eba2ae80c89ad157a18ae9b7d40600da7efd0e2c3458a4
```

Normal and optimized executions are byte-identical. The independent oracle records 18 one-digit checks, 132,858 mode checks, 132,858 frozen-program comparisons, 9,268 exhaustive complete-router checks, 270 larger structured tests, and 195,852 conditional arithmetic checks.

## Boundary

The three-element find-first/flip-flop monoid and balanced associative evaluation are classical. The candidate contribution is the exact original-signature embedding, the shared all-branch construction, the signed-router fusion, and the resulting quantitative ledger. Novelty remains unverified.

The new result currently has a paper proof and independent executable oracle. A compiled Lean port is still required before labeling the refinement Lean-checked. The integrated theorem remains conditional on the manuscript's existing interfaces.
