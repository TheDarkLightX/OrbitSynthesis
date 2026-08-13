# Native find-first modes for exact signed routers

**Status.** Proposed strengthening of Sections 6.9--6.10 of `FIXED_Q_TERM_COMPLEXITY_DRAFT.md`. The exact statements below have a paper proof and an independent executable oracle. They are **not yet Lean-checked**. The final compiler corollary remains conditional on the manuscript's existing interface propositions.

## 1. The hidden three-state algebra

Work on the nonbinary branch, where the anchor has value `A=2`, and put

```text
two=A,  one=u(A),  zero=u(u(A)).
```

For a target word `t` and physical branch word `p`, both in `{0,1,2}^w`, the recursive signed-router program has exactly three possible outcomes after their common prefix is consumed:

```text
E: t=p, so the bottom cell remains in projection mode;
G: the first mismatch is (t_j,p_j)=(1,2), so it enters constant-one mode;
L: the first mismatch is any other unequal pair, so it enters constant-zero mode.
```

For consecutive blocks, define `x*y` to be their first non-`E` outcome, or `E` if both are `E`. Thus

```text
E*x=x,  G*x=G,  L*x=L.
```

This operation is associative. More importantly, the encoding

```text
eta(E)=2,  eta(G)=1,  eta(L)=0
```

satisfies the exact identity

```text
eta(x*y)=d(eta(x),two,eta(y)).
```

Indeed, `two` is an identity for `d(left,two,right)`, while `zero` and `one` are left zeros. The discriminator is therefore not merely used to implement Boolean summary logic; it is the multiplication of the semantic summary algebra itself.

The abstract three-element find-first/flip-flop monoid is classical. The scoped contribution here is its exact original-signature embedding and the resulting quantitative router constructions.

## 2. A drop-in Boolean control vector below `4q`

Retain the old two-control interface, but encode the reachable states by

```text
E=(G,L)=(0,0),
G=(1,0),
L=(0,1).
```

For consecutive blocks `X,Y`, their coordinates compose as

```text
G_XY=d(G_X,L_X,G_Y),
L_XY=d(L_X,G_X,L_Y).
```

Thus each physical concatenation costs two discriminator nodes, rather than the three Boolean nodes used by the historical `(equal,gain)` recurrence.

For one target digit `x`, define

```text
n=u(x),
g=u(n),
l_0=d(x,two,n),
l_2=u(l_0).
```

The three physical-digit summaries are

```text
p=0: (G,L)=(zero,l_0),
p=1: (G,L)=(zero,n),
p=2: (G,L)=(g,l_2).
```

These use four operation nodes beyond the two shared dynamic names. Let `S(w)` count all state nodes, excluding those names, under a balanced split. Then

```text
S(1)=4,
S(w)=S(floor(w/2))+S(ceil(w/2))+2*3^w.
```

A positive root has `(q-1)/2` negative bottom cells, and a negative root has `(q+1)/2`, where `q=3^w`. Positive bottom cells use `(L,G)` directly; negative cells use `(G,u(L))`. Hence

```text
V_+(w)=2+S(w)+(q-1)/2,
V_-(w)=2+S(w)+(q+1)/2.
```

The recurrence gives

```text
9*S(w)<=28q,
27*V_+(w)<=100q,
27*V_-(w)<=100q.
```

The last constant is attained by the negative root at `w=3`. Therefore:

**Theorem A (improved reusable program vector).** For either root sign and every `w>=1`, all `2q` controls of the capacity-`q=3^w` strong signed router are realized simultaneously by legal original-signature terms with

```text
size <= (100/27)q < 4q,
depth <= 4+ceil(log_2 w)
```

above the raw anchor and target-address inputs. The vector is a drop-in replacement for the old `7q`, `6+2 ceil(log_2 w)` interface.

The executable closure search also shows that the six-node one-digit construction, including the two names, is locally minimal in the stated unary shared-DAG model.

## 3. The native `Q`-valued mode vector

The two Boolean controls are not the smallest semantic interface. Materialize one mode root `m_p(t)` per physical word:

```text
m_p(t)=2 in state E,
m_p(t)=1 in state G,
m_p(t)=0 in state L.
```

For one digit `x`, define

```text
m_0(x)=d(zero,x,two),
h_1(x)=d(one,x,two),
m_1(x)=d(h_1(x),one,zero),
m_2(x)=x.
```

Their tables are

```text
m_0=(2,0,0),
m_1=(0,2,0),
m_2=(0,1,2).
```

For a physical concatenation `p=p_Lp_R`, set

```text
m_p(t)=d(m_pL(t_L),two,m_pR(t_R)).
```

Let `R(w)` exclude the two shared name nodes. Balanced materialization gives

```text
R(1)=3,
R(w)=R(floor(w/2))+R(ceil(w/2))+3^w.
```

Consequently

```text
3R(w)<=5q,
9(R(w)+2)<=17q,
depth<=3+ceil(log_2 w),
R(w)=q+O(3^ceil(w/2)).
```

**Theorem B (native mode vector).** All `q=3^w` mode roots are simultaneously realizable with at most `17q/9` operation nodes including the two names, depth at most `3+ceil(log_2 w)`, and asymptotic size `q+O(sqrt q)`.

This leading coefficient is optimal. The `q` mode functions are pairwise distinct: `m_p(p)=2`, while `m_p'(p)` is `0` or `1` for `p'!=p`. A multi-output DAG has only the `w` target digits and anchor as free roots, so at least `q-(w+1)` distinct operation nodes are necessary. Every mode root also depends on every target digit, giving a fan-in-three depth lower bound `ceil(log_3 w)`. Thus the construction has optimal leading size coefficient one and asymptotically optimal logarithmic preprocessing depth up to the logarithm base and fixed name depth.

The five-node one-digit vector, including the two names, is locally minimal in the checked unary shared-DAG model.

## 4. Fusing modes into the signed router

For a Boolean payload `x_p`, replace the old two-control bottom cell by

```text
positive cell: d(m_p,two,x_p),
negative cell: d(m_p,two,u(x_p)).
```

The three mode values immediately give constant zero, constant one, or the correctly signed payload. The signed recursion above the base cells is unchanged.

The frozen router skeleton has `(3q-1)/2` discriminator nodes. With arbitrary payload roots, fresh complements at negative leaves give exact totals

```text
F_+(w)=2q+R(w)+1,
F_-(w)=2q+R(w)+2,
```

and hence

```text
9F_+(w)<=35q,
9F_-(w)<=35q,
depth<=w+4+ceil(log_2 w).
```

If the payload family is complement-closed, every negative leaf can instead point to an already available opposite-polarity root. Then no payload-complement node is added and

```text
C(w)=(3q-1)/2+R(w)+2,
3C(w)<=10q,
C(w)=(5/2)q+O(sqrt q).
```

**Theorem C (payload-fused signed router).** A complete capacity-`q` signed router, including preprocessing and the routing skeleton, uses at most `35q/9` nodes for arbitrary Boolean payloads and at most `10q/3` nodes for a complement-closed payload family. The latter has asymptotic size `(5/2)q+O(sqrt q)`.

A generous exhaustive local grammar finds no one-operation negative bottom formula; the displayed two-operation cell is locally optimal at that interface. This is not a global lower bound for complete routers.

## 5. Conditional compiler consequence

The two Boolean-plane local library is complement-closed: it contains every Boolean function on the local block, hence the complement of every payload root. The local constant payloads `zero,one` are also an available complementary pair. Therefore one width-`b` native mode vector can be shared by every local table and both planes, while one width-`r-b` vector is shared by both prefix routers.

Keep the manuscript's parameters, for `r>=64`,

```text
L=4+ceil(log_3(r^2)),
H=r-L,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b).
```

Replacing only the nonbinary interface gives the inclusive count

```text
N_nb(r)
 =(3M-1)3^M
  +R(b)
  +(3P-1)
  +R(r-b)
  +4r+7.
```

The inherited reserve inequalities imply

```text
N_nb(r)<15*3^r/r.
```

Retaining the separately audited binary allowance below one additional unit gives

```text
size<16*3^r/r.
```

The corresponding nonbinary depth ledger is

```text
depth<=r+4*ceil(log_2 r)+9.
```

**Conditional Corollary D.** Conditional on the manuscript's selector representation, anchor, binary compiler, same-DAG substitution, glue, and finite fallback interfaces, every conservative term operation has one original-signature shared DAG with

```text
size=O(3^r/r),
depth=r+O(log r).
```

For `r>=64`, the sharpened explicit ledger is

```text
size<16*3^r/r,
depth<=r+4*ceil(log_2 r)+9.
```

This improves the previous conditional constants `63` and `r+5 ceil(log_2 r)+12`; it does not make the integrated theorem unconditional.

## 6. Claim boundary

The evidence currently consists of the displayed proofs and an independent fail-closed oracle that checks exact semantics, frozen-interface equivalence, full routers, local minima, recurrence extrema, mutations, and every compiler arity from `64` through `16384`. Normal and optimized executions are byte-identical.

The new theorems must not be labeled Lean-checked until the proposed formal port compiles. Novelty, freedom to operate, serialized hash-consed extraction, global router optimality, and the optimal additive depth term remain open.
