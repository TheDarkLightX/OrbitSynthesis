import DirectRail

/-!
# Sibling-shared direct rails

This file extends the frozen direct-rail checkpoint with the two exact
semantic reuse identities and the arithmetic ledger for the sharper
sign-specialized terminal merge.  It does not claim an integrated compiler,
formula-size bound, bounded-fanout bound, or exact finite-width optimum.
-/

namespace OrbitSynthesis.StrongSignedRouter.FormalOptimized

open OrbitSynthesis.StrongSignedRouter
open OrbitSynthesis.StrongSignedRouter.ProgramVector
open OrbitSynthesis.StrongSignedRouter.ProgramVectorCost

/-- A valid direct-rail state never activates both absorbing modes. -/
def Rails.Valid (rails : Rails) : Prop :=
  (rails.zeroMode && rails.oneMode) = false

/-- If the right block cannot enter one mode, its one rail is the left rail
itself.  This is semantic equality of output functions, so a shared DAG may
reuse the existing left root with no new operation node. -/
theorem Rails.oneMode_comp_of_right_false (left right : Rails)
    (leftValid : left.Valid) (rightFalse : right.oneMode = false) :
    (left.comp right).oneMode = left.oneMode := by
  rcases left with ⟨leftZero, leftOne⟩
  rcases right with ⟨rightZero, rightOne⟩
  cases leftZero <;> cases leftOne <;> cases rightZero <;> cases rightOne <;>
    simp_all [Rails.Valid, Rails.comp, boolDisc]

/-- Exact `O_(a s)=O_a` identity for every physical suffix over `{0,1}`.
The paired list carries arbitrary target digits and physical digits; the
`noRightPhysical` premise is exactly the suffix-alphabet restriction. -/
theorem oneRail_trailing_zero_one_suffix
    (initial suffix : List (Digit × Digit))
    (noRight : noRightPhysical suffix = true) :
    (summarizePairs (initial ++ suffix)).gain =
      (summarizePairs initial).gain :=
  trailing_noRight_gain_reuse initial suffix noRight

/-- Exact cross-rail sibling identity `N_(a1)=O_(a2)`: after every valid
earlier prefix summary `a`, the complement of the zero-mode rail at physical
digit `1` equals the one-mode rail at physical digit `2`. -/
theorem sibling_notZero_middle_eq_one_right (prior : SegmentSummary)
    (target : Digit) (priorDisjoint : (prior.eqFlag && prior.gain) = false) :
    !(railsOfSummary (prior.comp (digitSummary target .middle))).zeroMode =
      (railsOfSummary (prior.comp (digitSummary target .right))).oneMode := by
  rcases prior with ⟨priorEqual, priorGain⟩
  cases priorEqual <;> cases priorGain <;> cases target <;>
    simp_all [railsOfSummary, SegmentSummary.comp, digitSummary]

/-- Powers of three are odd, so their predecessor has exact half. -/
theorem two_mul_half_pred_pow_three (exponent : Nat) :
    2 * ((3 ^ exponent - 1) / 2) = 3 ^ exponent - 1 := by
  obtain ⟨half, oddPower⟩ : Odd (3 ^ exponent) :=
    (show Odd (3 : Nat) by norm_num [Odd]).pow
  rw [oddPower]
  simp

/-- Powers of three are odd, so their successor has exact half. -/
theorem two_mul_half_succ_pow_three (exponent : Nat) :
    2 * ((3 ^ exponent + 1) / 2) = 3 ^ exponent + 1 := by
  obtain ⟨half, oddPower⟩ : Odd (3 ^ exponent) :=
    (show Odd (3 : Nat) by norm_num [Odd]).pow
  rw [oddPower]
  omega

/-- Generic `(zero,one)` library count for the sharper longer-left split.
The two absolute names are excluded. -/
def sharpRailNodes : Nat → Nat
  | 0 => 0
  | 1 => 4
  | width@(_ + 2) =>
      sharpRailNodes ((width + 1) / 2) + sharpRailNodes (width / 2) +
        3 ^ width +
          3 ^ ((width + 1) / 2) * ((3 ^ (width / 2) - 1) / 2)
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

/-- Extended `(zero,one,not-zero)` suffix-library ledger.  The
`3^(width-1)` saving is the `N_(a1)=O_(a2)` sibling reuse. -/
def extendedRailNodes : Nat → Nat
  | 0 => 0
  | 1 => 4
  | width@(_ + 2) =>
      sharpRailNodes ((width + 1) / 2) +
        extendedRailNodes (width / 2) +
        (2 * 3 ^ width - 3 ^ (width - 1)) +
        3 ^ ((width + 1) / 2) * ((3 ^ (width / 2) - 1) / 2)
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

/-- Top-level overlaps between a requested not-zero middle sibling and its
already requested one-mode right sibling. -/
def siblingOverlap (root : Sign) (width : Nat) : Nat :=
  match root with
  | .positive => (3 ^ (width - 1) + 1) / 2
  | .negative => (3 ^ (width - 1) - 1) / 2

/-- Safe exact operation ledger for one fixed root sign.  It includes both
absolute names and all `2*3^width` output roots. -/
def siblingSharedNodes (root : Sign) : Nat → Nat
  | 0 => 2
  | 1 => if root = .positive then 5 else 6
  | width@(_ + 2) =>
      let leftWidth := (width + 1) / 2
      let rightWidth := width / 2
      2 + sharpRailNodes leftWidth + extendedRailNodes rightWidth +
        3 ^ leftWidth * ((3 ^ rightWidth - 1) / 2) +
        (3 ^ width - siblingOverlap root width)

theorem sharpRailNodes_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    sharpRailNodes width =
      sharpRailNodes ((width + 1) / 2) + sharpRailNodes (width / 2) +
        3 ^ width +
          3 ^ ((width + 1) / 2) * ((3 ^ (width / 2) - 1) / 2) := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [sharpRailNodes]

theorem extendedRailNodes_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    extendedRailNodes width =
      sharpRailNodes ((width + 1) / 2) +
        extendedRailNodes (width / 2) +
        (2 * 3 ^ width - 3 ^ (width - 1)) +
        3 ^ ((width + 1) / 2) * ((3 ^ (width / 2) - 1) / 2) := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [extendedRailNodes]

theorem siblingSharedNodes_recurrence (root : Sign) (width : Nat)
    (atLeastTwo : 2 ≤ width) :
    siblingSharedNodes root width =
      2 + sharpRailNodes ((width + 1) / 2) +
        extendedRailNodes (width / 2) +
        3 ^ ((width + 1) / 2) * ((3 ^ (width / 2) - 1) / 2) +
        (3 ^ width - siblingOverlap root width) := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [siblingSharedNodes]

theorem sharpRailNodes_small :
    sharpRailNodes 1 = 4 ∧ sharpRailNodes 2 = 20 ∧
      sharpRailNodes 3 = 60 := by
  norm_num [sharpRailNodes]

theorem siblingSharedNodes_small :
    siblingSharedNodes .positive 1 = 5 ∧
      siblingSharedNodes .negative 1 = 6 ∧
      siblingSharedNodes .positive 2 = 20 ∧
      siblingSharedNodes .negative 2 = 21 := by
  norm_num [siblingSharedNodes, sharpRailNodes, extendedRailNodes,
    siblingOverlap]
  all_goals decide

theorem ternary_cross_product_ceiling (width : Nat) :
    3 ^ ((width + 1) / 2) * 3 ^ (width / 2) = 3 ^ width := by
  rw [Nat.mul_comm]
  exact ternary_cross_product width

/-- The generic rail library remains below `7q/3` under the sharper
longer-left split. -/
theorem three_mul_sharpRailNodes_le_seven_mul_pow (width : Nat) :
    3 * sharpRailNodes width ≤ 7 * 3 ^ width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 4
      · interval_cases width <;> norm_num [sharpRailNodes]
      · have widthAtLeast : 4 ≤ width := by omega
        let leftWidth := (width + 1) / 2
        let rightWidth := width / 2
        let leftPower := 3 ^ leftWidth
        let rightPower := 3 ^ rightWidth
        have leftLess : leftWidth < width := by
          dsimp [leftWidth]
          omega
        have rightLess : rightWidth < width := by
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
            _ ≤ 3 ^ leftWidth :=
              Nat.pow_le_pow_right (by omega) leftWidthAtLeast
        have rightPowerAtLeast : 9 ≤ rightPower := by
          dsimp [rightPower]
          calc
            9 = 3 ^ 2 := by norm_num
            _ ≤ 3 ^ rightWidth :=
              Nat.pow_le_pow_right (by omega) rightWidthAtLeast
        have productPower : leftPower * rightPower = 3 ^ width := by
          dsimp [leftPower, rightPower, leftWidth, rightWidth]
          exact ternary_cross_product_ceiling width
        have childPowers :
            14 * leftPower + 14 * rightPower ≤
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
            6 * (sharpRailNodes leftWidth + sharpRailNodes rightWidth +
                leftPower * rightPower +
                leftPower * ((rightPower - 1) / 2)) ≤
              14 * (leftPower * rightPower) := by
          omega
        have namedBound :
            3 * (sharpRailNodes leftWidth + sharpRailNodes rightWidth +
                leftPower * rightPower +
                leftPower * ((rightPower - 1) / 2)) ≤
              7 * (leftPower * rightPower) := by
          omega
        rw [sharpRailNodes_recurrence width (by omega)]
        rw [← productPower]
        exact namedBound

theorem pow_three_eq_three_mul_pred (width : Nat) (positive : 1 ≤ width) :
    3 ^ width = 3 * 3 ^ (width - 1) := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 1 :=
    ⟨width - 1, by omega⟩
  rw [Nat.add_sub_cancel, pow_succ]
  omega

/-- A deliberately convenient all-width envelope for the extended suffix
library.  The sharper terminal theorem only needs this `3q` bound. -/
theorem three_mul_extendedRailNodes_le_nine_mul_pow (width : Nat) :
    3 * extendedRailNodes width ≤ 9 * 3 ^ width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 4
      · interval_cases width <;>
          norm_num [extendedRailNodes, sharpRailNodes]
      · have widthAtLeast : 4 ≤ width := by omega
        let leftWidth := (width + 1) / 2
        let rightWidth := width / 2
        let leftPower := 3 ^ leftWidth
        let rightPower := 3 ^ rightWidth
        have rightLess : rightWidth < width := by
          dsimp [rightWidth]
          omega
        have leftWidthAtLeast : 2 ≤ leftWidth := by
          dsimp [leftWidth]
          omega
        have rightWidthAtLeast : 2 ≤ rightWidth := by
          dsimp [rightWidth]
          omega
        have leftBound :=
          three_mul_sharpRailNodes_le_seven_mul_pow leftWidth
        have rightBound := ih rightWidth rightLess
        have leftPowerAtLeast : 9 ≤ leftPower := by
          dsimp [leftPower]
          calc
            9 = 3 ^ 2 := by norm_num
            _ ≤ 3 ^ leftWidth :=
              Nat.pow_le_pow_right (by omega) leftWidthAtLeast
        have rightPowerAtLeast : 9 ≤ rightPower := by
          dsimp [rightPower]
          calc
            9 = 3 ^ 2 := by norm_num
            _ ≤ 3 ^ rightWidth :=
              Nat.pow_le_pow_right (by omega) rightWidthAtLeast
        have productPower : leftPower * rightPower = 3 ^ width := by
          dsimp [leftPower, rightPower, leftWidth, rightWidth]
          exact ternary_cross_product_ceiling width
        have childPowers :
            14 * leftPower + 18 * rightPower ≤
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
        have powerStep := pow_three_eq_three_mul_pred width (by omega)
        have middleScaled :
            6 * (2 * 3 ^ width - 3 ^ (width - 1)) =
              10 * 3 ^ width := by
          omega
        have doubledBound :
            6 * (sharpRailNodes leftWidth +
                extendedRailNodes rightWidth +
                (2 * (leftPower * rightPower) - 3 ^ (width - 1)) +
                leftPower * ((rightPower - 1) / 2)) ≤
              18 * (leftPower * rightPower) := by
          rw [productPower]
          omega
        have namedBound :
            3 * (sharpRailNodes leftWidth +
                extendedRailNodes rightWidth +
                (2 * (leftPower * rightPower) - 3 ^ (width - 1)) +
                leftPower * ((rightPower - 1) / 2)) ≤
              9 * (leftPower * rightPower) := by
          omega
        rw [extendedRailNodes_recurrence width (by omega)]
        rw [← productPower]
        exact namedBound

theorem siblingOverlap_le_pow (root : Sign) (width : Nat) :
    siblingOverlap root width ≤ 3 ^ width := by
  have exponentLe : width - 1 ≤ width := Nat.sub_le width 1
  have smallerPower : 3 ^ (width - 1) ≤ 3 ^ width :=
    Nat.pow_le_pow_right (by omega) exponentLe
  have powerPositive : 1 ≤ 3 ^ width :=
    one_le_pow₀ (by norm_num : 1 ≤ (3 : Nat))
  cases root <;> simp only [siblingOverlap] <;> omega

theorem six_mul_siblingOverlap_ge_pred_pow (root : Sign) (width : Nat)
    (positive : 1 ≤ width) :
    3 ^ width - 3 ≤ 6 * siblingOverlap root width := by
  have powerStep := pow_three_eq_three_mul_pred width positive
  cases root with
  | positive =>
      have halfExact := two_mul_half_succ_pow_three (width - 1)
      simp only [siblingOverlap]
      omega
  | negative =>
      have halfExact := two_mul_half_pred_pow_three (width - 1)
      simp only [siblingOverlap]
      omega

/-- Exact finite convergence envelope for one fixed root sign.  Since the
error term is `O(3^(ceil(width/2)))`, this is the arithmetic content of the
`(4/3+o(1))*3^width` sibling-shared upper bound. -/
theorem siblingSharedNodes_scaled_envelope (root : Sign) (width : Nat) :
    3 * siblingSharedNodes root width ≤
      4 * 3 ^ width + 15 * 3 ^ ((width + 1) / 2) := by
  by_cases small : width < 5
  · interval_cases width <;>
      cases root <;>
      norm_num [siblingSharedNodes, sharpRailNodes, extendedRailNodes,
        siblingOverlap]
    all_goals decide
  · have widthAtLeast : 5 ≤ width := by omega
    let leftWidth := (width + 1) / 2
    let rightWidth := width / 2
    let leftPower := 3 ^ leftWidth
    let rightPower := 3 ^ rightWidth
    have leftWidthAtLeast : 3 ≤ leftWidth := by
      dsimp [leftWidth]
      omega
    have rightWidthAtLeast : 2 ≤ rightWidth := by
      dsimp [rightWidth]
      omega
    have leftPowerAtLeast : 27 ≤ leftPower := by
      dsimp [leftPower]
      calc
        27 = 3 ^ 3 := by norm_num
        _ ≤ 3 ^ leftWidth :=
          Nat.pow_le_pow_right (by omega) leftWidthAtLeast
    have widthsOrdered : rightWidth ≤ leftWidth := by
      dsimp [leftWidth, rightWidth]
      omega
    have powersOrdered : rightPower ≤ leftPower := by
      dsimp [leftPower, rightPower]
      exact Nat.pow_le_pow_right (by omega) widthsOrdered
    have productPower : leftPower * rightPower = 3 ^ width := by
      dsimp [leftPower, rightPower, leftWidth, rightWidth]
      exact ternary_cross_product_ceiling width
    have railBound :=
      three_mul_sharpRailNodes_le_seven_mul_pow leftWidth
    have extendedBound :=
      three_mul_extendedRailNodes_le_nine_mul_pow rightWidth
    have railBoundTwice :
        6 * sharpRailNodes leftWidth ≤ 14 * leftPower := by
      dsimp [leftPower] at *
      omega
    have extendedBoundTwice :
        6 * extendedRailNodes rightWidth ≤ 18 * rightPower := by
      dsimp [rightPower] at *
      omega
    have halfExact := two_mul_half_pred_pow_three rightWidth
    have crossExact :
        2 * (leftPower * ((rightPower - 1) / 2)) =
          leftPower * rightPower - leftPower := by
      calc
        2 * (leftPower * ((rightPower - 1) / 2)) =
            leftPower * (2 * ((rightPower - 1) / 2)) := by ac_rfl
        _ = leftPower * (rightPower - 1) := by rw [halfExact]
        _ = leftPower * rightPower - leftPower := by
          rw [Nat.mul_sub_left_distrib]
          simp
    have leftPowerLeProduct : leftPower ≤ leftPower * rightPower := by
      have rightPowerPositive : 1 ≤ rightPower :=
        one_le_pow₀ (by norm_num : 1 ≤ (3 : Nat))
      nlinarith
    have crossScaled :
        6 * (leftPower * ((rightPower - 1) / 2)) =
          3 * (3 ^ width - leftPower) := by
      rw [← productPower]
      omega
    have overlapBound :=
      six_mul_siblingOverlap_ge_pred_pow root width (by omega)
    have overlapLe := siblingOverlap_le_pow root width
    have remainingBound :
        6 * (3 ^ width - siblingOverlap root width) ≤
          5 * 3 ^ width + 3 := by
      omega
    have errorBound :
        11 * leftPower + 18 * rightPower + 15 ≤ 30 * leftPower := by
      omega
    have doubledBound :
        6 * (2 + sharpRailNodes leftWidth +
            extendedRailNodes rightWidth +
            leftPower * ((rightPower - 1) / 2) +
            (3 ^ width - siblingOverlap root width)) ≤
          8 * 3 ^ width + 30 * leftPower := by
      omega
    have namedBound :
        3 * (2 + sharpRailNodes leftWidth +
            extendedRailNodes rightWidth +
            leftPower * ((rightPower - 1) / 2) +
            (3 ^ width - siblingOverlap root width)) ≤
          4 * 3 ^ width + 15 * leftPower := by
      omega
    rw [siblingSharedNodes_recurrence root width (by omega)]
    exact namedBound

/-- Uniform finite-width corollary: the sibling-shared ledger is at most
`7q/3` for either fixed root sign. -/
theorem three_mul_siblingSharedNodes_le_seven_mul_pow
    (root : Sign) (width : Nat) :
    3 * siblingSharedNodes root width ≤ 7 * 3 ^ width := by
  by_cases small : width < 4
  · interval_cases width <;>
      cases root <;>
      norm_num [siblingSharedNodes, sharpRailNodes, extendedRailNodes,
        siblingOverlap]
    all_goals decide
  · have widthAtLeast : 4 ≤ width := by omega
    let leftWidth := (width + 1) / 2
    let rightWidth := width / 2
    let leftPower := 3 ^ leftWidth
    let rightPower := 3 ^ rightWidth
    have rightWidthAtLeast : 2 ≤ rightWidth := by
      dsimp [rightWidth]
      omega
    have rightPowerAtLeast : 9 ≤ rightPower := by
      dsimp [rightPower]
      calc
        9 = 3 ^ 2 := by norm_num
        _ ≤ 3 ^ rightWidth :=
          Nat.pow_le_pow_right (by omega) rightWidthAtLeast
    have productPower : leftPower * rightPower = 3 ^ width := by
      dsimp [leftPower, rightPower, leftWidth, rightWidth]
      exact ternary_cross_product_ceiling width
    have errorAbsorbed : 15 * leftPower ≤ 3 * 3 ^ width := by
      rw [← productPower]
      nlinarith
    have envelope := siblingSharedNodes_scaled_envelope root width
    dsimp [leftPower, leftWidth] at *
    omega

end OrbitSynthesis.StrongSignedRouter.FormalOptimized
