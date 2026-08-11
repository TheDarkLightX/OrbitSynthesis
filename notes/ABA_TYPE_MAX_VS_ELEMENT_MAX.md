# Greatest response type is not greatest Boolean-algebra element

**Status:** DERIVED conceptual distinction; directly cross-checked against the behavior documented in Tau's `solve --min/--max` demo.

OrbitSynthesis repeatedly uses a **greatest support/type response** for an upward fragment. Tau already has solver options called `--min` and `--max` for Boolean equations. These must not be confused.

They optimize different orders on different objects.

## 1. Element-level order used by Tau solve --max

For concrete Boolean-algebra elements,

`x <= y`

means ordinary BA inclusion/order.

Tau's solver can ask whether a system has a greatest concrete solution in this order.

The Tau demo explicitly notes that a solvable system need not have one.

Example:

`x != 0 AND x' != 0`.

In an atomless BA, x must be a proper nonzero element.

There is no greatest such x: any proper nonzero x can be enlarged slightly while remaining proper and nonzero.

Tau therefore needs a splitter to produce one solution, but no maximum element exists.

Source: `IDNI/tau-lang/demos/demo_2.2-solver-min_max.tau` at pinned Tau commit `fd137e860b60083b36f9159ec8090cb1a3c3cb5a`.

## 2. Type-level support order used by OrbitSynthesis

For one BA variable x, a complete ABA type is the nonempty support on the two cells

- `x=0` region, i.e. x';
- `x=1` region, i.e. x.

There are exactly three complete 1-types:

1. support `{0}`: x=0;
2. support `{1}`: x=1;
3. support `{0,1}`: `0<x<1` (both x and x' nonzero).

The constraint

`x != 0 AND x' != 0`

admits **exactly one complete type**:

`{0,1}`.

So at type level the legal-response fiber has a greatest element—indeed a singleton—even though at concrete-element level it has no greatest element.

## 3. Why the orders differ

Support inclusion compares **which Venn regions are required to be nonzero**.

Concrete BA inclusion compares how much actual Boolean-algebra mass lies inside x.

Within one nontrivial support type `{0,1}`, the relative sizes/shapes of the two nonzero pieces are intentionally forgotten. Many concrete elements realize the same type.

Atomlessness lets those pieces be refined indefinitely.

Thus:

`same support type`

does not mean

`same concrete BA element`,

and a top element of the finite type fiber need not lift to a greatest concrete realization.

## 4. Noether-style mechanism

The apparent paradox disappears once the quotient is visible:

`concrete BA elements`

`-- quotient by complete first-order type over the current parameters -->`

`finite support patterns`.

The quotient collapses all nontrivial splitters of a coarse cell into the same qualitative state: both child regions are nonzero.

The finite quotient can therefore have a top even when the original BA order has no maximum in that equivalence class.

## 5. Consequence for synthesis

The dominant strategy theorem is a **type-level strategy**:

1. choose the greatest legal support/type code `Max(P)`;
2. use an effective extension-witness routine to realize that type by some concrete BA output.

It is not:

1. compute the greatest concrete BA output value.

The second object may not exist.

## 6. Tau integration consequence

Do **not** implement the protected OrbitSynthesis path by replacing response synthesis with

`solve --max`.

Tau's maximum-solution solver can still be useful when a concrete maximum happens to exist, but it is neither necessary nor sufficient for the type-level extremal theorem.

The correct integration primitive is closer to:

`realize this prescribed complete extension/support type over these concrete parameters`.

That is exactly the effective-witness operation assumed in Asor's ocLTL extension construction and instantiated by the dyadic reference model in this repository.

## 7. Strong example

Let a coarse nonzero region C be required to split into both y and y'.

The maximal support code activates both refinements.

Any concrete realization chooses

`0 < y & C < C`.

But there is no greatest possible `y&C` satisfying both it and its complement in C are nonzero: it can always be enlarged while leaving a smaller nonzero complement.

So the mismatch between support-top and element-max is not exceptional; it appears exactly in the atomless splitting operation that makes ABA powerful.

## 8. Research implication

When generalizing extremal synthesis to other theories, distinguish at least three notions:

1. greatest concrete response element;
2. greatest abstract/type response code;
3. a concrete canonical witness realizing the greatest code.

ABA has (2) and effective (3) without generally having (1).

This is one reason type-fiber semilattices are a more general synthesis abstraction than semilattice orders on the concrete model itself.
