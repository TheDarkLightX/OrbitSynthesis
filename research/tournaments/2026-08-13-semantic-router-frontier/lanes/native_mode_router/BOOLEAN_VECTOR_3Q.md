# Reusable Boolean program vector with size at most `3q`

Retain `E=(G,L)=(0,0)`, `G=(1,0)`, `L=(0,1)` and

```text
G_XY=d(G_X,L_X,G_Y),
L_XY=d(L_X,G_X,L_Y).
```

For a physical word `p`, `G_p` is zero when `p` has no digit `2`. Otherwise it depends only on the prefix ending at the final `2`. Thus the distinct nonzero width-`w` gain roots are indexed by ternary prefixes ending in `2`, exactly `(3^w-1)/2` roots.

For a balanced split `w=a+b`, let `T(w)` count all loss roots and distinct nonzero gain roots, excluding the two shared names. Gains whose final `2` lies in the left block reuse an existing left root; gains whose final `2` lies in the right block are indexed by an arbitrary left word and a nonzero right gain root. Therefore

```text
T(1)=4,
T(w)=T(a)+T(b)+3^w+3^a(3^b-1)/2.
```

Direct calculation handles widths one through three. For `w>=4`, induction reduces `3T(w)<=7*3^w` to

```text
(11/2)3^a+7*3^b <= (5/2)3^(a+b),
```

which holds in the two balanced cases `a=b` and `b=a+1` because `a>=2`.

With `q=3^w`, the positive and negative root counts are

```text
V_+(w)=2+T(w)+(q-1)/2,
V_-(w)=2+T(w)+(q+1)/2.
```

Hence, for either root sign,

```text
size<=3q,
depth<=4+ceil(log_2 w).
```

The unique worst case is the negative root at width two. Moreover `T(w)=(3/2)q+O(3^ceil(w/2))`, so the complete reusable vector has size `2q+O(3^ceil(w/2))`.

This is a drop-in strengthening of the first `100q/27` construction. The native `Q`-valued mode vector and payload-fused router remain smaller interfaces.
