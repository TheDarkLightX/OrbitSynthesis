# Parallel program vectors for signed discriminator routers

Date: 2026-08-13

Status: **exact program-vector theorem / conditional compiler sharpening**.

## Result

The proposed parallel control construction is correct.

For the frozen signed router `P_h`, write its `q=3^w` physical branch positions
as ternary words `p in {0,1,2}^w`, where `w=h-1`. If the requested target is
the ternary word `t`, define

```text
E_p(t) = [t=p],
G_p(t) = [at the first mismatch j, (t_j,p_j)=(1,2)].
```

The bottom cell containing physical branch p is in projection mode exactly
when `E_p=1`; otherwise it is in constant mode `G_p`. If the bottom cell has
positive sign, its compact left-to-right control pair is

```text
(not(E_p or G_p), G_p).
```

If it has negative sign, the pair is

```text
(G_p, E_p or G_p).
```

These formulas simultaneously generate all `2q` logical controls in

```text
size  <= 7q original-signature d/u nodes,
depth <= 6+2*ceil(log_2 w)
```

above the raw nonbinary anchor and target digits. The two shared name nodes
`u(A),u(u(A))` are charged separately. Constant modes require no vector logic:
their positive/negative pairs are `(1-c,c)` and `(c,c)`.

This closes the control-ROM bottleneck in the variable signed-router compiler.
Using one giant local router and one giant prefix router, the resulting
nonbinary compiler has the conditional bounds

```text
size  = O(3^r/r),
depth = r+O(log r).
```

With the retained complement-relative binary branch, the conservative checked
ledger gives, for `r>=64`,

```text
total size <= 63*3^r/r,
nonbinary depth <= r+5*ceil(log_2 r)+12.
```

The binary bound is strictly below r from arity 339 onward under the retained
conservative schedule, and is asymptotically
`log_3(2)r+O(sqrt(r))`. Finitely many smaller arities can use the frozen
compiler and do not affect the theorem.

The program-vector theorem is self-contained and exact. The all-arity statement
still composes the frozen selector-table characterization, global anchor,
binary branch, decoder, and glue lemmas, so it remains a conditional manuscript
theorem rather than a machine-checked end-to-end compiler theorem.

## 1. Frozen inputs

The checker fails closed unless these exact public repository bytes are
present:

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
```

No frozen artifact, manuscript, note, or shared experiment was edited.

## 2. Derivation of the program law

### 2.1 First mismatch determines the mode

At every recursive node the requested group digit is `t_j`. The three child
modes are

```text
t_j=0: (project, const 0, const 0),
t_j=1: (const 0, project, const 1),
t_j=2: (const 0, const 0, project).
```

As long as `p_j=t_j`, the physical branch remains in projection mode. At the
first mismatch it becomes constant 1 only in the case `t_j=1,p_j=2`; every
other mismatch gives constant 0. Once a subtree has a constant mode, all its
descendants receive that constant. Thus the final cell mode is exactly

```text
projection if E_p=1,
constant G_p otherwise.
```

This conclusion is independent of the root sign.

### 2.2 The bottom sign determines the pair

For a positive bottom cell `P_1=d(x,c0,c1)`, the three compact programs are

```text
projection (0,0), constant 0 (1,0), constant 1 (0,1).
```

Because `E_p` and `G_p` cannot both be one, these are precisely

```text
(not(E_p or G_p),G_p).
```

For a negative cell `N_1=d(c0,x,c1)`, the programs are

```text
projection (0,1), constant 0 (0,0), constant 1 (1,1),
```

which equal

```text
(G_p,E_p or G_p).
```

If the root is P, the cell sign is the parity of the number of digit 1s in p.
If the root is N, that parity is flipped. This is exactly the frozen
middle-edge polarity rule; no signed leaf or free NOT operation is introduced.

The same analysis proves both constant modes. A positive cell receives
`(1-c,c)` and a negative cell receives `(c,c)`. Consequently every P/N mode in
the strong-family interface is covered.

## 3. Parallel balanced construction

Split a target/physical word into consecutive blocks `A,B`. Directly from the
definition of first mismatch,

```text
E_AB = E_A and E_B,
G_AB = G_A or (E_A and G_B).
```

If A already differs, its first mismatch owns G; B matters only when A is
equal. This also proves inductively that E and G remain Boolean and disjoint.

For one ternary target digit x, the states for physical digits 0,1,2 are

```text
p=0: (delta_0(x),0),
p=1: (delta_1(x),0),
p=2: (delta_2(x),delta_1(x)).
```

On the nonbinary branch let

```text
two=A, one=u(A), zero=u(u(A)),
```

so `A=2` gives the intended names. Exact original-signature equality indicators
are

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

Therefore every displayed operation is a legal d/u node. The generated terms
reference only `A` and the target-address digits; no router branch/payload wire
appears.

### Size

Let `S(w)` count the E/G state nodes for a balanced width-w block. One digit
costs five nodes. If `a=floor(w/2)` and `b=ceil(w/2)`, each of the `3^w`
physical concatenations needs three d nodes, hence

```text
S(1)=5,
S(w)=S(a)+S(b)+3*3^w.
```

Directly check `w=1,2,3`. For `w>=4`, both children have width at least two,
so induction gives

```text
S(a)+S(b) <= 5(3^a+3^b) <= (10/9)3^w.
```

Thus `S(w)<=5*3^w`. The final `E or G` costs one node per physical word, and
at most `(3^w+1)/2` positive cells require one u node. Consequently

```text
V(w) <= 5q+q+(q+1)/2 <= 7q.
```

All nodes at a block size are independent and live in one shared DAG. This is
not `q` separately compiled decision lists.

### Depth

The one-digit indicators have depth at most four above raw A/address inputs.
Each balanced composition level adds at most two d layers. Final pair formation
adds at most two layers. A balanced split has height `ceil(log_2 w)`, giving

```text
depth(V_w) <= 6+2*ceil(log_2 w).
```

The width-zero router is the base P1/N1 and uses only the two shared name
levels.

## 4. Giant-router compiler

Fix the explicit reserve constant `C=4`. For `r>=64`, put

```text
L = 4+ceil(log_3(r^2)),
H = r-L,
M = 3^floor(log_3 H),
b = log_3 M,
P = 3^(r-b).
```

Then

```text
H/3 < M <= H,
H >= r/2,
M > r/6.
```

The local address block has b coordinates and M assignments. The prefix has
`r-b` coordinates and P assignments.

### 4.1 Local universal library

There are `3^M` Q-valued tables on the M-point local block. Encode each output
with the frozen two-bit code. For each table, two `P_(b+1)` routers select the
high and low bits. Together those two routers use exactly

```text
3M-1
```

discriminator nodes. One parallel width-b program vector is shared across all
tables and both planes. Hence

```text
local nodes <= (3M-1)3^M+7M.
```

The two-logarithm reserve is load-bearing. Since

```text
M <= r-4-ceil(log_3(r^2)),
```

we obtain

```text
3M*3^M <= 3r*3^(r-4)/r^2 = (1/27)*3^r/r.
```

### 4.2 One prefix router

For the requested global table, each prefix assignment points to one of the
already shared local functions. Two `P_(r-b+1)` routers select the encoded
pair. Their combined size is `3P-1`. The complete parallel prefix program
costs at most `7P`, so

```text
prefix routers plus controls <= 10P.
```

Because `M>r/6`,

```text
P=3^r/M < 6*3^r/r,
```

and the prefix contribution is below `60*3^r/r`.

The balanced anchor costs at most `4(r-1)` nodes; its two names, one decoder,
and final normal-selector glue cost seven more. Since `M<=r`, all of these
lower-order terms obey

```text
(7M+4r+7)*r/3^r <= (11r+7)*r/3^r < 1              (r>=64).
```

The last ratio decreases after 64. Combining this unit with the local-library
`1/27` unit and the strict prefix bound of 60 units gives less than
`61+1/27` units. Therefore the deliberately rounded conservative ledger is

```text
nonbinary nodes <= 62*3^r/r.
```

The retained binary branch is at most one additional unit in this range, so
the displayed total constant 63 is valid. These constants are deliberately
loose; the largest exact nonbinary normalized count over all 4,033 checked
arities `64..4096` is `25.833333333333` at `r=93`.

### 4.3 Depth

The local router contributes `b+1` d layers. The giant prefix router contributes
`r-b+1`. Local and prefix program vectors are precomputed in parallel, not
serially per control or physical router. The balanced anchor has depth at most
`3*ceil(log_2 r)`. Charging its names, both vector depths, one decoder, and the
final selector gives the explicit bound

```text
D_nonbinary <= r+5*ceil(log_2 r)+12.
```

Thus the additive overhead drops from the preceding square-root schedule to
`O(log r)` without changing the order-optimal same-DAG size.

## 5. Binary branch and padding

Absolute 0/1 names from `A=2` are illegal on the all-binary cube. This lane does
not reuse the nonbinary equality formulas there. It retains the independently
audited square-root signed-router branch with logical relative controls and
physical names `x0,u(x0)`.

For `k=floor(sqrt r)`, its conservative depth ledger is

```text
(k+1)*ceil((r-1)/floor(log_2(3^k)))
  +2*floor(log_2(3^k))+3*ceil(log_2 r)+8.
```

Exact integer replay shows this is below r for every `339<=r<=4096`. For the
tail, `floor(log_2(3^k))>=floor(3k/2)` and is below `2k`. When `k>=30`, the
required slack reduces to

```text
k^3-27k^2-19k+9 > 0,
```

which holds at 30 and increases thereafter. Its size is

```text
O(2^r+r*3^(2sqrt r))=o(3^r/r).
```

More explicitly, residual-first routing has at most
`(N+Q)/(Q-1)` router instances for `N=2^(r-1)`,
`Q=2^floor(log_2 q)`, and `q=3^k<2Q`. Router nodes are therefore below
`6(N+Q)`, while all shared control tables are below `6r*q^2`. For `r>=64`,
we have `Q<N`, and the inequalities

```text
6r*(2/3)^r < 1/4,
3^(r-2floor(sqrt(r))) >= r^4,
(4r+10)*r/3^r < 1/4
```

bound respectively the routers, control tables, and fixed overhead by less
than `1/4`, `6/r^2<1/4`, and `1/4` units of `3^r/r`. Thus the retained binary
branch is below one unit. The first and third ratios decrease after 64. For
the middle inequality it suffices to check the square boundary
`r=k^2,k>=8`, where `3^(k^2-2k)>=k^8`; both sides preserve the inequality
between consecutive squares, and the boundary margin increases with k. The
exact integer checker independently verifies the full bound through arity
4,096.

Binary chunks can have fewer live children than the enclosing power-of-three
router. Duplicate the last live branch in unused slots and request only live
targets. The independent direct-ROBDD checker verifies 232 such padded P/N
projections through width four. The giant nonbinary local and prefix arities
are exact powers of three and need no padding.

Important control qualification: the logical relative binary program is
address-only, but its physical wires `x0,u(x0)` are payload-relative. Their
legality comes from complement equivariance, not from pretending they are
absolute constants.

## 6. Deterministic evidence

`check_parallel_program_vector.py` is a self-contained checker. It does not
import the frozen family implementation. It performs:

```text
program-pair semantic checks                           1,200,114
dependency-set checks                                 18
concrete full-router checks through width two         11,356
direct-ternary ROBDD mode checks through width four   262
padding ROBDD checks                                   232
exact compiler arities                                 4,033
```

The ROBDD applies d directly; it does not reuse the author's Boolean-majority
decomposition. It checks every P/N projection/complement target and both
constant modes. The program-pair census covers all target/physical pairs
through width six and both signs. Materialized vectors through width eight
satisfy the proved node/depth bounds. Every generated program term's dependency
set is confined to the anchor and address digits.

Normal and optimized Python receipts are byte-identical:

```text
check_parallel_program_vector.py
  2ba586a1ef97822aebbbcf692d29cd5bd3f8bbc8e785ddce43aff2180df3c350

receipt.json
receipt_optimized.json
  c9e8b1ad9c57f4ef55ea458b2573f20578a137a6c7b5fb1a66707bb7ee68b632

receipt semantic SHA-256
  9699a3fe058369ac22a4a4d8050d07825cc80112cbc4c601a85914100db13f88
```

## 7. Killer falsifiers

1. **Unguarded right block.** Replacing
   `G_A or (E_A and G_B)` by `G_A or G_B` fails at
   `t=(0,1),p=(1,2)`: the first mismatch is bad, so correct G is zero, while
   the mutation returns one.
2. **Sign swap.** Giving P1 the N1 projection pair `(0,1)` makes
   `d(x,0,1)` constant one instead of x.
3. **Binary absolute names.** Reusing `A,u(A),u(u(A))` as 2,1,0 when A is
   binary changes the width-one vector and is rejected.
4. **Sequential program ROM.** A `Theta(qw)` prefix program at `r=512` costs
   more than `100*3^r/r`; the parallel `O(q)` construction is necessary.
5. **One-log reserve.** If H reserves only `log_3 r+C`, then at `r=6574`
   it selects `M=6561`; the local library alone exceeds
   `62*3^r/r`. Reserving two logarithms is necessary for this ledger.

## 8. Falsifier matrix and nonclaims

| Falsifier | Verdict |
|---|---|
| `F-input` | PASS. Exact frozen public bytes are hash-bound. |
| `F-grammar` | PASS locally: only d/u terms and variables; anchor, names, two planes, decoder, and glue are charged. |
| `F-control` | PASS on nonbinary branch: terms depend on A/address digits, not router payloads. Binary physical controls are explicitly complement-relative. |
| `F-polarity` | PASS. Every cell sign is root sign XOR middle-edge parity; P/N pair formulas are separately checked. |
| `F-size` | PASS for the stated same-DAG ledger. Sequential vectors and one-log reserve are explicit rejected mutations. |
| `F-depth` | PASS for program vectors and arithmetic; complete compiler remains a composition of named frozen lemmas. |
| `F-degenerate` | PASS: width zero, both signs, both constants, every small target, padding, arity thresholds, and power jumps. |
| `F-boundary` | Exact vector theorem; conditional integrated compiler; no ordinary-tree or lower-bound claim. |
| `F-prior` | OPEN. Parallel decoder/multiplexer synthesis, universal circuits, Lupanov depth-size work, and multivalued logic require dedicated comparison. |

This lane does not establish novelty, an optimal additive term, an unshared
formula bound, practical performance, Lean verification, publication
readiness, patent freedom to operate, rights under the unsigned Tau license, or
any private Tau capability.

## 9. Reproduction

From the repository root:

```text
python3 research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/check_parallel_program_vector.py \
  --out research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/receipt.json

python3 -O research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/check_parallel_program_vector.py \
  --out research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/receipt_optimized.json

cmp -s research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/receipt.json \
  research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/receipt_optimized.json
```
