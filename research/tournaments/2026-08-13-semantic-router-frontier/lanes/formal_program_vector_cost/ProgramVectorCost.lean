import ProgramVector
import Mathlib.Data.Nat.Log

/-!
# Balanced cost ledger for strong-router program vectors

This file extends the frozen semantic program-vector theorem with a checked
combinatorial cost recurrence and a small original-signature legality model.
-/

namespace OrbitSynthesis.StrongSignedRouter.ProgramVectorCost

open OrbitSynthesis.StrongSignedRouter
open OrbitSynthesis.StrongSignedRouter.ProgramVector

/-- The three-element algebra used only for the nonbinary `A = 2` legality
check. -/
inductive Q where
  | zero
  | one
  | two
  deriving DecidableEq, Repr

def qDisc (x y z : Q) : Q :=
  if x = y then z else x

def qUnary : Q → Q
  | .zero => .one
  | .one => .zero
  | .two => .one

/-- Original `d/u` terms.  There is no constant constructor. -/
inductive QTerm (Var : Type) where
  | variable : Var → QTerm Var
  | unary : QTerm Var → QTerm Var
  | disc : QTerm Var → QTerm Var → QTerm Var → QTerm Var

namespace QTerm

def eval {Var : Type} (environment : Var → Q) : QTerm Var → Q
  | .variable variableId => environment variableId
  | .unary child => qUnary (eval environment child)
  | .disc left middle right =>
      qDisc (eval environment left) (eval environment middle)
        (eval environment right)

def operationCount {Var : Type} : QTerm Var → Nat
  | .variable _ => 0
  | .unary child => operationCount child + 1
  | .disc left middle right =>
      operationCount left + operationCount middle + operationCount right + 1

def depth {Var : Type} : QTerm Var → Nat
  | .variable _ => 0
  | .unary child => depth child + 1
  | .disc left middle right =>
      max (depth left) (max (depth middle) (depth right)) + 1

/-- Structural certificate for the declared constant-free `d/u` signature. -/
def OriginalSignature {Var : Type} : QTerm Var → Prop
  | .variable _ => True
  | .unary child => OriginalSignature child
  | .disc left middle right =>
      OriginalSignature left ∧ OriginalSignature middle ∧ OriginalSignature right

@[simp] theorem originalSignature {Var : Type} (term : QTerm Var) :
    term.OriginalSignature := by
  induction term <;> simp [OriginalSignature, *]

end QTerm

def anchorTwo {Var : Type} (anchor : Var) : QTerm Var := .variable anchor
def anchorOne {Var : Type} (anchor : Var) : QTerm Var := .unary (.variable anchor)
def anchorZero {Var : Type} (anchor : Var) : QTerm Var := .unary (anchorOne anchor)

def deltaZero {Var : Type} (anchor digit : Var) : QTerm Var :=
  .unary (.disc (.variable digit) (anchorTwo anchor) (anchorOne anchor))

def deltaOne {Var : Type} (anchor digit : Var) : QTerm Var :=
  .disc (.variable digit) (anchorTwo anchor) (anchorZero anchor)

def deltaTwo {Var : Type} (anchor digit : Var) : QTerm Var :=
  .unary (.disc (.variable digit) (anchorZero anchor) (anchorOne anchor))

def andTerm {Var : Type} (one left right : QTerm Var) : QTerm Var :=
  .disc left one right

def orTerm {Var : Type} (zero left right : QTerm Var) : QTerm Var :=
  .disc left zero right

def notTerm {Var : Type} (term : QTerm Var) : QTerm Var := .unary term

def qBit : Bool → Q
  | false => .zero
  | true => .one

def qDelta (expected actual : Q) : Q :=
  if actual = expected then .one else .zero

theorem anchor_names_correct {Var : Type} (environment : Var → Q)
    (anchor : Var) (anchorValue : environment anchor = .two) :
    QTerm.eval environment (anchorTwo anchor) = .two ∧
      QTerm.eval environment (anchorOne anchor) = .one ∧
      QTerm.eval environment (anchorZero anchor) = .zero := by
  simp [anchorTwo, anchorOne, anchorZero, QTerm.eval, qUnary, anchorValue]

/-- The `A = 2` premise is load-bearing: at `A = 1` the two names swap. -/
theorem anchor_one_mutation {Var : Type} (environment : Var → Q)
    (anchor : Var) (anchorValue : environment anchor = .one) :
    QTerm.eval environment (anchorOne anchor) = .zero ∧
      QTerm.eval environment (anchorZero anchor) = .one := by
  simp [anchorOne, anchorZero, QTerm.eval, qUnary, anchorValue]

theorem deltaZero_correct {Var : Type} (environment : Var → Q)
    (anchor digit : Var) (anchorValue : environment anchor = .two) :
    QTerm.eval environment (deltaZero anchor digit) =
      qDelta .zero (environment digit) := by
  cases digitValue : environment digit <;>
    simp [deltaZero, anchorTwo, anchorOne, QTerm.eval, qDisc, qUnary,
      qDelta, anchorValue, digitValue]

theorem deltaOne_correct {Var : Type} (environment : Var → Q)
    (anchor digit : Var) (anchorValue : environment anchor = .two) :
    QTerm.eval environment (deltaOne anchor digit) =
      qDelta .one (environment digit) := by
  cases digitValue : environment digit <;>
    simp [deltaOne, anchorTwo, anchorZero, anchorOne, QTerm.eval, qDisc,
      qUnary, qDelta, anchorValue, digitValue]

theorem deltaTwo_correct {Var : Type} (environment : Var → Q)
    (anchor digit : Var) (anchorValue : environment anchor = .two) :
    QTerm.eval environment (deltaTwo anchor digit) =
      qDelta .two (environment digit) := by
  cases digitValue : environment digit <;>
    simp [deltaTwo, anchorZero, anchorOne, QTerm.eval, qDisc,
      qUnary, qDelta, anchorValue, digitValue]

theorem andTerm_correct {Var : Type} (environment : Var → Q)
    (anchor : Var) (anchorValue : environment anchor = .two)
    (left right : QTerm Var) (leftBit rightBit : Bool)
    (leftValue : left.eval environment = qBit leftBit)
    (rightValue : right.eval environment = qBit rightBit) :
    (andTerm (anchorOne anchor) left right).eval environment =
      qBit (leftBit && rightBit) := by
  cases leftBit <;> cases rightBit <;>
    simp [andTerm, anchorOne, QTerm.eval, qDisc, qUnary, qBit,
      anchorValue, leftValue, rightValue]

theorem orTerm_correct {Var : Type} (environment : Var → Q)
    (anchor : Var) (anchorValue : environment anchor = .two)
    (left right : QTerm Var) (leftBit rightBit : Bool)
    (leftValue : left.eval environment = qBit leftBit)
    (rightValue : right.eval environment = qBit rightBit) :
    (orTerm (anchorZero anchor) left right).eval environment =
      qBit (leftBit || rightBit) := by
  cases leftBit <;> cases rightBit <;>
    simp [orTerm, anchorZero, anchorOne, QTerm.eval, qDisc, qUnary, qBit,
      anchorValue, leftValue, rightValue]

theorem notTerm_correct {Var : Type} (environment : Var → Q)
    (term : QTerm Var) (bit : Bool)
    (termValue : term.eval environment = qBit bit) :
    (notTerm term).eval environment = qBit (!bit) := by
  cases bit <;> simp [notTerm, QTerm.eval, qUnary, qBit, termValue]

/-- Two original-signature terms materializing one E/G state. -/
structure StateTerms (Var : Type) where
  eqTerm : QTerm Var
  gainTerm : QTerm Var

def StateTerms.Realizes {Var : Type} (terms : StateTerms Var)
    (environment : Var → Q) (summary : SegmentSummary) : Prop :=
  terms.eqTerm.eval environment = qBit summary.eqFlag ∧
  terms.gainTerm.eval environment = qBit summary.gain

def StateTerms.depth {Var : Type} (terms : StateTerms Var) : Nat :=
  max terms.eqTerm.depth terms.gainTerm.depth

def composeTerms {Var : Type} (anchor : Var)
    (left right : StateTerms Var) : StateTerms Var :=
  ⟨andTerm (anchorOne anchor) left.eqTerm right.eqTerm,
    orTerm (anchorZero anchor) left.gainTerm
      (andTerm (anchorOne anchor) left.eqTerm right.gainTerm)⟩

theorem composeTerms_correct {Var : Type} (environment : Var → Q)
    (anchor : Var) (anchorValue : environment anchor = .two)
    (left right : StateTerms Var) (leftSummary rightSummary : SegmentSummary)
    (leftCorrect : left.Realizes environment leftSummary)
    (rightCorrect : right.Realizes environment rightSummary) :
    (composeTerms anchor left right).Realizes environment
      (leftSummary.comp rightSummary) := by
  rcases leftCorrect with ⟨leftEq, leftGain⟩
  rcases rightCorrect with ⟨rightEq, rightGain⟩
  have equalCorrect := andTerm_correct environment anchor anchorValue
    left.eqTerm right.eqTerm leftSummary.eqFlag rightSummary.eqFlag
      leftEq rightEq
  have guardedCorrect := andTerm_correct environment anchor anchorValue
    left.eqTerm right.gainTerm leftSummary.eqFlag rightSummary.gain
      leftEq rightGain
  have gainCorrect := orTerm_correct environment anchor anchorValue
    left.gainTerm
      (andTerm (anchorOne anchor) left.eqTerm right.gainTerm)
      leftSummary.gain (leftSummary.eqFlag && rightSummary.gain)
      leftGain guardedCorrect
  exact ⟨equalCorrect, gainCorrect⟩

def digitQ : Digit → Q
  | .left => .zero
  | .middle => .one
  | .right => .two

def digitStateTerms {Var : Type} (anchor digit : Var) : Digit → StateTerms Var
  | .left => ⟨deltaZero anchor digit, anchorZero anchor⟩
  | .middle => ⟨deltaOne anchor digit, anchorZero anchor⟩
  | .right => ⟨deltaTwo anchor digit, deltaOne anchor digit⟩

theorem digitStateTerms_correct {Var : Type} (environment : Var → Q)
    (anchor digit : Var) (target physical : Digit)
    (anchorValue : environment anchor = .two)
    (digitValue : environment digit = digitQ target) :
    (digitStateTerms anchor digit physical).Realizes environment
      (digitSummary target physical) := by
  cases target <;> cases physical <;>
    simp [StateTerms.Realizes, digitStateTerms, digitSummary, deltaZero,
      deltaOne, deltaTwo, anchorZero, anchorOne, anchorTwo, QTerm.eval,
      qDisc, qUnary, qBit, anchorValue, digitValue, digitQ]

theorem composeTerms_originalSignature {Var : Type} (anchor : Var)
    (left right : StateTerms Var) :
    (composeTerms anchor left right).eqTerm.OriginalSignature ∧
      (composeTerms anchor left right).gainTerm.OriginalSignature := by
  simp

theorem digitStateTerms_originalSignature {Var : Type} (anchor digit : Var)
    (physical : Digit) :
    (digitStateTerms anchor digit physical).eqTerm.OriginalSignature ∧
      (digitStateTerms anchor digit physical).gainTerm.OriginalSignature := by
  simp

theorem digitStateTerms_depth_le_four {Var : Type} (anchor digit : Var)
    (physical : Digit) :
    (digitStateTerms anchor digit physical).depth ≤ 4 := by
  cases physical <;>
    norm_num [StateTerms.depth, digitStateTerms, deltaZero, deltaOne,
      deltaTwo, anchorZero, anchorOne, anchorTwo, QTerm.depth]

theorem composeTerms_depth_le {Var : Type} (anchor : Var)
    (left right : StateTerms Var) :
    (composeTerms anchor left right).depth ≤
      max 2 (max left.depth right.depth) + 2 := by
  simp only [StateTerms.depth, composeTerms, andTerm, orTerm, anchorOne,
    anchorZero, QTerm.depth]
  omega

def activeTerm {Var : Type} (anchor : Var) (state : StateTerms Var) : QTerm Var :=
  orTerm (anchorZero anchor) state.eqTerm state.gainTerm

/-- Frozen slot order: positive cells use `(!active,gain)` and negative cells
use `(gain,active)`. -/
def finalPairTerms {Var : Type} (anchor : Var) (negative : Bool)
    (state : StateTerms Var) : QTerm Var × QTerm Var :=
  if negative then (state.gainTerm, activeTerm anchor state)
  else (notTerm (activeTerm anchor state), state.gainTerm)

def termPairDepth {Var : Type} (pair : QTerm Var × QTerm Var) : Nat :=
  max pair.1.depth pair.2.depth

theorem finalPairTerms_correct {Var : Type} (environment : Var → Q)
    (anchor : Var) (anchorValue : environment anchor = .two)
    (negative : Bool) (state : StateTerms Var) (summary : SegmentSummary)
    (stateCorrect : state.Realizes environment summary)
    (disjoint : (summary.eqFlag && summary.gain) = false) :
    (finalPairTerms anchor negative state).1.eval environment =
        qBit (firstControlBit summary.eqFlag summary.gain negative) ∧
      (finalPairTerms anchor negative state).2.eval environment =
        qBit (secondControlBit summary.eqFlag summary.gain negative) := by
  rcases stateCorrect with ⟨equalCorrect, gainCorrect⟩
  have activeCorrect := orTerm_correct environment anchor anchorValue
    state.eqTerm state.gainTerm summary.eqFlag summary.gain
      equalCorrect gainCorrect
  have complementCorrect := notTerm_correct environment (activeTerm anchor state)
    (summary.eqFlag || summary.gain) activeCorrect
  rcases summary with ⟨eqFlag, gain⟩
  cases negative <;> cases eqFlag <;> cases gain <;>
    simp_all [finalPairTerms, activeTerm, firstControlBit, secondControlBit,
      qBit]

theorem finalPairTerms_match_frozen_program {Var : Type}
    (environment : Var → Q) (anchor : Var)
    (anchorValue : environment anchor = .two) (n : Nat) (root : Sign)
    (target branch : Address n) (state : StateTerms Var)
    (stateCorrect : state.Realizes environment
      (addressSummary n target branch)) :
    (finalPairTerms anchor
        (boolXor (isNegative root) (middleParity n branch)) state).1.eval
          environment =
        qBit (program root n (.project target) (.first, branch)) ∧
      (finalPairTerms anchor
        (boolXor (isNegative root) (middleParity n branch)) state).2.eval
          environment =
        qBit (program root n (.project target) (.second, branch)) := by
  rw [projection_program_first, projection_program_second]
  exact finalPairTerms_correct environment anchor anchorValue
    (boolXor (isNegative root) (middleParity n branch)) state
      (addressSummary n target branch) stateCorrect
      (addressSummary_disjoint n target branch)

theorem finalPairTerms_originalSignature {Var : Type} (anchor : Var)
    (negative : Bool) (state : StateTerms Var) :
    (finalPairTerms anchor negative state).1.OriginalSignature ∧
      (finalPairTerms anchor negative state).2.OriginalSignature := by
  cases negative <;> simp [finalPairTerms]

theorem finalPairTerms_depth_le {Var : Type} (anchor : Var)
    (negative : Bool) (state : StateTerms Var) :
    termPairDepth (finalPairTerms anchor negative state) ≤
      max 2 state.depth + 2 := by
  cases negative <;>
    simp [termPairDepth, finalPairTerms, activeTerm, orTerm, notTerm,
      anchorZero, anchorOne, StateTerms.depth, QTerm.depth] <;> omega

/-- Counts of physical words with even and odd middle-digit parity.  Appending
`left` or `right` preserves parity; appending `middle` toggles it. -/
def parityCounts : Nat → Nat × Nat
  | 0 => (1, 0)
  | width + 1 =>
      let previous := parityCounts width
      (2 * previous.1 + previous.2, previous.1 + 2 * previous.2)

theorem parityCounts_sum (width : Nat) :
    (parityCounts width).1 + (parityCounts width).2 = 3 ^ width := by
  induction width with
  | zero => norm_num [parityCounts]
  | succ width inductionHypothesis =>
      rcases previousValue : parityCounts width with ⟨evenCount, oddCount⟩
      simp only [previousValue] at inductionHypothesis
      simp only [parityCounts, previousValue]
      rw [pow_succ]
      omega

theorem parityCounts_even_eq_odd_add_one (width : Nat) :
    (parityCounts width).1 = (parityCounts width).2 + 1 := by
  induction width with
  | zero => norm_num [parityCounts]
  | succ width inductionHypothesis =>
      rcases previousValue : parityCounts width with ⟨evenCount, oddCount⟩
      simp only [previousValue] at inductionHypothesis
      simp only [parityCounts, previousValue]
      omega

theorem parityCounts_even_closed (width : Nat) :
    (parityCounts width).1 = (3 ^ width + 1) / 2 := by
  have sumRule := parityCounts_sum width
  have differenceRule := parityCounts_even_eq_odd_add_one width
  omega

def positiveCellCount (root : Sign) (width : Nat) : Nat :=
  match root with
  | .positive => (parityCounts width).1
  | .negative => (parityCounts width).2

theorem positiveCellCount_le (root : Sign) (width : Nat) :
    positiveCellCount root width ≤ (3 ^ width + 1) / 2 := by
  cases root with
  | positive =>
      simp [positiveCellCount, parityCounts_even_closed]
  | negative =>
      have differenceRule := parityCounts_even_eq_odd_add_one width
      rw [← parityCounts_even_closed width]
      simp only [positiveCellCount]
      omega

theorem half_width_sum (width : Nat) :
    width / 2 + (width + 1) / 2 = width := by
  omega

theorem ternary_cross_product (width : Nat) :
    3 ^ (width / 2) * 3 ^ ((width + 1) / 2) = 3 ^ width := by
  rw [← pow_add, half_width_sum]

/-- Dropping the `E_A` guard incorrectly lets a later gain override an earlier
non-gain mismatch. -/
theorem unguarded_gain_counterexample :
    let left : SegmentSummary := ⟨false, false⟩
    let right : SegmentSummary := ⟨false, true⟩
    (left.comp right).gain = false ∧ (left.gain || right.gain) = true := by
  decide

/-- Cost of all E/G states for a recursively bisected width. -/
def stateNodes : Nat → Nat
  | 0 => 0
  | 1 => 5
  | width@(_ + 2) =>
      stateNodes (width / 2) + stateNodes ((width + 1) / 2) +
        3 * 3 ^ width
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

/-- Cost beyond the two shared anchor-name nodes, including all active bits
and all sign-dependent final complements. -/
def vectorNodes (width : Nat) : Nat :=
  if width = 0 then 0
  else stateNodes width + 3 ^ width + (3 ^ width + 1) / 2

/-- Root-sign-specific ledger: one active-OR node per physical word and one
final complement exactly for each positive bottom cell. -/
def signedVectorNodes (root : Sign) (width : Nat) : Nat :=
  if width = 0 then 0
  else stateNodes width + 3 ^ width + positiveCellCount root width

/-- Complete shared-DAG ledger, now charging the two shared names
`u(A),u(u(A))` as well. -/
def totalSharedDAGNodes (root : Sign) (width : Nat) : Nat :=
  2 + signedVectorNodes root width

/-- State depth above raw anchor/address inputs. -/
def stateDepth : Nat → Nat
  | 0 => 0
  | 1 => 4
  | width@(_ + 2) =>
      max (stateDepth (width / 2)) (stateDepth ((width + 1) / 2)) + 2
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

/-- Final vector depth; the width-zero program uses only the two shared names. -/
def vectorDepth (width : Nat) : Nat :=
  if width = 0 then 2 else stateDepth width + 2

theorem stateNodes_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    stateNodes width =
      stateNodes (width / 2) + stateNodes ((width + 1) / 2) +
        3 * 3 ^ width := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [stateNodes]

theorem stateDepth_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    stateDepth width =
      max (stateDepth (width / 2)) (stateDepth ((width + 1) / 2)) + 2 := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [stateDepth]

theorem stateNodes_small :
    stateNodes 1 = 5 ∧ stateNodes 2 = 37 ∧ stateNodes 3 = 123 := by
  norm_num [stateNodes]

theorem stateNodes_le_five_mul_pow (width : Nat) :
    stateNodes width ≤ 5 * 3 ^ width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 4
      · interval_cases width <;> norm_num [stateNodes]
      · have widthAtLeast : 4 ≤ width := by omega
        obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
          ⟨width - 2, by omega⟩
        have leftLess : (rest + 2) / 2 < rest + 2 := by omega
        have rightLess : (rest + 2 + 1) / 2 < rest + 2 := by omega
        have leftBound := ih ((rest + 2) / 2) leftLess
        have rightBound := ih ((rest + 2 + 1) / 2) rightLess
        have leftExponent : (rest + 2) / 2 ≤ rest := by omega
        have rightExponent : (rest + 2 + 1) / 2 ≤ rest := by omega
        have leftPower : 3 ^ ((rest + 2) / 2) ≤ 3 ^ rest :=
          Nat.pow_le_pow_right (by omega) leftExponent
        have rightPower : 3 ^ ((rest + 2 + 1) / 2) ≤ 3 ^ rest :=
          Nat.pow_le_pow_right (by omega) rightExponent
        have leftBound' : stateNodes ((rest + 2) / 2) ≤ 5 * 3 ^ rest :=
          leftBound.trans (Nat.mul_le_mul_left 5 leftPower)
        have rightBound' : stateNodes ((rest + 2 + 1) / 2) ≤ 5 * 3 ^ rest :=
          rightBound.trans (Nat.mul_le_mul_left 5 rightPower)
        calc
          stateNodes (rest + 2) =
              stateNodes ((rest + 2) / 2) +
                stateNodes ((rest + 2 + 1) / 2) + 3 * 3 ^ (rest + 2) := by
                rw [stateNodes]
          _ ≤ 5 * 3 ^ rest + 5 * 3 ^ rest + 3 * 3 ^ (rest + 2) := by
                omega
          _ ≤ 5 * 3 ^ (rest + 2) := by
                rw [pow_add]
                norm_num
                omega

theorem vectorNodes_le_seven_mul_pow (width : Nat) :
    vectorNodes width ≤ 7 * 3 ^ width := by
  by_cases zeroWidth : width = 0
  · subst width
    norm_num [vectorNodes]
  · have stateBound := stateNodes_le_five_mul_pow width
    have powerPositive : 1 ≤ 3 ^ width := Nat.one_le_pow width 3 (by omega)
    simp only [vectorNodes, zeroWidth, ite_false]
    omega

theorem signedVectorNodes_le_vectorNodes (root : Sign) (width : Nat) :
    signedVectorNodes root width ≤ vectorNodes width := by
  by_cases zeroWidth : width = 0
  · subst width
    norm_num [signedVectorNodes, vectorNodes]
  · have complementBound := positiveCellCount_le root width
    simp only [signedVectorNodes, vectorNodes, zeroWidth, ite_false]
    omega

theorem signedVectorNodes_le_seven_mul_pow (root : Sign) (width : Nat) :
    signedVectorNodes root width ≤ 7 * 3 ^ width :=
  (signedVectorNodes_le_vectorNodes root width).trans
    (vectorNodes_le_seven_mul_pow width)

theorem totalSharedDAGNodes_le_seven_mul_pow (root : Sign) (width : Nat) :
    totalSharedDAGNodes root width ≤ 7 * 3 ^ width := by
  by_cases small : width < 2
  · interval_cases width <;>
      cases root <;>
      norm_num [totalSharedDAGNodes, signedVectorNodes, stateNodes,
        positiveCellCount, parityCounts]
  · have widthAtLeast : 2 ≤ width := by omega
    have stateBound := stateNodes_le_five_mul_pow width
    have complementBound := positiveCellCount_le root width
    have powerAtLeast : 9 ≤ 3 ^ width := by
      calc
        9 = 3 ^ 2 := by norm_num
        _ ≤ 3 ^ width := Nat.pow_le_pow_right (by omega) widthAtLeast
    have nonzero : width ≠ 0 := by omega
    simp only [totalSharedDAGNodes, signedVectorNodes, nonzero, ite_false]
    omega

theorem stateDepth_le_four_add_two_mul_clog (width : Nat) :
    stateDepth width ≤ 4 + 2 * Nat.clog 2 width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 2
      · interval_cases width <;> norm_num [stateDepth]
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
            stateDepth ((rest + 2) / 2) ≤
              4 + 2 * Nat.clog 2 ((rest + 2 + 1) / 2) := by
          omega
        have maximumBound :
            max (stateDepth ((rest + 2) / 2))
                (stateDepth ((rest + 2 + 1) / 2)) ≤
              4 + 2 * Nat.clog 2 ((rest + 2 + 1) / 2) :=
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
          stateDepth (rest + 2) =
              max (stateDepth ((rest + 2) / 2))
                (stateDepth ((rest + 2 + 1) / 2)) + 2 := by
                  rw [stateDepth]
          _ ≤ (4 + 2 * Nat.clog 2 ((rest + 2 + 1) / 2)) + 2 :=
            Nat.add_le_add_right maximumBound 2
          _ = 4 + 2 * (Nat.clog 2 ((rest + 2 + 1) / 2) + 1) := by
            omega
          _ = 4 + 2 * Nat.clog 2 (rest + 2) := by
            rw [clogStep]

theorem vectorDepth_zero : vectorDepth 0 = 2 := by
  rfl

theorem vectorDepth_le_six_add_two_mul_clog (width : Nat)
    (positive : 1 ≤ width) :
    vectorDepth width ≤ 6 + 2 * Nat.clog 2 width := by
  have nonzero : width ≠ 0 := by omega
  have stateBound := stateDepth_le_four_add_two_mul_clog width
  simp only [vectorDepth, nonzero, ite_false]
  omega

/-- Main combinatorial checkpoint.  `Nat.clog 2 width` is the natural-number
ceiling of `log_2(width)`. -/
theorem balanced_materialization_bounds (root : Sign) (width : Nat)
    (positive : 1 ≤ width) :
    totalSharedDAGNodes root width ≤ 7 * 3 ^ width ∧
      vectorDepth width ≤ 6 + 2 * Nat.clog 2 width :=
  ⟨totalSharedDAGNodes_le_seven_mul_pow root width,
    vectorDepth_le_six_add_two_mul_clog width positive⟩

end OrbitSynthesis.StrongSignedRouter.ProgramVectorCost
