# Quasi-primal list-constrained subpower intersection

**Status:** derived algorithmic theorem, 2026-08-14.  The generated-subpower
representation and quasi-primal interpolation theorem are classical.  The
component criterion, witness/obstruction API, and reactive interpretation are
implemented and independently reconstructed.  Lean and external review remain
pending; novelty is **UNKNOWN**.

## 1. Problem

Fix a finite algebra `A`.  The input consists of nonempty generators

```text
g^1,...,g^m in A^n
```

and one arbitrary unary list `L_i subseteq A` for each coordinate.  Decide

```text
Sg_(A^n)({g^1,...,g^m})
  intersect
(L_1 x ... x L_n)
!= empty.
```

Singleton lists recover ordinary subpower membership.  The product of arbitrary
lists need not be a subalgebra, so this is not merely standard Subpower
Intersection.

## 2. Evaluation rows

Transpose the generators.  Coordinate `i` gives the row

```text
z_i=(g^1_i,...,g^m_i) in A^m.
```

Every generated vector is

```text
(t(z_1),...,t(z_n))
```

for one `m`-ary term `t`.  Repeated rows represent repeated constraints on the
same table entry.

Assume from now on that `A` is finite quasi-primal.

## 3. Row groupoid

Create a graph on the distinct rows.  For every internal isomorphism

```text
phi:B -> C
```

and listed row `z in B^m`, add

```text
z --phi--> phi(z)
```

when the image is also listed.

A term value at `z` lies in `Sg_A(z)`, and every edge forces

```text
t(phi(z))=phi(t(z)).
```

Transport is path-independent.  The row coordinates generate `Sg_A(z)`;
therefore an internal automorphism fixing the row fixes every generator and is
the identity on the generated subalgebra.

## 4. Exact criterion

For each connected component choose a representative `z`.  For every

```text
a in Sg_A(z)
```

transport `a` through the component.  It is acceptable exactly when every
transported value belongs to every coordinate list attached to its row.

### Theorem

The list-constrained generated subpower is nonempty iff every row-groupoid
component has at least one acceptable representative value.

**Necessity.**  Any term preserves generated subalgebras and internal
isomorphisms, so its value at a representative is an acceptable candidate.

**Sufficiency.**  Choose one candidate in every constrained component and
transport it.  Complete all other components by a projection.  The resulting
total function preserves generated subalgebras and all internal isomorphisms,
so quasi-primal interpolation makes it a term.

## 5. Complexity and certificates

For fixed `A`, carrier size and the internal groupoid are constants.  With `n`
coordinates and `m` generators, the direct implementation is polynomial and
linear in the explicit generator matrix up to algebra-dependent constants.

A positive result contains:

- the generated evaluation vector;
- one chosen value per component; and
- every transported row value.

A negative result contains one component and, for every representative
candidate, the coordinate positions rejecting its transported values.  This
is a compact nogood for incremental domain search.

## 6. Controller hierarchy

- **Primal:** all row choices are independent.
- **Semi-primal:** only generated-subalgebra membership remains.
- **Demi-semi-primal:** components are global-automorphism orbits with
  stabilizer consistency.
- **Quasi-primal:** genuinely partial internal isomorphisms couple rows, but
  each component is still solved by testing at most `|A|` values.

Thus fixed-domain list synthesis is tractable for every fixed finite
quasi-primal algebra even though variable-domain optimization may remain hard
and a greatest winning domain may fail to exist.

## 7. Boundary with broader algebra classes

Easy ordinary SMP does not imply easy list intersection.
`F3_ROW_LIST_REACTIVE_HARDNESS.md` gives a fixed three-element module with
polynomial-time SMP but NP-complete binary-list interpolation.

The quasi-primal proof relies on the exact internal-isomorphism
characterization and does not settle general cube-term or Mal'cev algebras.
The broader list-constrained generated-subpower classification remains open.

## 8. Implementation and evidence

Implementation:

```text
src/orbitsynthesis/subpower_lists.py
```

The solver returns `ListSubpowerWitness` or `ListSubpowerObstruction`; a
separate verifier checks the finite groupoid certificate.

The primary audit compares the solver with explicit generated-subpower closure
on the pure three-element discriminator and Quackenbush's `Q`.  It exhausts

```text
(generator count, coordinate count)
=(1,1),(1,2),(1,3),(2,1),(2,2)
```

with every nonempty coordinate-list assignment: `27,510` exact instances.

An independent no-import implementation checks `14,280` complementary
instances, including all `13,755` exact `Q` cases.

The load-bearing mutation uses generator `(0,1)` and lists `{0} x {0}`.  Both
rows are locally admissible, but the internal complement couples their values;
the exact solver rejects and returns a two-position obstruction.

## 9. Practical use

For a fixed candidate invariant domain:

```text
observation rows
  -> safe successor lists
  -> groupoid components
  -> compatible table or component obstruction
  -> original-signature DAG
  -> verification receipt.
```

Next work:

1. learn component obstructions during maximal-domain search;
2. minimize nogoods;
3. support vector-valued outputs without repeating groupoid analysis;
4. benchmark against explicit closure and generic CSP;
5. investigate broader cube-term and Mal'cev list languages.
