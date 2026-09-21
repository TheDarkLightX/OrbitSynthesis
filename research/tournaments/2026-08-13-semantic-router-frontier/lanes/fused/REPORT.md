# Recursive signed discriminator routers

Date: 2026-08-13

Status: **major conditional theorem candidate; independent audit pending**.  The
recursive router theorem below has an explicit induction and deterministic
exact checks.  Its substitution into the frozen same-DAG compiler gives the
candidate bounds

```text
size  = O(3^r/r),
depth = r + O(sqrt(r)).
```

This matches the leading coefficient of the existing counting lower bound,
but does not close the lower-order gap.  No novelty, optimality beyond that
leading coefficient, practical-performance, patent/FTO, license, Tau, or
publication claim is made here.

## 1. The polarity repair

On the Boolean subalgebra, the discriminator is

```text
d(x,y,z) = majority(x,1-y,z),
```

not ordinary positive majority.  The frozen counterexample to the discarded
two-extreme argument remains

```text
F(x0,x1)=d(x0,x1,0),
F(0,1)=0, F(1,0)=1, but F(1,1)=0.
```

The construction here does not use that false extremal lemma.  It instead
tracks the sign created by every middle edge exactly.  This was the useful
combination of the Morph/Tricki-style moves used in this lane: normalize the
polarity coordinate, factor the desired interface into projection and
constant modes, then prove the interface compositionally.

## 2. Strong positive and negative routers

Let a strong positive router `P_h` have the following three programmable
modes on Boolean inputs:

- project any one of its branch variables unchanged;
- return constant `0`; or
- return constant `1`.

A strong negative router `N_h` has the same constant modes and can project the
complement of any branch variable.

At depth one, use

```text
P_1(x;c0,c1) = d(x,c0,c1),
N_1(x;c0,c1) = d(c0,x,c1).
```

The exact programs are

| router | project | constant 0 | constant 1 |
|---|---|---|---|
| `P_1` | `(0,0)` | `(1,0)` | `(0,1)` |
| `N_1` | `(0,1)` | `(0,0)` | `(1,1)` |

For `h>1`, partition the branches into three consecutive equal groups and set

```text
P_h = d(P_(h-1), N_(h-1), P_(h-1)),
N_h = d(N_(h-1), P_(h-1), N_(h-1)).
```

The three recursive projection programs, for either sign, are

```text
target in group 0: (project, constant 0, constant 0),
target in group 1: (constant 0, project, constant 1),
target in group 2: (constant 0, constant 0, project).
```

For a positive parent these give, respectively,

```text
d(x,0,0)=x,
d(0,1-x,1)=x,
d(0,0,x)=x.
```

For a negative parent the corresponding expressions return `1-x`.  To force
a parent constant `c`, force all three children to `c`, since `d(c,c,c)=c`.
This proves the following family by induction.

### Strong-router theorem

For every `h>=1`, there are original-signature full discriminator trees
`P_h,N_h` with

```text
capacity q_h             = 3^(h-1),
branch leaves            = q_h,
address-control leaves   = 2q_h,
discriminator nodes      = (3^h-1)/2 = (3q_h-1)/2,
dependency depth         = h.
```

Every branch occurs once.  In `P_h` its number of middle edges is even; in
`N_h` it is odd.  Thus the construction is an exact polarity lift in the
original `d` syntax, not a free-signed-leaf over-approximation.

At `h=4` this is an exact depth-four `R27`, substantially beyond the frozen
depth-four target `R19`.  At `h=6` it is an `R243`, beyond `R82`.  For fixed
`h`, the routing coefficient is

```text
h*log_(3^(h-1))(3) = h/(h-1).
```

Ordinary serial composition of the old `R9` is not being presented as the
result: the signed constant modes are the compositional invariant that
produces the whole family and permits `h` to grow with `r`.

## 3. Boolean-orbit and Q lifts

Every `d` term commutes with Boolean complement:

```text
d(1-x,1-y,1-z) = 1-d(x,y,z).
```

Consequently the same `P_h` program works on the all-binary branch with
relative names.  If the orientation bit is `a`, logical program bit `p` is
materialized as `p xor a` using `(a,u(a))`; complementing both branches and
controls complements the routed result.  Controls still depend only on the
address chunk.

On a nonbinary anchor slice use the established code

```text
e(0)=(0,0), e(1)=(0,1), e(2)=(1,0).
```

Run two sibling copies of `P_h` with the same controls, one per bit plane, and
decode once with

```text
Dec(high,low)=d(d(high,one,two),zero,low).
```

The two copies are ordinary sub-DAGs, not a new multi-output primitive.  They
double router-node count but run in parallel.  Exact replay checks the
complement-relative bridge on all `9*2*2^9=9,216` depth-three cases and the Q
bridge on all `9*3^9=177,147` payload/target cases.

## 4. Variable router and local-code parameters

The strongest schedule in this lane chooses, for sufficiently large arity
`r`,

```text
k = floor(sqrt(r)),
h = k+1,
q = 3^k.
```

For the local encoded library define

```text
R = floor(3^r/(r*q)),
H = floor(log_3 R),
b = floor(log_3 H),
M = 3^b,
P = 3^(r-b) = 3^r/M.
```

Here `M` is the number of assignments in the local block and `b` is its
number of ternary coordinates.  Since

```text
H = r-k-log_3(r)+O(1) = r-O(sqrt(r)),
H/3 < M <= H,
```

we have `M=Theta(r)`, `b=Theta(log r)`, and eventually `b<=k`.  All finitely
many smaller arities can use the already frozen compiler and are absorbed by
the asymptotic constants.

## 5. Same-DAG size ledger

### Encoded local library

Because `M<=H` and `3^H<=3^r/(r*q)`, all `3^M` local Q-valued functions cost
at most two routers each:

```text
2*((3^h-1)/2)*3^M
  < 3*q*3^M
  <= 3*3^r/r.
```

The local block has `M<=q` assignments, so it needs one router level.  Its
`2q` program-control terms are shared by every local function and by the two
planes.

### Prefix routers and the residual-first lemma

Chunk the remaining `r-b` coordinates into widths at most `k`, with the short
residual first.  Write those widths as `(s,k,...,k)`, put `a=3^s`, and let
there be `m` full chunks.  Then `P=a*q^m`, and the exact number `I` of router
instances in the shared prefix DAG is

```text
I = 1+a+a*q+...+a*q^(m-1),
(q-1)I = P+q-a-1 <= P+q.
```

With two planes and fewer than `3q/2` nodes per router, the prefix costs

```text
< 3q*I = O(P+q) = O(3^r/r).
```

Residual-first is essential, not cosmetic.  At `r=512`, the square-root
schedule has `k=22`, `q=3^22`, `b=5`, and `r-b=507=1+23*22`.  The correct
widths `(1,22,...,22)` satisfy

```text
(q-1)I = P+q-4.
```

Moving the residual to the end gives

```text
(q-1)I_wrong = q^24-1 > P+q,
```

an extra growing factor `q/3`.  The checker freezes and rejects this exact
mutation.  The binary chunks also use residual-first order.

### Address controls

At each routing level there are exactly `2q` Boolean program slots.  A generic
control table on a ternary address chunk of width `w<=k` is compiled by the
existing seven-discriminator ternary selector, using at most

```text
7*(3^w-1)/2 nodes and depth 3w
```

above its names.  All router instances at that level share those terms.
Therefore all nonbinary controls cost

```text
O((r/k)*q^2)
 = O(sqrt(r)*3^(2sqrt(r)))
 = o(3^r/r).
```

This deliberately generic bound does not assume a hidden recursive decoder
for the program bits.

### Binary branch and glue

Let `w=floor(log_2 q)=Theta(k)`.  Residual-first binary chunks have fanout
`2^w<=q<2^(w+1)`.  The complement-relative binary branch therefore costs

```text
O(2^r + (r/k)q^2) = o(3^r/r)
```

and has depth

```text
log_3(2)*r + O(sqrt(r)).
```

The anchor, final binary/nonbinary selector, one decoder, and name terms are
polynomial size and `O(log r)` depth.  Thus the complete object remains one
original-signature shared DAG of size `O(3^r/r)`.

## 6. Depth ledger

The nonbinary data path crosses one local-library router plus at most
`ceil((r-b)/k)` prefix routers.  Controls are precomputed in parallel, so
their depth is charged once as a maximum rather than incorrectly added at
every router instance.  Hence

```text
D_nonbinary
 <= (k+1)*(1+ceil((r-b)/k)) + O(k+log r)
 = r + O(r/k+k)
 = r + O(sqrt(r)).
```

The binary coefficient `log_3(2)<1` is smaller, so the nonbinary branch
dominates.  A conservative checked calibration `k=floor(log_3 r)` gives the
weaker `r+O(r/log r)` bound; it is retained in the receipt but is not the main
result.

Subject to independent review of the frozen predecessor bridges, the result
is therefore

```text
Delta_r(Q) <= r+O(sqrt(r))
```

at order-optimal same-DAG size `O(3^r/r)`.  Together with the repository's
counting lower bound, this identifies the leading depth coefficient as one.
It does not prove an `O(log r)` additive gap, an exact second-order term, or
an ordinary unshared-formula bound.

## 7. Common falsifiers

| Falsifier | Result |
|---|---|
| `F-input` | Uses only the frozen repository state and public repository mathematics. |
| `F-grammar` | Family nodes are full legal `d` trees; Q names, decoder, binary-relative names, and glue are charged by the predecessor compiler. |
| `F-control` | Every program term is a function only of its address chunk. Generic truth-table compilation is charged; no payload-dependent program is used. |
| `F-polarity` | Every middle-edge reversal is represented by the `P/N` sign. The false ordinary-majority and false two-extreme claims are explicit rejected controls. |
| `F-quotient` | No lossy four-state quotient is used. Canonical BDD equality or exhaustive replay owns finite acceptance. |
| `F-tree` | This is a construction, not an UNSAT transfer. Short fanout is padded only by repeating the last live branch; 716 bounded padding controls pass. |
| `F-rate` | Both Q planes, all router nodes, `2q` controls per level, anchor, decoder, binary branch, glue, and residual order are charged on the same DAG. |
| `F-degenerate` | Constant modes, both signs, every target through depth six symbolically, all R27 target mutations, padding, and complement orientations are exercised. |
| `F-boundary` | The generic induction is a manuscript proof, while the integrated compiler consequence remains conditional pending independent audit and formalization. |
| `F-prior` | **OPEN.** Recursive majority/discriminator multiplexers, universal-circuit routing, and Lupanov/Shannon depth-size synthesis require a dedicated prior-art comparison. |

## 8. Deterministic evidence

Checker:

`check_strong_router_family.py`

Frozen outputs:

- `summary.json`
- `r27_witness.json`

The checker performs:

- canonical ROBDD equality for `P_h,N_h`, both constants, and every target for
  `h=1,...,6` (up to `q=243`);
- `11,356` direct Boolean checks through depth three;
- exact R27 projection checks plus one explicit failing bit mutation per
  target;
- `9,216` complement-relative R9 checks;
- `177,147` two-plane Q checks;
- all eight primitive complement-equivariance cases;
- 716 repeated-last-branch padding checks;
- exact arithmetic for both schedules at every `r=27,...,1024`; and
- the exact residual-last rejection at `r=512`.

Normal command:

```text
python3 research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/check_strong_router_family.py --out research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/summary.json --witness-out research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/r27_witness.json
```

Optimized replay:

```text
python3 -O research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/check_strong_router_family.py --out /tmp/strong_router_summary_opt.json --witness-out /tmp/strong_router_r27_opt.json
```

Required comparison:

```text
cmp -s research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/summary.json /tmp/strong_router_summary_opt.json
cmp -s research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/r27_witness.json /tmp/strong_router_r27_opt.json
```

The normal and optimized bytes agree.  Exact final hashes are listed in the
handoff message after the final regeneration.

## 9. What remains

1. Independently reimplement the family and compiler arithmetic without
   importing this checker.
2. Materialize representative variable-`h` Expr DAGs, not just the frozen R27,
   and compare their measured node/depth counts to the ledger.
3. Formalize the strong-router induction and residual-first prefix lemma.
4. Run focused international and Chinese prior-art searches for signed
   majority/discriminator multiplexers and simultaneous Shannon-size/depth
   synthesis before drafting a novelty claim.
5. Keep the result research-only until the integrated compiler and the
   predecessor semantic bridges receive an independent PASS.
