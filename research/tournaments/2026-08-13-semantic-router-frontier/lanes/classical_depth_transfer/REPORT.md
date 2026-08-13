# Classical Boolean depth sharpening and fixed-Q transfer

Date: 2026-08-13

Status: **primary source recovered; direct transfer does not improve the
compiler; native Q-valued analogue OPEN**.

## Verdict

Gashkov's 1978 result is stronger and more model-specific than the abbreviated
survey attribution suggests.  For arbitrary Boolean functions it constructs,
over the standard basis `{AND,OR,NOT}`, a **formula** of

```text
depth <= ceil(n-log_2(log_2 n)+o(1))+2
formula complexity ~ 2^n/log_2 n.
```

Thus the same construction simultaneously has asymptotically optimal
**formula** size and near-optimal depth.  It does not state circuit-Shannon
size `Theta(2^n/n)`, a fixed programmable skeleton, or a uniform synthesis
family.

There is no cost-preserving direct transplant to the frozen parameter-free
`Q=({0,1,2};d,u)` compiler:

1. the ordinary binary-basis theorem is legal on relative Boolean rails, but
   its leading depth coefficient is `1`, whereas the retained signed-router
   binary branch has coefficient `log_3(2)<1`;
2. even an ideal dense Boolean encoding of `Q^r` needs
   `n>=ceil(r*log_2(3))`, so the transplanted standard-basis upper construction
   has leading depth `log_2(3)*r>r` and formula-witness size
   `Theta(3^r/log r)`, not the required same-DAG `O(3^r/r)`;
3. Gashkov's attractive full-ternary-Boolean-gate remark charges **every**
   three-input Boolean function as one gate.  The fixed `{d,u}` signature does
   not contain that unit-cost basis; and
4. the present nonbinary bridge has an `O(log r)` global-anchor/control
   dependency.  It would hide an isolated `-Theta(log log r)` core saving
   unless the bridge were recomposed.

The useful research direction is therefore a new, native Q-valued
Lupanov--Gashkov decomposition that preserves `O(3^r/r)` shared-DAG size and
does not serialize a global anchor.  This report does not establish such a
theorem.

## 1. Retrieval ledger

### Primary source

S. B. Gashkov, ["On the Depth of Boolean Functions" (Russian: "O glubine
bulevykh funktsii")](https://publ.lib.ru/ARCHIVES/P/%27%27Problemy_kibernetiki%27%27_%28seriya%29/%cf%f0%ee%e1%eb%e5%ec%fb%20%ea%e8%e1%e5%f0%ed%e5%f2%e8%ea%e8.%20%c2%fb%ef%f3%f1%ea%2034.(1978).pdf),
*Problemy Kibernetiki* 34 (1978), 265--268.

The complete issue scan was read at printed pages 265--268.  Local temporary
scan SHA-256 (the scan is not copied into the repository):

```text
164523ad836ea8ce315f60ea736be9808587ee1cdce1fc4d05d8c50301b5bfb0
```

Bibliographic metadata is independently listed by [MSU
ISTINA](https://istina.msu.ru/journals/1528286/) at issue 34, pages 265--268.
The source has no DOI in the inspected records.

### Secondary source used to locate and cross-check it

Ingo Wegener, [*The Complexity of Boolean
Functions*](https://cseweb.ucsd.edu/classes/fa23/cse248-a/papers/logic/cobf.pdf),
Wiley--Teubner, 1987, Chapter 4, section 4.4.  Wegener records the historical
sequence ending with "Gaskov (78): `n-log log n+2+o(1)`" and cites the same
primary pages.  His book's default `B_2` circuit convention permits all 16
binary Boolean gates and free `0,1` inputs.  That is a survey normalization,
not the basis printed in Gashkov's original theorem.

TheoremSearch was queried by theorem shape, adversarial model terms, and a
formal-library filter.  It returned no exact Gashkov source or model-complete
match.  Those searches are negative retrieval evidence only.

> TheoremSearch supplied retrieval-only prior art. The promoted claim depends
> only on the independently checked local evidence listed below.

Research Kernel run:

```text
orbit-fixed-q-gashkov-depth-transfer-20260813
```

## 2. What the 1978 theorem actually says

The labels in this section are deliberate: **SOURCE THEOREM** means a statement
read in the primary paper; **SOURCE CONVENTION UNKNOWN** means the four-page
paper delegates a detail to an earlier reference.

| Field | Primary-source finding |
|---|---|
| Function class | All one-output Boolean functions `f:{0,1}^n->{0,1}`; `D(n)=max_f D(f)`. |
| Named basis | `{AND,OR,NOT}`.  `AND` and `OR` are binary and `NOT` is unary. |
| Circuit model | An acyclic functional-element circuit.  A chain is a sequence of gates whose outputs feed later gates; depth is the number of gates in a longest chain.  Inputs are not counted. |
| Formula model | Fan-out-one gate tree.  The paper states that minimum circuit depth equals minimum formula depth: unsharing a circuit can increase size but not depth. |
| Main upper theorem | **SOURCE THEOREM:** `D(n)<=ceil(n-log_2(log_2 n)+o(1))+2`. |
| Lower comparison | The paper obtains `D(n)>=ceil(n-log_2(log_2 n)+o(1))` from the formula Shannon lower bound.  Hence the upper bound is tight up to a bounded additive term. |
| Witness size | **SOURCE THEOREM/CONSTRUCTION:** the formula `Phi` used in the proof can be chosen with `L_Pi(Phi)~2^n/log_2 n`. |
| Fan-out | The displayed witness is a formula, hence gate fan-out one.  Repeated input leaves are allowed.  The depth quantity itself also applies to unrestricted-fan-out circuits because of unsharing. |
| Constants | The named basis contains no nullary gate.  The proof visibly uses literals and can synthesize constant functions from a variable and its negation at constant cost.  Exact permission for free constant leaves is delegated to reference [2] and was not independently recovered; no transfer below relies on free constants. |
| Uniformity | No uniformity theorem or fixed circuit scheme is stated.  The proof chooses function-dependent `g` tables and index sets inside a Lupanov representation.  It is a nonuniform arbitrary-function synthesis/existence result. |
| Programmability | No common skeleton with address-only program inputs is supplied.  Wegener explicitly singles out McColl--Paterson, not Gashkov, for a fixed circuit scheme. |

### Size-order answer

The phrase "preserves Shannon-order size" needs a model subscript.

- **Yes for formulas:** the source construction is on the formula-Shannon
  scale `Theta(2^n/log n)`.
- **Not established for circuits:** the Boolean circuit-Shannon scale is
  `Theta(2^n/n)`.  Gashkov's formula, viewed as a DAG without discovering new
  sharing, is larger by `Theta(n/log n)`.  The paper gives no simultaneous
  `Theta(2^n/n)` circuit-size bound for its sharpened-depth witness.
- **No fixed-skeleton size statement:** nothing in the source makes the
  function-dependent formula a programmable universal circuit of the same
  size and depth.

This formula/circuit distinction is the main missing qualification in the
short modern attribution.

## 3. Proof mechanism in the primary source

Gashkov starts from Lupanov's representation arising in a universal
parallel-series network of depth three.  The variables are divided into four
blocks; characteristic functions, sparse literal disjunctions, and
function-dependent residual functions are assembled by a large outer
disjunction.  Parameters are chosen with blocks of order `log n`,
`log log n`, and polylogarithmic sparsity.

The elementary depth lemma is balanced aggregation:

```text
AND of t inputs and OR of t inputs have depth ceil(log_2 t).
```

The proof then bounds the depth of each component in parallel and balances the
outer aggregation.  Its final calculation is the displayed
`n-log_2(log_2 n)+o(1)+2` bound while retaining the Lupanov formula-size scale.
This is a structured block decomposition, not merely a balanced full DNF.

Two closing remarks matter for transfer:

1. **SOURCE THEOREM:** if the basis contains all `k`-input Boolean functions
   as unit gates, the worst-case depth is

   ```text
   (n-log_2(log_2 n))/log_2(k)+O(1).
   ```

2. **SOURCE THEOREM:** for a complete basis of gates of arity at most two that
   contains `{AND,NOT}` or `{OR,NOT}`, the depth is

   ```text
   n-log_2(log_2 n)+O(1).
   ```

The first remark changes the unit-cost basis.  It cannot be invoked merely
because Orbit's discriminator happens to have three input positions.

## 4. Precise transfer tests

### 4.1 All-binary slice without and with relative rails

On `{0,1}`,

```text
d(x,y,z)=majority(x,not y,z),   u(x)=not x.
```

Both generators commute with simultaneous complementation.  By structural
induction, every parameter-free `{d,u}` term on the Boolean cube is self-dual.
Absolute `AND`, `OR`, and constants are not in that clone, so a literal
gate-by-gate translation of Gashkov's absolute Boolean formula is illegal.

The frozen binary compiler does have the stronger complement-relative
representation.  For orientation `a` encode a logical bit by

```text
E_a(b)=a xor b.
```

Then all eight Boolean rows satisfy

```text
relative NOT: u(E_a(x))             = E_a(not x),
relative AND: d(E_a(x),u(a),E_a(y)) = E_a(x and y),
relative OR:  d(E_a(x),a,E_a(y))    = E_a(x or y).
```

Thus the standard `{AND,OR,NOT}` formula can be simulated one-for-one in
relative encoding.  This is not an absolute-constant bridge: the physical
names `a,u(a)` are payload-relative, and legality comes from complement
equivariance.

It still does not improve the compiler.  Gashkov gives binary depth

```text
r-log_2(log_2 r)+O(1),
```

whereas the retained signed-router binary branch is already

```text
log_3(2)*r+O(sqrt(r)).
```

Since `log_3(2)=0.630929...`, the classical formula is asymptotically deeper.

### 4.2 Nonbinary slice through the ordinary binary basis

On a slice with anchor `A=2`, the legal terms

```text
two=A, one=u(A), zero=u(u(A))
```

give one-node Boolean operations

```text
x and y=d(x,one,y), x or y=d(x,zero,y), not x=u(x).
```

This removes the gate-basis obstruction, but not the alphabet and size
obstructions.  Any injective encoding of the `3^r` ternary addresses into `n`
Boolean bits satisfies

```text
n >= ceil(log_2(3^r)) = ceil(r*log_2(3)).
```

Even granting this dense encoder, its inverse interpretation, and output
decoding for free, applying the standard-basis Gashkov construction to the two
output planes supplies only

```text
transplanted upper-bound leading term: log_2(3)*r = 1.584962...*r,
source formula-witness scale: 2^n/log n = Theta(3^r/log r).
```

The first loses to the current `r+O(log r)` nonbinary coefficient.  The second
exceeds the required shared-DAG order `O(3^r/r)` by `Theta(r/log r)`.  A local
two-bit encoding per ternary coordinate is still worse: `n=2r`, depth has
leading coefficient two, and the formula-size numerator is `4^r`.

These are optimistic barriers because a legal dense ternary-to-binary encoder
has not been charged.

### 4.3 Why the full three-input Boolean basis does not repair it

Combining the ideal dense bit count with Gashkov's `k=3` remark formally
cancels the factor `log_2(3)` and suggests a core near

```text
r-(log_2(log r))/log_2(3)+O(1).
```

That calculation is valid only when **each of the 256 three-input Boolean
functions is one depth unit**.  A single `{d,u}` node with literals or anchored
constants realizes only 40 distinct three-input truth tables.  Neither
three-input `AND` nor three-bit parity occurs.  Hence there is no depth-one
translation of the full `B_3` basis.

This finite obstruction refutes the cost-preserving gate substitution.  It
does not prove that a globally reorganized `{d,u}` construction cannot obtain
the same asymptotic depth; that would be a new theorem.

### 4.4 Anchor and glue obstruction

The current audited nonbinary compiler charges

```text
r+5*ceil(log_2 r)+12
```

as a conservative depth bound.  Its global anchor distinguishes the all-binary
cube from inputs containing a `2`.  Such a function depends essentially on
all `r` inputs.  A fan-in-three depth-`h` term can depend on at most `3^h`
inputs, so any standalone global anchor has depth at least
`ceil(log_3 r)`.

This does not force an additive `Omega(log r)` term in every imaginable
compiler: an anchor might be overlapped, distributed, or eliminated.  It does
show that inserting an unchanged Gashkov core behind the current serialized
anchor cannot expose a `-Theta(log log r)` improvement.  The bridge itself has
to change.

## 5. Transfer decision table

| Proposed route | Legality | Size | Depth | Verdict |
|---|---|---|---|---|
| Gashkov on the all-binary branch with absolute constants | Illegal in the parameter-free Boolean clone | Not reached | Not reached | **REJECT** |
| Gashkov on the all-binary branch with relative rails | Exact one-for-one gate bridge | `Theta(2^r/log r)`, globally negligible | Leading `1`, worse than `log_3(2)` | **LEGAL BUT DOMINATED** |
| Coordinatewise two-bit encoding of `Q^r` | Possible after anchor | `Theta(4^r/log r)` | Leading `2` | **REJECT** |
| Ideal dense Boolean encoding, standard basis | Encoder not supplied; granted free for falsification | Source witness is `Theta(3^r/log r)`, insufficient | Supplied bound has leading `log_2(3)>1` | **REJECT AS A BOUND TRANSFER, EVEN UNDER FREE ENCODER** |
| Ideal dense encoding plus full unit-cost `B_3` | Wrong gate-cost model | Source still gives formula rather than same-DAG order | Attractive coefficient one | **INAPPLICABLE** |
| Native Q-valued Lupanov--Gashkov decomposition in `{d,u}` | Not yet constructed | Must prove `O(3^r/r)` on the same DAG | Target below `r+O(log r)` | **OPEN / HIGH LEVERAGE** |

Consequently this classical theorem **does not improve** the frozen conditional
`O(3^r/r)`, `r+O(log r)` compiler as presently composed.

## 6. What is theorem, inference, and open

- **SOURCE THEOREM:** the exact Boolean basis, formula/circuit depth model,
  main depth bound, formula-size scale, and the two closing basis remarks.
- **CHECKED LOCAL THEOREM:** Boolean discriminator identity, generator
  self-duality, relative/anchored gate tables, depth-one `B_3` obstruction, and
  exact alphabet-count arithmetic.
- **PROVED INFERENCE:** the bound supplied by direct standard-basis dense
  Booleanization has leading depth above one, and the source formula witness
  does not establish `O(3^r/r)` size.
- **MODEL-SPECIFIC INFERENCE:** the current serialized anchor prevents an
  unchanged core transplant from changing the `r+O(log r)` theorem.
- **OPEN:** a native Q-valued version with function-dependent shared DAGs, a
  fixed `{d,u}` basis, no nullary constants, compiled controls, and a
  nonserialized anchor.

## 7. Preprint and research recommendation

This source does not erase the significance of the signed-router/program-vector
result, but it narrows the defensible contribution.  A research preprint may
present the exact fixed-signature router family and its audited conditional
same-DAG compiler, provided that it:

- cites Gashkov and Lupanov prominently as the classical simultaneous
  formula-size/depth ancestry;
- does not claim the bare leading-one depth shape, local coding, discriminator
  switching, or Shannon-order synthesis as new;
- states that the end-to-end `r+O(log r)` compiler remains conditional on the
  frozen bridge lemmas;
- distinguishes formula `Theta(2^n/log n)` from circuit `Theta(2^n/n)` and
  Orbit same-DAG `O(3^r/r)` throughout; and
- avoids novelty, optimality beyond the proved leading coefficient,
  practical-performance, patent/FTO, license, and Tau claims.

For a stronger theorem, the next bounded target should be:

> Rebuild Gashkov's block decomposition directly for ternary truth tables,
> replacing the full Boolean gate basis by signed discriminator interfaces,
> while certifying `O(3^r/r)` same-DAG size and overlapping or eliminating the
> global anchor.

The first killer tests are the local-library sharing factor, the formula-to-DAG
gap `r/log r`, the absence of free `B_3` gates, and whether anchor-relative
names can be introduced late without making physical controls branch-dependent.

This is a mathematical preprint recommendation only.  It is not a novelty,
copyright, licensing, patent, or freedom-to-operate opinion.

## 8. Deterministic evidence

Checker:

```text
research/tournaments/2026-08-13-semantic-router-frontier/lanes/classical_depth_transfer/check_transfer_barriers.py
SHA-256 82ec9946ebb759a099923136078d58290a08eb947a8cb8483dbddbc616e85a1d
```

Commands:

```text
python3 research/tournaments/2026-08-13-semantic-router-frontier/lanes/classical_depth_transfer/check_transfer_barriers.py
python3 -O research/tournaments/2026-08-13-semantic-router-frontier/lanes/classical_depth_transfer/check_transfer_barriers.py
```

Both exit zero with semantic SHA-256

```text
0e2f9218bb41de563c9eec29e05a8dc8a370f7b470d87fa36bb046d2de3113ed
```

The checker uses explicit exceptions rather than `assert`, so optimized mode
does not remove the gates.  It checks:

```text
Boolean d identity rows                       8
relative AND/OR/NOT rows                      8
anchored absolute AND/OR/NOT rows             4
depth-one truth tables with literals/constants 40
AND3 in that depth-one grammar                false
parity3 in that depth-one grammar             false
dense-encoding diagnostics                    r=16,64,256,1024
```

Receipt:

```text
research/tournaments/2026-08-13-semantic-router-frontier/lanes/classical_depth_transfer/receipt.json
```

Frozen comparison inputs read, not edited:

```text
STATE.md
  5304ad459b25928e14197dfb989af7dfae4d9df6b632eb79020e9f1cef812133
lanes/program_vector/REPORT.md
  d4a4a6e8c512b915c35129b7158da5a841456c26acc569e677fda8a965f30834
audits/program_vector/REPORT.md
  5d2c0b8c2fed0cdef046d93f3a5d28fcf18e0efe9a51302fa41bfe122e462cf1
audits/strong_family/REPORT.md
  e581a476ba8ecce1071113547709fcc1b0d2b1ff3e5f6e59683df23c2872975c
```

## 9. Falsifiers and nonclaims

| Falsifier | Verdict |
|---|---|
| `F-source` | PASS.  Complete primary pages read; survey and metadata are separately labeled. |
| `F-basis` | PASS.  Standard binary basis, full unit-cost `B_3`, and fixed `{d,u}` are never conflated. |
| `F-constants` | PASS with an explicit source-definition gap.  No free Boolean constant is used in the transfer; anchor/relative names are charged. |
| `F-model` | PASS.  Formula, unrestricted circuit, shared DAG, and programmable skeleton are distinct. |
| `F-size` | PASS.  Formula-Shannon and circuit-Shannon orders are separated; dense encoding exposes the `r/log r` loss. |
| `F-fanout` | PASS.  Gashkov witness is fan-out one; Orbit target relies on same-DAG sharing. |
| `F-uniformity` | PASS.  No fixed scheme or uniformity is attributed to Gashkov. |
| `F-control` | PASS with qualification.  Logical relative binary gates are exact; physical rails are payload-relative, not absolute controls. |
| `F-anchor` | PASS.  Current serialized overhead is charged; the lower bound is not generalized to redesigned compilers. |
| `F-boundary` | PASS.  Direct transfer is rejected; global impossibility, novelty, FTO, and publication readiness are not claimed. |

No statement here establishes that Gashkov's construction is the latest
classical depth theorem, that no many-valued analogue exists, or that a native
adaptation will succeed.  In particular, Orlov/Kochergin many-valued
size/depth sources identified by the prior-art lane remain separate mandatory
comparisons.
