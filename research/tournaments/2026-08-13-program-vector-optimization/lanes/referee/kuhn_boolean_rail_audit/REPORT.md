# Fresh-room audit: Kuhn Boolean rails and native sharing

Date: 2026-08-13  
Verdict: **PASS for the local program-vector theorem; READY FOR LOCAL PROMOTION with the exact scope below.**

## Executive finding

Kuhn's direct Boolean-rail construction is correct.  For either fixed root
sign it builds all `2q`, `q=3^w`, scalar controls in one original-signature
shared DAG, charges `one=u(A)`, `zero=u(u(A))`, every rail node, and every
negative-cell complement, and has

```text
size <= 3q,
size = (2+o(1))q,
depth <= 4+ceil(log_2 w)                 (w>=1).
```

The reported scalar-output lower bound is also correct in its declared
grammar:

```text
P sign: at least 4q/3 operation nodes,
N sign: at least 4q/3+1 operation nodes.
```

It is an address-only scalar-output lower bound, not a lower bound for an
arbitrary integrated router that need not materialize this exact vector.  The
additional `D+1` strengthening is bounded evidence (and exact at width one),
not an all-width theorem.

The native-scan counts are genuine DAG savings, not missing outputs or a
truth-table-counting artifact.  More strongly, the current native-scan bytes
already implement two exact canonicalizations:

1. reuse the left gain root when the right gain root is literally `zero`; and
2. reuse the already materialized sibling root in `N_(a1)=G_(a2)`.

Consequently the current construction is not merely `(3/2+o(1))q`.  Its exact
recurrence gives

```text
size = (4/3+o(1))q,
size <= 7q/3,
depth <= 3+ceil(log_2 w).
```

The apparent ratio near `1.5` at the checked medium widths is transient.  For
example, the current P counts are `20,57,151,398,1098` at widths `2,...,6`;
`1098/729=1.506...`, but the proved leading coefficient is `4/3`.

## Frozen subject and drift

The audit fail-closed when both candidate scripts changed during review.  This
report concerns the later, re-pinned bytes only:

| artifact | SHA-256 |
|---|---|
| `STATE.md` | `6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6` |
| Kuhn/lower-bound checker | `3b02d4cd842e7b8b252a38b3cdcb4fb2fc6044cf04f72b0b0250709a6cda2785` |
| native-scan checker | `a41114a8f7bf21bd34d32b9fcc4b46e4558110de1aeb76817a071168c6d501e0` |
| optimal-scan recurrence checker | `02da40907d0495fbbc5e4d2a9420952c2676ece1229ed0fffbb22c757dda2b16` |
| independent audit checker | `dfdb50e08025aa63cbd2d7bd0263b40c54bf9a82c36dbd9a7f5e519ee74a34c6` |

The earlier native snapshot inspected at hash
`6820316242ad74c4d7ff0c0de7662ae3b55e522a52aa284a9beb5165b6f57e08`
did not perform zero-gain reuse.  Its actual recurrence really was
`(3/2+o(1))q`.  Thus that observation was mathematically real, but it has been
superseded by the current bytes.

An intermediate snapshot at
`dec1ce29bcbcb3d206ef7e3228e29e27feba46add91c9ad9e1189411bdeec490`
obtained the same `4/3` recurrence through syntactic hash-consing.  The current
snapshot makes the nested sibling reuse explicit in a two-pass BGN build.

## 1. Direct-rail reconstruction

Write `B_p` for the bad/zero-mode bit, `G_p` for the gain/one-mode bit, and
`N_p=1-B_p`.  For adjacent segments the exact Boolean composition is

```text
B_(ab) = d(B_a,G_a,B_b),
G_(ab) = d(G_a,B_a,G_b).
```

If `G_b` is the zero node, the second expression equals `G_a`, so reusing that
root is legal free fanout, not a free gate.  The one-digit bases use four
original-signature gates.  With `a=floor(w/2)`, `b=ceil(w/2)`, the exact rail
count excluding the two names is

```text
R(1)=4,
R(w)=R(a)+R(b)+q+3^a(3^b-1)/2.
```

There are `q` distinct bad roots and `(q+1)/2` gain functions.  At the top
level the new bad roots cost `q`; the nonzero right-gain classes cost
`3^a(3^b-1)/2`.  For P there are `(q-1)/2` negative cells, and for N there are
`(q+1)/2`; each direct construction explicitly charges the corresponding
`u(B_p)` node.  Hence

```text
S_P(w)=2+R(w)+(q-1)/2,
S_N(w)=2+R(w)+(q+1)/2.
```

Induction from the small bases gives `R(w)<=7q/3`; the balanced recurrence
also gives `R(w)=3q/2+O(3^ceil(w/2))`.  The displayed size claims follow.
The base rails have depth at most three, every balanced merge adds one, and
the final complement adds at most one, proving the depth bound.  Width zero
has the explicit two-name fallback.

No same-DAG charge was dropped: the audit counted reachable operation nodes,
not just rail functions.  It checked both fixed signs separately.  This does
not claim that one DAG of the same size simultaneously exposes both signs'
four-output-per-cell vectors.

## 2. Exact native recurrence

Let `a=ceil(w/2)`, `b=floor(w/2)`, `q_a=3^a`, and let `B(w)` and `C(w)` be the
operation counts excluding the two names for the canonical `(bad,gain)` and
`(bad,gain,not-bad)` segment libraries.  The current construction satisfies

```text
B(1)=C(1)=4,
B(w)=B(a)+B(b)+q+(q-q_a)/2,
C(w)=B(a)+C(b)+5q/3+(q-q_a)/2.
```

Reason:

- all `q` bad roots are distinct;
- canonical gain roots are indexed by zero plus the prefix ending at the last
  physical digit `2`, so there are `(q+1)/2` of them;
- only nonzero right-gain classes need a new merge gate, costing
  `q_a(3^b-1)/2=(q-q_a)/2`;
- all `q` not-bad functions are distinct; and
- exactly `q/3` of them are already gain roots, by `N_(a1)=G_(a2)`.

At the final vector, every gain with a zero right suffix reuses a child root.
The requested non-gain output is bad on positive cells and not-bad on negative
cells.  Its overlap with the gain family has size

```text
P: (q/3+1)/2,
N: (q/3-1)/2.
```

Therefore, for `w>=2`, the exact reachable counts including both names are

```text
V_P(w)=2+B(a)+C(b)+4q/3-q_a/2-1/2,
V_N(w)=2+B(a)+C(b)+4q/3-q_a/2+1/2.
```

At width one they are `5` and `6`.  Elementary induction gives
`B(w)<=7*3^w/3` and `C(w)<=26*3^w/9`; inserting half-width arguments proves
`V_P,V_N=(4/3)q+O(3^ceil(w/2))` and the uniform `7q/3` bound.  All fractions
above combine to integers because every relevant power of three is odd.

The advertised finite-width envelope is also valid:

```text
3V(w) <= 4*3^w + 15*3^ceil(w/2).
```

For `w>=3`, substitute `B(a)<=7*3^a/3` and
`C(b)<=26*3^b/9`, use `3^b<=3^a`, and retain the negative
`-3^a/2` term in `V`; the residual is at most `5*3^a` (the N
constant is absorbed already at `3^a>=9`).  Widths one and two are direct
bases.  Thus the 4,096-width arithmetic replay is validation of an induction,
not the source of the all-width quantifier.

The current construction has exactly as many distinct output root IDs as
distinct requested scalar functions.  It does not merge merely
truth-table-equivalent syntax after the fact: zero-gain cases point to an
existing prefix node, and negative `a1` cases point to the already built
`a2` gain node.  All remaining savings are ordinary syntactic hash-consing.

## 3. Scalar-output lower bound

The gain family has

```text
|{G_p}| = 1+sum_(j=0)^(w-1) 3^j = (q+1)/2.
```

This is not inferred from a bounded census.  Under the three target-first
blocks, the recursions are

```text
G_(0r)=(G_r,0,0),  G_(1r)=(0,G_r,0),  G_(2r)=(0,1,G_r),
N_(0r)=(N_r,0,0),  N_(1r)=(0,N_r,0),  N_(2r)=(0,1,N_r).
```

With bases `G_empty=0`, `N_empty=1`, block comparison proves inductively that
`N_p=G_s` exactly when `p=a1,s=a2`.  It also proves that gain classes are zero
plus prefixes ending at their last physical `2`.

The other requested output chooses `B_p` or `N_p` according to the physical
parity and root sign.  These `q` mixed functions are pairwise distinct.  The
only gain/not-bad coincidences are

```text
N_(a1)=G_(a2).
```

Even/odd ternary-parity prefixes number `(3^(w-1)+1)/2` and
`(3^(w-1)-1)/2`, yielding the two overlap counts above.  Inclusion-exclusion
then gives exactly `4q/3` distinct P controls and `4q/3+1` distinct N
controls.

For completeness, the analogous bad blocks are
`(B_r,1,1)`, `(1,B_r,1)`, and `(1,0,B_r)`.  They make the bad and not-bad
families separately injective.  Cross equality is impossible from width two
on; the two width-one cross equalities pair physical `0` with `2`, which have
the same parity.  Hence choosing bad versus not-bad by parity cannot collapse
two members of the mixed family.  This closes the claimed all-width `q`
census.

Every such control is Boolean-valued.  The free raw terminals in the declared
grammar are constant `A=2` and the Q-surjective address coordinates, so none
is a desired control.  A scalar operation node can root only one scalar
function.  The distinct-control counts are therefore valid gate lower bounds.

This argument does **not** establish an all-width extra `+1`.  The independent
semantic-set BFS confirms exact minima `5` (P) and `6` (N) at width one; the
candidate's target-only closure gives further bounded evidence.  It also does
not cover circuits with extra terminals, vector-valued primitive gates, or an
integrated router that avoids exposing these exact controls.

## 4. Legality and killer checks

| attack | result |
|---|---|
| all `2q` outputs | present and evaluated exhaustively through width six |
| both signs | P and N replayed independently; counts differ by exactly one |
| names | both `u(A)` and `u(u(A))` charged; absolute interpretation requires `A=2` |
| address representation | raw Q address variables are terminals; all per-digit base gates are charged |
| fanout | only explicit root reuse is free; no bounded-fanout claim is made |
| final pairs | gain plus the sign-selected bad/not-bad root are both included |
| constants | both Boolean constants and both signs checked; at most the two name nodes |
| depth | computed above raw `A,t_i`; sibling reuse does not add depth |

Effective smallest attacks include:

- reusing the left gain for a nonzero right gain fails already on left state
  `(bad,gain)=(0,0)` and right state `(0,1)`;
- ignoring the physical sign fails at `w=1`, P root, target `0`, physical `1`;
- using `A=0` or `A=1` destroys the absolute names;
- the false mutation `N_(a0)=G_(a2)` fails at target `0`; and
- treating the distinct-output lower bound as a complete construction fails
  at width one (`4` versus minimum `5` for P, `5` versus `6` for N).

## 5. Promotion gate

The local mathematics is ready after one documentation repair:

1. replace any proposed `(3/2+o(1))q` description of the **current** native
   bytes by the exact recurrences above and `(4/3+o(1))q`;
2. say “for either fixed P/N root sign” rather than implying simultaneous
   exposure of both signs at the same cost;
3. keep the lower bound explicitly scoped to address-only scalar control
   materialization; and
4. do not promote a global `D+1`, exact lower-order optimum, integrated
   compiler, novelty, FTO, or formula/bounded-fanout claim.

The frozen native checker currently advertises only the older loose
`2q+O(3^ceil(w/2))` analytic bound.  That statement remains true.  The new
`check_optimal_scan.py` correctly states the sharper recurrence envelope and
scope, while its 4,096-width loop alone is finite evidence; the induction in
this report closes the all-width step.  The independent checker and receipts
below close the local replay, not the manuscript-integration or prior-art
gates.

## Evidence

- `audit_boolean_rails.py`: no-import reconstruction and exact recurrence audit.
- `receipt.json`: normal interpreter run.
- `receipt_optimized.json`: `python -O` run, byte-identical to the normal receipt.
- `7,174,440` scalar semantic comparisons through width six.
- `4,372` constant-cell checks.
- structural and root-sharing checks through width nine.
- recurrence inequalities checked through width 4,096, in addition to the
  all-width induction above.

Both receipts have SHA-256
`250f9d5048d82fdef576e0fcb0d3d6260375b2e23e89280210cf4d5108c8212c`
and semantic SHA-256
`1be842ffaca9c0510834e0eac1ee38f0acc6c310d15bb954c1a76c24dcc6f342`.

The subject optimal-scan normal and optimized receipts are also byte-identical,
with SHA-256
`e16a27ec5c338ab69ff77c57eb0d48dec38e43a49057da2e6314c9440bc7f5d7`.
