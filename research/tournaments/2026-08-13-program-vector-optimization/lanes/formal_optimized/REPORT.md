# Formal optimized program vectors

Date: 2026-08-13

## Verdict

**PASS for the exact theorem coverage below.**  Lean 4 checks the direct
absorbing-rail construction in the original constant-free `{d,u}` term
signature under `A=2`, including its signed projection controls, legality,
depth ledger, and the frozen `<=3q` bound.  It also checks the two semantic
sharing identities behind the sharper sibling-shared construction and proves
its exact arithmetic recurrences and envelopes

```text
3*S(w) <= 4*3^w + 15*3^ceil(w/2),
3*S(w) <= 7*3^w.
```

Thus the formal ledger has leading coefficient at most `4/3`, matching the
separately proved scalar-output lower bound in leading order.  This lane does
not formalize that all-width distinct-output census, so it does not itself
prove the matching lower bound or global optimality.

The theorem is for one fixed P or N root sign, an address-only scalar
same-DAG with free fanout, and raw anchor/address terminals.  It is not a
formula-size, bounded-fanout, or integrated-compiler theorem.

## Exact formal coverage

`DirectRail.lean` proves:

- the Boolean restriction of the original ternary discriminator;
- the three valid rail states `(equal,zero,one)`, absorbing rail composition,
  and associativity;
- legal original-signature term composition using two parallel discriminator
  nodes, together with its semantic correctness and depth increment;
- four charged one-digit rail nodes, their exact semantics, legality, and
  depth at most three above raw terminals;
- the exact positive pair `(Z,O)` and negative pair `(O,u(Z))`, including
  equality with the frozen signed projection program for every address;
- the trailing physical-`{0,1}` identity `O_(a s)=O_a`;
- the balanced rail recurrence, root-sign-specific complement count, and
  complete ledger including the two anchor names;
- `totalRailNodes <= 3*3^w` for every width and sign;
- the explicit finite inequality

  ```text
  6*totalRailNodes
    <= 12*3^w + 14*(3^floor(w/2)+3^ceil(w/2)) + 15,
  ```

  which is the checked finite form of `(2+o(1))*3^w`; and
- depth at most `4+Nat.clog 2 w` for `w>=1`.

`SiblingShared.lean` additionally proves:

- rail validity and semantic zero-right gain reuse;
- `O_(a s)=O_a` for every paired suffix whose physical digits lie in
  `{0,1}`;
- `N_(a1)=O_(a2)` for every valid earlier prefix summary `a` and every target
  digit;
- exact natural-number recurrences for the generic `(Z,O)` library, extended
  `(Z,O,N)` suffix library, top sibling overlap, and one-sign terminal vector
  ledger;
- exact small bases `S_P(1)=5`, `S_N(1)=6`, `S_P(2)=20`, `S_N(2)=21`;
- `3*R(w)<=7*3^w`, `3*E(w)<=9*3^w`;
- the all-width convergence envelope

  ```text
  3*S(w) <= 4*3^w + 15*3^ceil(w/2);
  ```

- the uniform corollary `3*S(w)<=7*3^w`.

The sharp arithmetic theorem uses the exact `S` recurrence as its declared
cost ledger plus the separately proved reuse identities.  It does not define
an internal hash-consed DAG datatype or prove a refinement from that datatype
to `S`; that bridge is supplied by the executable construction and independent
referee lane, not silently claimed here.  The older `<=3q` theorem does include
the explicit legal term constructors and frozen-program semantic connection.

## Native ternary relation

The intermediate native state `K=0, G=1, P=2` with merge
`d(S_A,A,S_B)` is the same first-non-equal monoid represented in one ternary
wire.  It corroborates the absorbing-state algebra, but extracting the full
exposed scalar control vector costs more than the sibling-shared Boolean-rail
construction.  No `r+ceil(log_3 r)` lower barrier is inferred here beyond a
rigid exposed-control cascade.

## Replay and proof hygiene

`check.sh` fails closed on the frozen source hashes, compiles the frozen
dependency chain to lane-local `.olean` files with an explicit `LEAN_PATH`,
and compiles both theorem modules with `-EwarningAsError=true`.  It then runs
the proof-placeholder scanner with axiom declarations flagged.

`AxiomAudit.lean` reports only Lean/mathlib's standard logical dependencies
(`propext`, `Classical.choice`, and `Quot.sound` where tactics/imported
theorems require them).  The lane declares no axiom and contains no `sorry`,
`admit`, placeholder proof, or warning-as-error violation.

Normal and `python -O` receipt runs are byte-identical:

```text
receipt.json
receipt_optimized.json
  cd5f1a49799726c3009748b5634a30cc154dd05d28440881df07404738c4e42e

semantic_sha256
  6e376880f893fcfb698e17669c9db5f8adba3bcb0c1cd5629f8be168667876ee
```

Source and replay hashes:

```text
DirectRail.lean
  57963dadfb40cef30d94f630126f3179c55e98bea68e5974daa8e91913c404bd
SiblingShared.lean
  8eb02a3e2e5a4f7531d740b704422d09724376821f83b921aec98b77a0277e77
AxiomAudit.lean
  9fc5869e15ab1bb99d77503a3f0ee95cee02c536cfb08f090a18dd76d4c37de5
check.sh
  540398a33d5d003418069eeea9e48ee068fa5c72e35d743ee8f63eb30b6991d7
make_receipt.py
  b35906256d238b3c563515554cb79a9e12cc4bf5243d950f9553ea6a670c89c3
```

Frozen inputs are hash-bound in the receipt, including `STATE.md`, the three
formal dependency modules, and the earlier direct-rail checker/report/receipt.

## Nonclaims

- No all-width distinct-output census or lower-bound proof is formalized here.
- No exact optimum, extra `+1` lower bound, or global circuit lower bound.
- No simultaneous-both-sign theorem at the one-sign cost.
- No formula-size, bounded-fanout, integrated compiler, novelty, patent, or
  freedom-to-operate claim.
- No manuscript or frozen artifact was edited.
