# Recursive Boolean-library compiler

Date: 2026-08-14  
Verdict: **PASS for the recursive semantic library, charged recurrence,
finite proof, analytic tail, and integrated depth ledger.**

## Result

For every `r>=64` and every conservative parameter-free `r`-ary term
operation of the fixed algebra `Q`, this lane gives one original-signature
free-fanout scalar DAG with

```text
size  < (62/25)*3^r/r,
depth <= r+C+2*ceil((4C+2)/3)+15,
C=ceil(log_2 r).
```

The previous global size bound was `67/25`. The exact charged ratio over
`64<=r<=16384` is maximal at `r=64`:

```text
2.473270139955782682...
```

The local sibling-shared program-vector theorem is unchanged and retains its
matched leading scalar-output constant `4/3`.

## Recursive sharing

For a live subset `S` of `M` rows in `Q^t`, recursively split by the first
address coordinate. Every Boolean table on `S` points to its three restricted
child-table roots and combines them with one capacity-three positive signed
router. The capacity-three router costs four discriminator nodes and depth
two.

At each recursion level the nonempty child subsets partition `S`, and

```text
sum_i 2^|S_i| <= 2^M.
```

Thus the complete zero-extended Boolean function family on `S` costs at most

```text
4*t*2^M + 5*t
```

operation nodes and depth at most `2t+3` above the raw anchor/address inputs.
The `5t` term conservatively charges one complete one-digit program vector per
coordinate.

A Q-valued table is still an ordered pair of two scalar Boolean roots. No
multi-output gate or uncharged computation is introduced.

## Global portfolio

Let `J` be maximal with `9r^3 2^J<=3^r`, and let
`T=floor(log_3(rJ))`. Five explicit candidates use

```text
t=T+delta, delta in {-2,-1,0,1,2},
N=3^t,
g=ceil(N/J),
s=r-t,
P=3^s.
```

The local cube is partitioned into `g` balanced groups of at most `J` rows.
Each group receives its recursive Boolean library. Prefix routers select the
needed high/low roots. Two capacity-`N` routers select the correct group
outputs from the local address. Program vectors, the fast anchor, decoder,
binary branch, and final glue are charged once in the same DAG.

For each arity the least exact charged candidate is selected, with a fixed
tie-breaking rule.

## Proof split

For `64<=r<=339`, all five candidate ledgers are constructed with exact
integers and checked directly against the `62/25` inequality.

For `r>=340`, choose `t=ceil(log_3(rJ))`. A two-residue induction proves
`J>=3r/2`. This gives:

```text
prefix main <= 2+26/(9r),
recursive libraries <= (3r+1)/(36r),
lower-order groups < 4/1000.
```

The exact rational comparison at `r=340` closes the tail; every term decreases
or remains controlled thereafter.

## Evidence

The primary checker validates:

- exact Q-to-Boolean plane factorization through width six;
- all 512 subsets of `Q^2`;
- all 19,683 Boolean tables over those subsets;
- 177,147 recursive semantic evaluations;
- the recursive size recurrence and an effective wrong-branch mutation;
- selected non-product width-three subsets;
- every exact portfolio ledger through arity 16,384;
- the finite and analytic proofs separately;
- the depth theorem; and
- normal/optimized equality against the committed semantic receipt.

```text
primary checker SHA-256
  32560eb1802f274f7118f92b541c7a3a83eb1a84ac1d7e2211aec15225832b26
primary receipt/stdout SHA-256
  649ee47ad3342a834a5642cddc903007f5025655c61dd6dc233edb575dfc18b9
primary semantic SHA-256
  fb47ab33d1efa4648e8c11811ff18b283b1b3990c0ab35bcbcfdd29c4f21a07a
```

A separately written no-import checker independently reconstructs the
recursive libraries, rail recurrences, five-candidate portfolio, binary
branch, finite proof, analytic tail, and depth ledger.

## Boundary

This lane does not alter the local `4/3` program-vector constant, prove a
matching global lower constant, determine the exact global optimum, settle
the optimal additive depth term, or establish formula or bounded-fanout
bounds. The integrated construction is not yet serialized and proved end to
end in Lean. The lane makes no novelty, patent/FTO, license, publication, or
practical-performance finding.