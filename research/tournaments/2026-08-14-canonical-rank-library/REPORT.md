# Canonical-rank Boolean-library compiler audit

Date: 2026-08-14  
Verdict: **PASS for the semantic factorization, exact charged construction,
finite proof, analytic tail, and deterministic replay.**

## Result

The fixed-Q compiler can share one Boolean-function library across every local
group by explicitly materializing the canonical rank and group number of the
local address. For every `r>=64`, this gives one parameter-free
original-signature free-fanout scalar DAG with

```text
size < (12/5)*3^r/r.
```

Writing `C=ceil(log_2 r)`, the same DAG has

```text
depth
 <= r+C+ceil(2(C+1)/3)+2ceil(log_2(C+4))+23.
```

The exact checked size ratio is maximal at `r=64`:

```text
2.391548842960882081...
```

This is a size/depth Pareto point. The parent plane-shared construction keeps
a smaller explicit additive-depth bound; the present theorem does not combine
that separate DAG's depth with this DAG's smaller size.

## Canonical-rank factorization

For balanced local groups `G_i`, define `rho(y)` as the rank of `y` inside its
group and `gamma(y)` as its group number. Every Boolean group table is a
padded Boolean function of `rho`. Hence all groups share one library of
`2^M` scalar roots, where `M=max_i |G_i|`. Every Q-valued group table is an
ordered pair of references to that shared family.

The `w` rank digits and `e` group digits are legal Q-valued functions of the
raw local address. Each digit uses two signed routers and one decoder, so the
complete map costs `(w+e)(3N+1)` nodes. One rank router per Boolean function
costs `((3R-1)/2)2^M`. Group-specific prefix routers and one final group
selector complete the construction.

## Proof ledger

The exact schedule is

```text
J=max{j:9r^2*2^j<=3^r},
K=J-3,
m=3^b<=K<3m,
t=b+5,
d=9,
u=m/81,
h=floor(K/u),
g=ceil(19683/h),
M=ceil(19683/g)u.
```

Exact integer replay proves the bound for `64<=r<=267`. From `r=268`,
`K>=3r/2`, so `81<=h<=242`. The exact prefix maximum is

```text
361982/177147
```

at `h=240`, `g=83`. The universal rank library is below `1/8` Shannon unit,
and five lower-order groups contribute below `5/1000`. Their sum is below
`12/5`.

## Replay

The primary checker verifies:

- canonical rank and group maps;
- Boolean-function sharing across unequal group sizes;
- Q high/low root pairing;
- 1,728 selector reconstruction rows;
- effective rank and group mutations;
- the complete finite and analytic size proof;
- the exact depth ledger; and
- every integer arity through 16,384.

Normal and optimized runs are byte-identical.

```text
checker SHA-256
  375b27f98c7feb0c7cf1f6abf593bd6bb60dabf4791d13424792a41dcf7e3a69
stdout SHA-256
  5afcdbaacfe8ad79db7ee0311b214447c977ded48407d6a497fd205b95c8a3ba
semantic SHA-256
  a2746e4b1cc0921f9b1f4fd2ec228889a6447a024c6a4c297086b196046b8971
```

## Boundary

The local sibling-shared program vector and its scoped matched `4/3` leading
constant are unchanged. This lane proves no matching global lower constant,
exact global optimum, optimal additive depth, formula or bounded-fanout bound,
novelty result, or legal conclusion. The integrated canonical-rank compiler
is not yet formalized in Lean or externally refereed.