# Independent recursive Boolean-library audit

Date: 2026-08-14  
Verdict: **PASS.**

This lane independently reimplements the Boolean plane factorization,
recursive function-library semantics and cost, sibling-vector recurrences,
five-candidate portfolio, complement-relative binary branch, exact finite
proof, analytic tail, and depth accounting. It imports neither the primary
checker nor an OrbitSynthesis compiler implementation.

For every checked integer `64<=r<=16384`, it confirms

```text
25*size*r < 62*3^r,
depth <= r+C+2*ceil((4C+2)/3)+15.
```

It exhaustively checks all Boolean tables on all subsets of `Q^2`, including
177,147 target evaluations, and independently verifies the recursive bound

```text
L(S)<=4*t*2^|S|.
```

The finite maximum and complete-range maximum both occur at `r=64`:

```text
2.473270139955782682...
```

```text
independent checker SHA-256
  560257b42ba7d136f914b767dc188cad9636132f65a488ee8978e1990f70b4f7
independent receipt/stdout SHA-256
  dff1843ba2de72996a0a141407510675c1fd4d70ef0d5abe31d862ab331c4a10
independent semantic SHA-256
  a9f3fd40348d0040ff5baac1e284e712685c019f4f54f42b955c3c975a8b3005
```

The audit is deterministic evidence for the manuscript proof. It is not a
Lean formalization, external peer review, novelty result, exact global
optimality theorem, or legal finding.