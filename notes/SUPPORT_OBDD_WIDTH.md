# OBDD width of projected support clauses

**Status:** DERIVED special-case bound; connected to established knowledge-compilation results relating OBDD size to pathwidth/few-subterms. The general width theory is not novel; the point here is an explicit Tau/ABA cost parameter computable from projected support obligations.

## 1. Support clause

After direct ABA clause projection we have

`F(z_1,...,z_n)
 = AND_{v in D} NOT z_v
   AND
   AND_{j=1}^q OR_{v in H_j} z_v`.

Negative unit clauses D are deterministic and do not require multi-bit BDD memory. The positive obligations `H_j` are the interesting part.

Fix a variable ordering

`sigma=(z_{sigma(1)},...,z_{sigma(n)}).`

## 2. Crossing obligations

At cut t, let

`P_t={sigma(1),...,sigma(t)}`

and

`S_t={sigma(t+1),...,sigma(n)}`.

Call obligation H_j **crossing** at t if

`H_j intersect P_t != empty`

and

`H_j intersect S_t != empty`.

Let

`c_t(sigma)=# {j : H_j crosses cut t}`

and define

`c(sigma)=max_t c_t(sigma)`.

Call this the **crossing-obligation width** of the chosen order inside this repository. It is a simple cut parameter closely related to incidence/pathwidth viewpoints in knowledge compilation; permanent terminology should not be claimed without a literature check.

## 3. Residual-function theorem

### Theorem 1

After assigning the first t variables in order sigma, every non-false residual function is determined by the satisfied/unsatisfied status of the obligations crossing cut t.

### Proof

Consider a positive obligation H_j.

1. **H_j entirely in the prefix.** Its truth is already decided. If unsatisfied, the whole residual is false; if satisfied, it disappears.
2. **H_j entirely in the suffix.** No assigned variable could have satisfied it, so its residual is the same fixed suffix clause for every prefix assignment.
3. **H_j crosses the cut.** Prefix assignments may or may not already satisfy it. If satisfied it disappears; otherwise its residual is the fixed disjunction of its suffix variables.

Thus among non-false states, only crossing obligations carry assignment-dependent state, one satisfied/unsatisfied bit each.

Negative unit clauses either make the state false when violated or contribute no additional state.

## 4. OBDD size bound

### Theorem 2

Under variable order sigma, the reduced OBDD for F has at most

`n * 2^c(sigma)`

nonterminal nodes.

### Proof

At each variable level t there are at most `2^c_t <= 2^c(sigma)` non-false residual Boolean functions by Theorem 1. An OBDD has at most one node per distinct residual function at a level. Summing over n levels gives the bound. Reduction can only decrease the count.

### Corollary

If an ordering with constant crossing-obligation width exists, F has linear-size OBDD in the support width n.

This can be far sharper than the earlier universal `n*2^q` bound because only currently crossing obligations matter.

## 5. Relationship to pathwidth / knowledge compilation

The knowledge-compilation literature establishes polynomial/FPT OBDD compilation for structurally restricted CNFs and relates OBDD size to incidence pathwidth, subterm width, and related parameters.

Relevant primary sources:

- Simone Bova and Friedrich Slivovsky, *On Compiling Structured CNFs to OBDDs*, Theory of Computing Systems 61 (2017). They prove polynomial OBDD size for variable-convex incidence graphs and use the few-subterms property; the paper also discusses bounded-treewidth/pathwidth upper bounds.
- Antoine Amarilli, Florent Capelli, Mikael Monet, Pierre Senellart, *Connecting Knowledge Compilation Classes and Width Parameters*, arXiv:1811.02944 / later journal/conference versions, connecting pathwidth to OBDD compilation size with matching lower-bound phenomena for restricted CNFs.
- Igor Razgon, *On OBDDs for CNFs of Bounded Treewidth*, arXiv:1308.3829 / KR 2014, clarifying which treewidth notions do and do not yield FPT OBDD bounds.

Our crossing proof is deliberately elementary because the projected ABA clause has a special monotone-CNF-plus-units shape. It gives a direct cost quantity without requiring a full graph decomposition implementation.

## 6. Cost predictor for OrbitSynthesis

For a projected support clause compute:

- n = support width;
- q = number of positive obligations;
- a heuristic order sigma;
- `c(sigma)`.

Predicted OBDD upper bound:

`min(n*2^q, n*2^c(sigma)) = n*2^c(sigma)`.

Since exact minimization over orders is a combinatorial problem, use cheap heuristics initially:

1. order support cells by constant region, then variable minterm Gray/lex order;
2. greedy next-variable choice minimizing the number of newly crossing obligations;
3. order by first/last occurrence when H_j have interval-like structure;
4. if q is tiny, ignore ordering and use the q bound.

Benchmark predicted versus realized ROBDD nodes.

## 7. Why this can matter for Tau

The same q can describe very different formulas:

- q obligations with disjoint/local support may have tiny c(sigma);
- q highly interleaved obligations may have c(sigma) close to q.

Therefore raw disequation count is only a worst-case parameter. Crossing width may explain why some support-QE instances stay tiny while apparently similar instances blow up.

It also gives a principled backend decision:

- low estimated c: compile to ROBDD;
- high c but sparse support families: try ZDD/CNF representation;
- otherwise decline to Tau's existing path.

## 8. Next mathematical questions

1. Characterize the H_j sets produced by common Tau Boolean terms and recurrence formulas.
2. Determine when those sets are variable-convex under a natural minterm order.
3. Relate crossing width on support cells to the original BA-variable incidence graph, avoiding construction of all `2^k` support coordinates when possible.
4. Construct lower-bound families from expander-like H_j incidence to prove support OBDDs can genuinely blow up, preventing overgeneralization.
5. Compare crossing width with `rho(C)` and temporal lookback as joint predictors of synthesis complexity.
