# Direct-Q lane: packed semantic dynamic programming

Date: 2026-08-13

## Status

**Result: exact bounded `NO_HIT`, with a reusable non-SMT synthesis engine.**

No direct-Q R7, R8, R9, or R10 router was found in the explicitly enumerated
frozen-R6 neighborhoods. The result is useful narrowing, not a global
capacity theorem. It says that simply inserting new branch leaves into the
known R6 layout, or repartitioning its nine branch slots, does not preserve
all old projections while adding the requested new ones in the tested scope.

The search uses exact packed `Q^q` truth tables and bottom-up subtree semantic
sets. It does not use valuation-by-valuation SMT and does not use the Boolean
two-extreme proposal. In particular, it evaluates the actual discriminator

```text
d(x,y,z)=z if x=y, and x otherwise.
```

The frozen R6 witness was independently replayed first. All 4,374 projection
cases passed, and a one-control mutation caused 162 failures.

## 1. Representation

Order the `3^q` valuations of `Q^q` lexicographically. A `Q`-valued truth
table is the exact triple of Python integer bitsets

```text
(M_0,M_1,M_2),
```

where bit `a` belongs to `M_v` exactly when the function takes value `v` on
valuation `a`. The three masks are disjoint and cover the whole valuation
universe.

For packed semantics `A,B,C`, let

```text
E=(A_0 & B_0) | (A_1 & B_1) | (A_2 & B_2).
```

Then the discriminator is evaluated word-parallel by

```text
D_v=((not E) & A_v) | (E & C_v),  v in {0,1,2},
```

with the complement restricted to the finite universe mask. A branch leaf
has one fixed packed semantic. A program-control leaf has the exact set of
three constant semantics. At each internal node, the dynamic program takes
the discriminator closure of its three child sets and deduplicates equal
truth tables.

The root target test avoids materializing its full closure. For every
left/right pair it computes `E`, checks that the left semantic agrees with the
target off `E`, and asks whether some fallback agrees with the target on `E`.
This condition is necessary and sufficient for an exact root match.

## 2. Algorithmic cost

Let `T=3^q` and let a node's child semantic-set sizes be `a,b,c`. A direct
closure takes `O(a*b*c*T/w)` word operations and stores at most `a*b*c`
distinct triples of `T` bits, where `w` is the host integer word scale. The
actual sets in the frozen depth-three neighborhoods are small enough for
local CPU and memory. Bottom triples are cached; middle subtrees are cached
only in the small-q families where reuse beats their memory cost.

For R10, constructing all `3^10`-bit semantic sets for all 3,060 candidates
would be wasteful. The checker first applies an exact necessary condition:
for every proposed new target, specialize every other branch uniformly to
each of `0,1,2`; the resulting unary semantic closure must contain the
identity. Only one candidate survives all these exact specializations, and
that candidate is then checked with the full packed `Q^10` semantics.

## 3. Frozen R6 control-insertion neighborhoods

The R6 full depth-three tree has 27 leaves: 18 independent absolute-Q control
positions and nine branch occurrences with multiplicities

```text
b0:2, b1:1, b2:1, b3:1, b4:3, b5:1.
```

For direct R7, radius `k` replaces `k` of the 18 controls by occurrences of a
new branch `b6`, leaving every other leaf frozen. The exact results are:

| Radius | Candidates | Skeletons projecting `b6` | Full R7 hits |
|---:|---:|---:|---:|
| 1 | 18 | 0 | 0 |
| 2 | 153 | 0 | 0 |
| 3 | 816 | 5 | 0 |
| 4 | 3,060 | 29 | 0 |

The radius-three case shows why single-target reachability is not enough. The
best survivor projects only `b1,b3,b6`; it loses four of the old projections.
At radius four, every new-target survivor projects only `b6`.

Separately, the checker enumerates every partition of the nine frozen branch
positions into seven nonempty branch labels while keeping all 18 control
positions fixed. There are exactly 462 unlabeled partitions: one triple plus
six singletons, or two pairs plus five singletons. None is a full R7 router.

## 4. Minimal R8--R10 insertion neighborhoods

For R8, R9, and R10, the minimal insertion family replaces respectively two,
three, or four frozen controls by one occurrence of each new branch. A
canonical increasing label order is enough because another order is a global
renaming of the new variables.

| Target | Insertions | Candidates modulo renaming | Result |
|---:|---:|---:|---|
| R8 | 2 | 153 | `NO_HIT`; no skeleton projects both new targets |
| R9 | 3 | 816 | `NO_HIT`; no skeleton projects all three new targets |
| R10 | 4 | 3,060 | `NO_HIT`; one specialization survivor fails all four new targets under full `Q^10` replay |

The unique R10 specialization survivor inserts branches at leaf positions
`(0,6,18,24)`. Full packed replay proves that it projects none of
`b6,b7,b8,b9`. Every other candidate has an explicit failed unary
specialization, which is already a proof that it cannot be a full router.

## 5. Interpretation

The negative pattern is structural: adding branch leaves removes control
freedom. At radius three a new direct-Q projection first becomes possible,
but its program flexibility is bought by destroying most of the original
projection capacity. The fixed R6 layout is therefore a poor seed for direct
alphabet capacity growth.

This does not say direct-Q R7 is impossible. The next direct-Q search should
change a middle-subtree topology or jointly relocate branch and control
leaves, rather than continue monotone control-to-branch insertion. The packed
semantic DP is suitable as the exact evaluator for such a search, with a
separate bounded outer enumerator or symmetry-reduced optimizer.

## 6. Falsifiers and boundaries

| Falsifier | Result |
|---|---|
| `F-input` | Baseline source bytes are pinned at SHA-256 `c38e9c006f0109397827345c42acb24debae55a373ee6861b8eafc35e1b65265`. |
| `F-grammar` | Every candidate is one complete depth-three `d` tree; no new gate or uncharged depth is introduced. |
| `F-control` | Each target gets independent constants in its control leaves; they are program/address values, never payload-dependent. |
| `F-monotone` | The false naive Boolean-majority/extreme-valuation route is not used. Full direct-Q semantics owns acceptance. |
| `F-quotient` | Packing is lossless: it stores all `3^q` valuations in three disjoint planes. |
| `F-tree` | Results concern only the exact full-tree leaf neighborhoods stated above. |
| `F-degenerate` | Repeated labels, every target, constants `0,1,2`, malformed tree width, and an effective control mutation are checked. |
| `F-boundary` | `NO_HIT` is not global R7--R10 `UNSAT`, an arbitrary-Q-term lower bound, novelty, or FTO evidence. |

Absolute `0,1,2` controls are intended for the compiler's nonbinary branch,
where the frozen anchor supplies legal dynamic names. This lane does not
claim such absolute constants on the Boolean branch.

## 7. Deterministic evidence

Checker:

`research/tournaments/2026-08-13-semantic-router-frontier/lanes/direct_q/search_direct_q_bitparallel.py`

Checker SHA-256:

`46ef0c3037912c698f8a6327720b2469f73b37e8472860caa53e4cf7f6bf2c20`

Replay:

```text
python3 research/tournaments/2026-08-13-semantic-router-frontier/lanes/direct_q/search_direct_q_bitparallel.py
python3 -O research/tournaments/2026-08-13-semantic-router-frontier/lanes/direct_q/search_direct_q_bitparallel.py
```

Both runs exit zero with byte-identical output and semantic SHA-256

`3711f2d9370537c9bf9b587385f4a540e38006d3f52d99937a19139d4b39b029`.

Across the displayed families the checker enumerates 8,538 candidate
skeletons, in addition to the frozen R6 replay and effective mutation. The
receipt is `receipt.json` in this directory.

## 8. Verdict

**Exact verdict for the enumerated neighborhoods:** `NO_HIT`.

**Global direct-Q R7--R10 verdict:** `UNKNOWN`.

No paper, novelty, optimality, patent, license, FTO, practical-performance,
or Tau conclusion is authorized by this lane.

