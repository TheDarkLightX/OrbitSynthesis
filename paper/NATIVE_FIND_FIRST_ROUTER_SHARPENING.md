# Final sharpening of the native find-first router theorem

**Status.** Paper theorem with deterministic normal/optimized replay. The semantic monoid, original-signature bridge, fused signed-tree induction, and recurrence-level `17q/9` and `10q/3` bounds have new Lean sources without placeholders; compiler validation is still pending. The all-arity compiler remains conditional on the frozen interfaces inherited from the base manuscript.

## Exact router statements

Let `q=3^w`. Encode the three first-mismatch outcomes by

```text
loss -> 0,
gain -> 1,
equal -> 2.
```

Their associative product is exactly

```text
x*y=d(x,2,y).
```

This yields the following hierarchy.

### Reusable Boolean controls

Deduplicating gain roots by the physical prefix ending at their final digit `2` gives all `2q` frozen control wires with

```text
size  <=3q,
depth <=4+ceil(log_2 w),
size  =2q+O(sqrt q).
```

This is a drop-in replacement for the historical `7q` theorem.

### Native mode vector

One `Q`-valued mode root per physical branch has

```text
size  <=17q/9,
depth <=3+ceil(log_2 w),
size  =q+O(sqrt q).
```

For `w>=2`, the `q` roots are pairwise distinct and every root depends on every target coordinate. Consequently every multi-output DAG in the declared model needs at least `q` operation nodes. The leading size coefficient one is optimal.

### Fused signed router

Replacing each historical two-control bottom cell by one mode root gives

```text
arbitrary Boolean payloads:       size <=35q/9,
complement-closed payload family: size <=10q/3.
```

The complement-closed construction has asymptotic size `(5/2)q+O(sqrt q)` while retaining signed-router dependency depth `w+O(log w)`.

## Adaptive all-arity ledger

For `r>=64`, choose

```text
ell=ceil(log_3(r^2)),
H=r+1-ell,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b).
```

This advances each power-of-three block transition by one arity relative to the first conservative schedule. Exact replay plus the analytic tail in `ADAPTIVE_BLOCK_BOUND.md` proves

```text
nonbinary size <(53/4)3^r/r.
```

The retained binary proof already bounds its router skeletons, shared controls, and fixed overhead separately by strict quantities below `1/4`, `1/4`, and `1/4`. Hence the complete conditional ledger is

```text
size  <14*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

The finite normalized maximum occurs at `r=88` and is approximately `13.037037037037036` before adding the binary branch.

## Claim boundary

The abstract first-mismatch/flip-flop monoid and balanced associative evaluation are classical. The candidate contribution is the exact embedding into this fixed parameter-free discriminator algebra, simultaneous all-branch materialization, fused signed-router construction, optimal leading coefficient for its mode vector, and the resulting conditional size-depth ledger.

This note does not claim an unconditional end-to-end compiler, serialized DAG extraction, practical performance, global complete-router optimality, novelty clearance, or freedom to operate.
