# Direct-rail program vectors: sharper upper bound and output lower bound

Date: 2026-08-13

## Verdict

**The untrusted `4q` candidate is true, and a different representation is
strictly stronger.**

For width `w`, let `q=3^w`. There is an explicit original-signature shared
`{d,u}` DAG producing all `2q` projection controls of either signed router
with

```text
size  <= 3q,
depth <= 4+ceil(log_2 w)                 (w>=1),
```

including `one=u(A)`, `zero=u(u(A))`, every preprocessing node, every output
wire conversion, and both root signs. More precisely, the construction has

```text
size <= 2q + (7/3)(3^floor(w/2)+3^ceil(w/2)) + 5/2,
```

so its leading size is `(2+o(1))q`. Constant-zero and constant-one router modes
use only the shared names.

The key representation carries the two Boolean absorbing-mode rails directly:

```text
Z_p(t) = [the first mismatch gives constant zero],
O_p(t) = [the first mismatch gives constant one].
```

They compose with two parallel discriminators, and duplicate one-mode rails
are shared by the position of the last physical digit `2`.

There is also an all-width lower bound in the declared scalar shared-DAG
grammar. The P vector has exactly `4q/3` distinct Boolean control functions,
and the N vector has exactly `4q/3+1`. Since no raw address input is Boolean on
the full ternary domain, each distinct output requires an operation wire.
Thus the leading constant lies in

```text
4/3 <= optimal leading constant <= 2.
```

The factor between the proved leading bounds is at most `3/2`. This does not
identify the optimum.

An independently reconstructed native ternary-state construction also proves
the external agent's weaker target:

```text
size  <= 4q,
depth <= 5+ceil(log_2 w).
```

No manuscript or frozen semantic-router artifact was edited.

## Frozen contract

```text
STATE.md
  6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6
```

The checker fails closed on byte drift. The external progress log supplied no
formulas; both constructions below were reconstructed in this lane.

## 1. Exact grammar and cost model

For a fixed width, the semantic domain is

```text
A=2,
t_0,...,t_(w-1) in Q={0,1,2}.
```

Raw `A` and target digits are cost-zero terminal wires. A cost-one scalar gate
is exactly

```text
u(previous wire)
```

or

```text
d(previous wire, previous wire, previous wire),
d(x,y,z)=z if x=y, else x.
```

Outputs point to existing wires. Identical operations are hash-consed, and
fanout is free. Size is the number of distinct operation nodes; depth is the
longest operation path above raw terminals. The model forbids nullary
constants, payload inputs, signed leaves, free negation, and free decoding.
P and N root vectors are costed separately.

This is a same-DAG circuit theorem. It is not an unshared formula or
bounded-fanout theorem.

## 2. Reconstructing the native ternary state

Encode the three first-mismatch modes by

```text
zero mode = 0,
one mode  = 1,
equal     = 2.
```

If left and right consecutive segments have codes `s_L,s_R`, their combined
state is

```text
s_L star s_R = d(s_L,A,s_R).
```

When `s_L=2`, the left segment is equal and `d` returns `s_R`; otherwise `d`
returns the absorbing left state. This is the exact first-mismatch product in
one gate.

For one target digit `x`, the states at physical digits `0,1,2` are

```text
s_0=d(zero,x,A)                         = (2,0,0),
b  =d(x,A,zero)                         = (0,1,0),
s_1=d(b,one,A)                          = (0,2,0),
s_2=x                                   = (0,1,2).
```

Thus the base state vector costs three operations beyond the two names. A
balanced block construction has

```text
T(1)=3,
T(w)=T(floor(w/2))+T(ceil(w/2))+3^w.
```

Direct bases `w=1,2,3` and the balanced recurrence give

```text
T(w) <= (5/3)3^w.
```

From a state `s`, the required Boolean mode indicators are

```text
Z(s)    =d(zero,s,one),
O(s)    =d(s,A,zero),
not Z(s)=d(s,A,one).
```

So a positive cell receives `(Z,O)`, while a negative cell receives
`(O,not Z)`, at two new nodes per physical word. Including the names,

```text
2+T(w)+2q <= 4q
```

for `w>=2`, and widths zero and one are direct bases. The base state depth is
four, each balanced merge adds one layer, and output extraction adds one,
giving `5+ceil(log_2 w)`.

This confirms the proposed native ternary idea. It is not the best survivor.

## 3. Direct absorbing-mode rails

Carry `Z_p,O_p` themselves. For consecutive left and right segments,

```text
Z_LR = d(Z_L,O_L,Z_R),
O_LR = d(O_L,Z_L,O_R).
```

There are three possible left modes:

| left mode | `(Z_L,O_L)` | combined `(Z,O)` |
|---|---:|---:|
| zero | `(1,0)` | `(1,0)` |
| one | `(0,1)` | `(0,1)` |
| equal | `(0,0)` | `(Z_R,O_R)` |

The two gates therefore implement the exact first-mismatch product in
parallel.

### One-digit base

For target digit `x`, the six rails reduce to four new nodes:

```text
Z_0=d(x,A,one)       = (0,1,1),    O_0=zero,
Z_1=d(one,x,zero)    = (1,0,1),    O_1=zero,
Z_2=d(zero,x,one)    = (1,0,0),    O_2=d(x,A,zero)=(0,1,0).
```

This base has depth at most three above raw terminals.

### Sharing all duplicate one rails

`O_p` is identically zero when the physical word `p` contains no digit `2`.
Otherwise it depends only on the prefix ending at the last `2`; every suffix
over `{0,1}` gives the same function. Hence a width-`b` block has exactly

```text
(3^b-1)/2
```

distinct nonzero one rails.

When a right physical word contains no `2`, `O_R=zero` and the combined rail
is exactly `O_L`, so no gate is emitted. For each of the `3^a` left words and
each distinct nonzero right rail, one discriminator is emitted. Every combined
zero rail still costs one gate. If `a=floor(w/2)`, `b=ceil(w/2)`, and
`q=3^(a+b)`, the rail library satisfies

```text
R(1)=4,
R(w)=R(a)+R(b)+q+3^a(3^b-1)/2.
```

The checker materializes this exact hash-consed construction. Direct bases
give

```text
R(1)=4, R(2)=20, R(3)=63.
```

For `w>=4`, both child widths are at least two. Induction, together with
`3^a+3^b<=(2/9)q`, gives the convenient global envelope

```text
R(w) <= (7/3)q.
```

### Final signed pairs and total size

Positive cells already have their final pair `(Z,O)`. Negative cells need
only

```text
(O,u(Z)).
```

There are `(q-1)/2` negative cells for a P root and `(q+1)/2` for an N root.
Thus, for either sign,

```text
S(w) <= 2+R(w)+(q+1)/2.
```

For `w>=3`, the right side is at most `3q`; widths zero, one, and two are
direct bases. A sharper asymptotic substitution at the top merge gives

```text
R(w) <= (3/2)q+(7/3)(3^a+3^b),
S(w) <= 2q+(7/3)(3^a+3^b)+5/2
     = (2+o(1))q.
```

The base rails have depth three. Each balanced merge adds one parallel
discriminator layer, and final negative-cell complementation adds one layer:

```text
D(w) <= 4+ceil(log_2 w).
```

All terms depend only on `A` and target digits. No payload wire enters the
control DAG.

### Exact materialized counts

| `w` | `q` | P nodes | N nodes | depth |
|---:|---:|---:|---:|---:|
| 0 | 1 | 2 | 2 | 2 |
| 1 | 3 | 7 | 8 | 4 |
| 2 | 9 | 26 | 27 | 5 |
| 3 | 27 | 78 | 79 | 6 |
| 4 | 81 | 199 | 200 | 6 |
| 5 | 243 | 566 | 567 | 7 |
| 6 | 729 | 1,572 | 1,573 | 7 |
| 9 | 19,683 | 39,927 | 39,928 | 8 |

The width-nine N ratio is about `2.0285q`, already close to the leading-two
limit.

## 4. Projection and constant semantics

At the first target/physical mismatch, `Z=1` unless the mismatch is
`(target,physical)=(1,2)`; in that exceptional case `O=1`. If no mismatch
occurs, both rails are zero. The final pairs are therefore exactly

```text
positive: (Z,O),
negative: (O,not Z).
```

These are respectively

```text
positive projection/zero/one: (0,0), (1,0), (0,1),
negative projection/zero/one: (0,1), (0,0), (1,1).
```

Constant modes bypass the projection preprocessing:

```text
positive constant c: (1-c,c),
negative constant c: (c,c).
```

The independent checker compares every generated pair with the first-mismatch
definition through width six, both signs. It also evaluates the complete
recursive discriminator router for all Boolean payload valuations through
width two. Projection, complement, and both constants all pass.

## 5. All-width output-count lower bound

Let

```text
N_p=not Z_p=E_p or O_p.
```

Every signed program vector contains `O_p` for every physical word. Its other
control is

```text
H_p = Z_p for a positive cell,
H_p = N_p for a negative cell.
```

### Counting the one rails

All physical words with no `2` give the same zero function. Every other
function is indexed uniquely by the physical prefix ending at its last `2`.
Consequently

```text
|{O_p}| = 1+sum_(j=0)^(w-1) 3^j = (q+1)/2.
```

The uniqueness can also be read inductively from the three target-first-digit
blocks:

```text
O_(0r)=[O_r,0,0],
O_(1r)=[0,O_r,0],
O_(2r)=[0,1,O_r].
```

### Counting the mixed `H` family

The physical cell sign is root sign XOR the parity of the number of digit-1
edges in `p`. For a nonempty suffix, every `Z_r` and `N_r` is nonconstant.
According to first physical digit and cell sign, `H` has one of six block
templates:

```text
[f,1,1], [f,0,0], [1,f,1], [0,f,0], [1,0,f], [0,1,f].
```

The location of the nonconstant block recovers the first physical digit, and
the two constant blocks recover whether `f` is the zero-mode or not-zero-mode
rail. Induction recovers the suffix. Hence all `q` functions `H_p` are
distinct.

### Exact overlaps

The block templates show that an `O` function can equal an `H` function only
through the base identity

```text
O_(a2)=N_(a1),
```

with the same length-`w-1` prefix `a`, and only when the cell `a1` is negative.
There are

```text
(3^(w-1)+1)/2
```

even-parity prefixes and

```text
(3^(w-1)-1)/2
```

odd-parity prefixes. For a P root, `a1` is negative when `a` has even parity;
for an N root, it is negative when `a` has odd parity. Inclusion-exclusion now
gives

```text
P: q+(q+1)/2-(q/3+1)/2 = 4q/3,
N: q+(q+1)/2-(q/3-1)/2 = 4q/3+1.
```

Every control function is Boolean, whereas each raw `t_i` assumes the value
`2` and raw `A` is constant `2`. No required control is a terminal wire. A
scalar gate creates at most one new output function, proving the lower bound.

This is a genuine all-width lower bound in the declared grammar. It is only an
output-count lower bound; auxiliary-sharing constraints might strengthen it,
but that is not proved here.

## 6. Exact and bounded small-width synthesis

For one target digit, there are only `3^3=27` semantic functions
`Q->{0,1,2}`. The exact search represents a circuit state by the set of
semantic functions already available. With free fanout, a minimum circuit
never needs two wires with the same semantics. From each set, the search adds
every new function obtainable by `u` or by every ordered `d` triple. Breadth-
first search over these finite sets is therefore complete for the declared
grammar.

Starting only from

```text
A=(2,2,2), t=(0,1,2),
```

the exact minima are

```text
width 0: P=2, N=2,
width 1: P=5, N=6.
```

The width-one P search expands 162 semantic sets and visits 990; the N search
expands 304 and visits 1,750. Full gate witnesses are frozen in the receipt.
This also shows that the uniform direct-rail construction, with 7 and 8 gates
at width one, is not an exact small-width optimum.

For larger widths, the checker gives lower bounds rather than minima. If `D`
distinct noninput outputs were realized with exactly `D` gates, every gate
would have to be one of the required outputs—there would be no auxiliary wire.
The checker exhaustively closes the required output set under every legal gate
whose arguments are raw inputs or already available required outputs. Failure
of that target-only closure proves `D+1` gates are necessary.

| width | P lower bound | N lower bound | status |
|---:|---:|---:|---|
| 1 | 5 | 6 | exact minima by full semantic-set BFS |
| 2 | 13 | 14 | target-only no-auxiliary lower bound |
| 3 | 37 | 38 | target-only no-auxiliary lower bound |
| 4 | 109 | 110 | target-only no-auxiliary lower bound |
| 5 | 325 | 326 | target-only no-auxiliary lower bound |

No width-two-or-larger exact minimum is claimed.

## 7. Alternative native encodings

All six assignments of `equal/zero/one` to `0,1,2` were exhaustively compared
on the one-digit semantic domain. The names are treated as already available
in this table; “base” is the additional cost of producing all three physical
state functions, and extractors produce a generic cell's two controls.

| `(equal,zero,one)` | base minimum | positive extractor | negative extractor |
|---:|---:|---:|---:|
| `(2,0,1)` | 3 | 2 | 2 |
| `(2,1,0)` | 5 | 2 | 2 |
| `(0,1,2)` | 4 | 3 | 3 |
| `(0,2,1)` | 4 | 3 | 2 |
| `(1,0,2)` | 4 | 3 | 2 |
| `(1,2,0)` | 4 | 3 | 3 |

The chosen ternary code `(2,0,1)` is the unique best row under these local
metrics. Every permutation still has the one-gate segment product

```text
d(left,equal,right).
```

One gate is optimal in that local grammar: a zero-gate result can return only
one input or a constant, whereas the segment product depends on both
independent operands. Given a generic surjective state and the three names,
two scalar gates are likewise necessary and sufficient to expose two distinct
missing Boolean controls. These local lower bounds do not imply a global
vector optimum; direct rails beat the native-state global construction.

## 8. Killer mutations

| Mutation | Smallest frozen mismatch |
|---|---|
| Reverse native composition | left zero, right one: correct zero, mutation one. |
| Omit the lift in physical state `s_1` | target digit one: required equal code 2, unlifted indicator 1. |
| Use `u(s)` as `not Z` for native code `(2,0,1)` | state zero: required 0, `u(0)=1`. |
| Replace the opposite-rail guard in the Z formula by zero | left one/right zero: correct Z=0, mutation Z=1. |
| Replace the opposite-rail guard in the O formula by zero | left zero/right one: correct O=0, mutation O=1. |
| Reuse `O_L` when `O_R` is nonzero | left equal/right one: correct O=1, mutation O=0. |
| Omit final negative-cell complementation | negative equal mode: required second control 1, raw Z is 0. |
| Use absolute names on a binary anchor | `A=0` gives `(0,1,0)` and `A=1` gives `(1,0,1)`, never `(2,1,0)`. |

## 9. Deterministic evidence

The checker imports no frozen implementation. It contains its own algebra,
hash-consed DAG, native and direct-rail constructions, recursive router
evaluator, finite semantic-set BFS, output-function census, alternate-code
search, and mutations.

```text
projection-pair comparisons through width six       2,391,484
constant bottom-cell payload checks                    236,192
complete router checks through width two                11,356
native recurrence widths                                   512
direct-rail recurrence widths                              512
bounded output-count widths                                  5
```

Normal and optimized Python receipts are byte-identical:

```text
check_lower_bound.py
  3b02d4cd842e7b8b252a38b3cdcb4fb2fc6044cf04f72b0b0250709a6cda2785

receipt.json
receipt_optimized.json
  11daf965c409e41192e3be2cf81655e554a5881c60d1011b1f1e52259b93d20b

receipt semantic SHA-256
  a577c3b1ea343bc01781b7c46b04a902e93382bf648b70f80e959f5ac618931c
```

Reproduce from the repository root:

```text
python3 research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/check_lower_bound.py \
  --out research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/receipt.json

python3 -O research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/check_lower_bound.py \
  --out research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/receipt_optimized.json

cmp -s research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/receipt.json \
  research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/receipt_optimized.json
```

## 10. Claim boundary

Proved here:

- exact legal direct-rail construction with `size<=3q`, leading size at most
  `2q`, and depth `4+ceil(log_2 w)`;
- exact legal native-state construction with `size<=4q` and depth
  `5+ceil(log_2 w)`;
- exact all-width scalar-output lower counts `4q/3` and `4q/3+1`;
- exact width-zero and width-one minima in the declared grammar;
- bounded target-only lower bounds through width five.

Not proved here:

- exact minimum for width two or larger;
- optimality of the leading constant two, the `3q` envelope, or the depth
  additive constant;
- an unshared formula or bounded-fanout theorem;
- any integrated-compiler size constant or manuscript theorem;
- novelty, prior-art clearance, patent freedom to operate, copyright
  clearance, rights under the unsigned Tau license, practicality, or
  publication readiness.

Novelty and FTO remain **UNKNOWN**.
