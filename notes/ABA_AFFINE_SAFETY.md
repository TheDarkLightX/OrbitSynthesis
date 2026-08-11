# Affine/XOR ABA safety via Gaussian elimination

**Status:** DERIVED exact source-level algorithm; bounded explicit-cell falsification passed for thousands of random small games. Linear algebra itself is classical. The synthesis contribution under investigation is the exact ABA cell-label reduction plus the closure/dimension bound for this protected Tau fragment.

`ABA_CELL_LABEL_SYMBOLIC_GAME.md` shows that the zero/equation phase of an ABA game is an ordinary Boolean game on the labels of Venn cells. When all zero equations are affine/XOR-linear in those label bits, the game has substantially more structure than a generic Boolean circuit.

## 1. Affine cell-label Step equations

Let state, environment, and next-cell labels be

`s in F_2^d`,

`i in F_2^e`,

`n in F_2^d`.

Suppose the conjunction of Step zero equations is equivalent, on cell labels, to the affine linear system

`A_s s + A_i i + A_n n = c`

over `F_2`.

This covers Tau terms built from XOR/parity and constants after equations are normalized to zero.

Suppose the current target set of next cells is an affine set

`T = {n : B n = b}`.

The target may be all of `F_2^d` when B has no rows.

## 2. One controllable predecessor is affine

A state s belongs to the cell predecessor iff

`forall i exists n:
   A_s s + A_i i + A_n n = c
   AND
   B n = b.`

Stack the next-state equations:

`M_n := [ A_n ; B ]`,

`M_s := [ A_s ; 0 ]`,

`M_i := [ A_i ; 0 ]`,

`r_0(s) := [ c + A_s s ; b ]`.

Then the quantified condition is

`forall i exists n. M_n n = [c;b] + M_s s + M_i i`.

## 3. Left-nullspace criterion

Let L be any full-row-rank matrix whose row space is the left nullspace of M_n:

`row(L) = ker(M_n^T)`.

Classical linear algebra gives

`r in im(M_n)  iff  L r = 0`.

Therefore every environment value i is controllable iff

`L([c;b] + M_s s + M_i i)=0`

for every i.

This separates into:

1. **environment-direction condition**

   `L M_i = 0`;

2. **state condition**

   `L M_s s = L [c;b]`.

### Theorem 1 — affine predecessor formula

If `L M_i != 0`, then

`Pre(T)=empty`.

If `L M_i = 0`, then

`Pre(T)
 = {s : (L M_s)s = L[c;b]}`,

an affine subspace/coset of `F_2^d`.

Thus the cell predecessor of an affine target under an affine Step relation is affine or empty.

## 4. Permanent affine safety remains affine

Let the permanent zero Safe condition be

`S_0 = {s : C s = d_0}`.

The safety operator is

`F(T)=S_0 intersect Pre(T)`.

Intersection of affine sets is affine or empty. Therefore every greatest-fixed-point approximation

`T_0=F_2^d`,

`T_(k+1)=S_0 intersect Pre(T_k)`

is affine or empty.

No arbitrary subset of the `2^d` cell arena is ever generated.

## 5. Dimension bound on fixed-point iterations

A nonempty affine subset of `F_2^d` has a dimension between 0 and d.

If two nonempty affine sets satisfy

`T' proper-subset T`,

then

`dim(T') < dim(T)`.

Equal-dimensional affine subspaces/cosets cannot be proper subsets of one another.

Hence:

### Theorem 2 — linear iteration bound

The equation-only affine safety greatest fixed point has at most

`d+1`

strict decreases, counting a possible final transition from a singleton affine set to empty.

If the winning set remains nonempty, there are at most d strict decreases.

Compare this with:

- explicit cell-state count `2^d`;
- complete ABA state-type count `2^(2^d)-1`.

The affine invariant collapses the semantic iteration bound from doubly exponential complete-type space to linear in the number of BA state coordinates.

## 6. Source-level algorithm

Represent every affine set by a row-reduced linear system.

For each safety iteration:

1. stack Step's A_n with the current target matrix B;
2. compute a basis L for the left nullspace of the stacked next matrix;
3. test `L M_i = 0`;
4. if it fails, predecessor is empty;
5. otherwise emit the affine state equations `L M_s s = L[c;b]`;
6. stack these equations with permanent Safe equations;
7. row-reduce to canonical form;
8. compare canonical affine systems for fixed-point equality.

All operations are Gaussian elimination over `F_2`.

For fixed source matrices, standard incremental/nullspace updates can reduce repeated work further, but the basic polynomial algorithm is already exact.

## 7. Complexity

Let p be the number of Step equations and r the number of equations describing the current affine target.

A straightforward iteration performs Gaussian elimination on matrices with roughly

`p+r` rows and O(d+e) columns.

There are at most d+1 strict iterations.

Thus equation-only affine safety is polynomial in the source matrix dimensions and d, rather than exponential in the cell count.

The exact polynomial depends on the chosen GF(2) linear-algebra implementation; bit-packed Gaussian elimination is the natural engineering baseline.

## 8. Relation to Tau syntax

Tau's term-level XOR operator `^` is exactly the Boolean symmetric-difference/XOR operation. The pinned demos include XOR-heavy recurrence examples, and the compact LFSR lower-bound family in OrbitSynthesis is written naturally in this syntax.

The affine fast path should recognize equations whose normalized cell-label truth functions are affine without first expanding them to CNF.

A safe recognizer can traverse the term DAG:

- constants and variables are affine;
- XOR of affine terms is affine;
- complement toggles the constant coefficient;
- AND/OR of nonconstant affine terms generally leave the affine class and should terminate this fast path unless simplification proves the result affine.

## 9. Why this does not contradict the LFSR lower bound

`ABA_LFSR_LOWER_BOUND.md` uses an affine/permutation Step relation but adds a **positive Safe disequation**.

The zero/equation safety arena is trivial/easy; the exponential orbit occurs in positive obligations.

Theorem 2 applies only to the equation-only zero phase.

This cleanly separates:

- affine zero-safety: polynomial Gaussian elimination, <=d+1 strict decreases;
- positive support obligations: potentially exponential orbit/output behavior even under affine dynamics.

## 10. Positive affine obligations remain structured

If a positive state disequation term h is affine on cell labels, its witness-cell mask

`{s : h(s)=1}`

is an affine hyperplane/coset (or empty/all in degenerate cases).

By Theorem 1, the robust predecessor of an affine target under affine Step remains affine or empty.

Therefore every individual positive-obligation orbit in the Bekić decomposition can be stored as a sequence of canonical affine systems rather than explicit `2^d` masks.

This does **not** bound the number of distinct orbit members: the LFSR singleton orbit already has `2^d-1` members, each represented compactly.

It does make each orbit step polynomial and supports algebraic cycle acceleration for special transition relations.

## 11. Stronger special cases

### Deterministic affine next map

If Step determines

`n = M s + N i + c`

and environment independence/robustness conditions reduce the target transform to an affine inverse image, use direct matrix preimages.

### Linear permutation

If the next-state map is a linear permutation, obligation dynamics are group/orbit dynamics under GL(d,2). Use cycle/minimal-polynomial machinery rather than iterative QBF.

The primitive-LFSR family is the flagship example.

## 12. Bounded validation

An independent explicit-cell test generated random affine Step equation systems and random affine Safe systems for `d=1..4`.

For 4,000 random games:

- every explicit `Pre(T)` of an affine T was affine or empty;
- every safety approximant was affine or empty;
- every chain respected the `d+1` strict-decrease bound.

This is bounded falsification, not the proof.

## 13. Backend consequence

Add the following priority before generic treewidth/BDD handling:

`affine zero equations`

-> compile coefficient matrices

-> Gaussian-elimination safety backend

-> retain positive affine obligations as affine descriptors when present

-> use permutation/linear-orbit accelerator when detected

-> fall back to structured QBF/d-DNNF or general Tau machinery when non-affine term structure appears.

This is a theorem-backed backend class whose complexity is controlled by source algebra rather than by complete-type count.
