# Closed-form ocLTL feasibility for atomic ABA equation predicates

**Status:** DERIVED exact theorem; exhaustive bounded validation against all 255 pure-ABA `T_3` supports completed for randomized predicate families; Lean pending; novelty not yet claimed.

This sharpens the support-coded implementation of Asor's ocLTL §5.2 optimization for the important case where the data-predicate set

`Delta={delta_1,...,delta_d}`

consists of atomic Boolean-algebra equations

`delta_i(m,x,y) := [f_i(m,x,y)=0]`.

The result removes the existential `T_3`/support witness entirely and replaces the explicit feasibility table by a small Boolean circuit.

## 1. Three-variable support geometry

Use the pure ABA three-variable presentation `(m,x,y)`.

A complete `T_3` type is a nonempty support on the 8 Venn cells. Arrange the cells as a `4 x 2` matrix:

- rows `r in {0,1,2,3}` are the four `(m,x)` minterms;
- columns `c in {0,1}` are the two `y` minterms.

Let:

- `P_r` be the four support bits encoding the chosen `T_2` type of `(m,x)`;
- `R_c` be the two support bits encoding the chosen `T_1` type of `y`;
- `D_i` be the declared truth value of `delta_i`.

For each equation term `f_i`, let

`A_i subseteq [4] x [2]`

be the set of fine Venn cells where its two-element truth table is 1.

Then, for a candidate support `Q`,

`delta_i(Q)=true iff Q intersect A_i = empty`.

## 2. Available cells

For a given outer assignment `(P,R,D)`, define a fine cell `e=(r,c)` to be **available** iff:

1. its row is selected: `P_r=1`;
2. its column is selected: `R_c=1`;
3. no equation declared true forbids it.

Formally,

`Avail_(r,c)
 := P_r AND R_c AND AND_{i : (r,c) in A_i} NOT D_i.`

Let

`E(P,R,D) = { (r,c) : Avail_(r,c)=true }`.

This is the maximal support compatible with every equation declared true.

## 3. Closed-form feasibility theorem

### Theorem

Assume `P` and `R` are valid nonzero support codes. There exists a complete ABA 3-type `Q` whose row projection is `P`, whose y-column projection is `R`, and whose `Delta` truth vector is exactly `D` iff all of the following hold:

### Row coverage

For every row `r`,

`P_r -> (Avail_(r,0) OR Avail_(r,1)).`

### Column coverage

For every column `c`,

`R_c -> OR_r Avail_(r,c).`

### False-equation witnesses

For every `i`,

`NOT D_i -> OR_{(r,c) in A_i} Avail_(r,c).`

Equivalently,

`Feas_atomic(P,R,D)
 = Valid_P
   AND Valid_R
   AND AND_r [P_r -> OR_c Avail_(r,c)]
   AND AND_c [R_c -> OR_r Avail_(r,c)]
   AND AND_i [NOT D_i -> OR_{e in A_i} Avail_e].`

## 4. Proof: choose the maximal allowed witness

### Necessity

Suppose a witness support `Q` exists.

If `D_i=true`, then `Q` must avoid `A_i`. Hence every edge of `Q` is available.

Because the row projection of `Q` is `P`, every selected row has some edge of `Q`, and therefore some available edge. The same applies to selected columns.

If `D_i=false`, then `f_i!=0`, so `Q` contains at least one cell of `A_i`. Since every cell of `Q` is available, `A_i` contains an available cell.

Thus all three families of conditions are necessary.

### Sufficiency

Assume the displayed conditions. Choose

`Q := E(P,R,D)`,

i.e. make **every available fine cell nonzero**.

- Row coverage makes the row projection of `Q` exactly `P`.
- Column coverage makes the y projection exactly `R`.
- By construction, `Q` avoids every `A_i` with `D_i=true`, so those equations hold.
- For every `i` with `D_i=false`, the false-equation witness condition gives a cell of `Q intersect A_i`, so `f_i!=0`.

`Q` is a nonempty valid ABA support and is therefore realized by an actual tuple `(m,x,y)` in an atomless Boolean algebra.

Hence `Q` is the required complete type.

## 5. The inner ground

The existence problem looks like a search over as many as 255 complete `T_3` types. But for equation predicates, all positive requirements have a monotonic direction:

- equations declared true only **forbid** cells;
- equations declared false only require that **at least one** cell survive inside their term support;
- type projections only require that every selected row/column have at least one surviving cell.

Therefore there is never a reason to choose a delicate sparse witness. The unique maximal allowed support contains every other possible witness, and it works exactly when the local coverage/hitting conditions hold.

This maximal-witness principle is the Noether-style explanation of the closed form.

## 6. Circuit size

There are only 8 fine cells.

Each `Avail_e` is a conjunction of:

- one `P` bit;
- one `R` bit;
- the negations of those `D_i` whose term support contains `e`.

Across all eight cells, the total predicate-incidence work is

`sum_i |A_i| <= 8d`.

The row and column coverage uses a constant number of gates, and the false-equation witness clauses use at most another

`sum_i |A_i| <= 8d`

incidences.

Thus the explicit circuit size is

`O(8d)=O(d)`

for the literal three-variable pure-ABA case.

This replaces the explicit §5.2 outer combination table of size

`|T_2| |T_1| 2^d = 45 * 2^d`

with a circuit linear in `d` for atomic equation predicates.

The proposition count remains Asor's optimized count `4+2+d`; the improvement is in the **feasibility relation representation**, not the number of outer propositions.

## 7. General packed-dimension theorem

Suppose ocLTL's product reduction packs `s` underlying ABA coordinates into each of `m,x,y`.

Then:

- `(m,x)` has `2^(2s)` support cells;
- `y` has `2^s` support cells;
- `(m,x,y)` has `2^(3s)` fine cells.

A full fine cell can be viewed as an edge between one selected `(m,x)` cell and one selected `y` cell.

For atomic equation data predicates, define `Avail_e` exactly as above.

Feasibility is still equivalent to:

1. every selected `(m,x)` cell has an available incident fine cell;
2. every selected `y` cell has an available incident fine cell;
3. every equation declared false has an available fine cell in its term support.

The maximal available support is again a witness whenever these conditions hold.

Therefore the feasibility circuit has size

`O(2^(3s) * d)`

under explicit truth-table/minterm masks.

This is linear in the width of the full support representation and avoids enumerating the

`2^(2^(3s))-1`

possible complete full-state ABA types.

## 8. Interpreted constants

With a finite interpreted-constant set `C`, refine each fine cell by one of the `rho(C)` nonzero constant regions.

The same maximal-witness proof applies independently across those regions, while a false equation may take its witness in any region.

The explicit incidence circuit therefore scales as

`O(rho(C) * 2^(3s) * d)`.

Again the semantic constant-partition rank `rho(C)`, not raw constant count, is the relevant multiplier.

## 9. Relation to ABA_BLOCK_QE.md

This theorem is a projection-with-marginals version of the direct block QE theorem.

- A true equation contributes forbidden fine cells.
- A false equation contributes a nonzero/hitting requirement.
- The fixed `T_2` and `T_1` projections add row/column coverage requirements.

The same maximal-allowed-support witness proves sufficiency.

## 10. Scope boundary

This closed form is **not** asserted for arbitrary data subformulas `delta_i`.

If a `delta_i` is an arbitrary Boolean combination of equations after QE, then declaring its truth value can impose a non-monotone Boolean condition on the support. The maximal available support need not preserve that truth value.

For arbitrary `Delta`, the support-BDD/QBF feasibility projection in `ABA_OCLTL_SUPPORT_ENCODING.md` remains the general exact route.

The compiler should therefore use a portfolio:

1. closed-form atomic-equation feasibility when applicable;
2. possibly extend the closed form to larger monotone/unate predicate classes after proof;
3. otherwise fall back to symbolic support projection;
4. retain explicit type enumeration as a differential oracle for bounded development tests.

## 11. Validation completed

A private exhaustive checker compared the closed form against explicit enumeration of all 255 nonzero `T_3` supports for randomized atomic-equation predicate families, across all:

- 15 nonzero `P` support codes;
- 3 nonzero `R` support codes;
- truth patterns `D` for tested predicate counts.

No divergence was found. A reproducible repository checker is committed separately.

## 12. Next theorem target

Characterize the largest syntactic/semantic class of ABA data predicates for which a canonical extremal witness (maximal or minimal support) decides §5.2 feasibility.

Promising classes to test, not yet claimed:

- conjunctions of atomic equations;
- conjunctions of equation/inequation literals;
- unate support formulas;
- Horn or dual-Horn support formulas;
- bounded-incidence CNF classes.

The falsification test is immediate: find two feasible witnesses whose union changes the required data truth vector. Any class lacking closure under the maximal-witness operation cannot use this theorem unchanged.
