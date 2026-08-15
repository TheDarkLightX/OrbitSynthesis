# Fresh-room reconstruction of the integrated order-pair compiler

Date: 2026-08-15  
Status: **explicit manuscript construction plus independent bounded semantics and integer replay**  
Base: `research/order-pair-program-vector` / PR #15  
Not the byte-exact local packet identified by `01ddf456…`

## 1. The theorem reconstructed here

Fix

```text
Q=({0,1,2};d,u),
d(x,y,z)=z if x=y and d(x,y,z)=x otherwise,
u(0)=1, u(1)=0, u(2)=1.
```

Let `sigma:Q^r->{0,...,r-1}` be a total coordinate-selector table such that

```text
sigma(x)=sigma(bar x)
```

on the binary cube. The desired conservative operation is

```text
f_sigma(x)=x_(sigma(x)).
```

For every `r>=64`, the construction below produces one parameter-free original-signature shared DAG with

```text
size  <34*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

Every component is described as a finite DAG constructor. The proof therefore no longer has a separate same-DAG or compiler-interface hypothesis: the local library, both Boolean planes, both order-pair vectors, the prefix routers, binary branch, anchor, decoder, and final glue are united explicitly in one graph.

The selector-existence theorem and exact conservative-clone characterization remain earlier theorems of the manuscript. Applying the present constructor to a selector supplied by that theorem gives the corresponding conservative term operation.

## 2. One global legal anchor

Use the binary operation

```text
h(x,y)=d(x,u(u(x)),d(y,u(x),x)).
```

A direct nine-case check gives

```text
h(x,y)=2  iff x=2 or y=2,
h(x,y)=x  otherwise.
```

Balance-fold `h` over the `r` input variables and call the result `A`. Then

```text
A=2 on every nonbinary tuple,
A=x_0 on the all-binary cube,
size(A)<=4(r-1),
depth(A)<=3*ceil(log_2 r).
```

On the nonbinary branch, define the shared dynamic names

```text
two=A,
one=u(A),
zero=u(u(A)).
```

These are not global constants: their Boolean meanings are used only under the explicit branch condition `A=2`.

## 3. Exact order-pair vector used as an address program

For a width-`w` signed router, `q=3^w`. PR #15 constructs all `2q` ordered control roots from the anchor and target-address digits in one shared DAG. For either root sign its exact recurrence has

```text
C_s(w)=(4/3+o(1))q,
depth <=3+ceil(log_2 w),
2*C_s(w)<=5q-1.
```

For a positive root, the lower-bound output census is `4q/3-1`; for a negative root it is `4q/3`. The present compiler needs only positive-root projection vectors.

Most importantly, each vector depends on the address and anchor but not on any routed payload. It can therefore be adjoined once and referenced by every router having the same address inputs and root sign.

## 4. Two-plane encoding

Encode `Q` by two Boolean planes:

```text
0 -> 00,
1 -> 01,
2 -> 10.
```

Decode only after all routing by

```text
Dec(high,low)=d(d(high,one,two),zero,low).
```

Direct substitution gives `0,1,2` on the three legal codes. The unused code `11` is never generated.

The two plane DAGs run in parallel. A program vector is shared by both planes because its control roots depend only on the address.

## 5. Local universal library

For `r>=64`, put

```text
ell=ceil(log_3(r^2)),
L=4+ell,
H=r-L,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b).
```

Thus the local block has `b` ternary coordinates and exactly `M=3^b` assignments. The remaining prefix has `r-b` coordinates and exactly `P` assignments.

There are `3^M` `Q`-valued local tables. For each table `T`:

1. encode its `M` values into high and low Boolean payload lists;
2. instantiate one positive capacity-`M` signed router for the high list;
3. instantiate one positive capacity-`M` signed router for the low list;
4. connect both routers to the same width-`b` order-pair vector.

Each router skeleton has `(3M-1)/2` discriminator nodes. The two skeletons therefore use exactly `3M-1` nodes per local table. All `3^M` tables and both planes share one vector. The local union has at most

```text
(3M-1)3^M + C_+(b)
```

operation nodes beyond the globally shared anchor infrastructure.

This is an actual multi-output sub-DAG: it has two distinguished roots for every local table, not `3^M` separate copies of the controls.

## 6. Prefix selection

For every prefix assignment `z in Q^(r-b)`, freeze the prefix coordinates in `f_sigma`. The resulting map of the local block is one of the `3^M` tables already present in the library. Let

```text
T_z:Q^b->Q
```

be that table and let `T_z^hi,T_z^lo` be its two existing library roots.

Build two positive capacity-`P` signed routers:

```text
Prefix_hi(z)=T_z^hi,
Prefix_lo(z)=T_z^lo.
```

Both routers share one width-`r-b` order-pair vector. Their union costs at most

```text
(3P-1)+C_+(r-b).
```

The final nonbinary root is

```text
N=Dec(Prefix_hi,Prefix_lo).
```

### Semantic proof

On a nonbinary input, `A=2`, so the order-pair terms are legal Boolean controls.

- The prefix vector programs each prefix router to select the branch indexed by the actual prefix input.
- That branch points to the high or low root of the frozen local table `T_z`.
- The shared local vector programs every local router to select the branch indexed by the actual local-block input.
- Hence the two prefix outputs are exactly the legal two-bit code of `f_sigma(x)`.
- The single decoder returns `f_sigma(x)`.

No control depends on a payload root, no vector is copied per table or per plane, and no decoder is repeated at a routing level.

## 7. Explicit binary branch

On the all-binary cube, absolute `zero,one` names are unavailable. Normalize relative to `x_0`. For a binary input `x`, write

```text
a_i=0 if x_i=x_0,
a_i=1 if x_i=u(x_0).
```

Complement invariance of `sigma` means the desired output is a complement-equivariant Boolean function of this relative address.

Use the frozen strong signed-router binary construction:

1. choose a ternary-router width `k`;
2. let `m=floor(log_2(3^k))`;
3. partition the `r-1` relative address bits into residual-first chunks of width at most `m`;
4. inject each live binary chunk address into a ternary capacity-`3^k` target set and duplicate the final live payload in unused branches;
5. compile each logical control bit as a relative Boolean table and realize physical `0/1` by `x_0,u(x_0)`;
6. share the controls at each route level across all router instances at that level.

For `64<=r<339`, choose the least-depth `k` from the finite set `1<=k<=32`. For `r>=339`, choose `k=floor(sqrt r)`. This is a total deterministic algorithm, not an existence choice.

The explicit upper count used by the audit is

```text
6(2^(r-1)+2^floor(log_2(3^k)))
 +6r*3^(2k)
 +4r+10.
```

The first term charges all router skeletons under residual-first telescoping, the second charges every shared relative control table, and the final term charges fixed construction overhead. It is below `3^r/r` for `r>=64` by a very large margin.

The checked depth is

```text
(k+1)*ceil((r-1)/floor(log_2(3^k)))
 +2*floor(log_2(3^k))
 +3*ceil(log_2 r)+8.
```

With the finite choice above it is at most

```text
r+4*ceil(log_2 r)+7.
```

The final glue adds two more levels.

## 8. Final branch glue

Let `B` be the binary root and `N` the nonbinary root. Put `s=zero=u(u(A))` and define

```text
Glue(A,B,N)=d(d(s,A,B),d(s,A,N),N).
```

This adds three discriminator nodes and two depth levels.

- On the binary cube, `s=A`, so `Glue=B`.
- Off the binary cube, `(s,A)=(0,2)`, so `Glue=N`.

The final root is therefore exactly `f_sigma` on all of `Q^r`.

## 9. Shared-DAG size ledger

The one-graph upper count is

```text
N_total(r)
 = (3M-1)3^M
   + C_+(b)
   + (3P-1)
   + C_+(r-b)
   + 4r+3
   + N_binary(r).
```

The terms are, respectively:

1. every local-table router skeleton on both planes;
2. the one shared local vector;
3. the two prefix router skeletons;
4. the one shared prefix vector;
5. anchor, two names, one decoder, and final glue;
6. the explicit binary branch.

The two vector terms both include their two name nodes in their standalone theorem count. Adding them without subtracting the repeated names is a safe overcount.

### Uniform analytic bound

The order-pair theorem gives

```text
C_+(w)<(5/2)3^w.
```

Maximality of `M` gives `M>H/3`. The deliberately coarse estimate `H>=r/2` gives

```text
P=3^r/M<6*3^r/r.
```

Therefore the prefix skeletons and vector are strictly below

```text
(3+5/2)P <33*3^r/r.
```

The two-logarithm reserve gives

```text
(3M-1)3^M <(1/27)3^r/r.
```

The retained binary proof splits into three strict normalized quantities below `1/4`: router skeletons, shared controls, and fixed overhead. Hence

```text
N_binary(r)<(3/4)3^r/r.
```

Finally, `M<=r` and `C_+(b)<(5/2)M` imply

```text
(C_+(b)+4r+3)r/3^r
 <=((13/2)r+3)r/3^r
 <1/100
```

for `r>=64`. Consequently

```text
N_total(r)r/3^r
 <33+1/27+3/4+1/100
 <34.
```

This proves the displayed size theorem for every `r>=64`, not only the replay range.

## 10. Depth ledger

Let

```text
c=ceil(log_2 r),
s=r-b.
```

The anchor has depth at most `3c`. The local vector has absolute depth at most

```text
3c+3+ceil(log_2 b).
```

After the local signed router,

```text
D_local<=3c+b+ceil(log_2 b)+4.
```

The prefix vector has absolute depth at most

```text
3c+3+ceil(log_2 s).
```

The prefix router adds `s+1` levels after the deeper of its payload and controls, so

```text
D_prefix
 <=max(D_local,3c+3+ceil(log_2 s))+s+1
 <=r+4c+5.
```

One two-level decoder and the two-level final glue give

```text
D_nonbinary<=r+4c+9.
```

The explicit binary choice in Section 7 is no deeper. Thus the complete DAG satisfies

```text
depth<=r+4*ceil(log_2 r)+9.
```

## 11. Finite arities

For `1<=r<64`, use any named earlier explicit compiler in the manuscript. This is a finite, constructive fallback and affects neither asymptotic statement. The exact constant `34` is asserted only from arity 64 onward.

## 12. The integrated theorem

**Theorem (explicit order-pair compiler).** For every complement-invariant coordinate selector `sigma` and every `r>=64`, the construction in Sections 2–8 produces one parameter-free original-signature shared DAG computing

```text
x |-> x_(sigma(x))
```

with

```text
size  <34*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

Combining this with the selector representation theorem gives the same bounds for every conservative `r`-ary term operation of `Q`. Together with the manuscript’s counting lower bounds,

```text
max_f C_r(f)=Theta(3^r/r)
```

and

```text
r-log_3(log r)-O(1)
 <= Delta_r(Q)
 <= r+4*ceil(log_2 r)+9.
```

The leading depth coefficient is one.

## 13. Fresh-room evidence

The accompanying reconstruction implements one hash-consed `d/u` graph and checks:

- the exact PR #15 node recurrence and semantics for both signs through width five;
- all `128` compatible arity-two selector-index tables;
- `32` deterministic independent arity-three selector tables;
- `2,016` complete integrated input rows;
- every integer size/depth ledger for `64<=r<=16384`;
- effective failures for per-branch vector duplication, plane serialization, and non-equivariant binary selectors;
- byte-identical normal and optimized Python receipts.

The finite replay’s largest normalized total is approximately

```text
14.925925925925938
```

at arity `93`. Thus the exact construction appears to admit a substantially smaller constant than `34`; this is recorded as a sharpening target, not promoted here without a separate all-arity tail proof and independent review.

## 14. Boundary

This reconstruction is independent evidence for the theorem shape reported for the local `01ddf456…` packet, but it is not a substitute for uploading and hash-binding that packet. It does not establish publication novelty, patent freedom to operate, practical performance, ordinary-tree complexity, bounded-fanout complexity, or exact finite-width optimality.
