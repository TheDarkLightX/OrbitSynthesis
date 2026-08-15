# Direct-Q local routing: a size-depth Pareto theorem below `8`

Date: 2026-08-15  
Status: **post-referee fresh-room theorem: explicit construction, bounded complete-DAG semantics, exact finite replay, and analytic tail**

## 1. Result

The coefficient-one signed router is optimal for the exact Boolean program vector, but not every short routing block needs the Boolean-plane representation. A five-node direct `Q`-valued selector is more size-efficient and costs only two additional dependency levels per routed coordinate. Using it on the `O(log r)` local and inner-prefix coordinates, then switching once to the long signed Boolean-plane router, gives a new Pareto point.

For every compatible coordinate selector and every `r>=64`, the construction below produces one parameter-free original-signature shared DAG satisfying

```text
size  <8*3^r/r,
depth <=r+6*ceil(log_2 r)+9.
```

The finite normalized maximum of the audited ledger is

```text
7.925011431184678...
```

at arity 84. The declared architecture has normalized limsup exactly

```text
15/2=7.5.
```

This theorem is intentionally maintained on a post-referee branch. It does not alter the immutable `4c88add7…` external-review target.

## 2. A five-node ternary multiplexer

On the nonbinary branch write

```text
two=A,
one=u(A),
zero=u(u(A)),
```

under the explicit premise `A=2`. Define

```text
Mux_Q(x;b0,b1,b2)
 =d(
    d(zero,x,b0),
    zero,
    d(d(one,x,b1),one,d(x,two,b2))
   ).
```

This uses five discriminator nodes. Direct substitution gives

```text
Mux_Q(0;b0,b1,b2)=b0,
Mux_Q(1;b0,b1,b2)=b1,
Mux_Q(2;b0,b1,b2)=b2.
```

Its maximum payload dependency depth is three.

The executable oracle checks all

```text
3^4=81
```

selector/payload valuations.

## 3. Two-node encoding and one-node decoding

For a `Q`-valued root `y`, define

```text
p(y)=d(zero,y,one),
q(y)=d(y,two,zero).
```

Then

```text
0 -> (1,0),
1 -> (0,1),
2 -> (0,0).
```

The inverse on those three legal codes is the single discriminator node

```text
Dec(p,q)=d(q,p,two).
```

Thus a direct `Q` root can be converted to two Boolean rails with two nodes and recovered after signed routing with one node.

## 4. Direct recursive local library

Put

```text
ell=ceil(log_3 r),
H=r+1-ell,
M=3^floor(log_3 H),
b=log_3 M.
```

The local block has `b` coordinates and `M=3^b` rows.

At width zero, the three constant local tables are represented by the shared roots `zero,one,two`. Inductively, every table on `j` coordinates is a triple of tables on `j-1` coordinates. Build its root by one `Mux_Q` on the new coordinate.

There are exactly

```text
3^(3^j)
```

`Q`-valued tables on `j` coordinates. Therefore the complete direct library has

```text
L_5(b)=5*sum_(j=1)^b 3^(3^j)
```

operation nodes beyond the shared names and depth

```text
3b
```

above those names.

Unlike the recursive two-plane library, this library has one native `Q` root per table and requires no local decoder.

## 5. Short direct residual block

Let

```text
a=b+1,
c=r-b-a,
U=3^a,
V=3^c,
P=UV=3^(r-b)=3^r/M.
```

For every assignment of the final `c` coordinates, build one direct `Q` selector on the preceding `a` coordinates. Its branches point to the already-existing local table roots. A full width-`a` ternary tree has `(U-1)/2` internal nodes, so all `V` direct selectors cost

```text
(5/2)V(U-1)
```

nodes.

Encode each of the `V` resulting `Q` roots by the two one-node rails in Section 3. This costs `2V` nodes.

## 6. Long coefficient-one outer block

Use two positive strong signed routers of capacity `V`, one for each rail. They share one width-`c` sibling-shared order-pair vector. The two router skeletons use

```text
3V-1
```

nodes, and the shared vector uses `C_+(c)` nodes.

A single one-node decoder then returns the selected `Q` value.

The exact residual union is

```text
R(r)
 =(5/2)V(U-1)
  +2V
  +(3V-1)
  +C_+(c)
 = (5/2)P+(5/2)V-1+C_+(c).
```

For `c>=7`, the exact order-pair recurrence gives

```text
C_+(c)<=3V/2,
```

and hence

```text
R(r)<=5P/2+4V.
```

The leading residual coefficient is therefore `5/2`, rather than `3` in the all-signed two-plane compiler.

## 7. Complete graph

The final graph contains

```text
L_5(b)                 direct local library,
R(r)                   direct/signed residual selector,
4r+2                   anchor, names, one decoder, and final glue,
B(r)                   complement-relative binary branch.
```

Thus

```text
N(r)=L_5(b)+R(r)+4r+2+B(r).
```

The binary branch and final glue are exactly the same as in the integrated reconstruction. No absolute Boolean constant is used on the binary cube.

## 8. Depth

Let

```text
D=ceil(log_2 r).
```

The balanced anchor has depth at most `3D`, and the dynamic names have depth at most `3D+2`.

The local library has depth at most

```text
3D+2+3b.
```

The direct residual block adds `3a` levels, its two encoders add one level, and the long signed block adds `c+1` levels. The one-node decoder and two-level final glue add three more levels. Therefore

```text
D_total
 <=3D+7+3b+3a+c
 =r+3D+2b+2a+7
 =r+3D+4b+9.
```

Since `3^b<=r`,

```text
2^(3b)<=(3^b)^2<=r^2<=2^(2D),
```

so `3b<=2D`. Consequently

```text
D_total<=r+6D+9.
```

The leading depth coefficient remains one; the price for the smaller size constant is two additional logarithmic-depth units compared with the immutable `19/2`, `r+4D+9` theorem.

## 9. Finite range

The exact integer audit checks every arity

```text
64<=r<1024.
```

It proves

```text
N(r)r<8*3^r
```

and the displayed depth inequality. The maximum occurs at `r=84`:

```text
N(84)*84/3^84
 =7.925011431184678...
 <8.
```

## 10. Analytic tail

Assume `r>=1024`. Put

```text
x=r/M,
g=r-M.
```

The adaptive schedule satisfies

```text
M>=729,
b>=6,
50(ell-1)<=M,
x<151/50.
```

The following four normalized terms are each below `1/100`:

1. all earlier levels of `L_5(b)` below the final `5*3^M` term;
2. the residual correction `4V`;
3. the fixed `4r+2` infrastructure; and
4. the explicit binary branch.

It remains to bound

```text
5r/3^g +(5/2)x.
```

### Transition case: `g=ell-1`

Here `H=M`, `ell=b+1`, and `3^g=M`. Also

```text
x=1+(ell-1)/M<=51/50.
```

Therefore the two main terms are

```text
5x+(5/2)x
 =(15/2)x
 <=153/20
 =7.65.
```

### Nontransition case with `x<=9/5`

Now `g>=ell`. Since `ell>=b+1`,

```text
3^g>=3^ell>=3M.
```

Hence the local-library main term is at most `(5/3)x`, and

```text
(5/3)x+(5/2)x
 =(25/6)x
 <=15/2
 =7.5.
```

### Nontransition case with `x>9/5`

Now

```text
g>(4/5)M.
```

For `M>=729`, exponential domination gives

```text
5r/3^g<1/100.
```

The residual main term satisfies

```text
(5/2)x<151/20=7.55.
```

### Tail total

Including the four common hundredths, every tail case is below

```text
7.69<8.
```

This proves the theorem for all `r>=1024` and hence for every `r>=64` together with the finite range.

## 11. Architecture-specific limsup

The tail bounds imply

```text
limsup_(r->infinity) N(r)r/3^r<=15/2.
```

For the reverse inequality, take

```text
r_b=3^b+b-1.
```

Then `ceil(log_3 r_b)=b+1` and

```text
r_b+1-ceil(log_3 r_b)=3^b-1,
```

so the selected local assignment count is `M=3^(b-1)`. Along this sequence,

```text
r_b/M ->3,
```

while the local library and all lower-order terms vanish after normalization. The direct residual skeleton contributes

```text
(5/2)r_b/M ->15/2.
```

Therefore

```text
limsup_(r->infinity) N(r)r/3^r=15/2
```

for this declared compiler architecture.

This is not a lower bound for arbitrary circuits over `{d,u}`.

## 12. Consolidated Pareto theorem

**Theorem.** For every complement-invariant coordinate selector and every `r>=64`, the direct-Q/local signed-outer compiler constructs one parameter-free original-signature shared DAG with

```text
size  <8*3^r/r,
depth <=r+6*ceil(log_2 r)+9.
```

Together with the selector representation theorem, the same result holds for every conservative `r`-ary term operation of `Q`.

The two currently strongest explicit Pareto points are therefore

```text
size <(19/2)*3^r/r, depth <=r+4ceil(log_2 r)+9,
size <8*3^r/r,      depth <=r+6ceil(log_2 r)+9.
```

## 13. Evidence boundary

The companion audit records:

```text
81 exact multiplexer cases,
66 complete selector tables,
2,214 complete semantic rows,
960 exact finite arities,
199,693 analytic-tail assertions,
all three tail cases with nonzero witnesses.
```

Normal and optimized receipts are byte-identical.

This is post-referee research. It is not part of the immutable review commit `4c88add7…`, the unavailable local `01ddf456…` packet, or its 65-source portfolio gate. Publication novelty and global constant optimality remain unknown.
