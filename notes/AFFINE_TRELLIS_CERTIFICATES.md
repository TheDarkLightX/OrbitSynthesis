# Affine controller synthesis through certified syndrome trellises

Date: 2026-09-22. Base: `0ab3648a724370786ac9ea573bf81ac7ef7db7fb`.

**Status:** DERIVED specialization of classical linear-code trellis theory;
independent implementation and bounded differential tests executed. Novelty of
this synthesis-specific combination is unverified. No Lean build, external peer
review, industrial performance superiority, or general polynomial-time claim.
The classical cut-rank/minimal-trellis invariant is explicitly NOT ours.

## 1. Exact scope and the earlier kernel

Work over the original-signature algebra `(F_2; xor, 0)`. A controller is a
homogeneous linear map `M:F_2^n -> F_2^k`, represented by `n*k` coefficient bits.
Input rows prescribe `M z_i in L_i`, with `L_i` an explicit finite list of output
vectors. Repeated observations intersect their lists. There is no arbitrary
constant one, AND/OR controller, hidden external parameter, or temporal frontend.
Counts below count distinct matrices/maps, NOT syntactically distinct terms.

The previously delivered `affine_row_lists.py` kernel is included unchanged.
Its exact affine-exception reduction is the starting point, not a new claim:

1. Replace each list by its affine hull and solve all resulting coefficient
   equations. An empty list or inconsistent relaxation is immediately UNSAT.
2. Write the relaxation as `c0 + V`, with `f = dim(V)`.
3. Keep only the exceptional rows whose original list differs from its hull.
   Let `T` record the outputs on these rows, and let `C=T(V)`, `d=dim(C)`.
4. Enumerate the `2^d` exceptional-output patterns. Each admitted pattern has
   exactly `2^(f-d)` coefficient-space preimages.

The new backend removes that last exhaustive-enumeration requirement on
low-cut-rank instances. It does not change the allowed controller semantics.

The prior F2 successor-list result remains scoped: for sparse, input-free,
fixed-domain safety, lists of size at most two are affine and hence polynomial;
three-element successor lists suffice to encode graph four-coloring. Here we
study structural tractability even when every list has three elements.

## 2. Representation: the exceptional outputs are an affine code

Fix an ordering of the `m` exceptional rows and pack their `k`-bit outputs into
`E=(F_2^k)^m`. The realizable output words are exactly `a+C`, where `a=T(c0)`.
Find an independent parity-check matrix `H` with `ker(H)=C`. It has
`h=mk-d` rows and full row rank. Thus the original question is exactly

```
y_i in L_i for every i, and H(y+a)=0.
```

All coefficient directions invisible to these outputs have already been counted
by the uniform factor `2^(f-d)`. The parity-check construction uses only linear
bases; it never enumerates all words of `C`.

## 3. The cut-rank theorem (classical mechanism, synthesis specialization)

After processing the first `i` output blocks, let `P` and `F` be past and future
coordinate sets. Write `H_P` and `H_F` for the corresponding column blocks.
A partial word has syndrome `s=H_P(y_P+a_P)`. It can extend to a word of the affine
relaxation exactly when

```
s in im(H_P) intersect im(H_F).
```

Consequently the number of relaxation states at this cut is exactly `2^lambda_i`,
where

```
lambda_i = rank(H_P)+rank(H_F)-rank(H)
         = dim(pi_P C)+dim(pi_F C)-dim(C).
```

**Proof.** Extendibility says `H_F(y_F+a_F)=s`. The displayed intersection is
therefore both necessary and sufficient. Since the two column spaces sum to the
whole syndrome space, the dimension-of-intersection formula gives the first
expression. A codeword supported only on P lies in the kernel of `H_P`, so
`rank(H_P)=|P|-dim(C supported on P)`, and
`dim(C supported on P)=d-dim(pi_F C)`. The symmetric identity gives the second
expression after cancellation. Here `|P|` denotes its number of scalar bits.

This cut rank is independent of the chosen coefficient basis and parity-check
basis, though it depends on the ordering/partition of output blocks.

### Exact residual meaning; no overstated minimization theorem

Two extendible past words have the same set of unrestricted affine-relaxation
suffixes iff their syndromes agree. Distinct syndromes have disjoint nonempty
suffix sets. Therefore a deterministic layered recognizer for this relaxation
needs at least `2^lambda_i` extendible states at this cut, and syndrome states
attain this bound. This is the classical minimal-trellis mechanism.

After imposing the original lists, states can disappear and suffix languages
can collapse further. We do NOT claim that the resulting list-constrained
recognizer is minimal, nor that the chosen row order is optimal. Minimizing
linear-code trellis width under coordinate permutations has established
hardness and parameterized-algorithm literature; this is not a new problem.

## 4. Exact transfer recurrence and controller count

Let `B_i` be the block of H columns for row i, and `R_i` the span of all columns
strictly after row i. Define `N_0(0)=1` and all other initial counts zero. For each
allowed output `y in L_i`, transfer

```
t = s xor B_i (y xor a_i)
N_i(t) += N_(i-1)(s)   only if t belongs to R_i.
```

`N_i(s)` counts ALL list-admissible length-i prefixes with syndrome s that admit
an affine-relaxation completion. Pruning is sound: a prefix of any final valid
word always has such a completion. Paths with equal syndromes share exactly the
same future affine condition, so their multiplicities add without identification
of distinct prefixes. At the last layer only syndrome zero survives. Hence

```
number of original controller matrices = N_m(0) * 2^(f-d).
```

A retained prefix representative provides an output word. Gaussian elimination
lifts it back to a matrix, which is checked against every ORIGINAL row list.

### Complexity and genuine improvement over the preceding backend

Let `w=max_i lambda_i`. After polynomial linear-algebra preprocessing, the
number of attempted transfers is bounded by

```
sum_i |L_i| * 2^lambda_(i-1) <= 2^w * sum_i |L_i|.
```

Bit operations, matrix preprocessing, and big-integer arithmetic contribute
polynomial factors in `nk`, `mk`, and the explicit input. Counting needs up to
`nk+1` bits per multiplicity. The whole certificate stores at most
`sum_i 2^lambda_i` state/count entries, not just the peak live frontier.
This is a bound in width, NOT a polynomial-time algorithm for unrestricted input.
Dense parity-check preprocessing can dominate runtime. No benchmark against
mature SAT, model-counting, or coding-theory software has been claimed.

## 5. An exponential separation within our solver portfolio

For the cycle graph on v vertices, take `n=v`, `k=2`, and one constraint

```
M(e_i+e_(i+1)) in {01,10,11}
```

per edge, with cyclic indexing. Every row list is non-affine. A matrix assigns
one of four colors to each vertex; the constraints say adjacent colors differ.
Here `f=2v`, `d=2v-2`, and every internal edge-order cut has rank two: the only
code constraints are the two coordinatewise cycle-parity equations.
Thus the old exhaustive image search has `2^(2v-2)` patterns, but this trellis
has at most four live states for arbitrarily large v.

The independent count oracle is

```
3^v + 3*(-1)^v.
```

**Proof of the oracle.** The color-transition matrix is `J_4-I_4`; its eigenvalues
are 3 once and -1 three times. A closed length-v walk is a proper cycle coloring,
so the count is the trace of its v-th power. This is established graph/coloring
mathematics, not a new counting formula.

Executed at v=256: exception rank 510, maximum cut rank 2, four peak live states,
3,060 attempted transfers, 1,021 certificate entries, and exact count `3^256+3`.
The old backend returns `unsupported` at its configured budget; we do not pretend
to have executed `2^510` operations or measured such a wall-clock speedup.

This is a constructed calibration, not a real deployed workload. Its purpose
is to refute the idea that a large exception-image rank necessarily forces a
large sequential search frontier.

## 6. Independent certificates: what is and is not trusted

`affine_trellis.py` is the producer. `affine_trellis_check.py` imports neither the
producer nor the old kernel. It independently reconstructs the affine hulls,
coefficient space, exceptional projection and parity checks using a separately
written batch Gauss-Jordan implementation. It then checks:

- a caller-supplied original problem pin, schema, and exact field set;
- all exceptional rows appear exactly once in the claimed order;
- dimensions, cut ranks and every state/count entry;
- the full local flow recurrence, with no missing or extra counts;
- the final uniform-fiber multiplier and direct original-row SAT witness;
- canonical integer types (Boolean values are not integers at the wire boundary).

By induction, an accepted sequence of flow tables has the true prefix counts.
The last layer and the exact fiber theorem therefore establish the matrix count.
Zero certifies UNSAT, not merely failure of a search heuristic. Linear-relaxation
inconsistency is rechecked in polynomial time; it is not accepted on assertion.

A budget miss is `unsupported`, with no count/witness. The checker rejects it.
Hashes bind the input but are not themselves proofs. Verification replays the
transfer recurrences and can cost as much as their generation; the benefit is a
separate auditable implementation and portable evidence, not universally faster
checking. The Python checker, integer semantics, and host runtime remain trusted.
It is NOT Lean-verified, CPOG-compatible, or a novel general counting proof system.

**API:** `verify(original_problem, certificate)` raises `ValueError` on rejection.
Never let a purported certificate choose the supposedly independent original
problem. JSON readers reject duplicate object keys. The CLI bounds input dimensions
and list counts. Producer preprocessing itself is not resource-capped; neither
API is claimed ready to accept arbitrary hostile-scale production workloads.

## 7. Executed evidence

The deterministic replay suites cover:

- all 65,536 four-row/two-input/two-output list instances; exact agreement with
  all 16 matrices (24,408 SAT and 41,128 UNSAT);
- all 1,099 labeled graphs on one through five vertices, both natural and reverse
  exceptional-row order (2,198 certificates), against direct four-color counts;
- 1,200 seeded arbitrary row-list instances against full matrix enumeration;
- 200 attempted cut-profile calibrations, checking all consistent cases by
  explicit relaxation-word enumeration and residual suffix-language classes;
- 147 rejected certificate mutations and resource-limit cases;
- cycles of lengths 3,4,8,32,128,256, including the exact formula above;
- the K4 fixed-domain safety helper construction, recovering 384 matrices.

Normal and optimized Python produce byte-identical output on all five suites.
The verifier is separately implemented by the same assistant, not a human or
external peer review. Falsification tests support, but do not replace, the proofs.

## 8. Reproduce

```
python3 -B experiments/affine_trellis_replay.py --suite tables
python3 -B experiments/affine_trellis_replay.py --suite graphs
python3 -B experiments/affine_trellis_replay.py --suite random
python3 -B experiments/affine_trellis_replay.py --suite adversarial
python3 -B experiments/affine_trellis_replay.py --suite cycles
python3 -B tools/affine_trellis.py demo --vertices 256 --directory /tmp/orbit-trellis
python3 -B tools/affine_trellis.py verify \
  --problem /tmp/orbit-trellis/problem.json \
  --certificate /tmp/orbit-trellis/certificate.json
```

Problem format: `{"n":3,"k":2,"rows":[[3,[1,2,3]],[5,[1,2,3]],[6,[1,2,3]]]}`.
The demo writes inspectable problem/certificate JSON. No installation or Tau
checkout is required. These new modules are additive and do not modify existing
controller runtimes, public exports, frozen referee branches, or prior PRs.

## 9. Prior art, Asor boundary, and next frontier

Primary sources consulted during this continuation:

1. Navin Kashyap, *Matroid Pathwidth and Code Trellis Complexity*, SIAM J. Discrete
   Math. 22(1), 256-272 (2008), https://doi.org/10.1137/070691152;
   author preprint https://arxiv.org/abs/0705.1384. The relation between matroid
   pathwidth and code trellis complexity, and ordering hardness, are prior art.
2. G. D. Forney Jr., *Dimension/Length Profiles and Trellis Complexity of Linear
   Block Codes*, IEEE Trans. Information Theory 40(6),1741-1752 (1994),
   https://doi.org/10.1109/18.340452. Classical foundation, identified through
   Kashyap's references and publisher metadata; no full-text examination claimed.
3. R. E. Bryant, W. Nawrocki, J. Avigad, M. J. H. Heule, *Certified Knowledge
   Compilation with Application to Formally Verified Model Counting* (2025),
   https://arxiv.org/abs/2501.12906. Their CPOG/Lean work is a stronger established
   formal-certification baseline, not something this Python checker supersedes.
4. Ohad Asor, *ocLTL: LTL Realizability and Synthesis Modulo omega-Categorical
   Structures* (2026), https://arxiv.org/abs/2605.12539. Its public description
   concerns complete-type reduction of temporal synthesis. Our lane is finite
   controller implementation expressibility and code-theoretic exact counting.

These are independently authored generic finite-matrix algorithms, not Tau
source, quantifier-elimination machinery, or a competing ocLTL reduction.
Unpublished overlap with Asor cannot be ruled out, and academic attribution is
not a patent or freedom-to-operate conclusion. No upstream Tau changes are made.

Next meaningful targets: a proved linear-code tree-decomposition backend,
order selection with verified width bounds, weighted transfer semantics with
careful treatment of kernel fibers, and a formally checked certificate calculus.
Before novelty promotion, compare with classical trellis/list-recovery algorithms,
code realizations on trees, CSP backdoors, and certified knowledge compilation.
A real workload and identical-semantics solver comparison are required before
claiming practical superiority beyond the previous enumeration backend.
