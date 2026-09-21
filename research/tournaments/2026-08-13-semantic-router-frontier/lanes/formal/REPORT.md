# Lean checkpoint: strong signed Boolean router induction

Date: 2026-08-13

Verdict: **PASS for the exact Boolean induction stated below.**  The new Lean
file compiles under the pinned Lean 4.34.0-rc1 toolchain with warnings treated
as errors, and the strict placeholder/axiom-declaration scan is clean.  The
frozen fused artifacts and manuscripts were not edited.

## Formalized object

`StrongSignedRouter.lean` defines the Boolean discriminator exactly as

```text
disc x y z = if x=y then z else x.
```

The term grammar `DTerm Branch Control` has exactly three constructors:

```text
branch, control, disc.
```

It has no Boolean-constant constructor and no unary/NOT constructor.  Program
bits are external assignments to typed control leaves.  The program function
accepts a sign, route depth, mode, and control address, but no branch valuation;
the address-only boundary is therefore enforced by its type.

The router uses two mutually recursive signs:

```text
P_(n+1) = d(P_n,N_n,P_n),
N_(n+1) = d(N_n,P_n,N_n).
```

At index `n`, addresses are ternary words of length `n`; the router has depth
`n+1` and externally stated depth `h=n+1`.

## Main realization theorem

The kernel-checked theorem

```text
eval_router
```

quantifies over every index `n`, both signs, both constant modes, every route
target, and every Boolean branch valuation.  It proves:

- `P_n` returns the requested branch unchanged;
- `N_n` returns the complement of the requested branch;
- both signs can be forced to constant `0` or constant `1`.

The induction uses the exact three child programs from the frozen mathematical
construction.  No monotonicity or two-extreme quotient is assumed.

The depth-indexed corollaries are

```text
positive_realization_at_depth
negative_realization_at_depth.
```

## Exact structural theorems

Lean also checks, for router index `n`,

```text
Fintype.card (Address n) = 3^n,
Fintype.card (Control n) = 2*3^n,
branchCount (router sign n) = 3^n,
controlCount (router sign n) = 2*3^n,
depth (router sign n) = n+1,
2*discCount (router sign n)+1 = 3^(n+1).
```

Thus at externally named depth `h>=1`, the branch capacity is exactly

```text
q_h = 3^(h-1),
```

the number of control leaves is `2q_h`, and the discriminator-node identity
is equivalent to `(3^h-1)/2` without using natural-number division in the
formal statement.

`router_originalSignature` checks the recursive grammar certificate.  More
fundamentally, a free `NOT` node is unrepresentable in the `DTerm` datatype.
The semantic complement in the negative theorem is an output specification,
not a term constructor.

## Checkpoint evidence

Narrow checker:

```text
lake env lean research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean
```

Strict warning check:

```text
lake env lean -EwarningAsError=true research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean
```

Both returned exit code zero with no output.

Strict placeholder and declaration scan:

```text
python3 /home/trevormoc/.codex/skills/proof-engineering/scripts/scan_proof_placeholders.py --flag-axiom research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean
```

Result: `No proof placeholders found.`

Temporary `#print axioms` checks reported only the standard Lean/mathlib
foundations `propext` and `Quot.sound` for the selected main theorems.  The
temporary commands were removed, and the final bytes were recompiled.

The skill-provided checkpoint audit also passed and emitted
`tool_receipt.json`.  The deterministic provenance and scope ledger is
`receipt.json`.

## Scope boundary

This checkpoint proves the abstract Boolean signed-router induction.  It does
not yet formalize:

- extraction equality between Lean programs and `r27_witness.json`;
- the two-plane Q encoder/decoder bridge;
- complement-relative binary control compilation;
- residual-first prefix-tree accounting;
- the same-DAG `O(3^r/r)` size proof;
- the `r+O(sqrt(r))` compiler-depth theorem; or
- novelty, patent/FTO, unsigned-license, Tau, or performance claims.

The Lean statement was manually transcribed from the frozen construction.  It
records the frozen artifact hashes in `receipt.json`, but does not parse those
bytes.  A later integration lane should either extract the R27 table from the
Lean functions or independently compare all generated leaves/program bits
before claiming a machine-checked bridge to the JSON witness.
