# Plane-shared Boolean libraries and a `67/25` integrated compiler

**Status:** exact manuscript strengthening, 2026-08-14. This note is stacked
on the integrated fixed-Q compiler, the sibling-shared program-vector theorem,
the pivot-normalized anchor, and the slicing schedules. It changes the
universal local library: instead of building two new router roots for every
Q-valued table, it materializes each scalar Boolean table once and lets every Q
table reference an ordered pair of those existing roots.

The semantic factorization, exact finite portfolio, analytic tail, and depth
ledger have a standalone replay and a separately written no-import
reconstruction. The result is not yet formalized end to end in Lean or
externally peer reviewed. Publication novelty, patent/FTO status, license
rights, and practical performance remain **UNKNOWN**.

## 1. Result

Let

```text
Q=({0,1,2};d,u),
d(x,y,z)=z if x=y and d(x,y,z)=x otherwise,
u(0)=1, u(1)=0, u(2)=1.
```

For every `r>=64` and every `f in CT_r(Q)`, there is one parameter-free
original-signature free-fanout scalar DAG with

```text
size < (67/25)*3^r/r.
```

Writing `C=ceil(log_2 r)`, the same portfolio has

```text
depth <= r+ceil(7C/5)+20.
```

The earlier explicit global constants were

```text
34, 15, 21/2, 46/5.
```

The local fixed-sign program vector is unchanged. For `q=3^w`, its size is
`(4/3+o(1))q`, its matched leading scalar-output lower constant is `4/3`, and
its depth is at most `3+ceil(log_2 w)`.

The exact charged ratio in the replay range `64<=r<=16384` is maximal at
`r=64`:

```text
size*r/3^r = 2.679666803224281973...
```

This bounded maximum is validation evidence, not an exact global optimum or a
matching global lower bound.

## 2. Plane sharing

On the nonbinary branch the legal two-plane code is

```text
0 -> (0,0),
1 -> (0,1),
2 -> (1,0).
```

Let a live local slice have `M` rows. There are `3^M` Q-valued tables, but each
individual plane is a Boolean table. The high and low coordinates both range
over the same family

```text
{ beta:[M]->{0,1} },
```

of cardinality `2^M`.

Materialize one scalar router root for every Boolean table `beta`. A Q table
`F` is then represented by the ordered pair

```text
(high_F,low_F)
```

of two already materialized scalar roots. Pairing distinguished roots costs no
operation node. The prefix high router points to `high_F`, and the prefix low
router points to `low_F`.

Thus a capacity-`N` padded local slice with `M` live rows costs at most

```text
((3N-1)/2)*2^M
```

router nodes, rather than

```text
(3N-1)*3^M.
```

This is literal same-DAG root reuse. It neither identifies unequal Boolean
functions nor introduces a vector-valued gate.

## 3. Boolean budget and the four-candidate portfolio

Let `J` be the largest integer satisfying

```text
9*r^3*2^J <= 3^r,
```

put

```text
K=J-3,
```

and let `m=3^b` be the largest power of three not exceeding `K`.

For each

```text
c in {2,3,4,5},
```

define one candidate by

```text
t=b+c,
d=min(7,t),
u=3^(t-d),
h=floor(K/u),
g=ceil(3^d/h),
s=r-t,
N=3^t,
P=3^s.
```

Designate `d` of the `t` local coordinates as splitter coordinates. The
remaining `t-d` coordinates contribute `u` rows per splitter word. Partition
the `3^d` splitter words into `g` balanced consecutive groups. A group has at
most

```text
ceil(3^d/g)*u <= h*u <= K
```

live rows.

For each group, zero-extend every Boolean table on its live rows to all `N`
local addresses and realize it with one capacity-`N` positive signed router.
Every group and every Boolean table shares one width-`t` sibling-shared program
vector.

For each group and each plane, one capacity-`P` positive router selects the
correct Boolean root from the prefix assignment. The `2g` prefix routers share
one width-`s` program vector and cost

```text
g*(3P-1)
```

nodes.

Finally, two capacity-`3^d` positive routers select the group high and low
outputs using the splitter coordinates. They cost

```text
3*3^d-1
```

nodes and share one width-`d` program vector. Their branch payloads may depend
on other local coordinates: the signed-router projection identity is
pointwise in every branch valuation and does not require syntactic variable
disjointness.

Decode the selected high/low pair once and apply the existing final
binary/nonbinary glue once.

For each arity, use the candidate with the least exact charged count, breaking
ties by the smaller `c`. This is an explicit four-element minimization, not an
existential optimization over arbitrary circuits.

## 4. Exact candidate ledger

Let the balanced groups of candidate `c` have live-row counts
`M_1,...,M_g`. Its complete charged upper ledger is

```text
((3N-1)/2)*sum_i 2^M_i       local Boolean libraries
+g*(3P-1)                     prefix plane routers
+S_P(t)+S_P(s)+S_P(d)-4       three vectors, shared names
+(3*3^d-1)                    two group-selection routers
+(2r-1)+2+3+1                 fast anchor, decoder, glue, u(x_0)
+B_router+B_control.          complement-relative binary branch
```

The `-4` leaves one copy of the two dynamic name nodes across the three
vectors. The formula is an upper bound: if two syntactic subgraphs hash to the
same node, the actual union is smaller.

## 5. Size proof

Write

```text
U=3^r/r.
```

### 5.1 Exact finite part

For every integer

```text
64<=r<=966,
```

the checker constructs all four candidate ledgers using exact integers,
selects the least, and verifies

```text
25*size*r < 67*3^r.
```

The maximum over this finite set is the `r=64` value displayed above. The
committed receipt records every input rule, source hash, semantic digest,
selected checkpoints, and normal/optimized equality. This is a finite exact
proof, not a floating-point sample.

### 5.2 Analytic tail

For `r>=967`, candidate `c=4` suffices. It has

```text
t=b+4,
d=7,
u=m/27,
h=floor(27K/m),
g=ceil(2187/h),
N=81m.
```

The Boolean budget satisfies

```text
K>=4r/3
```

from `r=107` onward. It is enough to check the three residue bases
`r=107,108,109` in

```text
9*r^3*2^(ceil(4r/3)+3) <= 3^r;
```

increasing `r` by three multiplies the power-of-two part by `16`, while

```text
16*(110/107)^3 < 27.
```

Since `m<=K<3m`, one has

```text
27<=h<=80,
g<=81.
```

#### Local Boolean libraries

Every live-row count is at most `K`, and

```text
2^K <= 3^r/(72r^3).
```

Also `m<K<J<2r`, hence `N<162r`. Therefore

```text
L_local/U
 < N*g/(48r^2)
 < 2187/(8r).
```

#### Prefix main term

The sibling-vector envelope is

```text
S_P(s) <= (4/3)P+5*3^ceil(s/2).
```

Because `h=floor(27K/m)`,

```text
m>27K/(h+1)>=36r/(h+1).
```

The normalized prefix-router and main-vector term is consequently below

```text
(9g+4)(h+1)/8748.
```

Checking the 54 integers `27<=h<=80`, with `g=ceil(2187/h)`, gives the exact
maximum

```text
20935/8748
```

at `(h,g)=(78,29)`.

#### Lower-order terms

The vector half-width error is below `U/1000` from

```text
5000r < 3^floor(r/2).
```

For this candidate, the local vector, width-seven vector, group routers, fast
anchor, decoder, glue, and `u(x_0)` are below `900r` nodes and hence below
`U/1000` for `r>=967`. The binary-router and binary-control proofs each give
another `U/1000`.

Thus

```text
size/U
 < 20935/8748 + 2187/(8r) + 4/1000
 <=20935/8748 + 2187/(8*967) + 4/1000
 <67/25.
```

The last comparison is an exact rational inequality.

## 6. Depth

For a selected candidate, put

```text
C=ceil(log_2 r).
```

The local Boolean roots have depth at most

```text
C+2+D_P(t)+t+1.
```

The prefix routers add `s+1` levels after the maximum of their payload roots
and width-`s` controls. The group routers add `d+1<=8` levels, followed by the
one-shot decoder and two-level final glue. Hence

```text
D
 <= r+C+max(ceil(log_2 t)+19,
             ceil(log_2 s)-t+18).
```

For the analytic range, `K>=4r/3` and maximality of `m` imply

```text
b>=C-ceil(2C/5)-1.
```

The four candidates satisfy `b+2<=t<=b+5`, while `b<C`. A five-residue
`27<32` induction gives

```text
ceil(log_2 t)<=ceil(2C/5)+1.
```

Also `ceil(log_2 s)<=C`. Substitution gives

```text
D<=r+ceil(7C/5)+20.
```

The remaining finite arities are checked exactly by the same ledger.

## 7. Evidence

Primary checker:

`research/tournaments/2026-08-14-plane-shared-library/check_plane_shared_library.py`

It verifies:

- exact plane factorization and saturation through six live rows;
- 1,728 grouped selector-reconstruction rows and effective mutations;
- all four exact candidate ledgers for every `64<=r<=16384`;
- the exact finite proof through arity 966;
- the analytic tail components separately;
- the discrete `20935/8748` prefix maximum;
- the depth ledger; and
- byte-identical normal and optimized receipts.

A second checker independently reimplements the Boolean planes, rail
recurrences, portfolio, binary branch, finite proof, analytic tail, and depth
ledger without importing the primary checker or an OrbitSynthesis compiler.

Recorded primary semantic SHA-256:

```text
b98aa602a17208dcb9b0af22bab96e65a02e4888f6293d23b6b59aa7442a4f16
```

Recorded independent semantic SHA-256:

```text
b96a891f6e94a5d5d4aefa1b1efd20ebe31583347244746c225329b3fca7ab95
```

## 8. Boundaries

The theorem does not alter the local `4/3` program-vector leading constant,
prove a matching global lower constant, determine the exact global optimum,
settle the optimal additive depth term, or give formula or bounded-fanout
bounds. It makes no publication-novelty or legal conclusion. The integrated
construction is not yet serialized and proved end to end in Lean.
