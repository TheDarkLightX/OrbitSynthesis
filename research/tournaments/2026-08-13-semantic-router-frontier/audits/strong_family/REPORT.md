# Independent audit: recursive signed discriminator routers

Date: 2026-08-13

## Verdict

**`EXACT PASS — PARAMETERIZED BOOLEAN FAMILY AND FROZEN R27`.**

The author construction survives an independent implementation and a
first-principles induction. For every `h>=1`, it supplies d-only full trees
`P_h` and `N_h` with

```text
q_h                    = 3^(h-1) branch leaves,
programmable controls  = 2*3^(h-1),
discriminator nodes    = (3^h-1)/2,
dependency depth       = h.
```

For every target, one fixed address program makes `P_h` return that branch and
`N_h` return its Boolean complement. Both signs can also be programmed to the
constant functions 0 and 1. Every `P_h` branch path has even middle-edge
parity; every `N_h` branch path has odd parity.

The frozen `h=4` member is therefore an exact depth-four `R27` with 40 d nodes,
27 branch leaves, and 54 Boolean controls. It passes a direct ternary ROBDD
checker for all 27 targets. This exceeds the tournament's depth-four R19
benchmark. The recurrence also gives R243 at depth six, exceeding R82.

This exact family theorem is distinct from the all-arity compiler implication.
The separate variable-compiler audit conditionally validates
`O(3^r/r)` size and `r+O(sqrt(r))` depth only after residual-first/balanced
chunk routing. Novelty and prior art remain open.

## Frozen subject

```text
STATE.md
  5304ad459b25928e14197dfb989af7dfae4d9df6b632eb79020e9f1cef812133

lanes/fused/check_strong_router_family.py
  07fb1d8d322e57a7af666bae5b699c072805ff1d15eef1f1e7c2d87208729ef8

lanes/fused/summary.json
  6042127fd9f214e63bc38aa8e6367d1db7580c24b2b2e7a3aeba16625279aff0

lanes/fused/r27_witness.json
  6dd402fd32bb560b341ee75805bd71c90e2fa2bd3c9274c982f908ef21c15e65
  semantic 5ca70c36b38668cee125e5d8b7778e3d1d7d5df5fdb9ad7e753c687ab2dbaea3

lanes/fused/REPORT.md
  5ed37d98357eb03a2f6ded9f741c9fb52d8f5ad821585c81be544f201945f8c6
```

The R27 artifact embeds the matching generator and state hashes. The
independent checker rejects byte drift before parsing and rejects a wrong
expected witness hash.

## First-principles proof

### Primitive identity and polarity

On `{0,1}`,

```text
d(x,y,z)=z if x=y, else x = majority(x,1-y,z).
```

Thus d is increasing in its first and third arguments and decreasing in its
middle argument. It also commutes with simultaneous complement. The independent
checker exhausts all eight truth-table rows for both identities.

A leaf's induced sign is the parity of middle-child edges on its root path.
The audit derives the branch positions directly from ternary path digits,
without using the author's recursive layout routine. In `P_h`, a branch at
prefix path `a` is placed in the last cell coordinate that makes the total
middle-edge parity even; for `N_h`, it makes that parity odd. This produces
exactly one branch per prefix, hence `3^(h-1)` branch leaves and twice as many
controls.

### Base case

The depth-one interfaces are

```text
P1(x;c0,c1)=d(x,c0,c1)
N1(x;c0,c1)=d(c0,x,c1).
```

Their programs are

```text
P1: projection (0,0), constant 0 (1,0), constant 1 (0,1)
N1: complement (0,1), constant 0 (0,0), constant 1 (1,1).
```

Direct evaluation proves all six modes. `N1` contains no NOT node: the
complement arises because x is in d's antitone middle argument.

### Induction

Assume `P=P_(h-1)` can return a selected branch `x`, and `N=N_(h-1)` can
return `1-x`, while both signs have constant modes. Define

```text
P_h=d(P,N,P),
N_h=d(N,P,N).
```

For a target in the first, second, or third branch group, program the three
children respectively as

```text
(projection, constant 0, constant 0),
(constant 0, projection, constant 1),
(constant 0, constant 0, projection).
```

At a positive parent these reduce to

```text
d(x,0,0)=x,
d(0,1-x,1)=x,
d(0,0,x)=x.
```

At a negative parent the projected child has the opposite sign, and the same
three transitions return `1-x`. The checker independently exhausts both x
values, all three groups, and both parent signs. Constants lift because
`d(c,c,c)=c`.

The recurrences are consequently

```text
q_h=3q_(h-1), q_1=1,
C_h=3C_(h-1), C_1=2,
D_h=1+D_(h-1), D_1=1,
S_h=1+3S_(h-1), S_1=1.
```

Solving gives the counts in the verdict. This is a universal induction, not an
extrapolation from bounded search.

## Independent executable evidence

`audit_strong_family.py` imports no author module. It contains:

- a direct implementation of d;
- a path-digit layout derivation;
- an independent semantic-mode program recursion;
- a concrete full-tree evaluator; and
- a canonical ROBDD whose primitive apply is the ternary discriminator itself,
  not the author's AND/OR majority decomposition.

The checker establishes:

```text
twisted-majority rows                         8
simultaneous-complement rows                  8
induction transition rows                    16
direct P/N checks through h=3                11,356
independent P4/N4 ROBDD mode checks           58
frozen P4/R27 ROBDD projection checks         27
binary complement-relative R9 bridge checks   9,216
R27 targets with effective control mutation   27/27
malformed artifact classes rejected           6
```

For every R27 target, the audit flips a control bit, proves the mutated ROBDD
differs from the requested projection, extracts a 27-bit counterexample, and
replays it with the concrete evaluator. Artifact mutations alter labels,
program domain, program width, position lists, node count, and semantic hash;
semantic hashes are recomputed for structural mutations so validation is not
merely a hash check.

Normal and optimized auditor outputs are byte-identical:

```text
audit_strong_family.py
  efcd43d8038b46d897611dac8414b380602b7114a7e4db138ae729bf6ad12f19

receipt.json
receipt_optimized.json
  41ebde43fb3dee99b995224670d607bba331aa498cb49fca477802b4aea632a8

receipt semantic SHA-256
  ac566d0b716575ff693bc3a1f125283c764ef608a04c183a17293fe66adc4cb2
```

The author checker was also rerun normally and under `python3 -O`. Each replay
is byte-identical to the frozen summary and witness.

## Hidden-resource and original-signature audit

### No free negation inside the router

Every recursive-family operation node is d. There is no signed-leaf primitive
and no u/NOT node in `P_h` or `N_h`. The negative sign is exactly the odd
middle-edge path polarity. The branch count, controls, d-node count, and depth
therefore charge the actual family syntax.

### Boolean constants are program parameters, not Q nullaries

The pure Boolean theorem permits fixed program bits 0 and 1. The parameter-free
original signature `Q=({0,1,2};d,u)` has no nullary constants. Thus the Boolean
family alone is not yet a parameter-free Q term DAG. The compiler must supply
physical representatives of every programmed bit.

On a nonbinary slice with an anchor `A=2`, the legal original-signature names

```text
one=u(A), zero=u(u(A))
```

evaluate to 1 and 0. This costs two shared u nodes. The independent audit
checks those names and all three two-plane decoder codewords; the decoder costs
two d nodes and is applied only once after routing.

On the all-binary branch, absolute constants are unavailable. A logical
relative program bit p is represented physically as

```text
x0       when p=0,
u(x0)    when p=1.
```

This costs one shared u node and is legal because u complements binary inputs.
The exact complement-equivariance of every d tree ensures the physical result
has the input orientation. The independent R9 bridge replay covers both
orientations, every target, and every relative payload.

Important qualification: the **logical** relative program is address-only,
but the **physical** wires `x0,u(x0)` are payload-relative. Calling those
physical controls literally payload-independent would be false. Their legality
comes from the complement-relative representation invariant already used by
the predecessor compiler.

## Compiler bridge

This audit does not derive the entire all-arity compiler from the router
identity. The separate independent report

`audits/variable_compiler/REPORT.md`

finds a real schedule bug in residual-last chunking and supplies the required
repair: route a short residual chunk first, or use an equivalent balanced
address tree. Under the exact family premise and the predecessor representation
bridges, that audit supports

```text
size  = O(3^r/r),
depth = r+O(sqrt(r)).
```

It charges the two planes, growing router size, `2q` program bits per level,
control compilation, local library, prefix instances, binary branch, anchor,
decoder, padding, and glue. Its bounded checker covers every
`64<=r<=10000`, with conservative inequalities

```text
size <= 11*3^r/r,
depth <= r+10*floor(sqrt(r))+50.
```

This makes the compiler theorem a well-supported conditional composition, not
part of the self-contained family theorem. Integrated original-signature DAG
materialization for representative growing h remains useful future evidence.

## Common falsifiers

| Falsifier | Verdict |
|---|---|
| `F-input` | PASS. Frozen public repository subjects only; exact byte hashes checked. |
| `F-grammar` | PASS for family: d-only full trees. Compiler bridge separately charges u names, two planes, decoder, and glue. |
| `F-control` | PASS with qualification: absolute bits on anchored nonbinary slices; logical address-only but physical payload-relative names on the binary branch. |
| `F-polarity` | PASS. Path parity derived independently; P is even and N odd. No free NOT. |
| `F-depth` | PASS for family: h actual d layers. Compiler depth remains the separate audited composition. |
| `F-size` | PASS for family exact counts. Compiler PASS requires residual-first/balanced repair. |
| `F-degenerate` | PASS: both signs, both constants, every target, small truth tables, R27 mutations, malformed artifacts. |
| `F-boundary` | PASS. Family theorem, compiler bridge, and novelty have separate verdicts. |
| `F-prior` | OPEN. Signed majority/discriminator multiplexers, universal circuits, and simultaneous Shannon size-depth synthesis require primary-source comparison. |

## Reproduction

From the repository root:

```text
python3 research/tournaments/2026-08-13-semantic-router-frontier/audits/strong_family/audit_strong_family.py \
  --witness research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/r27_witness.json \
  --expected-witness-sha 6dd402fd32bb560b341ee75805bd71c90e2fa2bd3c9274c982f908ef21c15e65 \
  --expected-author-sha 07fb1d8d322e57a7af666bae5b699c072805ff1d15eef1f1e7c2d87208729ef8 \
  --expected-state-sha 5304ad459b25928e14197dfb989af7dfae4d9df6b632eb79020e9f1cef812133 \
  --out research/tournaments/2026-08-13-semantic-router-frontier/audits/strong_family/receipt.json

python3 -O research/tournaments/2026-08-13-semantic-router-frontier/audits/strong_family/audit_strong_family.py \
  --witness research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/r27_witness.json \
  --expected-witness-sha 6dd402fd32bb560b341ee75805bd71c90e2fa2bd3c9274c982f908ef21c15e65 \
  --expected-author-sha 07fb1d8d322e57a7af666bae5b699c072805ff1d15eef1f1e7c2d87208729ef8 \
  --expected-state-sha 5304ad459b25928e14197dfb989af7dfae4d9df6b632eb79020e9f1cef812133 \
  --out research/tournaments/2026-08-13-semantic-router-frontier/audits/strong_family/receipt_optimized.json
```

Full command and subject hashes are frozen in `audit_manifest.json`.

## Scope-accurate conclusion

The recursive signed-router family is a genuine mathematical construction,
not a bounded search pattern. Its key invariant is the pairing of positive and
negative strong routers with both constant modes. It yields exact R27 and R243
gadgets and a fixed-h routing coefficient `h/(h-1)`, tending to one.

The strongest current project-level implication is conditional: combined with
the separately repaired variable compiler and predecessor representation
bridges, it supports order-optimal same-DAG size and depth
`r+O(sqrt(r))`. It does not establish an exact second-order bound, unshared
formula complexity, practical superiority, originality over prior art,
publication readiness, patent/FTO clearance, rights under any unsigned Tau
license, or any private Tau capability.
