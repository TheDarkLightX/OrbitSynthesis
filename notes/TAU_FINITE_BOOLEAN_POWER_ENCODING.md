# Encoding Boolean powers of arbitrary finite algebras inside Tau's atomless Boolean algebra

**Status:** DERIVED definitional encoding / implementation theorem. Finite truth-table bit encoding and Boolean-power semantics are standard ingredients; novelty is not claimed for the encoding itself. The point is its exact composition with the direct synthesis results in this repository.

Let M be any finite algebra with

`|M|=n>=2`,

and let B be a Boolean algebra, in particular the countable atomless BA used by Tau/Asor.

An element of the Boolean power M[B] is a locally constant M-valued function on the Stone space of B.

This note shows that M[B] can be represented using only ordinary B-valued variables and Boolean terms.

## 1. Binary code for local M-values

Let

`d = ceil(log2 n)`

and choose an injection

`code : M -> {0,1}^d`.

A candidate encoded M[B] element is a d-tuple

`b=(b_1,...,b_d) in B^d`.

At each Stone point xi, the Boolean tuple b has a local binary valuation

`q(xi) in {0,1}^d`.

We want every local valuation to be one of the n selected M-codes.

## 2. One ABA equation enforces code validity

For every bit vector

`q in {0,1}^d`,

let `C_q(b)` be its Boolean Venn minterm.

Let

`Unused = {0,1}^d \ code(M)`.

Define the bad-code term

`Bad_M(b) := OR_{q in Unused} C_q(b)`.

Then

`Bad_M(b)=0`

iff no Stone point carries an unused code.

If n is a power of two, `Unused` is empty and validity is automatic.

## 3. Exact representation theorem

### Theorem 1

The set

`Enc_M(B) := {b in B^d : Bad_M(b)=0}`

is in canonical bijection with the underlying set of M[B].

### Forward map

Given `f in M[B]`, define bit j by the clopen union

`b_j = OR { fiber_f(m) : code(m)_j=1 }`.

At each point, b carries exactly code(f(xi)), hence satisfies validity.

### Reverse map

Given valid b, the Venn cells

`C_code(m)(b)`

form an M-indexed clopen partition of 1 after empty cells are allowed. Label each point by the unique m whose cell contains it. This is an element of M[B].

The constructions are inverse.

## 4. Every finite operation becomes ordinary BA terms

Let

`o : M^r -> M`

be any fundamental operation of M.

For output code bit j define the finite Boolean truth function

`F_(o,j) : ({0,1}^d)^r -> {0,1}`

on valid input codes by

`F_(o,j)(code(m_1),...,code(m_r))
 = code(o(m_1,...,m_r))_j`.

Extend F arbitrarily to invalid code tuples; invalid tuples never occur on valid encoded inputs.

Every Boolean truth function has a Boolean term, so choose a BA term

`t_(o,j)`

for F_(o,j).

### Theorem 2

Under the bijection of Theorem 1, the Boolean-power operation o is represented coordinatewise by

`out_j = t_(o,j)(input code bits)`.

The output automatically satisfies `Bad_M(out)=0` on valid inputs.

Hence M[B] is a definable algebra inside the finite power B^d.

## 5. Compactness relative to one-hot representation

The direct partition representation of an M[B] value uses n Boolean regions

`e_m`,

with pairwise-disjointness and join-1 constraints.

Binary encoding uses only

`ceil(log2 n)`

BA variables per M-valued datum.

The price is that fundamental operations become Boolean circuits on encoded bits rather than simple relabelings of one-hot regions.

This is the ordinary binary-vs-one-hot tradeoff, now applied pointwise over the Boolean skeleton.

## 6. Equality and inequation

Two encoded values b,c are equal in M[B] iff all code bits are equal:

`AND_j [b_j=c_j]`.

In BA equation form this can be squeezed to

`OR_j (b_j XOR c_j) = 0`.

They are unequal as Boolean-power elements iff they differ somewhere:

`OR_j (b_j XOR c_j) != 0`.

Thus the equation/inequation support semantics used throughout OrbitSynthesis is available directly in the encoding.

## 7. Arbitrary local relations

Let

`R subseteq M^r`

be any finite relation.

Compile its Boolean characteristic function on valid code tuples.

### Universal/pointwise occurrence

To require R at **every** Stone point, build the Boolean term whose local truth value is 1 exactly outside R and require

`Bad_R(inputs)=0`.

### Existential/nonzero occurrence

To require that R holds on **some nonzero region**, build the term whose truth value is 1 exactly on R and require

`Hit_R(inputs)!=0`.

Therefore finite relational constraints can also be embedded into Tau's ABA equations/inequations.

## 8. Controller compilation does not require primality at the Tau representation layer

Suppose the finite local safety game produces an arbitrary positional strategy

`sigma : M^(k+p) -> M^k`.

Even if sigma is not a term operation of the original algebra M, its encoded output bits are ordinary finite Boolean functions of the encoded state/input bits.

Hence each output bit can be compiled to a BA term.

### Corollary 3

When M[B] is implemented through its BA code, **every finite positional local strategy has an ordinary Tau/BA term implementation**, regardless of whether M is primal.

Primality is only required if the controller must be expressed using terms of M's *original signature* rather than the Boolean representation substrate.

This sharply separates algebraic expressibility from implementation expressibility.

## 9. Composition with the safety-lifting theorem

`FINITE_BOOLEAN_POWER_SAFETY.md` proves that equation-only causal safety over M[B] reduces exactly to the finite local game on M^k.

Combining it with Corollary 3 gives a complete implementation path:

1. compile the Tau-level finite-algebra operations/relations to BA bit terms;
2. solve the local finite safety game on M^k;
3. synthesize a finite positional strategy sigma;
4. compile sigma's code bits to BA terms;
5. run those terms pointwise over the atomless Boolean-power data.

No complete omega-categorical type enumeration is required in this fragment.

## 10. Composition with clause/hypergraph synthesis

For equation+inequation clauses over an atomless Boolean skeleton:

- local M^k labels are the support vertices;
- equations define allowed local labels/triples;
- inequations define hit sets;
- `FINITE_BOOLEAN_POWER_SAFETY.md` transfers the exact hypergraph recurrence.

The maximal-response support strategy may request several local M output labels inside one nonzero joint region. Tau's underlying atomless BA is exactly the splitting substrate needed to realize those labels.

The final output consists of d BA bit regions reconstructed from the split local labels.

## 11. Three-valued example

For n=3:

`d=2`.

Choose codes, e.g.

- `0 -> 00`
- `1 -> 01`
- `2 -> 10`

and forbid `11` by

`b_1 AND b_2 = 0`

(up to bit-order convention).

Every ternary operation table becomes two Boolean functions of two bits per argument.

Thus a ternary Boolean-power data stream costs only two atomless-BA streams in Tau.

For k local ternary state variables, the semantic local support universe has

`3^k`

labels rather than the raw `2^(2k)=4^k` binary Venn labels; the validity equation removes all tuples containing unused `11` codes.

## 12. General code-space support geometry

For k M-valued variables, there are

`n^k`

valid local labels in M^k.

An atomless Boolean power can realize every nonempty subset of these labels as a joint support.

If M is primal/rigid enough that local labels are first-order fixed, this yields the exact complete-type count

`2^(n^k)-1`

from `PRIMAL_BOOLEAN_POWER_GEOMETRY.md`.

For a general M with local automorphisms, the BA encoding remains exact operationally but may over-refine the orbit/type quotient. Do not equate encoded support states with complete first-order types without analyzing Aut(M).

## 13. Complexity tradeoff

The representation is logarithmic in n per data value, but arbitrary operation/strategy truth tables can have worst-case circuit/DNF size exponential in the number of local arguments.

Use the same portfolio principle as elsewhere:

- truth-table/minterm masks for small local arity;
- ROBDD/AIG/circuit representations when truth tables grow;
- one-hot encoding when operations are sparse and relabeling dominates;
- binary encoding when stream count is the bottleneck.

The theorem is an exact encoding, not a guarantee that binary representation is always fastest.

## 14. Tau engineering implication

A future Tau library layer could define a **finite local algebra type** by:

- finite carrier values;
- a binary code;
- truth tables for primitive operations/relations;
- generated validity and operation BA formulas.

The core Tau solver would still see only ordinary atomless-BA terms.

OrbitSynthesis can therefore prototype finite-valued Boolean-power synthesis without modifying Tau's foundational logic or adding a new decision procedure.

## 15. Prior-art discipline

Binary encoding of finite-valued logic, Post/ternary switching synthesis, Boolean powers, and pointwise truth-table compilation are classical ideas.

The candidate research value is their composition with:

- Asor's omega-categorical synthesis setting;
- the Boolean-power causal predecessor commutation theorem;
- the direct clause/hypergraph fixed-point carrier;
- exact support/type/extension geometry;
- a concrete structure-preserving Tau backend.
