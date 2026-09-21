# Morph minimum-sufficient-abstraction certificate: quasi-primal pointed orbits

**Certificate ID:** `orbit-synthesis/quasiprimal-pointed-orbits/v1`  
**Date:** 2026-08-12  
**Skill provenance:** `TheDarkLightX/Morph`, PR #10, `minimum-sufficient-abstraction`  
**Primary theorem:** `notes/QUASIPRIMAL_POINTED_ORBIT_FACTORIZATION.md`

## Contract

| Field | Value |
| --- | --- |
| Raw domain | Table positions `z in Q^n` and complete scalar/vector operation tables |
| Declared query family | Original-signature termhood, sparse singleton/list interpolation, table-value reconstruction, fixed-domain safety feasibility |
| Candidate abstraction | Isomorphism class of `(Sg(z);z_1,...,z_n)` plus unique transport to/from a canonical representative |
| Losslessness tier | Semantic losslessness with canonical complete-table reconstruction |
| Retained operations | Internal-isomorphism transport; pullback/intersection of scalar and vector output lists |
| Decoder | Choose one seed in each representative generated subalgebra and transport it to every raw tuple |
| Claim domain | Finite quasi-primal `Q`, arity `n>1`; fixed-`Q` complexity statement uses explicit sparse tuples/lists |

## Generic soundness certificate

If two tuples have the same abstract class, their pointed generated subalgebras have a **unique** isomorphism carrying one tuple to the other. A representative seed therefore transports without path ambiguity. Every reconstructed table preserves every internal isomorphism and is a term operation by Pixley's characterization.

**False-merge count on the theorem domain:** `0` by proof.

## Generic minimality certificate

The product theorem proves

`Term_n(Q) ~= product_C Sg(r_C)`.

Every class seed can be selected independently. Hence two distinct pointed classes have no residual preservation constraint linking them.

**False-split count on the theorem domain:** `0` by product-factorization proof.

This is structural minimality of the independent coordinates, not a universal minimum-bit coding claim.

## Factorization and reconstruction

For `z` in class `C`, let

`theta_z:Sg(r_C)->Sg(z)`

be the unique pointed isomorphism. The query consumer for table evaluation is

`eval_z((a_D)_D)=theta_z(a_C)`.

For vector controllers, apply `theta_z` coordinatewise.

For a sparse allowed set `L_z`, the quotient consumer is

`theta_z^(-1)(L_z intersect Sg(z))`.

All constraints in one class combine by intersection; different classes remain independent.

## Operation-descent certificate

- Internal-isomorphism composition descends because pointed transports are unique on generated subalgebras.
- Scalar allowed-output pullback descends to a subset of the representative seed domain.
- Vector allowed-output pullback descends coordinatewise.
- Fixed-domain safety descends to one transported allowed-seed intersection per pointed observation class.

**Operation-descent failure count on the theorem domain:** `0` by proof.

## Bounded falsification receipt

Algebra:

`Q=({0,1,2}; discriminator,u)` with `u(0)=1`, `u(1)=0`, `u(2)=1`.

Arity: `2`.

| Metric | Result |
| --- | ---: |
| Raw tuple/table positions | 9 |
| Pointed abstract classes | 7 |
| Raw-to-abstract ratio | `9/7` |
| Direct preserving term tables | 972 |
| Product-factorized tables | 972 |
| Direct/factorized table symmetric difference | 0 |
| Restricted observation subpowers exhausted | 512 |
| Sparse singleton instances exhausted | 262144 |
| List instances checked | 27205 |
| Bounded false merges | 0 |
| Bounded false splits | 0 |

Additional calibration:

- pure three-element discriminator, arity `3`;
- `27` raw tuples -> `5` pointed equality-pattern classes;
- `24` factorized functions = `24` independently generated discriminator-term functions;
- `282` stabilizer-redundancy element checks pass.

Commands:

```bash
python experiments/quasiprimal_pointed_orbit_factorization.py
python -O experiments/quasiprimal_pointed_orbit_factorization.py
```

Both modes produced the same successful semantic counts.

The generated finite corpus was then checked with the validator committed in the Morph skill branch under both normal and optimized Python. The validation outputs were byte-identical and reported:

```text
status: PASS_EXACT_ON_BOUNDED_CORPUS
object_count: 9
query_count: 972
abstract_state_count: 7
semantic_class_count: 7
raw_index_bits: 4
abstract_index_bits: 3
```

Reproducibility hashes:

```text
SHA256(corpus JSON)     b839548644b801ce187c24fcce66d2c49879228dcceee796cdfbb212ed608002
SHA256(validation JSON) 17a22af8bb72fa671ab803fa7cd656afc54ab2403d77170c4c72245c92cd40d6
```

The corpus is generated on demand rather than committed as a 227 KB derived file:

```bash
python experiments/quasiprimal_pointed_orbit_factorization.py \
  --emit-morph-corpus /tmp/quasiprimal_pointed_orbit_corpus.json
```

## Rejected stronger abstractions

### Generated subalgebra alone

Rejected: two tuples can generate the same subalgebra without a pointed automorphism carrying one tuple to the other. Their seed coordinates need not be identified.

### Global automorphism orbit for every quasi-primal algebra

Rejected by the Quackenbush algebra: the swap on `{0,1}` is an internal automorphism that does not extend globally. Global orbits miss a real table constraint.

### Raw tuple per table variable

Sound but nonminimal: tuples in one pointed class are deterministically related and should share one seed.

### One local choice per tuple with no transport

Rejected: it creates false independent choices and reproduces the known quasi-primal coupling bug.

## Scope and unknowns

- Unary arity is outside the generic Pixley theorem version used here and should be precomputed separately.
- Explicit term-expression extraction cost is `UNKNOWN` in this certificate.
- Complexity with succinctly represented lists is `UNKNOWN` without charging the list evaluator.
- Publication novelty is `UNKNOWN`; classical ingredients are old and the factorization may be implicit in discriminator-algebra literature.
- Lean formalization is pending.
