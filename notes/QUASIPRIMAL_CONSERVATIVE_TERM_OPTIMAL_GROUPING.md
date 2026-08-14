# Exact balanced-group optimization and a `123/50` fixed-Q compiler

**Status:** exact manuscript strengthening, 2026-08-14. This note is stacked
on the recursive Boolean-library compiler. It changes no algebraic gadget,
program vector, anchor, binary branch, decoder, or glue. It removes a residual
integer-rounding loss by choosing the exact best balanced group count in the
finite arity range and retaining the preceding analytic schedule in the tail.

A primary checker and a separately written no-import reconstruction verify the
optimizer, all finite ledgers, analytic tail, and depth theorem. The result is
not yet formalized end to end in Lean or externally peer reviewed. Novelty and
legal conclusions remain **UNKNOWN**.

## 1. Result

For every `r>=64` and every `f in CT_r(Q)`, there is one parameter-free
original-signature free-fanout scalar DAG with

```text
size < (123/50)*3^r/r.
```

Writing `C=ceil(log_2 r)`, the depth bound remains

```text
depth <= r+C+2*ceil((4C+2)/3)+15.
```

The previous clean global constant was `62/25=2.48`. The exact charged ratio
in the new construction is maximal at `r=65`:

```text
2.456979991212798512...
```

The local fixed-sign program-vector theorem remains unchanged and retains its
matched leading scalar-output constant `4/3`.

## 2. Exact balanced-group cost

Fix an arity `r` and local width `t`. Put

```text
N=3^t,
s=r-t,
P=3^s.
```

Partition the `N` local rows into `g` balanced groups. Write

```text
q=floor(N/g),
a=N-qg.
```

There are `a` groups of size `q+1` and `g-a` groups of size `q`. The total
number of Boolean-table roots charged by the recursive libraries is therefore

```text
E_N(g)=a*2^(q+1)+(g-a)*2^q
      =(N-(q-1)g)*2^q.
```

The part of the global node ledger depending on `g` is

```text
F_(r,t)(g)=4t*E_N(g)+5t+g*(3P-1).
```

## 3. Quotient-interval optimizer

For fixed `q`, the condition `floor(N/g)=q` defines one integer interval

```text
floor(N/(q+1))+1 <= g <= floor(N/q).
```

On this interval,

```text
F_(r,t)(g)
 =4tN2^q+5t
  +g*((3P-1)-4t(q-1)2^q),
```

so it is affine in `g`. Its minimum on the interval is therefore attained at
one of the two endpoints.

The exact optimizer enumerates the distinct quotient intervals and checks
only their endpoints. There are `O(sqrt N)` such intervals. It returns the
least minimizing `g`, making the schedule deterministic.

The checker compares this endpoint algorithm with brute force for 4,000 small
instances. A mutation that checks only lower endpoints fails at

```text
N=8, t=1, P=3:
correct g=4, cost=101;
lower-endpoints-only g=3, cost=109.
```

## 4. Compiler schedule

Let `J` be maximal with

```text
9r^3*2^J <= 3^r,
```

and put

```text
T=floor(log_3(rJ)).
```

For `64<=r<=339`, evaluate the five local widths

```text
t=T+delta,
delta in {-2,-1,0,1,2},
```

using the exact quotient-interval group optimizer for each width, and select
the least exact charged ledger.

For `r>=340`, retain the already proved analytic candidate

```text
t=ceil(log_3(rJ)),
g=ceil(3^t/J).
```

This candidate belongs to the five-width portfolio and requires no new tail
analysis.

## 5. Size proof

### 5.1 Finite exact range

For every integer `64<=r<=339`, the checker constructs all five width
candidates, exactly minimizes every balanced group count, and verifies

```text
50*size*r < 123*3^r.
```

The maximum occurs at `r=65`, with the ratio displayed in Section 1.

At that arity the chosen parameters are

```text
t=7,
g=26,
```

with balanced groups of 84 and 85 rows. The prior schedule used 27 groups of
81 rows; exact optimization trades a slightly larger recursive library for a
smaller dominant prefix-router term.

### 5.2 Analytic tail

For `r>=340`, use the preceding recursive-library tail candidate. Its proved
normalized bound is

```text
2 + 26/(9r) + (3r+1)/(36r) + 4/1000.
```

At `r=340` this is already strictly below `123/50`, and the variable terms
decrease thereafter. Thus the same analytic proof closes the entire tail.

## 6. Depth

Changing the number of balanced groups changes only how many parallel roots
are materialized. It adds no router level. The finite optimizer and analytic
tail therefore retain the previous bound

```text
r+C+2*ceil((4C+2)/3)+15.
```

## 7. Evidence

Primary checker:

`research/tournaments/2026-08-14-optimal-grouping/check_optimal_grouping.py`

It verifies:

- the exact balanced-table formula;
- endpoint optimization against brute force on 4,000 small instances;
- an effective one-endpoint mutation;
- all five optimized finite ledgers through arity 339;
- the analytic tail through arity 16,384;
- the unchanged depth theorem; and
- normal/optimized byte equality.

A second checker independently reimplements the quotient-interval optimizer,
rail recurrences, finite portfolio, binary branch, tail proof, and depth
ledger.

```text
primary checker SHA-256
  a9c9027241443e46363b0263bd3608db26ebc5fd1663396187a0bc0935334ca0
primary receipt/stdout SHA-256
  f8a28355b38c8feacfeaced7e3c4faab6e3992e2b6ec744ed4ae49c46da5473f
primary semantic SHA-256
  9a4aeadad1d07406b7eaa0f7bc22b9df5c3f6f6fb0d2912a470707784cd75e87

independent checker SHA-256
  37d7ca02b941f8116150bbaed0c4201bf2260e0bf8be35e2d296a1ca83e99b0b
independent receipt/stdout SHA-256
  6585b18f4d67dac5d343372d531ee7753055767c3f542d7942fa67c81b0cc90d
independent semantic SHA-256
  8c86365240f969b7bc3639c5167b36c8b7a78b8f253e65e747b98d533b8c49b5
```

## 8. Boundaries

This theorem does not alter the local `4/3` program-vector constant, prove a
matching global lower constant, determine the exact global optimum, or settle
the optimal additive depth term. It gives no formula or bounded-fanout theorem
and makes no novelty or legal conclusion. The integrated construction is not
yet serialized and proved end to end in Lean.
