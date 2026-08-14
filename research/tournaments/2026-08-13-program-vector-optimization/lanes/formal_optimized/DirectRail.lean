import ProgramVectorCost
import Mathlib.Data.Nat.Log

/-!
# Formal direct-rail program vectors

This file formalizes the frozen `<= 3q` construction from the independent
lower-bound lane.  It uses only the original discriminator/unary term grammar
imported from `ProgramVectorCost`; in particular, there is no constant term
constructor and no free negation.
-/

namespace OrbitSynthesis.StrongSignedRouter.FormalOptimized

open OrbitSynthesis.StrongSignedRouter
open OrbitSynthesis.StrongSignedRouter.ProgramVector
open OrbitSynthesis.StrongSignedRouter.ProgramVectorCost

/-- The discriminator restricted to Boolean values. -/
def boolDisc (x y z : Bool) : Bool :=
  if x = y then z else x

theorem qDisc_qBit (x y z : Bool) :
    qDisc (qBit x) (qBit y) (qBit z) = qBit (boolDisc x y z) := by
  cases x <;> cases y <;> cases z <;> rfl

/-- Direct rails for the two absorbing first-mismatch modes.  The remaining
valid state `(false,false)` is equality/projection. -/
structure Rails where
  zeroMode : Bool
  oneMode : Bool
  deriving DecidableEq, Repr

def Rails.equal : Rails := ⟨false, false⟩
def Rails.zero : Rails := ⟨true, false⟩
def Rails.one : Rails := ⟨false, true⟩

/-- Left-to-right first-mismatch composition. -/
def Rails.comp (left right : Rails) : Rails :=
  ⟨boolDisc left.zeroMode left.oneMode right.zeroMode,
    boolDisc left.oneMode left.zeroMode right.oneMode⟩

@[simp] theorem Rails.equal_comp (right : Rails) :
    Rails.equal.comp right = right := by
  rcases right with ⟨zeroMode, oneMode⟩
  rfl

@[simp] theorem Rails.zero_comp (right : Rails) :
    Rails.zero.comp right = Rails.zero := by
  rcases right with ⟨zeroMode, oneMode⟩
  rfl

@[simp] theorem Rails.one_comp (right : Rails) :
    Rails.one.comp right = Rails.one := by
  rcases right with ⟨zeroMode, oneMode⟩
  rfl

theorem Rails.comp_assoc (left middle right : Rails) :
    (left.comp middle).comp right = left.comp (middle.comp right) := by
  rcases left with ⟨leftZero, leftOne⟩
  rcases middle with ⟨middleZero, middleOne⟩
  rcases right with ⟨rightZero, rightOne⟩
  cases leftZero <;> cases leftOne <;>
    cases middleZero <;> cases middleOne <;>
      cases rightZero <;> cases rightOne <;> rfl

/-- The direct rails represented by two legal original-signature terms. -/
structure RailTerms (Var : Type) where
  zeroTerm : QTerm Var
  oneTerm : QTerm Var

def RailTerms.Realizes {Var : Type} (terms : RailTerms Var)
    (environment : Var → Q) (rails : Rails) : Prop :=
  terms.zeroTerm.eval environment = qBit rails.zeroMode ∧
    terms.oneTerm.eval environment = qBit rails.oneMode

def RailTerms.depth {Var : Type} (terms : RailTerms Var) : Nat :=
  max terms.zeroTerm.depth terms.oneTerm.depth

/-- Two discriminator nodes, evaluated in parallel, compose two rail pairs. -/
def composeRailTerms {Var : Type} (left right : RailTerms Var) : RailTerms Var :=
  ⟨.disc left.zeroTerm left.oneTerm right.zeroTerm,
    .disc left.oneTerm left.zeroTerm right.oneTerm⟩

theorem composeRailTerms_correct {Var : Type} (environment : Var → Q)
    (left right : RailTerms Var) (leftRails rightRails : Rails)
    (leftCorrect : left.Realizes environment leftRails)
    (rightCorrect : right.Realizes environment rightRails) :
    (composeRailTerms left right).Realizes environment
      (leftRails.comp rightRails) := by
  rcases leftCorrect with ⟨leftZero, leftOne⟩
  rcases rightCorrect with ⟨rightZero, rightOne⟩
  constructor <;>
    simp [composeRailTerms, QTerm.eval,
      leftZero, leftOne, rightZero, rightOne, qDisc_qBit, Rails.comp]

theorem composeRailTerms_originalSignature {Var : Type}
    (left right : RailTerms Var) :
    (composeRailTerms left right).zeroTerm.OriginalSignature ∧
      (composeRailTerms left right).oneTerm.OriginalSignature := by
  simp [composeRailTerms]

theorem composeRailTerms_depth_le {Var : Type} (left right : RailTerms Var) :
    (composeRailTerms left right).depth ≤ max left.depth right.depth + 1 := by
  simp [composeRailTerms, RailTerms.depth, QTerm.depth]
  omega

/-- Convert the frozen equality/gain summary to zero/one absorbing rails. -/
def railsOfSummary (summary : SegmentSummary) : Rails :=
  ⟨(!summary.eqFlag) && (!summary.gain), summary.gain⟩

theorem railsOfSummary_comp (left right : SegmentSummary)
    (leftDisjoint : (left.eqFlag && left.gain) = false)
    (rightDisjoint : (right.eqFlag && right.gain) = false) :
    railsOfSummary (left.comp right) =
      (railsOfSummary left).comp (railsOfSummary right) := by
  rcases left with ⟨leftEqual, leftGain⟩
  rcases right with ⟨rightEqual, rightGain⟩
  cases leftEqual <;> cases leftGain <;>
    cases rightEqual <;> cases rightGain <;>
      simp_all [railsOfSummary, SegmentSummary.comp, Rails.comp, boolDisc]

def RailTerms.RealizesSummary {Var : Type} (terms : RailTerms Var)
    (environment : Var → Q) (summary : SegmentSummary) : Prop :=
  terms.Realizes environment (railsOfSummary summary)

theorem composeRailTerms_summary_correct {Var : Type}
    (environment : Var → Q) (left right : RailTerms Var)
    (leftSummary rightSummary : SegmentSummary)
    (leftCorrect : left.RealizesSummary environment leftSummary)
    (rightCorrect : right.RealizesSummary environment rightSummary)
    (leftDisjoint : (leftSummary.eqFlag && leftSummary.gain) = false)
    (rightDisjoint : (rightSummary.eqFlag && rightSummary.gain) = false) :
    (composeRailTerms left right).RealizesSummary environment
      (leftSummary.comp rightSummary) := by
  rw [RailTerms.RealizesSummary, railsOfSummary_comp leftSummary rightSummary
    leftDisjoint rightDisjoint]
  exact composeRailTerms_correct environment left right
    (railsOfSummary leftSummary) (railsOfSummary rightSummary)
      leftCorrect rightCorrect

/-- Four non-name nodes materialize all six one-digit rails. -/
def digitRailTerms {Var : Type} (anchor digit : Var) : Digit → RailTerms Var
  | .left =>
      ⟨.disc (.variable digit) (anchorTwo anchor) (anchorOne anchor),
        anchorZero anchor⟩
  | .middle =>
      ⟨.disc (anchorOne anchor) (.variable digit) (anchorZero anchor),
        anchorZero anchor⟩
  | .right =>
      ⟨.disc (anchorZero anchor) (.variable digit) (anchorOne anchor),
        .disc (.variable digit) (anchorTwo anchor) (anchorZero anchor)⟩

theorem digitRailTerms_correct {Var : Type} (environment : Var → Q)
    (anchor digit : Var) (target physical : Digit)
    (anchorValue : environment anchor = .two)
    (digitValue : environment digit = digitQ target) :
    (digitRailTerms anchor digit physical).RealizesSummary environment
      (digitSummary target physical) := by
  cases target <;> cases physical <;>
    simp [RailTerms.RealizesSummary, RailTerms.Realizes, digitRailTerms,
      railsOfSummary, digitSummary, anchorTwo, anchorOne, anchorZero,
      QTerm.eval, qDisc, qUnary, qBit, anchorValue, digitValue, digitQ]

theorem digitRailTerms_originalSignature {Var : Type} (anchor digit : Var)
    (physical : Digit) :
    (digitRailTerms anchor digit physical).zeroTerm.OriginalSignature ∧
      (digitRailTerms anchor digit physical).oneTerm.OriginalSignature := by
  cases physical <;> simp [digitRailTerms]

theorem digitRailTerms_depth_le_three {Var : Type} (anchor digit : Var)
    (physical : Digit) :
    (digitRailTerms anchor digit physical).depth ≤ 3 := by
  cases physical <;>
    norm_num [RailTerms.depth, digitRailTerms, anchorTwo, anchorOne,
      anchorZero, QTerm.depth]

/-- Positive cells directly expose `(Z,O)`; negative cells expose
`(O,not Z)`. -/
def finalRailPairTerms {Var : Type} (negative : Bool)
    (rails : RailTerms Var) : QTerm Var × QTerm Var :=
  if negative then (rails.oneTerm, .unary rails.zeroTerm)
  else (rails.zeroTerm, rails.oneTerm)

def railTermPairDepth {Var : Type} (pair : QTerm Var × QTerm Var) : Nat :=
  max pair.1.depth pair.2.depth

theorem finalRailPairTerms_correct {Var : Type} (environment : Var → Q)
    (negative : Bool) (terms : RailTerms Var) (summary : SegmentSummary)
    (termsCorrect : terms.RealizesSummary environment summary)
    (disjoint : (summary.eqFlag && summary.gain) = false) :
    (finalRailPairTerms negative terms).1.eval environment =
        qBit (firstControlBit summary.eqFlag summary.gain negative) ∧
      (finalRailPairTerms negative terms).2.eval environment =
        qBit (secondControlBit summary.eqFlag summary.gain negative) := by
  rcases termsCorrect with ⟨zeroCorrect, oneCorrect⟩
  rcases summary with ⟨eqFlag, gain⟩
  cases negative <;> cases eqFlag <;> cases gain <;>
    simp_all [finalRailPairTerms, railsOfSummary,
      firstControlBit, secondControlBit,
      QTerm.eval, qUnary, qBit]

theorem finalRailPairTerms_match_frozen_program {Var : Type}
    (environment : Var → Q) (n : Nat) (root : Sign)
    (target branch : Address n) (terms : RailTerms Var)
    (termsCorrect : terms.RealizesSummary environment
      (addressSummary n target branch)) :
    (finalRailPairTerms
        (boolXor (isNegative root) (middleParity n branch)) terms).1.eval
          environment = qBit (program root n (.project target) (.first, branch)) ∧
      (finalRailPairTerms
        (boolXor (isNegative root) (middleParity n branch)) terms).2.eval
          environment = qBit (program root n (.project target) (.second, branch)) := by
  rw [projection_program_first, projection_program_second]
  exact finalRailPairTerms_correct environment
    (boolXor (isNegative root) (middleParity n branch)) terms
      (addressSummary n target branch) termsCorrect
      (addressSummary_disjoint n target branch)

theorem finalRailPairTerms_originalSignature {Var : Type}
    (negative : Bool) (terms : RailTerms Var) :
    (finalRailPairTerms negative terms).1.OriginalSignature ∧
      (finalRailPairTerms negative terms).2.OriginalSignature := by
  cases negative <;> simp [finalRailPairTerms]

theorem finalRailPairTerms_depth_le {Var : Type}
    (negative : Bool) (terms : RailTerms Var) :
    railTermPairDepth (finalRailPairTerms negative terms) ≤ terms.depth + 1 := by
  cases negative <;>
    simp [railTermPairDepth, finalRailPairTerms, RailTerms.depth, QTerm.depth]
  omega

/-- A Boolean test that every physical digit in a paired suffix is left or
middle, never right. -/
def noRightPhysical : List (Digit × Digit) → Bool
  | [] => true
  | pair :: pairs => (pair.2 != .right) && noRightPhysical pairs

theorem summarizePairs_gain_false_of_noRight :
    ∀ pairs : List (Digit × Digit),
      noRightPhysical pairs = true → (summarizePairs pairs).gain = false
  | [], _ => rfl
  | (target, physical) :: pairs, noRight => by
      have tailNoRight : noRightPhysical pairs = true := by
        cases physical <;> simp_all [noRightPhysical]
      have tailGain := summarizePairs_gain_false_of_noRight pairs tailNoRight
      cases target <;> cases physical <;>
        simp_all [noRightPhysical, summarizePairs, digitSummary,
          SegmentSummary.comp]

/-- Appending a physical suffix over `{left,middle}` does not change the
one-mode rail.  This is the formal trailing-`{0,1}` reuse identity. -/
theorem trailing_noRight_gain_reuse (initial suffix : List (Digit × Digit))
    (noRight : noRightPhysical suffix = true) :
    (summarizePairs (initial ++ suffix)).gain = (summarizePairs initial).gain := by
  rw [summarizePairs_append]
  have suffixGain := summarizePairs_gain_false_of_noRight suffix noRight
  simp [SegmentSummary.comp, suffixGain]

/-- Root-sign-specific number of negative bottom cells. -/
def negativeCellCount (root : Sign) (width : Nat) : Nat :=
  match root with
  | .positive => (parityCounts width).2
  | .negative => (parityCounts width).1

theorem negativeCellCount_le (root : Sign) (width : Nat) :
    negativeCellCount root width ≤ (3 ^ width + 1) / 2 := by
  cases root with
  | positive =>
      have differenceRule := parityCounts_even_eq_odd_add_one width
      rw [← parityCounts_even_closed width]
      simp only [negativeCellCount]
      omega
  | negative =>
      simp [negativeCellCount, parityCounts_even_closed]

/-- Exact hash-consed rail-node ledger for balanced blocks.  The last term is
the number of distinct nonzero right one-mode rails, shared across left words. -/
def railNodes : Nat → Nat
  | 0 => 0
  | 1 => 4
  | width@(_ + 2) =>
      railNodes (width / 2) + railNodes ((width + 1) / 2) + 3 ^ width +
        3 ^ (width / 2) * ((3 ^ ((width + 1) / 2) - 1) / 2)
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

def signedRailNodes (root : Sign) (width : Nat) : Nat :=
  if width = 0 then 0 else railNodes width + negativeCellCount root width

def totalRailNodes (root : Sign) (width : Nat) : Nat :=
  2 + signedRailNodes root width

/-- Rail preprocessing depth above raw anchor/address terminals. -/
def railDepth : Nat → Nat
  | 0 => 0
  | 1 => 3
  | width@(_ + 2) =>
      max (railDepth (width / 2)) (railDepth ((width + 1) / 2)) + 1
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

def totalRailDepth (width : Nat) : Nat :=
  if width = 0 then 2 else railDepth width + 1

theorem railNodes_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    railNodes width =
      railNodes (width / 2) + railNodes ((width + 1) / 2) + 3 ^ width +
        3 ^ (width / 2) * ((3 ^ ((width + 1) / 2) - 1) / 2) := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [railNodes]

theorem railDepth_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    railDepth width =
      max (railDepth (width / 2)) (railDepth ((width + 1) / 2)) + 1 := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [railDepth]

theorem railNodes_small :
    railNodes 1 = 4 ∧ railNodes 2 = 20 ∧ railNodes 3 = 63 := by
  norm_num [railNodes]

/-- Convenient all-width rail-library envelope. -/
theorem three_mul_railNodes_le_seven_mul_pow (width : Nat) :
    3 * railNodes width ≤ 7 * 3 ^ width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 4
      · interval_cases width <;> norm_num [railNodes]
      · have widthAtLeast : 4 ≤ width := by omega
        obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
          ⟨width - 2, by omega⟩
        let leftWidth := (rest + 2) / 2
        let rightWidth := (rest + 2 + 1) / 2
        let leftPower := 3 ^ leftWidth
        let rightPower := 3 ^ rightWidth
        have leftLess : leftWidth < rest + 2 := by
          dsimp [leftWidth]
          omega
        have rightLess : rightWidth < rest + 2 := by
          dsimp [rightWidth]
          omega
        have leftBound := ih leftWidth leftLess
        have rightBound := ih rightWidth rightLess
        have leftWidthAtLeast : 2 ≤ leftWidth := by
          dsimp [leftWidth]
          omega
        have rightWidthAtLeast : 2 ≤ rightWidth := by
          dsimp [rightWidth]
          omega
        have leftPowerAtLeast : 9 ≤ leftPower := by
          dsimp [leftPower]
          calc
            9 = 3 ^ 2 := by norm_num
            _ ≤ 3 ^ leftWidth := Nat.pow_le_pow_right (by omega) leftWidthAtLeast
        have rightPowerAtLeast : 9 ≤ rightPower := by
          dsimp [rightPower]
          calc
            9 = 3 ^ 2 := by norm_num
            _ ≤ 3 ^ rightWidth := Nat.pow_le_pow_right (by omega) rightWidthAtLeast
        have productPower : leftPower * rightPower = 3 ^ (rest + 2) := by
          dsimp [leftPower, rightPower, leftWidth, rightWidth]
          exact ternary_cross_product (rest + 2)
        have childPowers : 14 * leftPower + 14 * rightPower ≤
            5 * (leftPower * rightPower) := by
          nlinarith
        have halfBound :
            2 * ((rightPower - 1) / 2) ≤ rightPower - 1 :=
          Nat.mul_div_le (rightPower - 1) 2
        have crossBound :
            2 * (leftPower * ((rightPower - 1) / 2)) ≤
              leftPower * rightPower := by
          have multiplied := Nat.mul_le_mul_left leftPower halfBound
          calc
            2 * (leftPower * ((rightPower - 1) / 2)) =
                leftPower * (2 * ((rightPower - 1) / 2)) := by ac_rfl
            _ ≤ leftPower * (rightPower - 1) := multiplied
            _ ≤ leftPower * rightPower :=
              Nat.mul_le_mul_left leftPower (Nat.sub_le rightPower 1)
        have doubledBound :
            6 * (railNodes leftWidth + railNodes rightWidth +
                leftPower * rightPower +
                leftPower * ((rightPower - 1) / 2)) ≤
              14 * (leftPower * rightPower) := by
          omega
        have namedBound :
            3 * (railNodes leftWidth + railNodes rightWidth +
                leftPower * rightPower +
                leftPower * ((rightPower - 1) / 2)) ≤
              7 * (leftPower * rightPower) := by
          omega
        rw [railNodes_recurrence (rest + 2) (by omega)]
        rw [← productPower]
        exact namedBound

/-- Full signed vector, including the two anchor names, is at most `3q`. -/
theorem totalRailNodes_le_three_mul_pow (root : Sign) (width : Nat) :
    totalRailNodes root width ≤ 3 * 3 ^ width := by
  by_cases small : width < 3
  · interval_cases width <;>
      cases root <;>
      norm_num [totalRailNodes, signedRailNodes, railNodes,
        negativeCellCount, parityCounts]
  · have widthAtLeast : 3 ≤ width := by omega
    have railBound := three_mul_railNodes_le_seven_mul_pow width
    have negativeBound := negativeCellCount_le root width
    have halfBound : 2 * ((3 ^ width + 1) / 2) ≤ 3 ^ width + 1 :=
      Nat.mul_div_le (3 ^ width + 1) 2
    have negativeTwice : 2 * negativeCellCount root width ≤ 3 ^ width + 1 := by
      omega
    have powerAtLeast : 15 ≤ 3 ^ width := by
      calc
        15 ≤ 3 ^ 3 := by norm_num
        _ ≤ 3 ^ width := Nat.pow_le_pow_right (by omega) widthAtLeast
    have nonzero : width ≠ 0 := by omega
    simp only [totalRailNodes, signedRailNodes, nonzero, ite_false]
    omega

/-- Explicit finite inequality behind the `(2+o(1))q` statement.  Dividing
by six gives leading term `2q`; the two balanced child powers are sublinear in
`q=3^width`. -/
theorem totalRailNodes_scaled_sharp (root : Sign) (width : Nat)
    (atLeastTwo : 2 ≤ width) :
    6 * totalRailNodes root width ≤
      12 * 3 ^ width +
        14 * (3 ^ (width / 2) + 3 ^ ((width + 1) / 2)) + 15 := by
  have recurrence := railNodes_recurrence width atLeastTwo
  have leftBound := three_mul_railNodes_le_seven_mul_pow (width / 2)
  have rightBound :=
    three_mul_railNodes_le_seven_mul_pow ((width + 1) / 2)
  have productPower := ternary_cross_product width
  have halfBound :
      2 * ((3 ^ ((width + 1) / 2) - 1) / 2) ≤
        3 ^ ((width + 1) / 2) - 1 :=
    Nat.mul_div_le (3 ^ ((width + 1) / 2) - 1) 2
  have crossBound :
      2 * (3 ^ (width / 2) *
          ((3 ^ ((width + 1) / 2) - 1) / 2)) ≤ 3 ^ width := by
    have multiplied := Nat.mul_le_mul_left (3 ^ (width / 2)) halfBound
    calc
      2 * (3 ^ (width / 2) *
          ((3 ^ ((width + 1) / 2) - 1) / 2)) =
          3 ^ (width / 2) *
            (2 * ((3 ^ ((width + 1) / 2) - 1) / 2)) := by ac_rfl
      _ ≤ 3 ^ (width / 2) * (3 ^ ((width + 1) / 2) - 1) := multiplied
      _ ≤ 3 ^ (width / 2) * 3 ^ ((width + 1) / 2) :=
        Nat.mul_le_mul_left _ (Nat.sub_le _ _)
      _ = 3 ^ width := productPower
  have negativeBound := negativeCellCount_le root width
  have negativeHalf :
      2 * negativeCellCount root width ≤ 3 ^ width + 1 := by
    have half := Nat.mul_div_le (3 ^ width + 1) 2
    omega
  have nonzero : width ≠ 0 := by omega
  simp only [totalRailNodes, signedRailNodes, nonzero, ite_false]
  omega

theorem railDepth_le_three_add_clog (width : Nat) :
    railDepth width ≤ 3 + Nat.clog 2 width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 2
      · interval_cases width <;> norm_num [railDepth]
      · have widthAtLeast : 2 ≤ width := by omega
        obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
          ⟨width - 2, by omega⟩
        have leftLess : (rest + 2) / 2 < rest + 2 := by omega
        have rightLess : (rest + 2 + 1) / 2 < rest + 2 := by omega
        have leftBound := ih ((rest + 2) / 2) leftLess
        have rightBound := ih ((rest + 2 + 1) / 2) rightLess
        have halvesOrdered : (rest + 2) / 2 ≤ (rest + 2 + 1) / 2 := by omega
        have logsOrdered :
            Nat.clog 2 ((rest + 2) / 2) ≤
              Nat.clog 2 ((rest + 2 + 1) / 2) :=
          Nat.clog_mono_right 2 halvesOrdered
        have leftBound' :
            railDepth ((rest + 2) / 2) ≤
              3 + Nat.clog 2 ((rest + 2 + 1) / 2) := by
          omega
        have maximumBound :
            max (railDepth ((rest + 2) / 2))
                (railDepth ((rest + 2 + 1) / 2)) ≤
              3 + Nat.clog 2 ((rest + 2 + 1) / 2) :=
          max_le leftBound' rightBound
        have clogStep :
            Nat.clog 2 (rest + 2) =
              Nat.clog 2 ((rest + 2 + 1) / 2) + 1 := by
          have quotientArgument :
              (rest + 2 + 2 - 1) / 2 = (rest + 2 + 1) / 2 := by
            congr 1
          calc
            Nat.clog 2 (rest + 2) =
                Nat.clog 2 ((rest + 2 + 2 - 1) / 2) + 1 :=
              Nat.clog_of_two_le (by omega) (by omega)
            _ = Nat.clog 2 ((rest + 2 + 1) / 2) + 1 := by
              rw [quotientArgument]
        calc
          railDepth (rest + 2) =
              max (railDepth ((rest + 2) / 2))
                (railDepth ((rest + 2 + 1) / 2)) + 1 := by
                  rw [railDepth]
          _ ≤ (3 + Nat.clog 2 ((rest + 2 + 1) / 2)) + 1 :=
            Nat.add_le_add_right maximumBound 1
          _ = 3 + (Nat.clog 2 ((rest + 2 + 1) / 2) + 1) := by
            omega
          _ = 3 + Nat.clog 2 (rest + 2) := by
            rw [clogStep]

theorem totalRailDepth_zero : totalRailDepth 0 = 2 := by
  rfl

theorem totalRailDepth_le_four_add_clog (width : Nat) (positive : 1 ≤ width) :
    totalRailDepth width ≤ 4 + Nat.clog 2 width := by
  have nonzero : width ≠ 0 := by omega
  have railBound := railDepth_le_three_add_clog width
  simp only [totalRailDepth, nonzero, ite_false]
  omega

/-- Machine-checked checkpoint for the frozen optimized theorem. -/
theorem optimized_materialization_bounds (root : Sign) (width : Nat)
    (positive : 1 ≤ width) :
    totalRailNodes root width ≤ 3 * 3 ^ width ∧
      totalRailDepth width ≤ 4 + Nat.clog 2 width :=
  ⟨totalRailNodes_le_three_mul_pow root width,
    totalRailDepth_le_four_add_clog width positive⟩

end OrbitSynthesis.StrongSignedRouter.FormalOptimized
