# Portable proof-bundle review checklist

Review target:

```text
base branch  research/state-search-optimality-certificates
head branch  research/portable-proof-bundles
```

## Semantic interface

- [ ] carrier order and operation-table product order are unambiguous;
- [ ] allowlist and denylist inputs canonicalize to the same safe relation;
- [ ] quasi-primality remains an explicit premise rather than an inferred fact;
- [ ] signed state utility, required states, and forbidden states are exact;
- [ ] unknown fields and malformed scalar types fail closed.

## Controller reconstruction

- [ ] the component-model hash covers every transported candidate rule;
- [ ] every serialized component choice is in range and accepts the domain;
- [ ] selected component rules reconstruct every observation exactly once;
- [ ] the serialized total controller equals that reconstruction;
- [ ] the controller is safe and invariant on every selected state.

## Optimality/infeasibility authority

- [ ] certificate weights equal the embedded problem weights;
- [ ] required/forbidden masks equal the embedded hard-state constraints;
- [ ] target domain and score agree with the serialized result;
- [ ] every conflict leaf names a genuinely impossible component;
- [ ] every bound leaf recomputes to at most the target score;
- [ ] infeasibility certificates contain no bound leaves;
- [ ] every branch partitions one undecided state.

## Portable envelope

- [ ] problem, component model, certificate, backend result, and manifest hashes
      are distinct and correctly scoped;
- [ ] missing manifests and malformed SHA-256 strings are rejected;
- [ ] unknown top-level, result, certificate, and strategy fields are rejected;
- [ ] timing and machine-local paths do not enter semantic hashes;
- [ ] normal and optimized Python produce byte-identical semantic artifacts.

## Claim boundary

- [ ] no quasi-primality decision claim;
- [ ] no polynomial-size certificate claim;
- [ ] no temporal or infinite-domain frontend claim;
- [ ] no original-signature DAG-in-bundle claim yet;
- [ ] no GitHub gate-pass claim until a runner executes the workflow.
