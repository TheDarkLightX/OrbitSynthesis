# Generator-compressed greatest-region converse

**Status:** derived strengthening, 2026-08-15. The construction is implemented
and has a primary plus no-import finite audit. It is not yet Lean-formalized or
externally peer reviewed. Publication novelty remains **UNKNOWN**.

## 1. Improvement

The existing generic converse to the demi-semi-primal greatest-region theorem
starts from a graph-maximal nonextendable internal isomorphism

```text
phi:B -> C
```

and lists every element of `B` in each distinguished state. Its state arity is
therefore

```text
|B|+2.
```

Listing all of `B` is unnecessary. Let

```text
g=(g_1,...,g_d)
```

be a minimum nonempty generating tuple for `B`, so

```text
Sg_A(g)=B.
```

An internal homomorphism is determined by its values on a generating tuple.
Consequently, any internal isomorphism that agrees with `phi` on `g` agrees
with `phi` on all of `B`.

The same critical/dead-orbit proof therefore works with state arity

```text
d(B)+2.
```

For a non-demi-semi-primal algebra, choose among graph-maximal nonextendable
internal isomorphisms one whose source has minimum generating rank. If

```text
mu(A)=min d(dom(phi))
```

over those maximal obstructions, the generic no-greatest witness has

```text
state arity mu(A)+2.
```

## 2. Compressed tags

Choose distinct `b_0,b_1 in B` and define

```text
p_0=(g,b_0,b_0),
p_1=(g,b_0,b_1),
a  =(g,b_1,b_0).
```

Transport them through `phi`:

```text
q_0=phi(p_0),
q_1=phi(p_1),
a' =phi(a).
```

The final two coordinates distinguish the three source states. The generator
prefix pins any internal isomorphism on all of `B`.

The critical observation permits exactly

```text
p_0,p_1,
```

while the transported observation permits exactly

```text
q_0,q_1.
```

The observation orbits of

```text
(p_1,beta),  beta outside B,
(q_0,gamma), gamma outside C,
```

are dead. A collision between one of those dead orbits and a protected state
would give a proper internal-isomorphism extension of `phi`, because agreement
on `g` implies agreement on all of `B`. Graph-maximal nonextendability rules
this out.

Thus

```text
W_L={a,p_0}
W_R={a',q_1}
```

are separately term-winning, but no term-winning domain contains both.

## 3. Why the old principal separator no longer suffices

The original principal-equation proof lists all elements of `B`. The first two
coordinates of every unsafe tuple are then distinct, so one can use

```text
p(x)=x_1,
g(x)=x_1 on safe tuples and x_2 on unsafe tuples.
```

A minimum generating tuple may have length one. After compression, no single
alternate coordinate need differ from the first coordinate on every unsafe
tuple. This failure occurs in the concrete Quackenbush algebra `Q`.

The correct replacement is orbitwise.

## 4. Orbitwise projection separator

Flatten a transition to

```text
x in A^(2k+1).
```

Use the first generator coordinate as

```text
p(x)=x_1.
```

The safe relation is invariant under every internal isomorphism, so the unsafe
tuples split into internal-groupoid orbits.

No unsafe tuple is constant:

- a critical observation contains the two distinct tags `b_0,b_1`;
- a source dead observation contains distinct tags; or
- a target dead observation contains an input outside its tagged subalgebra.

For every unsafe orbit `O`, choose one coordinate index `j_O` such that, at one
orbit representative,

```text
x_(j_O) != x_1.
```

Internal isomorphisms are injective, so the same inequality holds throughout
`O`. Define

```text
g(x)=x_1                  if x is safe,
g(x)=x_(j_O)              if x lies in unsafe orbit O.
```

Then:

1. `g(x)` is always one of the coordinates of `x`, hence belongs to
   `Sg_A(x)`;
2. safe/unsafe status is preserved by every internal isomorphism;
3. `j_O` is constant on each unsafe orbit; and therefore
4. `g(psi(x))=psi(g(x))` for every applicable internal isomorphism `psi`.

By quasi-primal interpolation, `g` is an original-signature term. Since the
chosen unsafe projection differs from `p`,

```text
x is safe iff p(x)=g(x).
```

The generator-compressed converse therefore remains inside the one-equation
fragment.

## 5. Exact three-element calibration

The audit exhausts all 27 unary expansions

```text
({0,1,2};d,u)
```

of the three-element discriminator algebra. It independently recovers

```text
15 demi-semi-primal expansions,
12 non-demi-semi-primal expansions.
```

Among the 12 converse witnesses:

```text
6 have state arity 3,
6 have state arity 4.
```

The historical full-list construction has arity 4 in all 12 cases, so six
witnesses are strictly compressed.

The number of flattened transition rows checked by the principal audit falls
from

```text
236,196
```

to

```text
131,220.
```

## 6. Quackenbush-Q checkpoint

For

```text
Q=({0,1,2};d,u),
u(0)=1, u(1)=0, u(2)=1,
```

the obstructing subalgebra is

```text
B={0,1}=Sg_Q(0).
```

Hence

```text
d(B)=1,
state arity=3,
states=27,
observations=81.
```

The one-equation audit checks all

```text
3^7=2,187
```

flattened rows. There are 104 unsafe rows in 98 internal-groupoid orbits. No
single alternate coordinate separates all unsafe rows from the first
projection; the orbitwise separator is genuinely load-bearing.

Compiling the principal witness to the eager domain model gives

```text
73 observation components,
1,762 deduplicated candidate rules,
1,789 CNF variables,
1,817 base hard clauses.
```

The historical arity-four witness gave

```text
227 components,
17,174 candidate rules,
17,255 variables,
17,405 clauses.
```

Thus the algebraic compression removes roughly 90% of the candidate rules and
variables in this checkpoint before any SAT-level optimization.

## 7. Implementation

```text
src/orbitsynthesis/generator_compressed_witness.py
```

Public API:

```text
minimum_generating_tuple
generator_minimal_maximal_nonextendable_internal_isomorphism
build_generator_compressed_no_greatest_region_witness
audit_generator_compressed_no_greatest_region_witness
build_generator_compressed_principal_no_greatest_region_witness
audit_generator_compressed_principal_no_greatest_region_witness
```

The historical builders remain unchanged. The compressed construction is an
additive, stacked strengthening so the existing PR #25 evidence packet retains
its exact semantics.

## 8. Remaining work

1. formalize the generator-determination lemma in Lean;
2. formalize unsafe-orbit projection selection and equivariance;
3. determine whether `d(B)+2` can be reduced further in general;
4. search for lower bounds on the state arity of universal converse witnesses;
5. integrate the compressed principal family into the eager/lazy solver
   benchmark portfolio.
