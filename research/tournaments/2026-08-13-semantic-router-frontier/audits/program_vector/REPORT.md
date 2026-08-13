# Independent audit: parallel program vectors and giant-router ledger

Date: 2026-08-13

## Verdict

**EXACT PASS for the program-vector theorem. CONDITIONAL PASS for the
integrated compiler ledger. No coefficient-breaking flaw found.**

The independent, no-author-import auditor verifies from first principles that
the guarded first-mismatch construction materializes every control pair of a
width-`w` signed discriminator router, `q=3^w`, in one original-signature
shared DAG with

```text
operation nodes <= 7q,
depth           <= 6+2*ceil(log_2 w)                 (w>=1).
```

The author's statement charges the two shared name nodes separately. The
independent count proves the slightly stronger inequality that the same `7q`
bound still holds after including those two nodes. The result relies on
unrestricted circuit fanout. It is not an ordinary formula-size or
bounded-fanout theorem.

The giant nonbinary arithmetic also survives. With the stated `C=4`, the
audited ledger has, for every `r>=64`,

```text
nonbinary size  < 62*3^r/r,
binary size     <     3^r/r,
combined size   < 63*3^r/r,
nonbinary depth <= r+5*ceil(log_2 r)+12.
```

The retained binary depth is below `r` for every `r>=339`. Therefore the
combined asymptotic depth is `r+O(log r)`.

This does **not** promote the integrated all-arity result to an unconditional
theorem. The exact vector theorem and arithmetic are independently proved, but
the end-to-end compiler still composes frozen premises for the global anchor,
selector library, binary schedule, decoder, final glue, and the finite
small-arity fallback. Manuscript wording must preserve that conditional
boundary.

## Frozen subject

The auditor fails closed unless all of these exact bytes are present:

```text
STATE.md
  5304ad459b25928e14197dfb989af7dfae4d9df6b632eb79020e9f1cef812133

lanes/fused/check_strong_router_family.py
  07fb1d8d322e57a7af666bae5b699c072805ff1d15eef1f1e7c2d87208729ef8
lanes/fused/summary.json
  6042127fd9f214e63bc38aa8e6367d1db7580c24b2b2e7a3aeba16625279aff0
lanes/fused/r27_witness.json
  6dd402fd32bb560b341ee75805bd71c90e2fa2bd3c9274c982f908ef21c15e65
lanes/fused/REPORT.md
  5ed37d98357eb03a2f6ded9f741c9fb52d8f5ad821585c81be544f201945f8c6

audits/variable_compiler/REPORT.md
  174a8fdf32e47fcce650298df5554a9f7c101fc67cc7be4ab4d2acb14bc5c661

lanes/program_vector/REPORT.md
  d4a4a6e8c512b915c35129b7158da5a841456c26acc569e677fda8a965f30834
lanes/program_vector/check_parallel_program_vector.py
  2ba586a1ef97822aebbbcf692d29cd5bd3f8bbc8e785ddce43aff2180df3c350
lanes/program_vector/manifest.json
  9d470da6b6f5559bc7e5b461255ce6d3bc3bfab10025d6ab48a99f41a34c694e
lanes/program_vector/receipt.json
lanes/program_vector/receipt_optimized.json
  c9e8b1ad9c57f4ef55ea458b2573f20578a137a6c7b5fb1a66707bb7ee68b632
```

The audit did not import or edit any of them.

## 1. First-mismatch law and recursive programs

For target `t` and physical word `p`, define

```text
E_p(t) = 1 iff t=p,
G_p(t) = 1 iff the first mismatch is (t_j,p_j)=(1,2).
```

The independent recursion expands the author's three child-mode tables
directly:

```text
t_j=0: (project, zero, zero),
t_j=1: (zero, project, one),
t_j=2: (zero, zero, project).
```

It does not call the `E/G` implementation. A physical path remains projected
while its digits agree. Its first disagreement fixes the mode forever: the
mode is one only for `(1,2)`, and zero otherwise. Exhaustive comparison through
width six gives exactly the displayed `E/G` law and verifies `E*G=0`.

For consecutive segments, set

```text
(E,G) star (F,H) = (E and F, G or (E and H)).
```

The guard `E` is essential: the right segment may own the first mismatch only
if the left segment is equal. The operation is associative on all four
Boolean pairs, not merely on reachable disjoint pairs, because both bracketings
reduce to

```text
(E F K, G or E H or E F L).
```

All 64 triples of Boolean pairs pass an independent exhaustive check.

## 2. Both cell signs and both constants

Let `a=E or G`. A positive cell `P1=d(x,c0,c1)` receives

```text
(not a,G).
```

This is `(0,0)` in projection mode, `(1,0)` in zero mode, and `(0,1)`
in one mode. A negative cell `N1=d(c0,x,c1)` receives

```text
(G,a).
```

This is `(0,1)` in signed projection mode, `(0,0)` in zero mode, and
`(1,1)` in one mode. The negative projection produces `1-x`, exactly as the
frozen `N` interface requires. For a requested constant `c`, the independent
formulas are

```text
positive cell: (1-c,c),
negative cell: (c,c).
```

The auditor evaluates every pair on both Boolean payload values, both root
signs, all target/physical pairs through width six, and both constants.

The sign used at physical word `p` is derived independently as root sign XOR
the parity of the digit-1 edges in `p`. A direct ternary-ROBDD reconstruction
of the entire recursive router then verifies every projection/complement and
constant mode through width four.

## 3. Exact original-signature realization

On the nonbinary branch, the premise `A=2` legally gives

```text
two=A,
one=u(A)=1,
zero=u(u(A))=0.
```

The one-digit indicators are exactly

```text
delta_0(x)=u(d(x,two,one)),
delta_1(x)=d(x,two,zero),
delta_2(x)=u(d(x,zero,one)).
```

For Boolean intermediates,

```text
x and y = d(x,one,y),
x or y  = d(x,zero,y),
not x   = u(x).
```

All rows are checked under the actual operations

```text
d(x,y,z)=z if x=y, else x,
u(0)=1, u(1)=0, u(2)=1.
```

The generated syntax contains only `d`, `u`, the anchor input, and target
address digits. It contains no payload input and no nullary constant. The
zero/one table leaves are fanout references to the two shared name terms, not
free constant gates.

The two-plane code is kept encoded through both router stages. The sole final
decoder uses the codewords

```text
0 -> (0,0), 1 -> (0,1), 2 -> (1,0)
```

and the two-node term

```text
d(d(high,one,A),zero,low).
```

All three decoder rows pass. No decoder is inserted at each local table.

## 4. Shared-DAG size and depth

Let `S(w)` count the balanced `E/G` state construction, excluding the two
shared names. The independently materialized DAG obeys

```text
S(1)=5,
S(w)=S(floor(w/2))+S(ceil(w/2))+3*3^w.
```

The three new nodes per physical concatenation are `E_left and E_right`,
`E_left and G_right`, and their guarded `G` disjunction. Child segment vectors
are built once and fan out to all concatenations; they are not rebuilt for
each output word.

Direct bases `w=1,2,3`, followed by

```text
5(3^a+3^b) <= (10/9)3^(a+b)       (a,b>=2),
```

give `S(w)<=5q`. Forming every final pair adds at most `q` active
disjunctions and `(q+1)/2` negations. Hence the logic beyond the names is at
most

```text
5q+q+(q+1)/2.
```

Adding the two names is still at most `7q` for `w>=2`; `w=0,1` pass as exact
bases. The auditor materializes both signs through width nine and checks this
recurrence through width 512.

At width nine, `q=19683`, the positive vector has:

```text
shared-DAG operation nodes including names   76,390,
certified 7q ceiling                        137,781,
expanded unshared output forest           5,704,790,
maximum observed fanout                       33,457.
```

This is concrete evidence against a hidden `q*w` construction in the shared
DAG and equally concrete evidence that the theorem cannot be relabeled as a
formula bound.

The one-digit indicator depth is at most four above raw anchor/address inputs.
Each balanced composition layer adds at most two `d` layers, and final pair
formation adds at most two. Therefore

```text
D_vector(w) <= 6+2*ceil(log_2 w).
```

The width-zero base uses only the two name levels.

## 5. Padding

For a non-power-of-three live arity, every unused physical slot is wired to
the last live branch and only live target words are requested. Inactive cells
are forced to constants by the exact program, so duplicate payload wires
cannot alter the selected live branch.

The independent ROBDD checker tests every live count, not only `q-1`, for each
capacity `q=3,9,27,81`, both root signs, and every live target. All 7,500
padding cases pass. Giant nonbinary local and prefix arities are already exact
powers of three.

## 6. Giant nonbinary size ledger

For `r>=64`, use exactly

```text
H = r-4-ceil(log_3(r^2)),
M = 3^floor(log_3 H),
b = log_3 M,
P = 3^(r-b)=3^r/M.
```

Then `H/3<M<=H`, `H>=r/2`, and `M>r/6`. For the middle inequality,
`r/2-4-log_3(r^2)>1` at `r=64` and its left side increases thereafter;
`ceil(x)<=x+1` then gives `H>=r/2`. Write `V(w)` for the program-vector logic
bound excluding the globally shared names. The complete audited nonbinary
upper ledger is

```text
local routers, two planes       (3M-1)3^M
local program, shared           V(b)
prefix routers, two planes      3P-1
prefix program, shared          V(r-b)
balanced anchor                 4(r-1)
shared names                    2
one final decoder               2
final glue                      3
```

There are `3^M` local `Q`-valued tables. Each table has two
`P_(b+1)` routers; together they contain exactly `3M-1` discriminator nodes.
One width-`b` vector is shared among all tables and both planes. At the prefix,
the two `P_(r-b+1)` routers contain `3P-1` nodes and share one width-`r-b`
vector. Thus there is no free control ROM, no per-plane program duplication,
and no per-table decoder.

The two-log reserve is sufficient because

```text
3^M <= 3^(r-4)/r^2,
(3M-1)3^M < 3r*3^(r-4)/r^2 = (1/27)3^r/r.
```

The prefix routers and vector satisfy

```text
(3P-1)+V(r-b) < 10P < 60*3^r/r.
```

Finally, `V(b)<=7M` and all anchor/name/decoder/glue terms are bounded by

```text
7M+4r+7 <= 11r+7,
(11r+7)r/3^r < 1.
```

The last ratio is below one at `r=64` and decreases thereafter; cross
multiplication reduces the step to `22r^2-8r-18>0`. Therefore

```text
S_nonbinary/(3^r/r) < 60+1/27+1 < 62.
```

Independent big-integer replay covers all 16,321 arities from 64 through
16,384, including every reserve and power jump. Its largest exact normalized
nonbinary ledger value is

```text
25.833333333333 at r=93.
```

The integer sweep is a falsifier; the inequalities above supply the universal
tail.

## 7. Giant nonbinary depth

The local and prefix address vectors are prepared in parallel with the data
they control. They are not evaluated once per physical router or stacked once
per control bit. With anchor depth `3*ceil(log_2 r)`, the exact audit ledger is

```text
local control  = anchor depth + D_vector(b),
local plane    = max(anchor names, local control) + b+1,
prefix control = anchor depth + D_vector(r-b),
prefix plane   = max(local plane, prefix control) + (r-b)+1,
final          = prefix plane + decoder + glue.
```

Using both vector bounds gives

```text
D_nonbinary <= r+5*ceil(log_2 r)+12.
```

The router depths contribute `(b+1)+(r-b+1)=r+2`; the remaining overhead is
logarithmic or constant.

## 8. Binary relative branch

Absolute names from `A=2` are unavailable on the all-binary cube. The retained
branch uses a logical relative bit `p` with the physical wire

```text
p=0: x0,
p=1: u(x0).
```

Thus the logical program is address-only, but the physical control depends on
the payload orientation `x0`. The auditor explicitly observes physical values
zero and one for the same logical zero under the two orientations. Legality
comes from all eight rows of

```text
u(d(x,y,z))=d(u(x),u(y),u(z))
```

on Boolean inputs, not from treating these wires as absolute constants.

For `k=floor(sqrt r)`, `q=3^k`, and `w=floor(log_2 q)`, the independent ledger
reconstructs residual-first chunk widths, every prefix instance, every router,
all relative-control tables, and fixed overhead. Put `Q=2^w` and
`N=2^(r-1)`. Since `Q<=q<2Q` and `Q<N`, router nodes are below
`6(N+Q)<6*2^r`. Control tables are below `6r q^2`, so

```text
routers normalized < 6r(2/3)^r < 1/4,
controls normalized < 6r^2/3^(r-2k) <= 6/r^2 < 1/4,
fixed normalized < (4r+10)r/3^r < 1/4.
```

The middle inequality uses `3^(r-2floor(sqrt r))>=r^4`. Its minima occur at
square boundaries; the base `r=64` passes and the boundary ratio increases.
Hence the binary branch is strictly below one `3^r/r` unit for every `r>=64`.

For depth, exact replay establishes `D_binary<r` for `339<=r<900`. For the
tail, let `a=floor(3k/2)`. Then `w>=a`, `w<2k`, and
`ceil(log_2 r)<=k`, giving

```text
D_binary < (k+1)r/a+8k+9.
```

Since `r>=k^2`, the sufficient inequality reduces at
`a=(3k-1)/2` to

```text
k^3-27k^2-19k+9 > 0.
```

It equals 2,139 at `k=30`; its forward difference is
`3k^2-51k-45>0` thereafter. This closes the universal tail. The exact sweep
continues through 16,384 and finds the same threshold `r=339`.

The binary result remains an integrated-premise claim: this audit verifies the
relative-control identity and complete arithmetic schedule, not a second
standalone construction of every frozen compiler component.

## 9. Killer falsifiers and boundary attacks

| Attack | Result |
|---|---|
| Unguarded `G_left or G_right` | Rejected at `t=(0,1),p=(1,2)`: correct `G=0`, mutated `G=1`. |
| Sequential `q*w` vector | Rejected at `r=512`; prefix controls alone exceed `100*3^r/r`. |
| One-log reserve | Rejected at `r=6574`, where `M=6561`; local routers alone exceed the full 62-unit allowance. |
| Round `M` upward | Rejected already at `r=64`: `H=52`, floor `M=27`, ceiling `M=81>H`. |
| Hidden `q*w` duplication | Absent in the hash-consed operation list; each segment vector is built once. |
| Reinterpret DAG as formula | Rejected; width-nine expansion is 5,704,790 operations versus 76,390 shared nodes. |
| Free nullary zero/one | Rejected; both are explicit `u` terms below `A=2`. |
| Binary absolute names | Rejected; `A,u(A),u(u(A))` is not `(2,1,0)` for binary `A`. |
| Decode every local table | Not used. At `r=93` it would add 15,251,194,969,972 nodes relative to one final decoder and invalidate the stated exact ledger. |
| Small-arity giant schedule | Not claimed for `r<64`; the frozen fallback is a named premise, not silently inferred. |
| Padding only at `q-1` | Strengthened: every live count through capacity 81 passes. |

## 10. Deterministic evidence

The independent auditor imports no author module. It contains its own
discriminator and unary operations, recursive mode expansion, guarded segment
algebra, hash-consed `d/u` DAG, direct ternary ROBDD, padding sweep, integer
compiler ledger, and mutation gates.

Key counts are:

```text
associativity rows                                      64
first-mismatch/disjoint rows                       597,871
segment composition rows                         4,110,364
pair and constant evaluations                    7,174,452
materialized pair evaluations through width five   132,860
state-recurrence widths                                512
full-router projection/complement checks               242
full-router constant checks                             20
all-live-count padding checks                        7,500
compiler arities                                  16,321
```

Normal and optimized Python receipts are byte-identical:

```text
audit_program_vector.py
  5324d81e377f8038795b97574eae9d4ba8728a3a74af189d39fda4f76abc6e5d

receipt.json
receipt_optimized.json
  f6af15d3b5a8330a0f8248f9ffa5410dd1dfc762a89dbc20ecfe0d21aee714b8

receipt semantic SHA-256
  4922df2221b3e6195d7b1af3a3ac770ae92a8aed10843430b9cffb20959c58ea
```

Reproduce from the repository root:

```text
python3 research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/audit_program_vector.py \
  --out research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/receipt.json

python3 -O research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/audit_program_vector.py \
  --out research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/receipt_optimized.json

cmp -s research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/receipt.json \
  research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/receipt_optimized.json
```

## 11. Exact boundary and nonclaims

The program-vector theorem is exact within the declared algebra and
same-DAG model. The size/depth compiler implication is conditional on the
named frozen composition premises. Nothing in this audit establishes:

- an unshared formula or bounded-fanout bound;
- an optimal constant or lower bound;
- an unconditional all-arity compiler theorem;
- Lean or other proof-assistant verification;
- practical performance or publication readiness;
- novelty, a complete prior-art search, copyright clearance, patent freedom
  to operate, or rights under the unsigned Tau development license.

Prior art, novelty, and FTO remain **UNKNOWN**.
