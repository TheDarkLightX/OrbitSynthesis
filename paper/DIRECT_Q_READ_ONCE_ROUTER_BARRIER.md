# A read-once barrier for direct `Q`-valued discriminator routers

**Status.** Elementary paper theorem. It explains why the Boolean-plane representation in the coefficient-one construction is structural rather than cosmetic. The theorem is restricted to a read-once payload grammar and is not a lower bound for arbitrary shared DAGs with duplicated payload use.

## 1. Unary contexts

Fix

```text
Q={0,1,2},
d(x,y,z)=z if x=y, and d(x,y,z)=x otherwise,
u(0)=1, u(1)=0, u(2)=1.
```

Consider a term in which one distinguished payload variable `x` occurs exactly once. After fixing every other input, the unique path from `x` to the root is a unary context built from

```text
u(C(x)),
d(C(x),a,b),
d(a,C(x),b),
d(a,b,C(x)),
```

with `a,b in Q`.

Call a context **outer-only** when its path contains no unary node and never places the distinguished child in the middle argument of `d`.

## 2. Image collapse

**Lemma 1.** If a unary function `f:Q->Q` has image size at most two, then each of

```text
u(f(x)),
d(f(x),a,b),
d(a,f(x),b),
d(a,b,f(x))
```

also has image size at most two.

**Proof.** The unary map `u` has image `{0,1}`. In the left position, `d(f(x),a,b)` replaces the value `a`, when present, by `b`, so it cannot enlarge the image. In the middle position, `d(a,f(x),b)` takes values only in `{a,b}`. In the right position it is either `f(x)` when `a=b` or the constant `a` when `a!=b`. `square`

**Lemma 2.** If a unique payload path contains a unary edge or a middle discriminator edge, then the induced unary function of that payload has image size at most two.

**Proof.** At the first such edge, the image collapses to at most two: `u` maps into `{0,1}`, while `d(a,f(x),b)` maps into `{a,b}`. Lemma 1 propagates the bound through every remaining ancestor. `square`

**Corollary 3.** A read-once term inducing a permutation of `Q`, in particular the identity payload projection, must place its unique payload occurrence on an outer-only path.

## 3. Capacity bound

A term tree of operation depth `h` has at most `2^h` leaf positions whose root paths use only left and right discriminator edges: at each operation level there are at most two admissible choices.

**Theorem 4 (read-once direct-routing barrier).** Let a programmable original-signature term tree have operation depth at most `h`. Suppose it contains `q` payload variables, each exactly once, and for every payload there is a setting of all address/program inputs under which the term returns that payload for every assignment in `Q^q`. Then

```text
q<=2^h.
```

Consequently, routing `q=3^w` direct `Q`-valued payloads in this grammar requires

```text
h>=ceil(log_2 q)=ceil(w log_2 3).
```

**Proof.** Fix one requested payload and its program. Fix all other payloads arbitrarily. The resulting unary function of the requested payload is the identity, so Corollary 3 forces its unique occurrence onto an outer-only path. Distinct payloads occupy distinct leaves, and there are at most `2^h` outer-only leaves. `square`

## 4. Meaning for the paper

The theorem rules out a direct `Q`-valued analogue of the one-occurrence strong signed family with dependency coefficient one. The middle argument of a discriminator can transport a two-valued signal through the positive/negative trick, but it cannot transport a surjective three-valued payload from a single dependent child.

The two Boolean planes evade the barrier because each plane has only two values. Payload duplication or a richer multi-output state can also evade it, so the theorem must not be presented as a lower bound for unrestricted free-fanout DAGs.

This barrier complements the positive native-mode result:

- native first-mismatch preprocessing has optimal leading size coefficient one;
- the signed skeleton uses every ternary branch at coefficient-one depth on Boolean planes;
- a direct read-once three-valued skeleton cannot use middle paths without losing a value.
