# Pivot-normalized fast anchor and sharpened integrated bounds

**Status:** exact manuscript strengthening, 2026-08-13.  The algebraic
construction and integer ledgers have an independent standalone replay with
normal/optimized equality and effective mutations.  The optimized local
program-vector theorem is unchanged.  The new anchor and the sharpened
integrated constants are not yet formalized in Lean or externally peer
reviewed.  Novelty, patent/FTO, license rights, and practical performance
remain **UNKNOWN**.

## 1. Result

Let

```text
Q=({0,1,2};d,u),
d(x,y,z)=z if x=y and d(x,y,z)=x otherwise,
u(0)=1, u(1)=0, u(2)=1.
```

For `r>=64`, the integrated sibling-vector compiler from Theorem 6.10 can be
realized by one parameter-free original-signature free-fanout scalar DAG with

```text
size  < 15*3^r/r,
depth <= r+ceil(7*ceil(log_2 r)/5)+11.
```

The exact schedule-dependent nonbinary critical-path bound is sharper.  Put

```text
C=ceil(log_2 r),
L=4+ceil(log_3(r^2)),
H=r-L,
M=3^floor(log_3 H),
b=log_3 M,
s=r-b.
```

Then the complete nonbinary path including decoder and final glue has depth at
most

```text
r+C+max(ceil(log_2 b)+11, ceil(log_2 s)-b+10).
```

Consequently its asymptotic additive term is

```text
(2-log_3 2)*log_2 r+O(log log r),
```

rather than the earlier explicit `4ceil(log_2 r)+9` term.  No lower bound on
the optimal additive term is asserted.

The size improvement uses the same block schedule and the same sibling-shared
vectors as the integrated compiler.  It is a sharper proof of the charged
ledger, not a new uncharged sharing convention.

## 2. Pivot-normalized anchor

For `r>=3`, distinguish the output payload `x_0`, choose pivot `y=x_1`, and
choose one robust witness `z=x_2`.  Define

```text
e   = u(y),
e2  = u(e),
rho = d(y,e2,d(z,y,e)),
delta_i = d(x_i,y,e)       for 3<=i<r,
mu(a,b) = d(a,e,b).
```

Use the ordered conceptual leaves

```text
x_1, x_2, delta_3, ..., delta_(r-1), x_0.
```

Start from the complete ordered binary tree of height `C=ceil(log_2 r)`, keep
its first `r` leaves, and contract every unary right-padding path.  Replace the
parent of the first two leaves by `rho`; label every other internal node by
`mu`.  Call the root `A_fast`.

### 2.1 Semantics

If `y=2`, then `rho=2`.  Since `e=u(2)=1`,

```text
mu(2,b)=d(2,1,b)=2,
```

so this leftmost failure propagates to the root.

Now suppose `y` is binary.  Then `e=1-y` and `e2=y`.  Direct substitution
gives

```text
rho=e  iff z is binary,       otherwise rho=2,
delta_i=e iff x_i is binary,  otherwise delta_i=2.
```

On the status set `{e,2}`, `mu` has identity `e` and absorber `2`:

```text
mu(e,b)=b,
mu(2,b)=2.
```

The rightmost payload is therefore returned exactly when every preceding
input is binary.  If the payload itself is `2`, it already supplies the
required nonbinary value.  Hence

```text
A_fast=2    iff some input is 2,
A_fast=x_0  on the Boolean cube.
```

This is the same semantic interface as the historical balanced `h` anchor.

### 2.2 Size and depth

The four nodes `e,e2,d(z,y,e),rho` are shared.  There are `r-3` detector
nodes.  A full binary tree with `r` retained leaves has `r-1` internal
positions; one is occupied by `rho`, leaving `r-2` `mu` nodes.  Thus

```text
size(A_fast) <= 4+(r-3)+(r-2)=2r-1.
```

The pruned tree has height at most `C`.  The robust pair has depth three and
occupies the parent of two conceptual leaves; every detector has depth two.
Therefore

```text
depth(A_fast) <= C+2.
```

For `r=2`, the three-node term

```text
d(x_1,u(u(x_1)),x_0)
```

has the required semantics and depth three; `r=1` is the identity.

The old anchor contained a reusable `u(x_0)` node.  The fast anchor need not,
so the binary branch charges one separate node.  For `r>=4`,

```text
size(A_fast)+1 <= 2r <= 4(r-1).
```

Thus the old `4(r-1)` size allowance remains valid while its depth drops from
`3C` to `C+2`.

## 3. Sharpened depth ledger

Let `D_P(w)<=3+ceil(log_2 w)` be the exact sibling-vector depth bound.  With
`A_fast` substituted for the old anchor,

```text
D_local  <= C+2+D_P(b)+b+1,
D_prefix <= max(D_local,C+2+D_P(s))+s+1.
```

Adding the one-shot decoder and the final two-level glue gives

```text
D_NB,final
 <= C+2+max(b+ceil(log_2 b)+4,ceil(log_2 s)+3)+s+5
 =  r+C+max(ceil(log_2 b)+11,ceil(log_2 s)-b+10).
```

It remains to eliminate the schedule parameters in favor of `C`.

The existing reserve proof gives `H>r/2`; maximality of `M` gives
`M>H/3>r/6`.  Also `b<C`.  For every integer `C>=6`,

```text
6*3^(floor(3C/5)-2) <= 2^(C-1).
```

It suffices to check `C=6,...,10`; increasing `C` by five multiplies the left
side by `27` and the right side by `32`.  If
`b<=floor(3C/5)-2`, then

```text
M=3^b <= 2^(C-1)/6 < r/6,
```

contradicting the preceding lower bound.  Therefore

```text
b >= floor(3C/5)-1 = C-ceil(2C/5)-1.
```

Likewise, `C-1<=2^ceil(2C/5)` for `C=6,...,10`, and the same five-step
induction preserves it.  Since `b<C`,

```text
ceil(log_2 b)<=ceil(2C/5).
```

Finally `s<=r<=2^C`, so `ceil(log_2 s)<=C`.  Substitution in the two branches
of the maximum gives

```text
D_NB,final <= r+ceil(7C/5)+11.
```

The intrinsic binary path remains lower.  Exact arithmetic handles
`64<=r<=99`.  For `r>=100`, the existing estimate

```text
D_B < 2r/3+(73/15)sqrt(r)+8/3
```

is enough: after including the two glue levels, the difference from the new
bound is at least

```text
G(r)=r/3-(73/15)sqrt(r)+(7/5)log_2(r)+19/3.
```

`G(100)>0`, and

```text
G'(r)>1/3-73/(30sqrt(r))>0
```

for `r>=100`.  The anchor/name path is trivially shorter.  This proves the
stated global depth theorem.

## 4. Sharpened size ledger

Write

```text
U=3^r/r.
```

The exact integrated union is grouped into:

1. the universal local-table routers;
2. the prefix routers and the width-`s` program vector;
3. the width-`b` vector, anchor, decoder, glue, and the separate `u(x_0)`;
4. binary routers; and
5. binary controls.

### 4.1 The schedule ratio

For every `r>=64`,

```text
r/M <= 31/9.
```

For `64<=r<=93`, one has `M=27`, and equality occurs at `r=93`.  For
`94<=r<=104`, one has `M=81`.  For `r>=105`,

```text
L <= 5+2log_3 r <= 4r/31.
```

The second inequality holds at `105`, and its right-minus-left derivative is
positive thereafter.  Hence `H>=27r/31` and
`M>H/3>=9r/31`.

### 4.2 Component bounds

The two-logarithm reserve gives

```text
3^M <= 3^r/(81r^2).
```

Therefore the local-table routers satisfy

```text
(3M-1)3^M < U/27.
```

For the prefix part, the local vector envelope gives

```text
(3P-1)+S_P(s)
 < (13/3)P+5*3^ceil(s/2)
 <= (403/27)U+5*3^ceil(s/2).
```

The error term is below `U/1000`.  It is enough to show

```text
5000r < 3^floor(r/2).
```

This holds at `r=64,65`; increasing `r` by two multiplies the right side by
three while the left side grows by a smaller factor.

For the fixed group,

```text
S_P(b) <= 7M/3 <= 7r/3,
size(A_fast)+size(u(x_0)) <= 4(r-1).
```

After adding decoder and glue this group is below `7r`, and hence below
`U/1000` because `7000r^2<3^r` from `r=64` onward.

The previous binary proof used quarter-unit bounds.  Its logarithmic margins
are much larger.  Define

```text
F_1(r)=(1-log_3 2)r-sqrt(r)-log_3(3r),
F_2(r)=r-2sqrt(r)-log_3(24r^2).
```

Both derivatives are positive for `r>=64`.  The integer inequalities

```text
192*2^64 < 3^50,
24*64^2   < 3^42
```

show `F_1(64)>6` and `F_2(64)>6`; since `250<3^6`, the old estimates gain an
extra factor greater than `250`.  Consequently

```text
B_router  < U/1000,
B_control < U/1000.
```

Summing the five groups gives

```text
size/U
 < 403/27+1/27+4/1000
 = 404/27+4/1000
 < 15.
```

The last inequality is exact because `4/1000<1/27`.

## 5. Deterministic evidence

Standalone checker:

`research/tournaments/2026-08-13-program-vector-optimization/lanes/fast_anchor_sharp_bounds/check_fast_anchor_sharp_bounds.py`

It independently performs:

- all `9,840` anchor evaluations through arity eight;
- exact operation-node and depth checks for those materializations;
- an effective mutation of the robust witness;
- exact schedule and union ledgers for every `64<=r<=16384`;
- each analytic component inequality separately;
- the `r/M<=31/9` schedule lemma and both depth-parameter inequalities;
- exact small binary-depth intervals and the analytic tail base; and
- byte-identical normal and optimized replay against the committed receipt.

Recorded hashes:

```text
checker SHA-256:
  2ddb696c85b4e94166df34ed8a0643710c916481e5e967cc0e1ac4685d077bd0
receipt/stdout SHA-256:
  6cabb4ef6654884c5676bf23a657e942a2a849dc7f5ee68dcd78fe2f217fb62e
semantic SHA-256:
  a477fb076e86283bc70cf63f20c2e2b8b43f6bca627e724b9e6afb20507ab610
```

The exact charged ratio over the replay range is maximized at `r=93`:

```text
14.925925925925929447...
```

This bounded observation is not used as the all-arity proof and is not claimed
to be the exact global compiler constant.

## 6. Boundaries

The sibling-shared local theorem and its `4/3` leading lower bound are
unchanged.  The present note proves neither an exact finite-width local minimum
nor a global compiler lower bound.  It does not formalize the integrated DAG
in Lean, improve ordinary formula size, address bounded fan-out, determine the
optimal additive depth term, or establish publication novelty.