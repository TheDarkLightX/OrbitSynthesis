# Ordered-response game quotient for upward reactive objectives

**Status:** DERIVED finite-poset theorem. This upgrades positive response frontiers from one-step monotone formulas to reactive fixed-point games whenever the response order is compatible with the next-state order.

## 1. Ordered reactive arena

Let `(S, <=_S)` be a finite state poset.

At state s, the environment chooses a move p from `Env(s)`.

For each `(s,p)`, the system has a finite nonempty set of **legal responses**

`E_(s,p)`

equipped with a preorder/partial order `<=_E`.

Each response has a next state

`Next_(s,p) : E_(s,p) -> S`.

Assume:

### Response monotonicity

If

`e <=_E e'`

then

`Next(e) <=_S Next(e')`.

Thus a response that is better in the response order cannot produce a smaller next-state abstraction.

All transition legality has already been absorbed into `E_(s,p)`. If legality is represented separately, it must be upward/closed so that moving to a dominating response remains legal.

## 2. Upward targets

A state set W is upward if

`s in W and s<=_S t => t in W`.

Define the ordinary controllable predecessor

`CPre(W)
 = { s : for every p in Env(s),
         exists e in E_(s,p), Next(e) in W }`.

## 3. Maximal response frontier

Let

`Max(E_(s,p))`

be the inclusion/order-maximal legal responses.

Because the response fiber is finite, every response lies below at least one maximal response.

### Theorem 1 — maximal-response quotient

For every upward W:

`s in CPre(W)`

iff

`for every p in Env(s),
 exists m in Max(E_(s,p)), Next(m) in W`.

### Proof

The right-to-left direction is immediate.

For the other direction, fix p and choose any witnessing response e with `Next(e) in W`. Extend e upward to a maximal response m. Response monotonicity gives

`Next(e) <=_S Next(m)`.

Since W is upward, `Next(m) in W`.

Thus every successful response can be replaced by a maximal legal response.

## 4. Exact system branching width

Define

`w(s,p)=|Max(E_(s,p))|`

and

`w=max_(s,p) w(s,p)`.

Theorem 1 replaces arbitrary/full response-type branching by at most w system branches after every environment move.

This is exact relative to the chosen response order: every nonmaximal response is semantically dominated for every upward target.

If the order is the positive-signature inclusion order from `POSITIVE_RESPONSE_FRONTIER.md`, this recovers the positive response width.

## 5. Dominant-response case

If every response fiber has one greatest element

`top_(s,p)`,

then `w=1` and

`CPre(W)
 = {s : for every p, Next(top_(s,p)) in W}`.

This is an ordinary box/universal predecessor on the environment-only transition system induced by the greatest system response.

Hence the ABA result in `ABA_DOMINANT_STRATEGY.md` is the width-one extreme of this theorem.

## 6. Upward fixed-point closure

Suppose:

1. the atomic state predicates used by the objective are upward;
2. AND and OR are interpreted normally;
3. fixed-point variables occur positively;
4. CPre is the operator above.

Then CPre maps upward sets to upward sets if the arena also satisfies **state monotonicity**:

for `s<=_S t`, every environment challenge at t can be matched by a challenge at s whose maximal-response next-state possibilities are no better than those from t.

This additional condition is theory/arena-specific and must not be silently assumed.

However, whenever the original semantic construction is already known to preserve the upward-state lattice—as in the ABA support game—the maximal-response quotient computes exactly the same CPre on that lattice by Theorem 1. Therefore all least/greatest fixed points built from that operator are unchanged.

### Theorem 2 — fixed-point quotient (conditional form)

On any invariant lattice L of upward state properties on which the original CPre acts, replacing each response fiber by its maximal-response frontier leaves CPre unchanged on L and therefore preserves every positive modal mu-calculus denotation over L.

### Proof

Theorem 1 gives pointwise equality of the original and quotient CPre for every W in L. Structural induction gives equality for compound formulas, and equality of monotone operators gives equality of least/greatest fixed points.

## 7. Positive-signature instantiation

Let Delta be the positive observation family and order responses by

`e <=_Delta e' iff sigma(e) subseteq sigma(e')`.

To use the reactive theorem, the next-state abstraction must be monotone in this signature order:

`sigma(e) subseteq sigma(e') => NextAbs(e) <= NextAbs(e')`.

This is the key closure condition that distinguishes a merely useful one-step signature quotient from a full reactive-game quotient.

### ABA

Response signature = fine support.

Support inclusion implies inclusion of the projected next-state support, so monotonicity holds. The zero-safe legal response fiber has a greatest support. Width 1 follows.

### Other theories

A fragment can have a one-step dominant signature but fail to induce a monotone next-state abstraction. Such a fragment does **not** automatically inherit the ABA synthesis/model-checking collapse.

This is an important kill condition for generalization attempts.

## 8. Partially collapsed system game

When `w>1`, the quotient remains a two-player game:

`forall environment p, exists maximal response m`.

But all dominated system types have disappeared.

This gives a hierarchy:

- `w=1`: environment-only model checking;
- bounded w: bounded-branching synthesis;
- structured large frontier: symmetry/hypergraph representation;
- unstructured large frontier: generic game fallback.

## 9. Product and symmetry integration

For independent coordinate-local products, `PRODUCT_RESPONSE_FRONTIERS.md` gives multiplicative width.

Under coordinate symmetry, quotient maximal-response tuples by the permutation group before constructing the game.

Thus a reactive backend can apply reductions in this order:

1. quotient response types by positive signature;
2. remove dominated signatures;
3. factor independent coordinates;
4. quotient symmetry orbits;
5. build the residual bounded-width game.

## 10. Strategy extraction

A winning strategy in the quotient selects a maximal response signature.

To execute it concretely the theory plugin needs:

1. a complete response type realizing that signature;
2. an effective concrete witness realizing the type over the observed parameters.

This separates abstract game reduction from model-theoretic witness realization.

## 11. General plugin contract

A theory backend aiming to use this theorem should provide:

- finite/effective response fibers or signature abstractions;
- response dominance preorder;
- maximal-response frontier computation;
- proof/check that the next-state abstraction is monotone in that preorder;
- representative complete types;
- concrete extension witnesses.

This is a candidate general OrbitSynthesis interface for theories beyond ABA.

## 12. Next questions

1. Find structural/model-theoretic sufficient conditions guaranteeing response-to-next monotonicity.
2. Determine when polymorphism/semilattice operations produce the required ordered arena.
3. Establish FPT synthesis algorithms parameterized by maximal response width w plus environment/type parameters.
4. Study whether bounded w is preserved under bounded-lookback/product transformations.
5. Develop counterexamples where one-step dominance exists but reactive monotonicity fails.
