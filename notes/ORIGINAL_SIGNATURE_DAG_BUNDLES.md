# Original-signature controller DAGs in portable proof bundles

**Status:** bounded exact compiler and exhaustive finite verifier. A successful
artifact is a term DAG over the input algebra's declared basic operations. An
`unsupported` artifact means only that the configured finite search did not
find a realization; it is not a nondefinability proof.

## 1. The missing executable layer

The portable proof bundle already certified:

```text
finite algebra and safety problem
winning domain or infeasibility
complete internal-groupoid-compatible controller table
signed objective optimum
```

A controller table is semantic evidence, but it is not yet an implementation
in the supplied algebraic language. This lane adds the final checked bridge:

```text
controller table
      -> bounded original-signature term search
      -> shared multi-output DAG
      -> exhaustive table/DAG equivalence certificate.
```

No selector, lookup, named carrier constant, or foreign operation is admitted
unless it is itself a declared basic operation. Nullary basic operations are
permitted because they belong to the original signature.

## 2. DAG format

An original-signature DAG contains:

```text
input arity
output arity
exact operation signature
ordered operation nodes
ordered output roots
semantic SHA-256
```

Each argument reference is either:

```text
input(i)
node(j), where j is strictly earlier than the current node.
```

A node is

```text
operation_name(argument_1,...,argument_k)
```

where the operation name and arity agree exactly with one declared basic
operation of the embedded finite algebra.

The verifier rejects:

- unknown operations;
- incorrect arities;
- forward or cyclic references;
- roots outside the DAG;
- duplicate/altered signatures;
- unreachable hidden nodes;
- a DAG whose roots do not match the controller output arity.

Requiring every operation node to be reachable from a distinguished root makes
the serialized node census an exact census of the executable artifact rather
than a count that can be padded with irrelevant nodes.

## 3. Bounded semantic-closure compiler

Let `A` be the finite carrier and let the controller have input arity `r`.
Every scalar function `A^r -> A` has a finite truth-table signature.

The compiler starts with the `r` projection signatures. At depth `h`, it
applies every permitted basic operation to signatures already realizable at
depth at most `h-1`, requiring at least one argument of exact depth `h-1`.
Only the first discovered representative of each semantic function is retained.

The search stops when every scalar output coordinate of the controller table
has been discovered. Their term representatives are then hash-consed into one
shared multi-output DAG, and nodes not reachable from an output are removed.

The configured resource bounds are:

```text
maximum term depth
maximum distinct semantic functions
maximum operation applications
maximum exploration nodes
maximum basic-operation arity searched
```

### Success theorem

If the compiler returns `compiled`, then every output root is an
original-signature term and the resulting shared DAG evaluates to the supplied
controller table on every input in `A^r`.

This follows independently of the search heuristics: the verifier checks the
node syntax and evaluates the final DAG over the complete finite input space.

### Bounded failure boundary

If the compiler returns `unsupported`, one of the following occurred:

```text
bounded_search_exhausted
semantic_function_limit
combination_limit
exploration_node_limit
operation_arity_limit
```

This establishes no lower bound and no impossibility theorem. A deeper search,
a specialized compiler, the fixed-Q asymptotic compiler, or a human-supplied
term may still realize the controller.

## 4. Table-to-DAG equivalence certificate

For a successful DAG the certificate binds:

```text
finite-algebra operation tables
complete controller table
DAG structure
number of input rows checked
output arity
operation-node count
dependency depth
ordered evaluation transcript
```

It records separate hashes for:

```text
algebra
strategy table
DAG
evaluation transcript
complete certificate
```

For every input `x in A^r`, the verifier computes

```text
expected = controller_table[x]
actual   = evaluate(DAG,x)
```

and requires exact equality. Since the input space is finite and explicit,
this is a complete semantic equivalence check rather than randomized testing.

## 5. Executable proof bundle

The outer format is:

```text
orbit-synthesis/executable-proof-bundle/v1
```

and contains:

```text
proof_bundle:
  canonical problem
  optimal domain or infeasibility
  complete controller table
  controller/model hashes
  optimum or infeasibility proof

controller_artifact:
  compiled | unsupported | not_applicable
  compiler identifier
  bounded-search limits and diagnostic statistics
  original-signature DAG, when compiled
  table/DAG equivalence certificate, when compiled

manifest_sha256:
  hash of both layers together
```

The status meanings are deliberately distinct:

### `compiled`

The artifact contains a DAG and equivalence certificate, and the verifier has
checked every controller row.

### `unsupported`

A feasible semantic controller exists, but the configured bounded compiler did
not find a DAG. No executable data is present. Search statistics are diagnostic
compiler provenance, not independently proved search-completeness evidence.

### `not_applicable`

There is no controller to compile because the synthesis problem is infeasible,
or compilation was explicitly disabled. No DAG or equivalence certificate may
be present.

## 6. End-to-end soundness statement

If an executable bundle verifies with controller status `compiled`, then:

1. the embedded finite algebra and safety problem parse canonically;
2. the selected domain is clone-compatible and winning;
3. the serialized total controller is reconstructed from internal-groupoid
   component rules;
4. the signed objective is globally optimal under the embedded state-search
   certificate;
5. every DAG node is a declared basic operation applied to prior inputs/nodes;
6. the DAG computes the serialized controller on every finite input;
7. the outer manifest binds the semantic proof and executable implementation.

Thus the executable DAG implements the same controller whose safety and
optimality were certified by the inner proof bundle.

## 7. Source-grounded calibration

For the Quackenbush algebra

```text
Q=({0,1,2}; d,u)
```

and the example policy

```text
x' = d(x,i_0,i_1),
```

the compiler returns exactly one operation node:

```text
node 0 = d(input 0,input 1,input 2)
root   = node 0.
```

The equivalence certificate checks all `3^3=27` observations and records depth
one.

A separate two-output calibration compiles

```text
(d(x,y,z),u(d(x,y,z)))
```

to two nodes sharing the discriminator root. A projection calibration uses no
operation nodes. A constant function over the parameter-free conservative
algebra is reported as bounded-search `unsupported`, not silently implemented
with an illegal named constant.

## 8. CLI

```bash
python3 tools/orbit_synthesize.py synthesize-executable \
  --input examples/proof_bundle/discriminator_policy.json \
  --out executable.json \
  --backend native \
  --dag-policy required \
  --dag-max-depth 1

python3 tools/orbit_synthesize.py verify-executable \
  --input executable.json
```

Policies are:

```text
required     fail synthesis unless a DAG is compiled
best_effort  preserve an explicit unsupported artifact
              when bounded compilation does not succeed
off          skip compilation explicitly
```

## 9. Practical relevance

The executable format enables:

- deployment of a checked shared controller rather than a raw lookup table;
- independent implementation review without trusting the optimizer;
- comparison between generic bounded search and specialized compilers;
- archival paper artifacts containing both theorem-level and executable
  evidence;
- future translation to code, HDL, smart-contract, Tau, or theorem-prover
  frontends;
- regression checking that an optimized/recompiled DAG still implements the
  certified controller.

The current DAG is an algebraic intermediate representation. It is not yet a
machine-code, gas-cost, timing, bounded-fanout, or hardware certificate.

## 10. Open research directions

1. integrate the asymptotically efficient fixed-Q compiler as a specialized
   backend for large truth tables;
2. accept externally supplied DAGs and verify them without running synthesis;
3. minimize node count or depth after semantic compilation;
4. emit Lean definitions and proofs from the portable DAG;
5. translate DAGs to Tau, SMT, functional code, Verilog, or smart contracts;
6. characterize finite algebras for which bounded semantic closure is complete
   at a known depth;
7. add proof-producing rewriting and DAG optimization;
8. support parameterized signatures while distinguishing parameters from
   original nullary operations.

## 11. Nonclaims

This lane does not prove:

- that an `unsupported` controller is not term-definable;
- minimality of a compiled DAG;
- polynomial compilation complexity;
- bounded-fanout or formula bounds;
- end-to-end Lean verification;
- production deployment safety;
- publication novelty or legal clearance.

It supplies an exact, portable, fail-closed bridge from a certified semantic
controller to a checked implementation over the declared original signature.