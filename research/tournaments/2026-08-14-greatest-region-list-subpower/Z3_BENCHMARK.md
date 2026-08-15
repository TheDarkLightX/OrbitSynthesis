# Z3 eager-versus-lazy calibration

Status: real-solver calibration, not a scalability theorem or checked MaxSAT
optimality proof.

The same Z3 4.15.4 weighted Boolean optimizer was used for both paths:

- **eager:** the complete state-plus-component-selector CNF;
- **lazy:** state variables only, with each failed proposal converted into a
  subset-minimal clause and replayed against the compiled component model
  before the clause was admitted.

Every solver result was replayed by the deterministic OrbitSynthesis model.
The 24 nine-state random objectives were also compared with exhaustive search.

## Deterministic counts

| Corpus | Eager variables | Eager hard clauses | Lazy state variables | Lazy clauses | Lazy calls |
|---|---:|---:|---:|---:|---:|
| 24 random nine-state games, total | 1,067 | 1,079 | 216 | 31 | 55 |
| 81-state principal obstruction | 17,255 | 17,405 | 81 | 3 | 4 |

For the principal obstruction both paths return objective 78. The three lazy
clauses contain six state literals in total.

## Timing observation on one host

Seven alternating-order repetitions under Python 3.12.3 gave:

| Corpus | Eager median | Lazy median |
|---|---:|---:|
| 24 tiny random games, total | 40.18 ms | 76.98 ms |
| 81-state principal obstruction | 209.23 ms | 13.07 ms |

The result is deliberately mixed. Eager compilation is faster on the tiny
random corpus; lazy learning is about 16 times faster on the structured
principal instance and avoids more than 17,000 selector variables. This is
evidence for a portfolio policy, not for replacing eager compilation
universally.

## Replay

```bash
bash research/tournaments/2026-08-14-greatest-region-list-subpower/check_z3_benchmark.sh

python3 research/tournaments/2026-08-14-greatest-region-list-subpower/benchmark_z3_learning.py \
  --repeats 7
```

The semantic receipt is byte-identical under normal and optimized Python. Its
semantic SHA-256 is:

```text
fa0020acc50e1a8afba3e3cf375d063206e11ebcefe7ef7b1b5fbc50083c1a80
```

## Nonclaims

- Z3 supplied optimization models; no MaxSAT proof trace was checked.
- This is not an Open-WBO, MaxHS, or RC2 benchmark.
- The principal witness is one structured instance, not a workload census.
- Compilation time, memory, incremental specification updates, and larger
  antichain/hardness families still need systematic measurement.
