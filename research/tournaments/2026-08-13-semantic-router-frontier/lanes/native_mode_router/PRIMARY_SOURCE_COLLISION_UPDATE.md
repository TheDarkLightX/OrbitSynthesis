# Primary-source collision update

Date: 2026-08-13  
Verdict: **no exact collision verified; novelty remains unknown**

## Classical ingredients

- Kenneth Krohn and John Rhodes, “Algebraic theory of machines. I. Prime decomposition theorem for finite semigroups and machines,” *Transactions of the AMS* 116 (1965), 450–464, DOI `10.1090/S0002-9947-1965-0188316-1`. This is the classical source line for the three-element flip-flop monoid. The abstract first-non-equal monoid is not claimed.
- A. F. Pixley, “The Ternary Discriminator Function in Universal Algebra,” *Mathematische Annalen* 191 (1971), 167–180. The ternary discriminator and its universal-algebraic role are classical.
- Balanced associative prefix evaluation is classical parallel-prefix/scan methodology and is not claimed.

## Closest quantitative comparator found

I. S. Sergeev, “On the complexity of fanout-bounded parallel prefix circuits,” *Discrete Analysis and Operations Research* 31(4) (2024), 151–167, DOI `10.33048/daio.2024.31.791`, studies universal prefix circuits with fanout bounded by two and proves a lower bound of order `(n-1)2^n` at exact logarithmic depth, together with upper bounds under extra depth.

That model is materially different from the theorem here:

- bounded fanout versus free fanout;
- one universal prefix network versus a shared family of fixed physical-word roots;
- binary input count `2^n` versus `q=3^w` branch roots;
- an arbitrary prefix operation versus the fixed three-state first-mismatch monoid embedded in the original `d/u` algebra;
- no parameter-free anchor or signed-router fusion in Sergeev’s stated model.

The comparison is nevertheless important: logarithmic-depth parallel prefix and its size/depth tradeoff are established territory. The paper should claim the exact embedding, all-root sharing law, fixed-algebra cost, fused signed-router semantics, and compiler consequence—not parallel prefix as an idea.

## Remaining high-risk prior art

A complete submission search still needs full-text comparison against:

1. Russian-language local-coding and multiplexer synthesis literature;
2. many-valued switching circuits over incomplete or precomplete bases;
3. automata/semigroup circuit implementations of the flip-flop monoid;
4. multi-output decoder and storage-access circuit complexity;
5. discriminator/switching-term quantitative constructions.

The bounded search supports a paper-worthy exact conjunction, but it is not a novelty opinion or freedom-to-operate analysis.
