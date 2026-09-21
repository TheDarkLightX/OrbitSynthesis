# Semantic-router frontier reduction

Date: 2026-08-13

## Verdict

The tournament produced an **exact, independently audited, Lean-checked local
breakthrough** and a **conditional all-arity compiler theorem**.

The exact result is a signed discriminator-router family together with a
balanced parallel program vector.  For width `w>=1` and `q=3^w`, all `2q`
program controls are realized in the original constant-free `{d,u}` signature
from a nonbinary anchor and address digits with

```text
shared-DAG operation nodes <= 7q,
depth <= 6+2*ceil(log_2 w).
```

The node bound includes the two shared dynamic value-name nodes.  It is a
shared-DAG/free-fanout theorem, not an ordinary formula or bounded-fanout
claim.  The exact E/G first-mismatch semantics, sign parity, legality, size,
and depth recurrence are independently audited and Lean-checked.

Conditional on the explicit interface propositions (I1)--(I7) stated in the
manuscript and authoritative note--covering the selector table, anchor,
two-plane representation, binary-relative branch, same-DAG substitution,
decoder, small-arity fallback, and exact three-node glue--the same construction gives

```text
size  = O(3^r/r),
depth = r+O(log r)
```

on one parameter-free original-signature DAG.  The arithmetic ledger has an
independent conditional pass, but the complete compiler has not been
independently reconstructed without importing those premises.  It must remain
labelled **conditional**.

## Winning mechanism

The recursive positive/negative routers are

```text
P_1=d(x,c0,c1),            N_1=d(c0,x,c1),
P_h=d(P_(h-1),N_(h-1),P_(h-1)),
N_h=d(N_(h-1),P_(h-1),N_(h-1)).
```

They have `3^(h-1)` branch variables, `2*3^(h-1)` controls, depth `h`, and
exact positive/negative projection and constant modes.  The negative sign is
created by odd middle-edge parity; there is no free NOT gate.

For target word `t` and physical word `p`, define

```text
E=[t=p],
G=[the first mismatch is (t_j,p_j)=(1,2)].
```

The positive bottom pair is `(not(E or G),G)` and the negative pair is
`(G,E or G)`.  Balanced segment composition uses

```text
E_AB=E_A and E_B,
G_AB=G_A or(E_A and G_B).
```

Sharing the two child vectors once at every merge removes the sequential
`Theta(qw)` control bottleneck and yields the linear-in-q node bound with
logarithmic-in-w depth.

## Acceptance evidence

- Author signed-family replay: summary SHA-256
  `6042127fd9f214e63bc38aa8e6367d1db7580c24b2b2e7a3aeba16625279aff0`;
  R27 witness SHA-256
  `6dd402fd32bb560b341ee75805bd71c90e2fa2bd3c9274c982f908ef21c15e65`.
- Independent signed-family audit: receipt SHA-256
  `41ebde43fb3dee99b995224670d607bba331aa498cb49fca477802b4aea632a8`.
- Author program-vector replay: normal/optimized receipt SHA-256
  `c9e8b1ad9c57f4ef55ea458b2573f20578a137a6c7b5fb1a66707bb7ee68b632`.
- Independent program-vector audit: normal/optimized receipt SHA-256
  `f6af15d3b5a8330a0f8248f9ffa5410dd1dfc762a89dbc20ecfe0d21aee714b8`.
- Lean router source SHA-256
  `687a77ed1f3b0bfe2a540bc670f6db942e15bddc339ccfbceffba9699766227a`.
- Lean vector semantics source SHA-256
  `c2f477edd110c4df96f3c30f31f02de09af93045720babfd38dd2dd79a5573dd`.
- Lean cost/legality source SHA-256
  `ea516b085cdedd3f0ee70f83a9d0240df55e7e68cf0ad8ce77558efd91db55d2`.
- Classical-transfer report SHA-256
  `e1ed0a4934810c81e74bf09805fb7f80885a3aa43fc9f7650ecbc553911a6888`.
- One-command portable gate:

  ```text
  python3 experiments/audit_fixed_q_preprint.py
  ```

  It replays normal and optimized evidence, both independent audits, the
  compiler ledger, the classical-transfer falsifiers, and the three Lean
  layers.

## Prior-art decision

Gashkov's 1978 Boolean theorem preserves the formula-Shannon scale
`Theta(2^n/log n)` while reaching depth `n-log_2(log_2 n)+O(1)`.  A checked
dense Booleanization of the ternary addresses has leading depth
`log_2(3)r>r` and source-witness size `Theta(3^r/log r)`, so it does not
directly imply the fixed-Q same-DAG theorem.  This nontransfer is not novelty
evidence.  A native Q-valued Lupanov--Gashkov decomposition and a model-complete
reading of Lupanov's separate delayed-circuit theorem remain open.

No exact match was verified in the bounded Russian, Chinese, and international
search.  Novelty and freedom to operate remain **UNKNOWN**.

## Preserved negative knowledge

- On Booleans, `d(x,y,z)=majority(x,not y,z)`, not ordinary majority.
- Positive-polarity depth-three routers have exact capacity nine in their
  scoped grammar; this does not bound mixed-sign or deeper families.
- Serial mixtures of fixed R6/R7/R8/R9 routers cannot beat their best primitive
  rate in the declared serial grammar; the winning vector is nonserial.
- Residual-last growing chunks break the size ledger at `r=512`; residual-first
  ordering repairs it.
- Sequential `Theta(qw)` program generation loses the target size order.
- A one-logarithm local-library reserve fails at a concrete large arity.
- Bounded `NO_HIT`, grammar-specific UNSAT, solver timeout, and failed search
  are not generic lower bounds or novelty evidence.

## Publication gate

Before a public preprint:

1. preserve the completed fresh internal-agent referee report, and obtain an
   external human referee review if practicable before journal submission;
2. keep the exact local theorem primary and the compiler explicitly
   conditional, as in the repaired manuscript, unless the full compiler is
   later reconstructed end to end;
3. complete the primary-source comparison with Lupanov's delayed-circuit
   model and strengthen Russian/Chinese coverage;
4. settle authorship and affiliations;
5. if patent protection might be desired, obtain legal advice before public
   disclosure; and
6. publish a versioned source/proof/receipt archive, not only a prose PDF.

This reduction makes no claim about private Tau capabilities, rights under an
unsigned developer license, patent freedom to operate, practical small-arity
speed, or an optimal additive depth term.
