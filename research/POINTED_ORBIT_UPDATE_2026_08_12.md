# Frontier update — pointed-orbit factorization, 2026-08-12

This ledger records the next result after `TERM_SYNTHESIS_COMPLEXITY_BOUNDARIES.md`, supersedes the raw-table implementation recommendation in `QUASIPRIMAL_TERM_SAFETY_CSP.md`, and sharpens the quasi-primal paragraph of `SUBPOWER_ROW_LIST_SYNTHESIS.md`: pointed-groupoid cycle consistency is automatic once representative seeds are restricted to their generated subalgebras.

## F2-B1 — exact pointed generated-subalgebra product

**Status:** DERIVED from Pixley's classical quasi-primal preservation theorem; exact bounded oracle passes; novelty unverified; Lean pending.

For a finite quasi-primal algebra `Q` and arity `n>1`, let `P_n(Q)` be the isomorphism classes of pointed generated subalgebras

`(Sg(z);z_1,...,z_n)`.

Choose a representative `r_C` for each class and write `S_C=Sg(r_C)`.

Then

`Term_n(Q) ~= product_(C in P_n(Q)) S_C`.

One seed `a_C in S_C` determines the table on the whole class by unique pointed-isomorphism transport. Seeds from different classes are independent.

**File:** `notes/QUASIPRIMAL_POINTED_ORBIT_FACTORIZATION.md`.

---

## F2-B2 — fixed-quasi-primal sparse list interpolation is linear-time

**Status:** DERIVED algorithm; explicit-input and fixed-algebra qualifications are essential.

For sparse lists `L_z subseteq Q`, pull every list in one pointed class back to its representative seed domain and intersect:

`A_C = intersection_z theta_z^(-1)(L_z intersect Sg(z)).`

The instance is feasible iff every active `A_C` is nonempty.

After constant preprocessing for fixed `Q`, the algorithm is linear in total explicit tuple/list length.

This resolves the quasi-primal half of target 1 in `TERM_SYNTHESIS_COMPLEXITY_BOUNDARIES.md`. The fixed-Mal'cev list-interpolation question remains open in this program.

**Important boundary:** the output is a compact semantic orbit-seed representation. Efficient extraction of an explicit original-signature term expression remains open.

---

## F2-B3 — fixed-domain term safety factorizes by pointed class

**Status:** DERIVED exact reactive specialization.

For a fixed candidate invariant domain `W`, each active observation `z` has an allowed output list

`Safe_W(z) subseteq Q^k`.

A term controller exists iff, in every pointed observation class `C`,

`intersection_(active z in C) theta_z^(-k)(Safe_W(z) intersect Sg(z)^k)`

is nonempty.

Thus the clone-consistency layer is not a generic global CSP after quotienting. It is a family of independent transported-list intersections.

The remaining global problem is domain selection: `W` changes the lists and the feasible-domain family need not be union-closed.

---

## F2-C1 — correction: demi-semi stabilizer filtering is redundant

**Status:** DERIVED simplification; does not change the old theorem's answer.

If an automorphism fixes an observation tuple `z` coordinatewise, it fixes every element of `Sg(z)` because those elements are term values on `z`.

Therefore

`v in Sg(z)^k`

already implies that `v` is fixed by the observation stabilizer.

In `DEMI_SEMIPRIMAL_TERM_SAFETY.md`, the explicit `Fix_z^k` condition can be removed. For demi-semi-primal algebras, the winning-region iteration is the same generated-subalgebra predecessor as in the semi-primal case; global automorphism orbits are needed only to reconstruct one coherent term strategy.

---

## F2-N1 — quotienting does not restore a greatest winning region

**Status:** NEGATIVE boundary preserved.

The no-greatest-region witness becomes one empty class intersection:

- observations `000` and `111` lie in one internal-isomorphism class;
- both locally allow only output `01` in the candidate union;
- pulling the second list back through the swap gives `10`;
- `{01} intersect {10}=empty`.

So the pointed quotient explains the obstruction but does not remove it.

---

## F2-V1 — bounded validation

`experiments/quasiprimal_pointed_orbit_factorization.py` checks:

- Quackenbush arity-2 direct preserving tables = factorized tables = `972`;
- all `512` restricted observation sets `Z`, confirming the product formula for the evaluation subpower `P_Z`;
- all `262144` singleton/undefined partial interpolation instances;
- `27205` list instances;
- Morph minimum-sufficient-abstraction false merges = `0`;
- Morph false splits = `0`;
- pure discriminator arity-3 factorized tables = direct term closure = `24`;
- `282` stabilizer-redundancy element checks;
- the existing no-greatest-region conflict as an empty transported-list intersection.

Normal and optimized Python runs agree.

**Certificate:** `research/MORPH_POINTED_ORBIT_CERTIFICATE.md`.

---

## Ranked next actions

1. Replace the standalone kernel's raw quasi-primal table variables with pointed-class seed variables.
2. Determine fixed-Quackenbush initial-set/domain-selection complexity after factoring out static interpolation.
3. Search older discriminator-algebra terminology for the product/list theorem before making novelty claims.
4. Study explicit term-expression extraction and size.
5. Formalize the product and list-intersection theorems in Lean.
6. Test whether analogous minimum abstractions exist for broader finitely related clones or whether higher-arity relation preservation creates irreducible coupling.
