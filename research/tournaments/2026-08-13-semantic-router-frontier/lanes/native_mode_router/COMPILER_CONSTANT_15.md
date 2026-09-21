# Conditional compiler constant below `15`

Keep the native-mode nonbinary ledger

```text
ell=ceil(log_3(r^2)),
H=r-4-ell,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b),

N_nb(r)=(3M-1)3^M+R(b)+(3P-1)+R(r-b)+4r+7.
```

Exact integer replay proves `N_nb(r)<14*3^r/r` for every `64<=r<=257`. The largest normalized value occurs at `r=93` and is approximately `13.777777777777779`.

For `r>=258`, one has `M>=243`; write `M=3^b`, `b>=5`. Put `k=floor(r/8)`. The inequality

```text
3^k >= (8k+7)^2
```

holds at `k=8` and propagates because the left side triples while the squared growth factor on the right is below three. Since `r<=8k+7`, this proves `ell<=floor(r/8)`.

Now `H<3M`, so first `r<4M`, and then

```text
ell<=2b+3,
2b+7<=3^(b-2)=M/9,
r/M<28/9.
```

Put `s=r-b`, so `P=3^s`. Direct calculation handles `8<=s<=15`; the balanced recurrence then proves `27R(s)<=28P` for every `s>=8`. The normalized prefix contribution is therefore below

```text
(3+28/27)*(28/9)=3052/243.
```

The reserve gives `3^M<=3^r/(81r^2)`, so the local universal-library contribution is below `1/27`. Also `R(b)<=5M/3<=5r/3`; the fixed remainder contributes below one because `3^r>6r^2` for `r>=258`. Consequently

```text
N_nb(r)r/3^r
 <3052/243+1/27+1
 =3304/243
 <14.
```

Combining the finite range and analytic tail gives

```text
nonbinary size <14*3^r/r.
```

Retaining the existing independently audited binary allowance below one additional unit sharpens the conditional all-branch ledger to

```text
total size <15*3^r/r,
depth <= r+4*ceil(log_2 r)+9.
```

This remains conditional on the frozen selector, anchor, binary-compiler, same-DAG, decoder, glue, and finite-fallback interfaces. It is not an unconditional integrated compiler theorem.
