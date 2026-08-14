# Plane-shared Boolean-library compiler

Date: 2026-08-14  
Verdict: **PASS for the plane factorization, four-candidate construction,
exact finite proof, analytic tail, and depth ledger.**

## Result

For every `r>=64` and every conservative parameter-free `r`-ary term
operation of the fixed algebra `Q`, the construction in this lane gives one
original-signature free-fanout scalar DAG with

```text
size  < (67/25)*3^r/r,
depth <= r+ceil(7*ceil(log_2 r)/5)+20.
```

The exact charged ratio over `64<=r<=16384` is maximal at `r=64`:

```text
2.679666803224281973...
```

The previous explicit constant was `46/5=9.2`. The local signed-router
program-vector theorem is unchanged and retains its matched leading
scalar-output constant `4/3`.

## New sharing principle

The legal Q code is

```text
0 -> 00, 1 -> 01, 2 -> 10.
```

Although there are `3^M` Q-valued tables on an `M`-row local slice, every
individual high or low plane belongs to the same family of only `2^M`
Boolean tables. The construction materializes each Boolean table once. A Q
table is an ordered pair of two already existing scalar roots. Pairing roots
is wiring, not an operation node.

A padded capacity-`N` group with `M` live rows therefore costs at most

```text
((3N-1)/2)*2^M
```

router nodes, replacing the old per-Q-table two-plane charge.

## Portfolio

Let `J` be maximal with `9r^3 2^J<=3^r`, put `K=J-3`, and let `m=3^b` be the
largest power of three not exceeding `K`. Four explicit candidates use

```text
c in {2,3,4,5},
t=b+c,
d=min(7,t),
u=3^(t-d),
h=floor(K/u),
g=ceil(3^d/h).
```

The `3^d` splitter words are partitioned into `g` balanced groups, so every
group has at most `K` live rows. Each candidate has an exact charged ledger;
the smallest is selected, with deterministic tie-breaking.

## Proof split

For `64<=r<=966`, all four candidate ledgers are constructed with exact
integers and the target inequality is checked directly. The maximum is the
`r=64` row above.

For `r>=967`, the `c=4` candidate alone gives an analytic proof. Its local
Boolean library is below

```text
2187/(8r)
```

Shannon units. The prefix main term is bounded by a finite 54-case integer
maximum

```text
20935/8748
```

at `(h,g)=(78,29)`. Four lower-order groups contribute less than `4/1000`.
The exact rational comparison

```text
20935/8748 + 2187/(8*967) + 4/1000 < 67/25
```

closes the tail.

## Evidence

The primary checker verifies:

- plane factorization and Boolean-library saturation through six rows;
- 1,728 grouped selector-reconstruction rows;
- effective plane and wrong-group mutations;
- all four candidate ledgers through arity 16,384;
- the exact finite proof and analytic tail separately;
- the 54-entry prefix maximum;
- the depth ledger; and
- normal/optimized byte equality.

A second no-import checker independently reconstructs the planes, rail
recurrences, portfolio, binary branch, finite proof, analytic tail, and depth
ledger.

```text
primary checker SHA-256
  872134ae213cc43f42649eaec76e31f0ef18df4a2751e05c0a3ba38334f7cdfe
primary stdout SHA-256
  d8a6477819d058ee468738a9c66a65c93697f7d1367b2b4402c4871792120977
primary semantic SHA-256
  b98aa602a17208dcb9b0af22bab96e65a02e4888f6293d23b6b59aa7442a4f16

independent checker SHA-256
  9c0900bfb2d7a72e4be5c0b3b8bc0509da9e1b3b54c6b2abb7766d68cc3a6b04
independent stdout SHA-256
  bdade906dc2e92049019157d611e5f4d27deb5590316ecb0a8578160a23f0f9b
independent semantic SHA-256
  b96a891f6e94a5d5d4aefa1b1efd20ebe31583347244746c225329b3fca7ab95
```

## Boundary

This lane proves no matching global lower constant, exact global optimum,
formula or bounded-fanout theorem, or optimal additive-depth term. The
integrated construction is not yet serialized and proved end to end in Lean.
The lane makes no novelty, patent/FTO, license, publication, or practical
performance finding.