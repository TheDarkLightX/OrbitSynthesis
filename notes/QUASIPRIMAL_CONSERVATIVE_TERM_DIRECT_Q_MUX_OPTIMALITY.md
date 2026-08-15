# Scoped optimality of the five-node direct-Q multiplexer

Date: 2026-08-15  
Status: **exact bounded synthesis theorem**

## 1. Grammar

The terminals are

```text
x,b0,b1,b2,zero,one,two.
```

A new node is either

```text
u(a)
```

or

```text
d(a,b,c),
```

where every argument is a terminal or an earlier operation node. Fan-out is free. The output is one operation node.

The target function is

```text
Sel(x,b0,b1,b2)=b_x
```

on all `3^4=81` assignments.

The value-name terminals model the exact local interface used by the compiler. Globally, those terminals are the three shared roots supplied under the nonbinary anchor premise `A=2`.

## 2. Upper bound

The term

```text
d(
  d(zero,x,b0),
  zero,
  d(d(one,x,b1),one,d(x,two,b2))
 )
```

uses five discriminator nodes and computes `Sel`. Exhaustive evaluation checks all 81 rows.

## 3. Lower bound

For each exact node count `s=1,2,3,4`, the bounded synthesis instance contains:

- one operation tag per node, selecting `u` or `d`;
- legal predecessor selectors for every operand;
- the value of every node on each of the 81 rows;
- the defining `u` and discriminator equations;
- the target equation at the last node;
- irredundancy constraints requiring every earlier node to feed a later node; and
- duplicate-node symmetry breaking.

The irredundancy restriction is lossless for exact minimum size. Any circuit with an unused node can be pruned to a smaller circuit, and every smaller exact size is checked separately.

Z3 4.16.0 returns

```text
size 1: UNSAT
size 2: UNSAT
size 3: UNSAT
size 4: UNSAT
size 5: SAT.
```

The size-five satisfiable program is exactly the displayed witness, modulo syntactic naming.

Therefore:

**Theorem.** Five operation nodes are necessary and sufficient to realize the direct ternary selector in the declared original-signature DAG grammar with the three value names available as shared terminals.

## 4. Scope

This theorem does not imply:

- a five-node lower bound when additional primitive operations are admitted;
- a lower bound on an entire local library with cross-table sharing;
- global optimality of the size-8 compiler;
- global optimality of either size-depth Pareto point; or
- publication novelty.

It proves that the local selector node used at every direct-Q library and short-prefix tree is individually size-optimal under its exact interface.

## 5. Evidence

```text
script
  research/tournaments/2026-08-15-direct-q-pareto/check_mux_minimality.py

receipt schema
  orbit-synthesis/direct-q-mux-minimality/v1

semantic SHA-256
  f3c706a0b912e1a492bfefffe9ae0af33777ea2acd6d245d00212c3c24d6e45f
```

Normal and optimized receipts are byte-identical under the pinned solver package

```text
z3-solver==4.16.0.0.
```
