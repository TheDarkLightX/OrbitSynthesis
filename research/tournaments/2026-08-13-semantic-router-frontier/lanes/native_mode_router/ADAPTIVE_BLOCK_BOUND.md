# Adaptive block bound

For `r>=64`, set

```text
ell=ceil(log_3(r^2)),
H=r+1-ell,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b).
```

The native nonbinary ledger is

```text
N=(3M-1)3^M+R(b)+(3P-1)+R(r-b)+4r+7,
R(1)=3,
R(w)=R(floor(w/2))+R(ceil(w/2))+3^w.
```

Exact replay proves `N<(53/4)3^r/r` for `64<=r<=740`; the maximum is at `r=88`, immediately before `M` changes from `27` to `81`.

For `r>=741`, write `M=3^b`, so `b>=6`. The earlier estimate `ell<=r/8` and `H<3M` give `r<24M/7`, hence `ell<=2b+3`. Therefore `50(ell-1)<=M`.

Put `x=r/M`, `g=r-M`, and `a=109/27`. The prefix router plus native prefix vector contributes less than `a*x` normalized units.

If `g=ell-1`, the local library contributes less than `9/x`; since `1<=x<=51/50`,

```text
9/x+a*x <=352/27.
```

If `g>=ell`, the local contribution is below `3/x` and `x<151/50`. For `x<=3`,

```text
3/x+a*x <=118/9;
```

for `x>3`, the sum is below `17809/1350`.

Also `R(b)+4r+7<6r`. Since `3^r>104r^2` from `r=741` onward, this remainder contributes less than `3/52`. Thus

```text
N*r/3^r <17809/1350+3/52
          =465059/35100
          <53/4.
```

The retained binary count already splits into three strict bounds below `1/4`: router skeletons, shared controls, and fixed overhead. Hence it is below `3/4`, and the complete conditional ledger is

```text
size <14*3^r/r,
depth<=r+4*ceil(log_2 r)+9.
```

This remains conditional on the frozen selector, anchor, binary branch, same-DAG, decoder, glue, and finite-fallback interfaces.
