# Plane-shared Boolean libraries and a sub-three integrated compiler

**Status:** exact manuscript strengthening, 2026-08-14. This note is stacked
on the integrated fixed-Q compiler, the sibling-shared program-vector theorem,
the pivot-normalized anchor, and the subsequent slicing schedules. It changes
the universal local library: instead of building two fresh router roots for
every Q-valued table, it materializes each scalar Boolean table once and lets
all Q tables reference an ordered pair of those roots.

The construction, semantic factorization, finite arithmetic, analytic tail,
and depth ledger have a standalone replay and a separately written no-import
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
size  < 3*3^r/r.
```

Put `C=ceil(log_2 r)`. The same construction has depth at most

```text
r+C+max(ceil(log_2 t)+17, ceil(log_2 s)-t+16),
```

for the explicit schedule parameters `t+s=r` below. In particular,

```text
depth = r+O(log r).
```

A convenient all-arity corollary is

```text
depth <= r+ceil(7C/5)+18.
```

The previous explicit global size constant was `46/5`. The local fixed-sign
program-vector theorem is unchanged: for `q=3^w`, its size remains
`(4/3+o(1))q`, with matched leading scalar-output lower constant `4/3` and
depth at most `3+ceil(log_2 w)`.

## 2. The missing sharing

On the nonbinary branch the legal two-plane code is

```text
0 -> (0,0),
1 -> (0,1),
2 -> (1,0).
```

Let a live local slice have `M` rows. There are `3^M` Q-valued tables, but a
plane is only a Boolean table. The set of possible high planes and the set of
possible low planes are both the same family

```text
{ beta : [M] -> {0,1} },
```

of cardinality `2^M`.

Materialize one router root for each Boolean table `beta`. A Q table `F` then
uses the ordered pair

```text
(high_F,low_F)
```

of two already existing Boolean roots. Pairing distinguished roots costs no
operation node. The prefix high router points directly to `high_F`, and the
prefix low router points directly to `low_F`.

Thus a capacity-`N` padded local slice with `M` live rows costs at most

```text
((3N-1)/2)*2^M
```

router nodes, rather than

```text
(3N-1)*3^M.
```

The sharing is literal same-DAG root reuse. It does not identify unequal
Boolean functions, add a vector-valued primitive, or treat a pair as one
scalar node.

## 3. Schedule and balanced live slices

Define `J` as the largest integer satisfying

```text
9*r^3*2^J <= 3^r,
```

and put

```text
K=J-3.
```

Let `m=3^b` be the largest power of three not exceeding `K`. Use

```text
t=b+3,
N=3^t=27m,
s=r-t,
P=3^s.
```

Among the `t` local coordinates designate five splitter coordinates. The
remaining `b-2` coordinates have

```text
u=3^(b-2)=m/9
```

assignments. The splitter cube has `3^5=243` words.

Put

```text
h=floor(K/u),
g=ceil(243/h).
```

Partition the 243 splitter words, in a fixed lexicographic order, into `g`
balanced consecutive groups. Every group has at most `h` splitter words and
therefore at most

```text
h*u <= K
```

live local rows. The groups cover the local cube exactly and are disjoint.

For each group `G`, extend every Boolean table on

```text
G x Q^(b-2)
```

by zero on the other local addresses and realize it with one capacity-`N`
positive signed router. All local Boolean roots and all groups share one
width-`t` sibling-shared program vector.

## 4. Prefix and group selection

For each prefix assignment and each group, the selector table induces one
high-plane root and one low-plane root in the corresponding Boolean library.
For each group and each plane, one capacity-`P` positive router selects the
proper root from the prefix assignment. The `2g` prefix routers share one
width-`s` program vector and cost exactly

```text
g*(3P-1)
```

skeleton nodes.

Two capacity-`243` positive routers then select the correct group output from
the five splitter coordinates. Each of their 243 leaves points to the
prefix-selected output of the unique group containing that splitter word.
The two group routers cost

```text
3*243-1=728
```

nodes and share one width-five program vector.

This second routing step is legal even though its branch payloads depend on
local variables. The signed-router projection identity is pointwise for every
branch valuation; it does not require syntactic variable disjointness between
payloads and address controls.

Decode the resulting high/low pair once and apply the existing final
binary/nonbinary glue once.

## 5. Exact charged ledger

Let the balanced groups have `M_1,...,M_g` live rows. The complete upper ledger
is

```text
((3N-1)/2)*sum_i 2^M_i        local Boolean libraries
+g*(3P-1)                      prefix plane routers
+S_P(t)+S_P(s)+S_P(5)-4        three vectors, two names shared
+(3*243-1)                     two group routers
+(2r-1)+2+3+1                  fast anchor, decoder, glue, u(x_0)
+B_router+B_control.           complement-relative binary branch
```

The `-4` counts the shared `one,zero` nodes once across the three program
vectors. The displayed formula is an upper bound: constant Boolean functions
and any additional structural hash coincidences may only reduce the actual
union.

## 6. Size proof

Write

```text
U=3^r/r.
```

### 6.1 Local Boolean libraries

Every `M_i<=K`, and

```text
2^K <= 3^r/(72r^3)
```

because `K=J-3`. Hence

```text
L_local
 <= (3N/2)*g*2^K,
L_local/U
 <= N*g/(48r^2).
```

Since `m<=K<J<2r`, one has `N=27m<54r`. Also
`m<=K<3m` gives

```text
9<=h<=26,
g=ceil(243/h)<=27.
```

Therefore

```text
L_local/U < 243/(8r).
```

### 6.2 Prefix main term

For `r>=107`,

```text
K>=4r/3.
```

A residue-three induction proves this. It is enough to check `r=107,108,109`
for

```text
9r^3*2^(ceil(4r/3)+3) <= 3^r.
```

Increasing `r` by three multiplies the power-of-two part by `16`, while

```text
16*(110/107)^3 < 27.
```

Now `h=floor(9K/m)` implies

```text
m>9K/(h+1).
```

The sibling-vector envelope gives

```text
S_P(s) <= (4/3)P+5*3^ceil(s/2).
```

Thus the prefix routers and the main vector term contribute less than

```text
(3g+4/3)*(h+1)/324
```

Shannon units. Checking the eighteen integers `9<=h<=26`, with
`g=ceil(243/h)`, gives the exact maximum

```text
644/243
```

at `(h,g)=(22,12)`.

### 6.3 Lower-order groups

The prefix half-width error is below `U/1000` because

```text
5000r < 3^floor(r/2)
```

from the parity bases `64,65` onward.

The local vector satisfies

```text
S_P(t)<=7N/3<126r.
```

Together with the width-five vector, 728 group-selector nodes, fast anchor,
decoder, glue, and `u(x_0)`, the fixed group is below `149r`, hence below
`U/1000` from

```text
149000*64^2<3^64
```

and monotonicity. The existing binary proofs give another `U/1000` each for
routers and controls.

Consequently, for `r>=107`,

```text
size/U
 < 644/243 + 243/(8r) + 4/1000
 <=644/243 + 243/(8*107) + 4/1000
 <3.
```

The finite range `64<=r<=106` is checked by exact integer arithmetic. Its
maximum occurs at `r=66`:

```text
size*r/3^r = 2.837104418458507959...
```

This finite check is a proof of forty-three explicit integer inequalities,
not an extrapolation to the tail.

## 7. Depth

Put `C=ceil(log_2 r)`. The local Boolean roots have depth at most

```text
C+2+D_P(t)+t+1.
```

The prefix routers add `s+1` levels after the maximum of local roots and their
width-`s` controls. The five-coordinate group routers add six levels. The
one-shot decoder and final glue add four.

Therefore the exact schedule-dependent bound is

```text
r+C+max(ceil(log_2 t)+17,
        ceil(log_2 s)-t+16).
```

The same schedule estimates used by the preceding compiler imply

```text
b>=C-ceil(2C/5)-1,
t=b+3,
ceil(log_2 t)<=ceil(2C/5)+1.
```

Both branches are consequently below

```text
r+ceil(7C/5)+18.
```

This retains leading depth coefficient one. The additive term is not claimed
optimal.

## 8. Evidence

Primary checker:

`research/tournaments/2026-08-14-plane-shared-library/check_plane_shared_library.py`

It checks:

- exhaustive plane factorization for local table widths one through five;
- saturation of the shared Boolean-plane family;
- 1,728 selector-reconstruction rows through grouped plane references;
- effective plane and wrong-group mutations;
- exact charged ledgers for every `64<=r<=16384`;
- the finite `64..106` proof and the analytic `r>=107` proof separately;
- all eighteen discrete prefix cases;
- the depth ledger; and
- byte-identical normal and optimized receipts.

A second checker independently reimplements the rail recurrences, Boolean
budget, group schedule, local libraries, binary branch, and exact totals. It
imports neither the primary checker nor an OrbitSynthesis compiler
implementation.

Recorded primary semantic SHA-256:

```text
9f3973a584f858b7cf4bc5ec6522944816963a6f51862d404847e4968961c389
```

Recorded independent semantic SHA-256:

```text
bb90f7cd44a567333aade1b38949e3a02ff7b7e8cfd6343e36a87e8d0e8e3116
```

## 9. Boundaries

The theorem does not improve or alter the local `4/3` program-vector lower
constant. It does not prove an exact global size constant, a global lower
bound matching three, an exact finite-width vector minimum, an optimal
additive depth term, a formula or bounded-fanout theorem, publication novelty,
or legal clearance. The integrated construction is not yet serialized and
proved end to end in Lean.