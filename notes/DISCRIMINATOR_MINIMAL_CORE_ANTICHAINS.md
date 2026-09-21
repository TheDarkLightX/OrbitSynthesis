# Binary minimal-core antichains in the three-element discriminator algebra

**Status:** structural obstruction derived from the classical internal-isomorphism characterization; exact finite classification and counts exhaustively checked; Lean abstraction layer pending compiler replay; publication novelty unverified.

## 1. Question

For the pure discriminator algebra

`D_3=({0,1,2};d)`,

where `d(x,y,z)=z` if `x=y` and `d(x,y,z)=x` otherwise, every carrier subset is a closed parameter core.

Given a binary operation `f`, let

`MinCore(f)`

be the inclusion-minimal cores `C` for which `f` is a `C`-polynomial operation. Since polynomial languages grow with the parameter core, `MinCore(f)` is an antichain in the Boolean lattice `P({0,1,2})`.

There are 20 antichains in the three-element Boolean lattice, 19 of them nonempty. Which nonempty antichains occur as `MinCore(f)` for a binary table?

## 2. Pair-collapse theorem

### Theorem

For distinct `a,b` in `D_3` and every arity `n>1`,

`Pol_{a}^n(D_3) intersection Pol_{b}^n(D_3) = Term_n(D_3)`.

### Proof

Let `c` be the third carrier element and suppose `f` is polynomial over both singleton cores.

A `{a}`-polynomial operation preserves every automorphism fixing `a`; in particular it commutes with the transposition swapping `b` and `c`. A `{b}`-polynomial operation commutes with the transposition swapping `a` and `c`. Those two transpositions generate the full symmetric group `S_3`. Hence `f` is equivariant under every global permutation.

The `{a}` language preserves every subalgebra containing `a`, while the `{b}` language preserves every subalgebra containing `b`. Together these cover all two-element subsets. They also preserve the singleton subsets `{a}` and `{b}`; full permutation equivariance transports singleton preservation to `{c}`. Thus `f` preserves every nonempty subalgebra.

Every internal isomorphism of a pure discriminator algebra is a bijection between subsets, and every such bijection on a three-element carrier extends to a global permutation. If `phi:S->T` is an internal isomorphism and `z in S^n`, then subalgebra preservation gives `f(z) in S`, while global equivariance gives

`f(phi z)=phi(f(z))`.

Therefore `f` preserves every internal isomorphism. The classical quasi-primal characterization for arity greater than one makes `f` a parameter-free term operation. The reverse inclusion is immediate.

### Consequence

If two distinct singleton cores are feasible for one operation, the empty core is already feasible. Therefore no inclusion-minimal feasible-core antichain can contain two distinct singleton cores.

This rules out exactly four nonempty antichains:

- `{{0},{1}}`;
- `{{0},{2}}`;
- `{{1},{2}}`;
- `{{0},{1},{2}}`.

## 3. Exact realizability classification at binary arity

Up to relabeling by `S_3`, the 19 nonempty antichains have nine symmetry types. Exactly seven types occur. The two missing symmetry types are represented by

- `{{0},{1}}`;
- `{{0},{1},{2}}`.

The following seven tables realize all remaining types. Matrices are indexed by row `x` and column `y`.

| Minimal-core type | Representative table |
|---|---|
| `{empty}` | `[[0,0,0],[1,1,1],[2,2,2]]` |
| `{{0}}` | `[[0,0,0],[0,0,0],[0,0,0]]` |
| `{{0,1}}` | `[[0,0,0],[0,0,0],[0,0,1]]` |
| `{{0,1,2}}` | `[[0,0,0],[0,2,0],[0,0,1]]` |
| `{{0},{1,2}}` | `[[0,0,0],[0,1,1],[0,2,2]]` |
| `{{0,1},{0,2}}` | `[[0,0,0],[0,0,0],[0,0,2]]` |
| `{{0,1},{0,2},{1,2}}` | `[[0,0,0],[0,1,1],[0,1,2]]` |

Relabeling the carrier generates all 15 realized antichains. The sixth row is the fixed-domain no-least-core witness from `FIXED_DOMAIN_PARAMETER_CORE_ANTICHAIN.md`.

## 4. Exact frequency census

`experiments/discriminator_minimal_core_antichains.py` checks all `3^9=19683` binary tables.

The exact minimal-family frequencies are:

| Minimal family | Count |
|---|---:|
| `{empty}` | 2 |
| one singleton core `{a}` | 16 for each `a` |
| one two-element core `{a,b}` | 2800 for each pair |
| the full core | 9683 |
| `{ {a}, {b,c} }` | 6 for each relabeling |
| two two-element cores sharing one element | 496 for each pair |
| all three two-element cores | 44 |

The totals sum to `19683`.

The oracle also checks directly that, for each distinct pair `a,b`, the intersection of the two singleton polynomial languages contains exactly the two parameter-free binary term tables.

## 5. ZAG falsification record

- Candidate: every nonempty antichain is realizable. **FAILED** on the four singleton-family obstructions.
- Candidate: multiple minimal cores are impossible. **FAILED** by 1,550 tables with a multi-member inclusion-minimal family.
- Candidate: no minimal family contains two distinct singleton cores. **DERIVED and exhaustively checked**.
- Candidate: every other nonempty antichain is realized at binary arity. **TESTED_ONLY** by the complete finite census and explicit representatives.

The count `1550` here concerns inclusion-minimal feasible cores: it includes the 18 mixed families `{ {a}, {b,c} }`. The earlier count `1532` concerns multiplicity at the minimum generator rank only. The distinction is intentional.

## 6. Morph interpretation

The correct abstract output for one target is the full inclusion-minimal feasible-core antichain, with generator rank and reconstruction witnesses attached. A minimum-rank antichain is a useful cost projection, but it can discard a larger-rank core incomparable by language inclusion, as in the mixed family `{{a},{b,c}}`.

Thus two different consumers require two different exact summaries:

- language-minimality queries require `inclusion_minimal`;
- minimum-budget queries require `minimum_rank`.

Neither summary should silently replace the other.

## 7. Next frontier

1. Generalize the pair-collapse theorem from `D_3` to pure discriminator algebras of arbitrary finite size.
2. Determine which antichains of `P(A)` are realizable at a fixed arity for `D_m`.
3. Find asymptotic bounds on minimal-family multiplicity.
4. Use the exact graph-game reduction to transfer these realizability constraints to fixed-domain reactive synthesis.
