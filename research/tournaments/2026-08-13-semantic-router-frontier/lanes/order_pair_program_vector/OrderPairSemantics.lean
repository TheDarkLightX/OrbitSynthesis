import ProgramVectorCost

/-!
# Order-pair semantics for exact strong-router program vectors

The three first-decision states are encoded as

* equality `E = (0,0)`;
* loss `L = (1,0)`; and
* gain `G = (0,1)`.

On these rails the original discriminator is exactly the left-to-right
first-decision product.  Both rails therefore compose in one operation layer.
-/

namespace OrbitSynthesis.StrongSignedRouter.OrderPairProgramVector

open OrbitSynthesis.StrongSignedRouter
open OrbitSynthesis.StrongSignedRouter.ProgramVector
open OrbitSynthesis.StrongSignedRouter.ProgramVectorCost

/-- The third first-mismatch state: neither equality nor gain. -/
def lossBit (summary : SegmentSummary) : Bool :=
  (!summary.eqFlag) && (!summary.gain)

/-- Direct two-rail encoding of the three legal first-decision states. -/
structure OrderPair where
  loss : Bool
  gain : Bool
  deriving DecidableEq, Repr

/-- The fixed discriminator acts coordinatewise as first-decision product. -/
def OrderPair.comp (left right : OrderPair) : OrderPair :=
  ⟨StrongSignedRouter.disc left.loss left.gain right.loss,
    StrongSignedRouter.disc left.gain left.loss right.gain⟩

/-- Translate the historical equality/gain summary into the new rails. -/
def pairOfSummary (summary : SegmentSummary) : OrderPair :=
  ⟨lossBit summary, summary.gain⟩

@[simp] theorem pairOfSummary_loss (summary : SegmentSummary) :
    (pairOfSummary summary).loss = lossBit summary := rfl

@[simp] theorem pairOfSummary_gain (summary : SegmentSummary) :
    (pairOfSummary summary).gain = summary.gain := rfl

/-- The new pair product is not merely equivalent bookkeeping: it is exactly
segment composition. -/
theorem pairOfSummary_comp (left right : SegmentSummary) :
    pairOfSummary (left.comp right) =
      (pairOfSummary left).comp (pairOfSummary right) := by
  rcases left with ⟨leftEqual, leftGain⟩
  rcases right with ⟨rightEqual, rightGain⟩
  cases leftEqual <;> cases leftGain <;>
    cases rightEqual <;> cases rightGain <;> rfl

/-- The discriminator realization is associative even before restricting to
legal pairs. -/
theorem OrderPair.comp_assoc (left middle right : OrderPair) :
    (left.comp middle).comp right = left.comp (middle.comp right) := by
  rcases left with ⟨leftLoss, leftGain⟩
  rcases middle with ⟨middleLoss, middleGain⟩
  rcases right with ⟨rightLoss, rightGain⟩
  cases leftLoss <;> cases leftGain <;>
    cases middleLoss <;> cases middleGain <;>
    cases rightLoss <;> cases rightGain <;> rfl

/-- The negative-cell upper rail `H=E or G` is the complement of loss. -/
def upperBit (summary : SegmentSummary) : Bool := !(lossBit summary)

/-- `H` also composes in one discriminator node. -/
theorem upperBit_comp (left right : SegmentSummary) :
    upperBit (left.comp right) =
      StrongSignedRouter.disc left.gain (lossBit left) (upperBit right) := by
  rcases left with ⟨leftEqual, leftGain⟩
  rcases right with ⟨rightEqual, rightGain⟩
  cases leftEqual <;> cases leftGain <;>
    cases rightEqual <;> cases rightGain <;> rfl

/-- Load-bearing suffix reuse: replacing a final physical middle digit by a
right digit turns the upper rail into the gain rail. -/
theorem upper_middle_eq_gain_right (prefix : SegmentSummary) (target : Digit)
    (prefixDisjoint : (prefix.eqFlag && prefix.gain) = false) :
    upperBit (prefix.comp (digitSummary target .middle)) =
      (prefix.comp (digitSummary target .right)).gain := by
  rcases prefix with ⟨prefixEqual, prefixGain⟩
  cases prefixEqual <;> cases prefixGain <;> cases target <;>
    simp_all [upperBit, lossBit, SegmentSummary.comp, digitSummary]

/-- Original-signature terms carrying one `(L,G)` pair. -/
structure PairTerms (Var : Type) where
  lossTerm : QTerm Var
  gainTerm : QTerm Var

/-- Semantic realization under the explicit nonbinary-anchor environment. -/
def PairTerms.Realizes {Var : Type} (terms : PairTerms Var)
    (environment : Var → Q) (summary : SegmentSummary) : Prop :=
  terms.lossTerm.eval environment = qBit (lossBit summary) ∧
    terms.gainTerm.eval environment = qBit summary.gain

/-- Maximum operation depth of the two distinguished roots. -/
def PairTerms.depth {Var : Type} (terms : PairTerms Var) : Nat :=
  max terms.lossTerm.depth terms.gainTerm.depth

/-- One discriminator node per output rail. -/
def composePairTerms {Var : Type} (left right : PairTerms Var) : PairTerms Var :=
  ⟨.disc left.lossTerm left.gainTerm right.lossTerm,
    .disc left.gainTerm left.lossTerm right.gainTerm⟩

/-- Exact semantic correctness of the one-layer pair product. -/
theorem composePairTerms_correct {Var : Type} (environment : Var → Q)
    (left right : PairTerms Var) (leftSummary rightSummary : SegmentSummary)
    (leftCorrect : left.Realizes environment leftSummary)
    (rightCorrect : right.Realizes environment rightSummary) :
    (composePairTerms left right).Realizes environment
      (leftSummary.comp rightSummary) := by
  rcases leftSummary with ⟨leftEqual, leftGain⟩
  rcases rightSummary with ⟨rightEqual, rightGain⟩
  cases leftEqual <;> cases leftGain <;>
    cases rightEqual <;> cases rightGain <;>
    simp_all [PairTerms.Realizes, composePairTerms, lossBit, QTerm.eval,
      qDisc, qBit, SegmentSummary.comp, StrongSignedRouter.disc]

/-- Pair composition adds one operation layer, rather than the two layers in
the historical equality/gain realization. -/
theorem composePairTerms_depth_le {Var : Type} (left right : PairTerms Var) :
    (composePairTerms left right).depth ≤ max left.depth right.depth + 1 := by
  simp only [PairTerms.depth, composePairTerms, QTerm.depth]
  omega

/-- Shared one-digit auxiliary `u(x)`. -/
def digitAux {Var : Type} (digit : Var) : QTerm Var :=
  .unary (.variable digit)

/-- The only nonzero one-digit gain function, `u(u(x))`. -/
def digitGain {Var : Type} (digit : Var) : QTerm Var :=
  .unary (digitAux digit)

/-- Loss for physical digit two. -/
def digitLossTwo {Var : Type} (anchor digit : Var) : QTerm Var :=
  .disc (anchorZero anchor) (.variable digit) (digitAux digit)

/-- Loss for physical digit zero. -/
def digitLossZero {Var : Type} (anchor digit : Var) : QTerm Var :=
  .disc (.variable digit) (anchorTwo anchor) (digitAux digit)

/-- Four nodes beyond the two shared anchor-name nodes realize all three
one-digit physical summaries. -/
def digitPairTerms {Var : Type} (anchor digit : Var) : Digit → PairTerms Var
  | .left => ⟨digitLossZero anchor digit, anchorZero anchor⟩
  | .middle => ⟨digitAux digit, anchorZero anchor⟩
  | .right => ⟨digitLossTwo anchor digit, digitGain digit⟩

/-- Exact one-digit legality and semantics under `A=2`. -/
theorem digitPairTerms_correct {Var : Type} (environment : Var → Q)
    (anchor digit : Var) (target physical : Digit)
    (anchorValue : environment anchor = .two)
    (digitValue : environment digit = digitQ target) :
    (digitPairTerms anchor digit physical).Realizes environment
      (digitSummary target physical) := by
  cases target <;> cases physical <;>
    simp [PairTerms.Realizes, digitPairTerms, digitAux, digitGain,
      digitLossTwo, digitLossZero, lossBit, digitSummary, QTerm.eval,
      qDisc, qUnary, qBit, anchorZero, anchorOne, anchorTwo, digitQ,
      anchorValue, digitValue]

/-- One-digit pair roots have depth at most three above raw inputs. -/
theorem digitPairTerms_depth_le_three {Var : Type} (anchor digit : Var)
    (physical : Digit) :
    (digitPairTerms anchor digit physical).depth ≤ 3 := by
  cases physical <;>
    norm_num [PairTerms.depth, digitPairTerms, digitAux, digitGain,
      digitLossTwo, digitLossZero, anchorZero, anchorOne, anchorTwo,
      QTerm.depth]

/-- The construction stays in the declared constant-free `d/u` signature. -/
theorem digitPairTerms_originalSignature {Var : Type} (anchor digit : Var)
    (physical : Digit) :
    (digitPairTerms anchor digit physical).lossTerm.OriginalSignature ∧
      (digitPairTerms anchor digit physical).gainTerm.OriginalSignature := by
  cases physical <;>
    simp [digitPairTerms, digitAux, digitGain, digitLossTwo, digitLossZero]

/-- Exact ordered base-cell controls from the order pair. -/
def frozenPairBits (negative : Bool) (summary : SegmentSummary) : Bool × Bool :=
  if negative then (summary.gain, upperBit summary)
  else (lossBit summary, summary.gain)

/-- The new rails reproduce the frozen first/second slot formulas exactly. -/
theorem frozenPairBits_correct (negative : Bool) (summary : SegmentSummary)
    (disjoint : (summary.eqFlag && summary.gain) = false) :
    frozenPairBits negative summary =
      (firstControlBit summary.eqFlag summary.gain negative,
        secondControlBit summary.eqFlag summary.gain negative) := by
  rcases summary with ⟨equal, gain⟩
  cases negative <;> cases equal <;> cases gain <;>
    simp_all [frozenPairBits, upperBit, lossBit, firstControlBit,
      secondControlBit]

/-- End-to-end semantic bridge to the already frozen recursive program. -/
theorem frozenPairBits_match_program (n : Nat) (root : Sign)
    (target branch : Address n) :
    frozenPairBits
        (boolXor (isNegative root) (middleParity n branch))
        (addressSummary n target branch) =
      (program root n (.project target) (.first, branch),
        program root n (.project target) (.second, branch)) := by
  rw [projection_program_first, projection_program_second]
  exact frozenPairBits_correct
    (boolXor (isNegative root) (middleParity n branch))
    (addressSummary n target branch)
    (addressSummary_disjoint n target branch)

end OrbitSynthesis.StrongSignedRouter.OrderPairProgramVector
