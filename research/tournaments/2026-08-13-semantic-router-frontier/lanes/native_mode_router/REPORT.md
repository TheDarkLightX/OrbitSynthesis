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

Repository-portable files:

```text
native_mode_model.py SHA-256:
  b239a7581266a53310286a682c5d429066737c0fd7885fc0685b06e4218456c2

check_native_mode_router.py SHA-256:
  5e2eb7782834d496cf78342e2f0161e5daf74fce83af15c1c319d76f5725c631

receipt.json SHA-256:
  216710173c1583607d3677a861e6561bb26f497d3fb4bef4d40ead3cc8d9d3eb

semantic SHA-256:
  60bce0041f7a185af491666f2252f4c5867480a1171ff8dc0fed72bd4e74a8f7
```

Replay from the lane directory:

```text
python3 check_native_mode_router.py > /tmp/native-normal.json
python3 -O check_native_mode_router.py > /tmp/native-optimized.json
cmp /tmp/native-normal.json /tmp/native-optimized.json
```

The checked normal and optimized outputs are byte-identical. The independent oracle records 18 one-digit checks, 132,858 mode checks, 132,858 frozen-program comparisons, 1,641 address-support checks, 9,268 exhaustive complete-router checks, 270 larger structured tests, and 195,852 conditional arithmetic checks. It also checks the exact finite extrema through width 256, local one-digit minima, and effective mutations.

## Boundary

The three-element find-first/flip-flop monoid and balanced associative evaluation are classical. The candidate contribution is the exact original-signature embedding, the shared all-branch construction, the signed-router fusion, and the resulting quantitative ledger. Novelty remains unverified.

The new result currently has a paper proof and independent executable oracle. A compiled Lean port is still required before labeling the refinement Lean-checked. The integrated theorem remains conditional on the manuscript's existing interfaces.
