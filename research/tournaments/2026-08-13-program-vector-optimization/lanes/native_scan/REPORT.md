# Native sibling-shared program-vector lane

Date: 2026-08-13  
Verdict: **EXACT LOCAL THEOREM; independently audited; manuscript promotion pending formal cost and prior-art gates.**

For width `w>=1`, put `q=3^w`.  For either fixed signed-router root sign,
the exact address-only Boolean projection controls on the `A=2` branch have
an original-signature scalar shared `{d,u}` DAG with

```text
3 S(w) <= 4q + 15*3^ceil(w/2),
D(w)   <= 3+ceil(log_2 w).
```

Thus `S(w)=(4/3+o(1))q`.  The independent scalar-output census proves that
any DAG in this declared address-only model needs at least `4q/3` gates for
the P vector and `4q/3+1` for the N vector.  Consequently the leading size
constant is exactly `4/3` in this model.

This supersedes both the paper's `7q`, `6+2 ceil(log_2 w)` construction and
the intermediate direct-rail result `S<=(2+o(1))q`.

## Construction

Let `B_p` indicate that the first target/physical mismatch is a zero-mode
mismatch, `G_p` indicate the exceptional one-mode mismatch `(1,2)`, and
`N_p=not B_p`.  Adjacent segments compose in one parallel discriminator
layer:

```text
B_ab = d(B_a,G_a,B_b),
G_ab = d(G_a,B_a,G_b),
N_ab = d(G_a,B_a,N_b).
```

There are two exact sharing identities:

```text
G_(a s)=G_a          when s contains no physical digit 2,
N_(a1)=G_(a2).
```

The first canonicalizes all trailing `{0,1}` suffix classes.  The second
lets every eligible not-bad output point to an already materialized sibling
gain output.  Both are ordinary root reuse under the declared free-fanout
same-DAG convention; neither is a free gate or formula-size assertion.

The exact one-digit base uses four digit-specific operations beyond the two
shared names `one=u(A)` and `zero=u(one)`.  The implementation explicitly
charges every digit base, merge, name, and scalar output root.

## Exact recurrence

Let `a=ceil(w/2)`, `b=floor(w/2)`, `q_a=3^a`; let `B(w)` count the complete
`(B,G)` library and `C(w)` the complete `(B,G,N)` suffix library, excluding
the two global names:

```text
B(1)=C(1)=4,
B(w)=B(a)+B(b)+q+(q-q_a)/2,
C(w)=B(a)+C(b)+5q/3+(q-q_a)/2.
```

The final P/N vectors have exact materialized counts

```text
w:       1   2   3    4    5     6
P:       5  20  57  151  398  1098
N:       6  21  58  152  399  1099
```

Induction gives `B(w)<=7q/3`, `C(w)<=26q/9`, and the displayed finite-width
envelope.  The independent referee reconstructed these recurrences without
importing the candidate checker.

## Evidence

- `check_native_scan.py` builds and evaluates the exact hash-consed DAG.
- `check_optimal_scan.py` checks the exact recurrence through width 4,096 and
  the full target/physical semantics through width six.
- Normal and optimized runs are byte-identical.
- `OptimalRailSemantics.lean` proves the discriminator rail laws, one-digit
  bases, final control decoding, zero-gain reuse, and the sibling identity in
  Lean with warnings as errors and no placeholders.
- The independent referee report is
  `../referee/kuhn_boolean_rail_audit/REPORT.md`; its normal/optimized receipt
  SHA-256 is
  `250f9d5048d82fdef576e0fcb0d3d6260375b2e23e89280210cf4d5108c8212c`.

Frozen subject hashes:

```text
STATE.md                  6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6
check_native_scan.py      a41114a8f7bf21bd34d32b9fcc4b46e4558110de1aeb76817a071168c6d501e0
check_optimal_scan.py     02da40907d0495fbbc5e4d2a9420952c2676ece1229ed0fffbb22c757dda2b16
OptimalRailSemantics.lean 5ee931fcc1e442943203b1e893724ca045956cb7879e0b0562afa76f0081bd94
```

## Scope and nonclaims

The result is for one fixed P or N vector at a time, raw ternary address
terminals, `A=2`, scalar `{d,u}` nodes, a shared DAG, and free fanout.  It does
not prove the same bound for simultaneous P and N exposure, formulas,
bounded fanout, an arbitrary integrated router that avoids materializing
these controls, the full compiler constant, or practical running time.

Novelty, prior art, FTO, patents, copyright, and rights under the unsigned Tau
development license remain **UNKNOWN**.  No manuscript or previously frozen
tournament artifact was edited by this lane.
