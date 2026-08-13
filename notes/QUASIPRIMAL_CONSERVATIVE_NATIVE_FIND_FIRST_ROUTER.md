# Native find-first modes for exact signed routers

Date: 2026-08-13  
Status: **new paper proof plus independent executable oracle; Lean port pending**  
Scope: strengthens the exact program-vector theorem on the nonbinary branch `A=2`; the end-to-end compiler corollary remains conditional on the frozen interfaces.

## 1. Result in one line

The old `(equal,gain)` summary is not the intrinsic state space. The three reachable outcomes are

```text
E = all compared digits are equal,
G = the first mismatch is the gain case (target,physical)=(1,2),
L = the first mismatch is any other case.
```

They form a three-element find-first monoid. Under

```text
L -> 0,  G -> 1,  E -> 2,
```

its multiplication is exactly

```text
x star y = d(x,2,y).
```

Thus the algebra's own discriminator is the summary operation: `2` is the identity, while `0` and `1` are left zeros. This is the inner reason the program vector can be made smaller and shallower.

## 2. Frozen setting

Let

```text
Q={0,1,2},
d(x,y,z)=z if x=y, and d(x,y,z)=x otherwise,
u(0)=1, u(1)=0, u(2)=1.
```

On the nonbinary branch an anchor term has value `A=2`. The legal dynamic names are

```text
two  = A,
one  = u(A),
zero = u(u(A)).
```

No parameter-free constants are added to the global grammar.

A physical branch and requested target are words `p,t in Q^w`; the router capacity is `q=3^w`. A middle physical digit flips the signed-cell polarity. The frozen positive base program is `(L,G)` and the frozen negative base program is `(G,not L)`.

## 3. The find-first monoid

Let `F={E,G,L}` and define

```text
E * x = x,
G * x = G,
L * x = L.
```

This is associative: the product of a word is its first non-`E` symbol, or `E` if none exists. For one aligned digit pair `(t_i,p_i)`, emit

```text
E  if t_i=p_i,
G  if (t_i,p_i)=(1,2),
L  otherwise.
```

The product over consecutive positions is therefore exactly the first-mismatch summary. The map

```text
eta(E)=2, eta(G)=1, eta(L)=0
```

is a monoid isomorphism from `F` to `(Q,star)`, where

```text
x star y = d(x,two,y).
```

Indeed, if `x=two`, the discriminator returns `y`; otherwise it returns `x`.

The abstract monoid is classical (identity adjoined to a two-element left-zero semigroup, commonly called a flip-flop/find-first monoid). The candidate new contribution is not that monoid. It is the exact original-signature embedding, the all-branch shared-DAG materialization, and the quantitative signed-router/compiler consequences below.

## 4. Drop-in reusable Boolean program vector

For consumers that must retain the old ordered pair of Boolean controls, encode a summary as

```text
(G,L) in {(0,0),(1,0),(0,1)}.
```

For consecutive blocks `X,Y`, native discriminator composition is

```text
G_XY = d(G_X,L_X,G_Y),
L_XY = d(L_X,G_X,L_Y).
```

This is the same find-first product in two Boolean coordinates. It uses **two** discriminator nodes per physical concatenation, rather than the old three-node `(E,G)` update.

### 4.1 Exact one-digit terms

For target digit `x`, define

```text
notOne  = u(x),
gainTwo = u(notOne),
lossZero = d(x,two,notOne),
lossTwo  = u(lossZero).
```

Then the three physical-digit states are

```text
p=0: (G,L)=(zero,lossZero),
p=1: (G,L)=(zero,notOne),
p=2: (G,L)=(gainTwo,lossTwo).
```

Exactly four new operation nodes are used beyond the two shared names. An exhaustive closure over all unary `Q`-functions, with inputs `x,A` and the original `d/u` operations, proves that the complete one-digit output set needs at least six operation nodes including the two generated names; the construction attains six.

### 4.2 Counts and depth

Let `S(w)` be the state-vector node count excluding the two shared names. Under a balanced split,

```text
S(1)=4,
S(w)=S(floor(w/2))+S(ceil(w/2))+2*3^w.
```

For a positive root, `(q-1)/2` physical cells are negative; for a negative root, `(q+1)/2` are negative. Therefore

```text
V_P(w)=2+S(w)+(q-1)/2,
V_N(w)=2+S(w)+(q+1)/2.
```

The exact construction satisfies

```text
9*S(w) <= 28*q,
27*V_P(w) <= 100*q,
27*V_N(w) <= 100*q.
```

The worst case is the negative root at `w=3`, where `V_N=100` and `q=27`. Hence every old-interface vector has

```text
size <= (100/27)q < 4q,
depth <= 4+ceil(log_2 w).
```

More sharply,

```text
V_P(w),V_N(w) = (5/2)q + O(3^ceil(w/2)).
```

This is a strict drop-in improvement over the frozen `7q` and `6+2 ceil(log_2 w)` theorem.

## 5. Native `Q`-valued mode vector

The reusable Boolean interface is still not the smallest semantic interface. Materialize one `Q`-valued mode root `m_p(t)` per physical word:

```text
m_p(t)=two  for E,
m_p(t)=one  for G,
m_p(t)=zero for L.
```

### 5.1 Exact one-digit terms

For target digit `x`, define

```text
m_0(x)=d(zero,x,two),
h_1(x)=d(one,x,two),
m_1(x)=d(h_1(x),one,zero),
m_2(x)=x.
```

These have truth tables

```text
m_0=(2,0,0),
m_1=(0,2,0),
m_2=(0,1,2).
```

Only three new operation nodes are needed beyond the two shared names. Exhaustive unary-DAG closure proves that no four-node original-signature DAG from raw inputs `x,A` can simultaneously produce `m_0,m_1`; five nodes including the two names are minimal.

### 5.2 Balanced materialization

For a physical concatenation `p=p_L p_R`, set

```text
m_p(t)=d(m_pL(t_L),two,m_pR(t_R)).
```

Let `R(w)` exclude the two shared name nodes. Then

```text
R(1)=3,
R(w)=R(floor(w/2))+R(ceil(w/2))+3^w.
```

The exact vector size `W(w)=R(w)+2` satisfies

```text
3*R(w) <= 5q,
9*W(w) <= 17q,
depth(W) <= 3+ceil(log_2 w).
```

The worst exact ratio is `W(2)/3^2=17/9`. Also

```text
R(w)=q+O(3^ceil(w/2)),
```

so the leading size coefficient is one.

### 5.3 Leading-constant optimality

The `q` mode functions are pairwise distinct: at target `t=p`, `m_p(p)=2`, whereas `m_p'(p)` is `0` or `1` for `p'!=p`. A multi-output DAG with the `w` address digits and anchor as free inputs can expose at most one semantic function per operation node. Consequently every such mode vector needs at least

```text
q-(w+1)
```

operation nodes. The construction's `q+O(sqrt(q))` size is therefore asymptotically optimal with leading coefficient one.

Every mode root depends on every target digit. Since an original-signature node has fan-in at most three, any one root has depth at least `ceil(log_3 w)` from the address inputs. Thus the logarithmic preprocessing depth is also asymptotically optimal up to the base-of-log constant and the fixed name-generation depth.

## 6. Payload-fused signed routers

The native mode root can replace the two Boolean controls at the bottom cell.

For a Boolean branch payload `x_p`, use

```text
positive cell: d(m_p,two,x_p),
negative cell: d(m_p,two,u(x_p)).
```

The three cases are immediate:

```text
m_p=0 -> 0,
m_p=1 -> 1,
m_p=2 -> x_p or u(x_p), according to the cell sign.
```

The frozen signed recursion above the base cells is unchanged, so the complete root still returns the requested branch (positive root) or its complement (negative root).

### 6.1 Generic payloads

The signed-router skeleton has `(3q-1)/2` discriminator nodes. If each negative physical leaf requires a fresh payload complement, the exact counts are

```text
F_P(w)=2q+R(w)+1,
F_N(w)=2q+R(w)+2.
```

They satisfy

```text
9*F_P(w) <= 35q,
9*F_N(w) <= 35q,
depth <= w+4+ceil(log_2 w).
```

The negative `w=2` case is tight for this displayed bound: `F_N=35`, `q=9`.

A deliberately generous exhaustive grammar admits the mode, payload, and all three value names as free terminals. It finds no one-operation negative bottom formula; `d(m,two,u(x))` is a two-operation witness. This is a local interface lower bound, not a global router lower bound.

### 6.2 Complement-closed payload families

If the available payload roots are closed under Boolean complement, a negative leaf wires directly to the already-existing opposite-polarity payload. No unary node is added. The complete fused router then has

```text
C(w)=(3q-1)/2+R(w)+2
```

nodes and obeys

```text
3*C(w) <= 10q.
```

The worst case is `w=2`, where `C=30` and `q=9`; asymptotically

```text
C(w)=(5/2)q+O(sqrt(q)).
```

This complete router is asymptotically the same size as the improved old-interface control vector alone.

## 7. Conditional compiler consequence

This section replaces only the frozen nonbinary interface clause. It continues to assume the manuscript's selector representation, anchor, binary compiler, same-DAG substitution, glue, and finite fallback propositions.

Use the same parameters for `r>=64`:

```text
L=4+ceil(log_3(r^2)),
H=r-L,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b).
```

### 7.1 Why complement closure is available

The local table library contains every `Q`-valued function on the block, represented by two Boolean planes.

* In each local router, branch payloads are the dynamic names `zero,one`; their complements are already available.
* In each prefix router, branch payloads are Boolean local functions. The universal local library contains the complement of every Boolean plane function, so a negative leaf can reference that existing root.

Thus one width-`b` native mode vector is shared by every local table and both planes, and one width-`r-b` mode vector is shared by both prefix routers. No payload-complement operation nodes are needed in this compiler specialization.

### 7.2 Inclusive node ledger

With `R` as above, the modified nonbinary union has at most

```text
N_nb(r)
 = (3M-1)3^M
   + R(b)
   + (3P-1)
   + R(r-b)
   + 4r+7.
```

The terms are respectively the two-router local library, local mode vector, two prefix routers, prefix mode vector, and the inherited inclusive fixed overhead.

For `r>=64`:

1. `ceil(log_3(r^2)) <= r/8`, so `H>=13r/16`.
2. Maximality of `M` gives `M>H/3>=13r/48`, hence `P<(48/13)3^r/r`.
3. The prefix width is at least eight and the balanced recurrence satisfies `27R(r-b)<=28P`.
4. Therefore

   ```text
   (3P-1)+R(r-b)
     < (109/27)P
     < (1744/117) 3^r/r.
   ```

5. The two-logarithm reserve gives

   ```text
   (3M-1)3^M < (1/27)3^r/r.
   ```

6. From `R(b)<=5M/3` and exponential domination,

   ```text
   R(b)+4r+7 < (1/27)3^r/r.
   ```

Consequently

```text
N_nb(r)
 < (1744/117+2/27)3^r/r
 = (5258/351)3^r/r
 < 15*3^r/r.
```

Retaining the manuscript's separately audited binary allowance below one additional unit yields the conditional same-DAG bound

```text
size < 16*3^r/r   for r>=64.
```

The old inclusive constant was `63`. The asymptotic theorem remains `O(3^r/r)`; this is an explicit-constant improvement inside the same conditional interface, not an unconditional compiler proof.

### 7.3 Depth ledger

Let `c=ceil(log_2 r)`. The anchor depth is at most `3c`. A width-`s` native mode vector has depth at most

```text
3c+3+ceil(log_2 s)
```

from raw inputs. The local route and prefix route give

```text
D_local <= 3c+b+ceil(log_2 b)+4,
D_prefix <= max(
    D_local,
    3c+3+ceil(log_2(r-b))
  ) +(r-b)+1.
```

One two-level decoder and the two-level final glue therefore give

```text
depth <= r+4*ceil(log_2 r)+9.
```

This improves the frozen explicit `r+5 ceil(log_2 r)+12` ledger while preserving the leading coefficient one.

## 8. Exact evidence and limitations

The independent checker performs, without importing repository implementations:

* all one-digit term tables;
* associativity and first-mismatch semantics;
* all target/physical pairs through width five;
* full Boolean-payload router truth tables through width two;
* structured router tests through width five;
* exact recurrences and extremal constants through width 256;
* the modified compiler ledger for every arity `64..16384`;
* exhaustive unary-DAG local minimality searches;
* effective mutation controls.

Normal and optimized Python outputs are byte-identical. The current receipt hashes are recorded in the lane report.

Not yet established:

* a compiled Lean port of the new mode theorem and modified cost layer;
* a serialized hash-consed graph certificate;
* an unconditional integrated proof of the frozen compiler interfaces;
* publication novelty or patent freedom to operate;
* global optimality of the complete signed router or the additive `O(log r)` term.

## 9. Recommended paper change

Do not delete the old exact theorem. Present the progression:

1. `(E,G)` vector: already Lean-checked historical theorem (`7q`).
2. `(G,L)` vector: drop-in old-interface strengthening (`<4q`).
3. native find-first mode vector: leading-one preprocessing and fused router.
4. complement-closed compiler corollary: conditional constant `<16` and depth `r+4 log r+9`.

Only stages that have received a compiled Lean receipt should be labeled Lean-checked. Until the port lands, stages 2--4 should be labeled paper proof plus independent executable oracle.
