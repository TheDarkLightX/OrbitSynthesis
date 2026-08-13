# Complete realizability classification of minimal parameter-core families

**Status:** arbitrary-carrier binary construction derived; exact reference verification complete for every classified family on carriers of sizes two through six; all nonempty antichains enumerated through size four; counting formulas verified; Morph certificate and fail-closed Research Kernel packet complete; Lean formalizes the partition shape only; publication novelty review pending.

## 1. From one operation to a partial partition

Let `D_A=(A;d)` be the pure discriminator algebra on a finite nonempty carrier, and let `f:A^n->A`, with `n>1`.

Define the **foreign-output core**

`N(f)={a in A : f(z)=a and a notin range(z) for some z}`.

By the exact membership normal form from `DISCRIMINATOR_CORE_INTERSECTION_LAW.md`, a parameter core `C` realizes `f` iff

1. `N(f) subseteq C`;
2. `Sym(A\C) subseteq Aut(f)`.

On `U=A\N(f)`, join two elements when their transposition is an automorphism of `f`. Transpositions along a connected graph generate the full symmetric group of each connected component. Hence the connected components `B_1,...,B_k` are precisely the maximal subsets `B subseteq U` with `Sym(B) subseteq Aut(f)`.

If `U` is nonempty, the inclusion-minimal feasible cores are exactly `A\B_1,...,A\B_k`. If `U` is empty, the unique minimal core is `A`.

Thus every operation intrinsically determines a common named core and an unordered partition of the remaining carrier into maximal anonymous blocks.

## 2. Complete classification theorem

### Theorem — binary realizability

Let `|A|>=2`. A nonempty family `F subseteq P(A)` is the complete family of inclusion-minimal parameter cores of some binary operation on `D_A` iff:

1. `F` is an antichain;
2. every two distinct `C,D in F` satisfy `C union D=A`.

Equivalently, the complements `B_C=A\C` are pairwise-disjoint nonempty blocks when `|F|>1`. A singleton family is allowed for every core.

The one-element carrier is exceptional: its unique operation is parameter-free, so the only realizable family is `{empty}`.

Necessity is the exact core-intersection theorem. Sufficiency is constructive.

## 3. Explicit constructor

Given a classified family, put `E=intersection_(C in F) C` and let the complement blocks be `B_i=A\C_i`. They are pairwise disjoint and partition `A\E`. Fix an order of the blocks.

First define a conservative block selector:

- on arguments from distinct blocks, return the argument from the lower-index block;
- otherwise return the first argument.

This commutes with every permutation internal to each block. A transposition exchanging elements of distinct blocks fails at the row containing those elements, so no cross-block transposition is an automorphism.

Now force the foreign-output core to be exactly `E`:

- if `E` is empty, do nothing;
- if `|E|>=2`, cycle the outputs on the diagonals `(e,e)`;
- if `E={e}` and `A\E` is nonempty, map every anonymous diagonal `(u,u)` to `e`.

All remaining outputs are arguments. Therefore `N(f)=E`, the transposition components on `A\E` are exactly the blocks, and the minimal cores are exactly the requested family.

For the singleton family `{A}` on `|A|>=2`, the cyclic diagonal rule forces every carrier element into `N(f)`. For `|A|=1`, this is impossible because every tuple already contains the unique element.

## 4. Enumeration

For carrier size `m>=2`, singleton families contribute `2^m`. A multi-member family is uniquely an unordered set partition of a chosen subset `U subseteq A`, `|U|=s>=2`, into at least two nonempty complement blocks. Therefore

`R_m = 2^m + sum_(s=2)^m binom(m,s) (Bell(s)-1)`.

For family size `k>=2`,

`R_(m,k)=sum_(s=k)^m binom(m,s) Stirling2(s,k)`,

while `R_(m,1)=2^m`.

The first total counts are:

```text
m:   1   2   3   4    5    6     7      8
R:   1   5  15  52  203  877  4140  21147
```

The maximum family size is `m`, attained uniquely by the family of all co-atoms.

## 5. Exact bounded campaign

`experiments/discriminator_core_family_realizability.py` verifies:

- every nonempty antichain for carrier sizes one through four;
- all `1,152` classified families on carriers of sizes two through six;
- `59,524` exact core-membership queries;
- zero minimal-family mismatches;
- zero foreign-output-core mismatches;
- complete family-size distributions;
- rejection of `{A}` on the one-element carrier;
- identical normal and optimized semantics.

Semantic receipt:

`cc2b87c5b94fa645a2d29cd7c72565e9d6320e49e745a32f690362a6fcd77a7f`.

## 6. Morph, ZAG, and Research Kernel posture

The canonical representation is `common core E + unordered partition of A\E`. The family is decoded as `{A\B : B is a partition block}`, with the no-block case representing `{A}`.

ZAG records pairwise-cover sufficiency as `TESTED_ONLY` on the bounded campaign with a generic paper proof; binary insufficiency and one-element full-core realizability are `FAILED`. Research Kernel promotes only the bounded constructor campaign. The generic classification and count theorem remain `UNDER_TEST` until formal/compiler and prior-art gates are complete.

## 7. Next frontier

1. Count the operations realizing each partial-partition family.
2. Classify automorphism groups of arbitrary polynomial operations.
3. Transfer the classification through deterministic table-to-safety reduction.
4. Formalize the constructor and counting theorem in Lean.
5. Search classical discriminator-clone terminology for prior statements.
