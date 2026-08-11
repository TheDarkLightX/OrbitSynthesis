# Support Booleanization of atomless Boolean algebra

**Status:** DERIVED semantic translation for the pure ABA signature `{0,1,meet,join,complement}`; prototype implementation pending in this branch; Lean pending.

This note gives a symbolic alternative to explicit complete-type enumeration and to DNF-first quantifier elimination.

It begins with the same support invariant as the earlier notes, but changes the computational object: instead of enumerating individual supports, represent **sets of supports as Boolean functions of support bits**.

## 1. Support variables

For `k` Boolean-algebra variables, let

`U_k = {0,1}^k`

be the `2^k` minterm cells.

For a tuple `a=(a_1,...,a_k)` in an atomless Boolean algebra, define support bits

`z_v(a) = 1  iff  C_v(a) != 0`,  for `v in U_k`.

The support vector

`z(a) in {0,1}^{2^k}`

is never all-zero, and every nonzero support vector is realizable in ABA.

Thus the complete type space is represented not by `2^(2^k)-1` opaque states, but by the nonzero assignments to only `2^k` Boolean variables.

This does not remove worst-case complexity: an arbitrary set of types is an arbitrary Boolean function of those `2^k` support variables. But it opens the door to compact symbolic representations such as ROBDDs, ZDDs, CNF, or other Boolean DAGs.

## 2. Atomic formulas become very simple Boolean formulas

Let `f(x_1,...,x_k)` be a simple Boolean function (no interpreted constants beyond 0 and 1). Let

`A_f subseteq U_k`

be the set of minterm cells on which the corresponding two-element-BA truth function is 1.

Then

`f(a)=0  iff  for every v in A_f, z_v(a)=0`.

So the support-level translation is

`hat(f=0) = AND_{v in A_f} NOT z_v`.

Likewise

`hat(f!=0) = OR_{v in A_f} z_v`.

Extend `hat(.)` homomorphically over logical `AND`, `OR`, and `NOT`.

### Theorem 1 — quantifier-free correctness

For every quantifier-free pure-ABA formula `phi(x_1,...,x_k)` and every ABA tuple `a`,

`ABA |= phi(a)  iff  hat(phi)(z(a)) = true`.

**Proof.** Atomic correctness follows from disjoint minterm normal form. Logical connectives are immediate by induction on formula structure.

## 3. Adding one BA variable is a local ternary refinement

Add a new Boolean-algebra variable `y`.

Every old minterm cell `v in U_k` splits into two fine cells

`(v,0)` and `(v,1)`.

Let their nonzero bits be

`w_(v,0), w_(v,1)`.

The old coarse support bit satisfies

`z_v = w_(v,0) OR w_(v,1)`.

Conversely, atomlessness gives every allowed local refinement:

- if `z_v=0`, the only possibility is `(0,0)`;
- if `z_v=1`, the possible fine patterns are `(1,0)`, `(0,1)`, `(1,1)`.

Different coarse minterm cells can be refined independently.

Therefore the complete extension relation is the propositional formula

`Ext_k(z,w) = AND_{v in U_k} [ z_v <-> (w_(v,0) OR w_(v,1)) ]`.

This is the support-level form of the ABA extension theorem.

## 4. Quantifier elimination becomes propositional abstraction

Let `phi(x_1,...,x_k,y)` be any formula whose support translation over the `2^(k+1)` fine cells is `hat(phi)(w)`.

### Theorem 2 — existential projection

On nonzero coarse support assignments,

`hat(exists y. phi)(z)
 = exists w. [ Ext_k(z,w) AND hat(phi)(w) ].`

Here `exists w` is ordinary propositional existential quantification over the `2^(k+1)` fine support bits.

### Proof

**Forward.** If some BA element `y` makes `phi(a,y)` true, its fine support `w=z(a,y)` satisfies the extension relation and, by Theorem 1 / induction on inner quantifiers, satisfies `hat(phi)`.

**Backward.** Suppose a fine support vector `w` satisfies `Ext_k(z(a),w)` and `hat(phi)(w)`. For each nonzero coarse minterm element `C_v(a)`, the requested fine pattern is one of left-only, right-only, or both. Atomlessness lets us split every coarse cell accordingly, independently. The joins of the chosen `y=1` pieces define an element `y` realizing exactly `w`. Correctness of the support translation then gives `phi(a,y)`.

### Universal quantification

Similarly,

`hat(forall y. phi)(z)
 = forall w. [ Ext_k(z,w) -> hat(phi)(w) ].`

Equivalently use negation plus existential abstraction.

## 5. Consequence: an alternative quantifier-elimination engine

For the pure ABA theory:

1. compile a quantifier-free matrix to a Boolean DAG over support bits;
2. eliminate an innermost BA variable by conjoining the local `Ext_k` relation and existentially abstracting the fine bits;
3. repeat outward;
4. retain the resulting Boolean DAG instead of expanding it into a BA formula unless a textual formula is required.

This is exact because every nonzero support assignment is realizable and every extension satisfying the local OR constraints is realizable.

Asor's GS presentation eliminates an existential after first converting the formula under that quantifier to logical DNF and then processing clauses (`Guarded Successor`, §2.2). The support-Booleanization route is therefore a genuinely different **representation strategy**, even though it computes the same first-order semantics.

It should be compared experimentally rather than assumed superior.

## 6. Why BDD/ZDD style representations are natural here

The support translation has unusually local structure:

- an atomic equation is a conjunction of negated support bits;
- an atomic inequation is a disjunction of support bits;
- the extension relation factors as one three-variable constraint per coarse cell;
- Boolean connectives are native symbolic operations;
- quantification is Boolean existential abstraction;
- equality of reduced canonical Boolean representations gives a direct fixed-point stopping test.

Classical symbolic model checking uses BDDs precisely to avoid explicit state enumeration and to compute temporal fixed points symbolically. Burch-Clarke-McMillan-Dill-Hwang (LICS 1990 / Information and Computation 1992) established this paradigm for finite-state systems.

OrbitSynthesis's new question is whether the ABA support translation produces BDD variable orderings and transition relations compact enough to make that technology effective for Tau-style infinite-data synthesis.

## 7. State-space comparison

For `k` BA variables:

- explicit complete types: `2^(2^k)-1` states;
- support-symbolic representation: `2^k` Boolean support variables.

Examples:

- `k=3`: 255 types versus 8 support variables;
- `k=4`: 65,535 types versus 16 support variables;
- `k=5`: 4,294,967,295 types versus 32 support variables.

A Boolean function of 32 variables can of course still require an enormous BDD in the worst case. The comparison is a representation opportunity, not a polynomial-time theorem.

## 8. Direct fixed-point synthesis in support space

Suppose a safety winning region is represented by a support-level Boolean function `W(z)`. A controllable-predecessor step has first-order form schematically

`CPre(W)(state) = forall input. exists output,next. Step(...) AND W(next)`.

Under support Booleanization, the BA quantifiers can be compiled into repeated local extension relations and propositional abstraction. The next winning approximation is therefore another Boolean function over state-support bits.

The greatest fixed point can be computed symbolically until the canonical representation stops changing.

This gives a concrete implementation path for issue #2:

`ABA formula -> support Boolean DAG -> symbolic CPre -> symbolic fixed point`.

It avoids both:

- explicit enumeration of all complete types; and
- mandatory materialization of logical DNF at each ABA quantifier.

## 9. What must be tested before promotion

### Correctness

- exhaustive comparison with support enumeration for small arities;
- differential comparison with Tau QE for generated pure-ABA formulas;
- formal proof of the support-extension theorem.

### Representation size

Compare at least:

- ROBDD with several variable orderings;
- ZDD for sparse support families;
- CNF/SAT-style quantified elimination;
- explicit type bitsets;
- Tau's current normalized formula representation.

The classical symbolic-model-checking literature warns that BDD variable ordering can make or break the method, and SAT/CNF representations can outperform BDDs on some fixed-point problems. The project should benchmark representations rather than canonize one.

### Scope

This note is for the pure ABA signature. Asor's interpreted-constant setting contains additional structure. Extending support Booleanization to finitely many interpreted constants requires refining the support invariant to record the relevant constant regions / atom information; do not assume the pure-ABA proof transfers unchanged.

## 10. Next mathematical questions

1. What is the smallest support-bit invariant sufficient in the presence of finitely many interpreted constants?
2. Can Asor's Hall-marriage QE conditions be recovered as a compact projection rule on the refined support representation?
3. Which variable ordering minimizes the BDD for `Ext_k` and for common Tau predecessor operators?
4. Which formula classes have provably polynomial-size BDDs under the natural minterm-cell order?
5. Do ZDDs exploit the sparse-support regime better than BDDs while preserving efficient quantifier projection?
6. Can support Booleanization be generalized from ABA to other omega-categorical structures using orbit-incidence bits and effective extension relations?
