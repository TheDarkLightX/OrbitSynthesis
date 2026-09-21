# Boolean-plane R9 routing for conservative Q-term DAGs

**Status:** manuscript theorem under independent review. The fixed R9 identity,
its two-plane transfer, and bounded composed compiler have deterministic
normal/optimized receipts and an independent no-solver audit. The all-arity
argument is not Lean-checked or peer reviewed. Novelty, optimality, practical
value, patent scope, freedom to operate, and any relationship to private Tau
work remain **UNKNOWN**.

## 1. Theorem

Let `Q=({0,1,2};d,u)`, with `d(x,y,z)=z` when `x=y` and `d(x,y,z)=x`
otherwise, and `u(0)=1`, `u(1)=0`, `u(2)=1`. Size counts operation nodes in a
parameter-free original-signature shared term DAG; fan-out is free and
variables have depth zero.

Every conservative `r`-ary term operation of `Q` has one such DAG with

```text
size  = O(3^r/r),
depth <= (3/2)r + O(r/log r).
```

With the syntax-counting lower bound this gives

```text
r-log_3(log r)-O(1) <= Delta_r(Q) <= (3/2)r+O(r/log r).
```

Neither endpoint is claimed optimal.

## 2. Exact Boolean R9

The router is a full depth-three ternary `d` tree with 13 discriminator nodes
and 27 leaves. Eighteen leaves are Boolean program controls and the other nine
are `b0,...,b8`, each occurring exactly once. There are nine fixed 18-bit
programs `p_j` satisfying

```text
R9(p_j;b0,...,b8)=b_j
```

for every `j` and every Boolean branch valuation. The frozen witness is

`research/tournaments/2026-08-13-router-frontier/lanes/capacity/boolean_q9_r8_radius1.json`

with byte SHA-256

`d3c25e47ce671d8a5d484d6c50cc0b3fccf7f6bb5507097ef8bff6bcbbbe529c`

and semantic SHA-256

`ae7f2fae8d16e64fc207b997c17424264d03c193d474f1ea6954a89f0c0bdb25`.

Because `d` commutes with simultaneous Boolean complement, the same router is
legal on the binary branch with program bit zero represented by `x_0` and bit
one by `u(x_0)`. No global Boolean constants are assumed there.

## 3. Two-plane transfer to Q

On the nonbinary branch the global anchor `A=2` legally names

```text
zero=u(u(A)), one=u(A), two=A.
```

Use the injective code

```text
0->00, 1->01, 2->10
```

and decode only after all route levels by

```text
Dec(high,low)=d(d(high,one,two),zero,low).
```

Run the same R9 program on the two Boolean planes in parallel. Each plane
therefore returns the same selected child's bit, and `Dec` returns that child's
`Q` value. This uses two ordinary sibling sub-DAGs, not a new multi-output
primitive. It changes the size constant but not routing depth.

## 4. Balanced-code compiler and size

For a finite address set of size `N`, recursively split each nonsingleton block
into `min(9,N)` nonempty balanced parts. The code has height at most
`ceil(log_9 N)` and at most `N-1` internal nodes. At one level, active nodes
partition the address set; their child digits combine into one total digit
function, so a single family of 18 compiled controls is shared across that
level and across both bit planes. For successive chunks with cumulative sizes
`P_j`, router counts telescope as

```text
sum_j P_(j-1)(N_j-1)=P_m-1.
```

Choose the local block exactly as in the programmable-depth compiler:

```text
H=max(1,floor(log_3(3^r/r))),
M=3^b, the largest power of 3 with M<=H,
P=3^(r-b).
```

For a local library on `t` block assignments, two R9 copies charge 26
discriminator nodes per generated `Q`-valued function. Balanced splitting
gives

```text
G(1)=0,
G(t)=26*3^t+sum_i G(t_i),
G(t)<=78*3^t.
```

The prefix contributes at most `26(P-1)` router nodes. Compile the 18 shared
control functions on ternary chunks of width `ceil(log_3 r)`. Each costs
`O(r)`, and there are `O(r)` route levels, so preprocessing is `O(r^2)`.
The two planes, one decoder, the global anchor, the binary branch, and final
selector therefore fit in `O(3^r/r)` nodes on the same DAG.

## 5. Depth

Let `L_9^Q` be the sum of nine-way code heights over the local block and all
ternary prefix chunks, and `L_9^B` the corresponding sum over complement-
relative binary chunks. Then

```text
L_9^Q <= log_9(3)r+O(r/log r) = r/2+O(r/log r),
L_9^B <= log_9(2)r+O(r/log r).
```

The two planes are parallel, each R9 adds three dependency layers, and the
decoder is applied once. Anchor and control preprocessing contribute only the
displayed lower-order term. Hence

```text
D_nonbinary <= (3/2)r+O(r/log r),
D_binary    <= (3*log_9(2))r+O(r/log r).
```

Since `3*log_9(2)=0.9463946303...`, the nonbinary branch dominates.

## 6. Serial-router barrier

For any declared serial router grammar with primitive capacities and charged
depths `(q_i,h_i)`, set

```text
rho=max_i log(q_i)/h_i.
```

Assign a leaf at accumulated depth `D` weight `exp(-rho D)`. At a node using
primitive `i`, the sum of child weights is at most
`q_i exp(-rho h_i)<=1` times its weight. Induction gives total leaf weight at
most one. If every leaf has depth at most `D`, then a tree with `N` leaves
satisfies

```text
N exp(-rho D)<=1,
D>=log(N)/rho.
```

Thus unbalanced, variable-depth, Huffman-like, arithmetic-like, nonuniform,
or mixed serial compositions of the known R6/R7/R8/R9 primitives cannot beat
R9's rate `log(9)/3`, and their lifted nonbinary coefficient cannot beat
`3/2`. This is a theorem only about the declared serial grammar, not a global
lower bound for all `Q`-term DAGs. A better coefficient needs a higher-rate
atomic or fused router, or a nonserial cross-level construction.

## 7. Deterministic evidence

`experiments/quasiprimal_boolean_r9_routing.py` checks:

- all 4,608 Boolean R9 projections and 9,216 relative-orientation cases;
- all 177,147 target/word cases for the local `Q` lift;
- decoder identities and an effective program mutation;
- all 128 compatible arity-two selector tables plus fixed-seed tables through
  arity five, totaling 135 tables and 1,641 full-tuple evaluations;
- the local-library recurrence through 256 points and structural depth
  arithmetic through arity 4,096; and
- rejection of serial-plane, per-node-control, repeated-decoder, omitted-
  decoder, and non-complement-invariant-table mutations.

Normal and optimized runs agree at semantic SHA-256

`e4a09ef72986c1221c28e80d8227879a9e0aa0f93679e49e9f750f7e65977fce`.

The self-binding v2 receipt is
`runs/quasiprimal_boolean_r9_routing/summary.json`; it records the checker and
dependency hashes, exact replay commands, and required normal/optimized
relation. The
independent no-solver audit is
`research/tournaments/2026-08-13-router-frontier/audits/capacity/audit_r9.py`.
The independent integrated-compiler audit is
`research/tournaments/2026-08-13-router-frontier/audits/compiler/REPORT.md`
with SHA-256
`22b2fe1d6326edb7f396897a4abdf7dda1f0762c9159722978c0c2b8b2ef707e`.
Finite replay validates the implementation and bounded arithmetic; it does
not prove the generic theorem.

## 8. Negative frontier and nonclaims

A complete search of the 18 one-leaf insertions of a tenth branch into the
frozen R9 found no R10. That is a radius-one `NO_HIT`, not a global R10
impossibility result. Wider searches and solver timeouts remain `UNKNOWN`.

The two-Boolean-plane representation, multiplexing, local coding, and
many-valued circuit synthesis all have substantial classical literature. The
paper candidate is the exact fixed-`Q`, parameter-free, original-signature
same-DAG specialization and coefficient, subject to a complete prior-art
review. Do not currently claim:

- that R9 is capacity-optimal at depth three;
- that `3/2` is a global optimal depth coefficient;
- practical small-arity improvement;
- an ordinary unshared-tree bound;
- the same theorem for arbitrary quasi-primal algebras;
- Lean verification, peer review, publication novelty, patent freedom to
  operate, or rights under the unsigned Tau developer license; or
- any result about private Tau capabilities.

All construction inputs are public mathematics and independently written
OrbitSynthesis artifacts. No Tau code, private specification, confidential
communication, or license term was used. This is provenance, not legal advice.
