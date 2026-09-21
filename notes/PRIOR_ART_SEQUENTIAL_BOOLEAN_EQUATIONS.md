# Prior art: sequential Boolean equations and the direct safety line

**Status:** PRIOR-ART CORRECTION / novelty guard. This note narrows claims in `EQUATIONAL_SAFETY_CUBE_GAME.md`; it does not refute the support-lifting theorem proved there.

## 1. Hao Wang, 1959

Hao Wang, **Circuit Synthesis by Solving Sequential Boolean Equations**, Zeitschrift für mathematische Logik und Grundlagen der Mathematik 5 (1959), 291–322; reprinted as Chapter X of *A Survey of Mathematical Logic* (1963).

The publisher summary describes the problem of solving sequential Boolean equations to obtain outputs as functionals of time and inputs, distinguishes deterministic, effective-predictive, and noneffective solutions, gives procedures for solvability/solution construction, and studies restricted quantifiers / richer languages.

Therefore:

> "reactive/sequential synthesis from Boolean equations" is classical prior art and must never be claimed as novel by OrbitSynthesis.

## 2. Even–Meyer, 1968/1969

Shimon Even and Albert R. Meyer, **Sequential Boolean Equations**, CMU technical report (March 1968), later IEEE Transactions on Computers (1969).

They consider binary independent variables X and binary dependent variables Y with discrete-time equation

`F(X,Y,dY)=0`,

where `dY(t)=Y(t+1)`.

Their basic solvability definition is:

> for every finite input sequence X there exists an output sequence Y satisfying the equation at every time.

They prove this is equivalent to a labeled-graph problem: for every sequence of edge labels there exists a path carrying those labels. They also study solutions with finite delay/lookahead and construct solutions when they exist.

This is very close to the finite Boolean transition graph underlying our equation-only work.

## 3. Their appendix already recalls general Boolean-equation elimination

The Even–Meyer appendix explicitly treats independent variables as fixed elements of a Boolean algebra and dependent variables as unknown elements of the same algebra. It recalls the classical expansion theorem and elimination of unknowns from ordinary Boolean equations.

So neither of the following is novel:

- ordinary Boolean-equation elimination over arbitrary Boolean algebras;
- finite graph/circuit synthesis from sequential equations over binary signals.

## 4. Exact distinction from our equation-only theorem

`EQUATIONAL_SAFETY_CUBE_GAME.md` studies a modern **causal two-player safety game** over an arbitrary Boolean algebra B:

1. current BA state tuple s is fixed;
2. environment chooses current BA input x;
3. controller observes it and chooses current BA output / next state y;
4. the equation `F(s,x,y)=0` must hold;
5. play repeats forever.

The theorem proves the commutation law

`CPre_B(W_A)=W_(Pre_2(A))`,

where `Pre_2` is the ordinary finite safety predecessor in the two-element Boolean algebra and

`W_A={s : Supp(s) subseteq A}`.

Consequences include:

- the whole BA greatest fixed point stays inside the principal support-ideal sublattice;
- it is determined by a finite game on the `2^k` Boolean state labels;
- a finite positional strategy lifts uniformly to a Boolean-term controller over B;
- atomlessness is unnecessary for the equation-only fragment.

This is best understood as a **lifting / commutation theorem**, not as invention of sequential Boolean-equation synthesis.

## 5. Why Even–Meyer does not immediately subsume the causal lifting theorem

Even–Meyer's basic solvability quantifiers are over whole finite sequences:

`for every input tape, there exists an output path`.

That permits the chosen path to depend on the whole tape. Their separate finite-delay notion explicitly allows bounded future input lookahead.

A causal safety strategy has the stronger prefix-consistency requirement that the output at a round depend only on information available at that round (plus controller memory/state), not on unknown future inputs.

Modern safety games enforce this through alternating round quantifiers / strategy semantics.

Thus the exact novelty question is:

> Does the literature already state the arbitrary-Boolean-algebra support lifting of the **causal safety predecessor / greatest fixed point**, with Boolean-term strategy extraction?

The sources inspected so far do not establish that exact statement, but absence of a found source is not proof of novelty.

## 6. Revised claim discipline

Do **not** write:

- "we reduce sequential Boolean equations to a finite graph";
- "we synthesize circuits from sequential Boolean equations for the first time";
- "the two-element Boolean game is new".

Potentially defensible claims, pending deeper prior-art search:

- the support-lattice commutation theorem for causal safety predecessor over arbitrary Boolean algebras;
- exact preservation of the principal-ideal carrier for equation-only games;
- uniform lifting of a finite positional strategy to Boolean terms over arbitrary B;
- extension to atomless inequality clauses via support-upset/hypergraph recurrence;
- integration of those carriers into Tau/ocLTL to avoid complete-type enumeration.

## 7. Stronger historical synthesis

There is a useful conceptual lineage:

`classical Boolean equation elimination`
→ `Wang sequential Boolean equations`
→ `Even–Meyer labeled graph solvability`
→ `modern alternating safety-game predecessor`
→ `OrbitSynthesis support lifting to arbitrary BA / ABA clause hypergraphs`.

A good paper should make this lineage explicit. It both improves scholarship and sharpens the genuinely new question.

## 8. PDF provenance note

The Even–Meyer CMU technical report was inspected through the public MIT-hosted PDF / parsed text. The PDF screenshot endpoint returned a cache-miss error during this research session, so no claim relies on visual interpretation of figures or typography; the cited claims above are present in the parsed text and abstract.
