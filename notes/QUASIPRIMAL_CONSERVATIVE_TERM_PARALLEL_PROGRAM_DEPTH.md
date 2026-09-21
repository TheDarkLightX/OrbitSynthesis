# Parallel program vectors for conservative Q-term DAGs

**Status:** the program-vector theorem below is exact, deterministically
replayed, independently audited, and Lean-checked at both the semantic and
shared-DAG cost levels. The all-arity compiler theorem is a **conditional
manuscript theorem** because it composes previously frozen
selector-table, anchor, binary-branch, decoder, and glue lemmas. Publication
novelty, optimality, practical value, patent scope, freedom to operate, rights
under an unsigned developer license, and any statement about private Tau work
remain **UNKNOWN**.

## 1. Algebra, cost model, and theorem boundary

Fix

```text
Q=({0,1,2};d,u),
d(x,y,z)=z if x=y and d(x,y,z)=x otherwise,
u(0)=1, u(1)=0, u(2)=1.
```

Size counts `d` and `u` nodes in one parameter-free original-signature shared
term DAG. Variables have depth zero and fan-out is free. A Boolean program bit
is not a free constant: on the nonbinary branch the anchor value `A=2` legally
supplies `one=u(A)` and `zero=u(u(A))`; on the binary branch the retained
construction instead uses the complement-relative physical names
`x_0,u(x_0)`.

A multi-output shared DAG has a finite ordered list of distinguished roots.
Its size is the number of operation nodes in the union of their ancestor
subgraphs, counted once.  Substitution into a larger shared DAG adjoins that
union once and permits unrestricted references to each distinguished root.
The final compiler has one output root.  Thus the theorem below is not an
ordinary formula-size or bounded-fanout statement.

### Exact program-vector theorem

For every integer `w>=0`, the signed discriminator router family has
`q=3^w` physical branch positions. For every requested target address, all
`2q` bottom-cell control wires can be realized from the nonbinary anchor and
the target-address digits in one original-signature shared DAG with

```text
size  <= 7q,
depth <= 6+2*ceil(log_2 w)
```

above the raw anchor/address inputs for `w>=1`. The displayed size includes
the two shared names. The width-zero base case uses only those names. The
construction depends on the address and anchor, not on a routed payload wire.

### Conditional all-arity compiler theorem

Assume the frozen conservative selector-table characterization, balanced
global anchor, two-plane Q encoder/decoder, complement-relative binary
compiler, and final glue lemmas cited below. Then every conservative `r`-ary
term operation has one parameter-free original-signature DAG satisfying

```text
size  = O(3^r/r),
depth <= r+O(log r).
```

For `r>=64`, the displayed ledger gives the explicit conservative bounds

```text
total size     <= 63*3^r/r,
nonbinary depth <= r+5*ceil(log_2 r)+12.
```

Together with syntax counting, the current conditional interval is

```text
r-log_3(log r)-O(1) <= Delta_r(Q) <= r+O(log r).
```

This does not prove an optimal additive term or a matching leading-size
constant.

The conditional statement uses the following exact interface propositions.

- **(I1) Selector representation.** Every conservative term operation has a
  total complement-invariant coordinate selector `sigma` satisfying
  `f(x)=x_(sigma(x))`.
- **(I2) Anchor.** An original-signature DAG computes `A=2` exactly off the
  binary cube and `A=x_0` on it, in at most `4(r-1)` nodes and depth at most
  `3*ceil(log_2 r)`.
- **(I3) Encoded nonbinary compiler and inclusive ledger.** For `r>=64`, the
  giant local/prefix construction, two Boolean planes, exact program vectors,
  and one final decoder compute `x_(sigma(x))` when `A=2`.  Together with the
  anchor, two shared names, and three reserved glue nodes, their shared-DAG
  union has fewer than `62*3^r/r` nodes.  Its depth before the glue is at most
  `r+5*ceil(log_2 r)+10`.
- **(I4) Binary compiler.** A complement-equivariant original-signature DAG
  computes `x_(sigma(x))` on the binary cube using physical controls
  `x_0,u(x_0)`, with size below `3^r/r` for `r>=64`, depth
  `log_3(2)r+O(sqrt r)`, and checked depth below `r` for `r>=339`.
- **(I5) Same-DAG substitution.** Each local and prefix program vector is
  adjoined once and shared across its consumers; the anchor and both branch
  DAGs are united once before the final glue.
- **(I6) Glue.** Put `s=u(u(A))`.  For binary result `B` and nonbinary result
  `N`, the legal term

  ```text
  Glue(A,B,N)=d(d(s,A,B),d(s,A,N),N)
  ```

  uses three discriminator nodes and two levels.  It returns `B` when `s=A`,
  exactly the binary cube, and `N` when `A=2,s=0`.
- **(I7) Finite fallback.** Named earlier original-signature compilers cover
  `1<=r<64`; the finitely many binary-ledger depths for `64<=r<339` are
  absorbed into the additive asymptotic constant.

Only the implication from (I1)--(I7) is claimed here.  In particular, the
`63*3^r/r` constant is asserted only for `r>=64`; the finite fallback supports
the asymptotic theorem but is not assigned that explicit constant.

## 2. Signed routers and the first-mismatch state

The exact Boolean base cells are

```text
P_1(x;c0,c1)=d(x,c0,c1),
N_1(x;c0,c1)=d(c0,x,c1).
```

Recursively,

```text
P_h=d(P_(h-1),N_(h-1),P_(h-1)),
N_h=d(N_(h-1),P_(h-1),N_(h-1)).
```

The family has dependency depth `h`, `3^(h-1)` branches, and two program
slots per branch. It realizes every projection, both constants, and the
corresponding complemented projections without a free NOT constructor. The
sign is supplied by the parity of middle-child edges.

Let `t,p in {0,1,2}^w` be the requested and physical branch words. Define

```text
E_p(t) = [t=p],
G_p(t) = [the first mismatch j has (t_j,p_j)=(1,2)].
```

Following `p` through the recursive program stays in projection mode exactly
when `E=1`. At the first mismatch it becomes constant one exactly in the case
recorded by `G`; every other mismatch gives constant zero. Thus the final mode
is

```text
projection,  if E=1,
constant G,  if E=0.
```

The two states are disjoint. If a bottom cell is positive, its ordered pair of
controls is

```text
(not(E or G), G).
```

If it is negative, the pair is

```text
(G, E or G).
```

Constant mode `c` uses `(1-c,c)` in a positive cell and `(c,c)` in a negative
cell. These formulas cover the complete P/N mode interface.

## 3. Balanced original-signature materialization

For two consecutive word segments `A,B`, first-mismatch ownership gives the
associative composition law

```text
E_AB = E_A and E_B,
G_AB = G_A or (E_A and G_B).
```

On the nonbinary branch, put

```text
two=A, one=u(A), zero=u(u(A)).
```

For one target digit `x`, the required equality indicators are the legal
original-signature terms

```text
delta_0(x)=u(d(x,two,one)),
delta_1(x)=d(x,two,zero),
delta_2(x)=u(d(x,zero,one)).
```

For Boolean intermediate values,

```text
x and y = d(x,one,y),
x or y  = d(x,zero,y),
not x   = u(x).
```

Let `S(w)` count the shared E/G state nodes for all physical words under a
balanced split, excluding the two shared anchor names. A one-digit vector
costs five nodes. If `a=floor(w/2)` and `b=ceil(w/2)`, every physical
concatenation adds three discriminator nodes, so

```text
S(1)=5,
S(w)=S(a)+S(b)+3*3^w.
```

Direct calculation handles `w=1,2,3`. For `w>=4`, induction gives

```text
S(a)+S(b) <= 5(3^a+3^b) <= (10/9)3^w,
```

and hence `S(w)<=5*3^w`. Forming `E or G` costs at most `q` more nodes, and
at most `(q+1)/2` positive cells need a final `u`. Therefore the complete
program vector uses at most `7q` nodes. The one-digit layer has depth at most
four, each balanced composition level adds at most two, and final pair
formation adds at most two, proving the displayed logarithmic-depth bound.

## 4. Giant local and prefix routers

For `r>=64`, choose

```text
L=4+ceil(log_3(r^2)),
H=r-L,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b)=3^r/M.
```

Then `H/3<M<=H`, `H>=r/2`, and `M>r/6`.

The local block has `b` coordinates and `M` assignments. There are `3^M`
Q-valued tables on that block. Two `P_(b+1)` routers encode each table's two
Boolean planes using exactly `3M-1` discriminator nodes, while one width-`b`
program vector of at most `7M` nodes is shared by every table. Hence

```text
local nodes <= (3M-1)3^M+7M.
```

The two-logarithm reserve implies

```text
3M*3^M <= (1/27)*3^r/r.
```

For the requested global table, each of the `P` prefix assignments selects one
shared local function. Two `P_(r-b+1)` routers cost `3P-1`, and their complete
program vector costs at most `7P`. Since `M>r/6`,

```text
prefix routers and controls <=10P <60*3^r/r.
```

Charging the anchor, names, decoder, local control vector, and selector glue
adds less than one further normalized unit for `r>=64`. Thus the nonbinary
branch is below `62*3^r/r`.

The local router adds `b+1` dependency layers and the prefix router adds
`r-b+1`. Both program vectors are computed in parallel. Charging the balanced
anchor, names, decoder, and final selector yields

```text
D_nonbinary <= r+5*ceil(log_2 r)+12.
```

## 5. Binary branch and the physical-control qualification

The nonbinary equality formulas cannot be used on the all-binary cube because
absolute zero and one are unavailable there. The compiler retains the audited
square-root signed-router branch with complement-relative controls. Its
logical program is a function only of the relative address, but each physical
wire is `x_0` or `u(x_0)` and is therefore payload-relative to the common
orientation. Legality follows from complement equivariance; the physical
wires must not be described as payload-independent constants.

With `k=floor(sqrt r)`, the retained depth ledger is

```text
(k+1)*ceil((r-1)/floor(log_2(3^k)))
  +2*floor(log_2(3^k))+3*ceil(log_2 r)+8.
```

It is below `r` from arity 339 onward and is
`log_3(2)r+O(sqrt r)` asymptotically. Residual-first padding gives binary size
`O(2^r+r*3^(2sqrt r))=o(3^r/r)`; the explicit ledger is below one normalized
unit for `r>=64`.  The retained finite-depth values cover `64<=r<339`; only
`r<64` uses the frozen earlier compiler.

## 6. Evidence and falsifiers

The exact checker is

`research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/check_parallel_program_vector.py`.

Normal and optimized runs regenerate byte-identical receipts with SHA-256

`c9e8b1ad9c57f4ef55ea458b2573f20578a137a6c7b5fb1a66707bb7ee68b632`

and semantic SHA-256

`9699a3fe058369ac22a4a4d8050d07825cc80112cbc4c601a85914100db13f88`.

The finite evidence includes 1,200,114 program-pair checks, 11,356 concrete
router checks, 262 direct ternary-ROBDD modes through width four, 232 padding
checks, dependency checks, materialized vectors through width eight, and exact
compiler arithmetic for every arity `64..4096`. The checker rejects:

- an unguarded `G` recurrence, with minimal witness `t=(0,1),p=(1,2)`;
- swapped P/N control ordering;
- illegal absolute binary constants;
- sequential `q*w` control construction, which exceeds 100 normalized units
  at `r=512`; and
- a one-logarithm reserve, whose local library exceeds 62 normalized units at
  `r=6574,M=6561`.

The exact E/G semantics, append composition, sign parity, and both program-bit
formulas are Lean-checked in

`research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/ProgramVector.lean`

with source SHA-256

`c2f477edd110c4df96f3c30f31f02de09af93045720babfd38dd2dd79a5573dd`

and receipt SHA-256

`5e79e4eb49af361fbed1c8962a67583a48e532526698da584b8825d55136cffa`.

The shared-DAG recurrence, the `7q` bound including both shared names, the
depth bound, and the nonbinary `A=2` original-signature bridge are Lean-checked
in

`research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/ProgramVectorCost.lean`

with source SHA-256

`ea516b085cdedd3f0ee70f83a9d0240df55e7e68cf0ad8ce77558efd91db55d2`

and receipt SHA-256

`4919835f32d8afdfc48f72979edf4ad4ef0b1f8b16271ed9858a60750d2b6211`.

An independent no-author-import audit also proves the exact vector theorem
and conditionally passes the integrated integer ledger through arity 16,384.
Its normal and optimized receipts are byte-identical with SHA-256

`f6af15d3b5a8330a0f8248f9ffa5410dd1dfc762a89dbc20ecfe0d21aee714b8`

and semantic SHA-256

`4922df2221b3e6195d7b1af3a3ac770ae92a8aed10843430b9cffb20959c58ea`.

Lean does not extract a serialized node-indexed DAG and does not prove the
all-arity compiler theorem. Those remain separate proof obligations.

## 7. Preserved negative knowledge and historical stages

The Boolean R9 compiler's `(3/2)r+O(r/log r)` depth and the variable signed
router's repaired `r+O(sqrt r)` depth remain valid historical stages. Serial
mixtures of fixed R6/R7/R8/R9 gadgets cannot beat the best primitive rate in
their declared serial grammar, but the present construction evades that
barrier by compiling an entire growing program vector in parallel.

The discarded residual-last square-root schedule is false: at `r=512`, its
prefix node exponent is 529 while the target exponent is about 506.321.
Residual-first ordering repairs that older schedule. The naive identity
`d=majority` is also false; on Booleans
`d(x,y,z)=majority(x,not y,z)`. These counterexamples remain part of the
research record.

## 8. Prior art, provenance, and nonclaims

Shannon counting, Lupanov local coding, multivalued functional constructions,
dual-rail encodings, multiplexer synthesis, universal circuits, and parallel
prefix composition are classical. Focused Russian, Chinese, and international
retrieval found no verified exact match for the signed P/N recurrence plus the
fixed no-nullary `{d,u}` accounting and simultaneous same-DAG bounds. Search
non-detection is weak negative evidence, not a novelty opinion. Full-text
comparison with arbitrary-basis k-valued Shannon complexity and finite-basis
linear-depth results remains mandatory before submission.

The construction uses public mathematics and independently written
OrbitSynthesis artifacts. It does not depend on Tau code, private
specifications, confidential communications, or acceptance of an unsigned
developer license. This provenance statement is not legal advice and does not
establish freedom to operate.

Do not currently claim:

- an optimal additive depth term or leading-size constant;
- a bound for ordinary unshared term trees;
- the same theorem for every quasi-primal algebra or incomplete clone;
- a practical small-arity speedup;
- an end-to-end Lean proof or external peer review;
- publication novelty over Russian, Chinese, or international literature;
- patent freedom to operate or rights under an unsigned license; or
- any result about private Tau capabilities.

## 9. Frozen dependencies

The conditional compiler uses the selector-table and global-anchor arguments
in the earlier authoritative notes, the signed-family report and independent
audit under

`research/tournaments/2026-08-13-semantic-router-frontier/`,

the repaired binary compiler audit

`research/tournaments/2026-08-13-semantic-router-frontier/audits/variable_compiler/REPORT.md`,

the independent program-vector and compiler-ledger audit

`research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/REPORT.md`,

and the frozen program-vector report

`research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/REPORT.md`.

The local semantic and cost formalizations are under

`research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/`

and

`research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/`.

No bounded replay, Lean declaration, Research Kernel label, Morph suggestion,
or failed literature search independently promotes the conditional compiler
to a publication theorem.
