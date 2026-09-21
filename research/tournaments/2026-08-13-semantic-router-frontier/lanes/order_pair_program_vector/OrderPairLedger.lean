import OrderPairSemantics
import Mathlib.Data.Nat.Log

/-!
# Checked recurrence and depth ledger for order-pair program vectors

This file records the exact balanced-package recurrences used by the concrete
hash-consed audit.  The cost model is the same recurrence-level shared-DAG
model as the preceding `ProgramVectorCost` checkpoint.
-/

namespace OrbitSynthesis.StrongSignedRouter.OrderPairProgramVector

open OrbitSynthesis.StrongSignedRouter
open OrbitSynthesis.StrongSignedRouter.ProgramVectorCost

/-- Nodes beyond the two shared names in all `(L,G)` summaries.  At a merge,
all loss roots are distinct syntactic nodes.  Gain roots are shared by the
right suffix through its last physical `2`; the zero class reuses the left
root. -/
def summaryNodes : Nat → Nat
  | 0 => 0
  | 1 => 4
  | width@(_ + 2) =>
      summaryNodes (width / 2) + summaryNodes ((width + 1) / 2) +
        3 ^ width +
        3 ^ (width / 2) * ((3 ^ ((width + 1) / 2) - 1) / 2)
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

theorem summaryNodes_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    summaryNodes width =
      summaryNodes (width / 2) + summaryNodes ((width + 1) / 2) +
        3 ^ width + 3 ^ (width / 2) * ((3 ^ ((width + 1) / 2) - 1) / 2) := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 := ⟨width - 2, by omega⟩
  rw [summaryNodes]

/-- Extra `H=not L` roots for physical words ending zero or two.  A middle
ending is represented by the existing sibling gain root. -/
def partialHNodes : Nat → Nat
  | 0 => 0
  | 1 => 0
  | width@(_ + 2) =>
      partialHNodes ((width + 1) / 2) + 2 * 3 ^ (width - 1)
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

theorem partialHNodes_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    partialHNodes width = partialHNodes ((width + 1) / 2) + 2 * 3 ^ (width - 1) := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 := ⟨width - 2, by omega⟩
  rw [partialHNodes]

/-- Number of negative bottom cells ending in a middle digit.  Their required
upper root is already a gain root. -/
def reusableCount (root : Sign) : Nat → Nat
  | 0 => 0
  | width + 1 =>
      match root with
      | .positive => (parityCounts width).1
      | .negative => (parityCounts width).2

/-- Complete sign-specific vector count, including `u(A),u(u(A))`. -/
def improvedVectorNodes (root : Sign) : Nat → Nat
  | 0 => 2
  | 1 => 6
  | width@(_ + 2) =>
      2 + summaryNodes width + partialHNodes ((width + 1) / 2) -
        reusableCount root width

theorem improvedVectorNodes_recurrence (root : Sign) (width : Nat)
    (atLeastTwo : 2 ≤ width) :
    improvedVectorNodes root width =
      2 + summaryNodes width + partialHNodes ((width + 1) / 2) -
        reusableCount root width := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 := ⟨width - 2, by omega⟩
  rw [improvedVectorNodes]

/-- Balanced dependency depth above the raw anchor/address inputs. -/
def improvedVectorDepth : Nat → Nat
  | 0 => 2
  | 1 => 3
  | width@(_ + 2) =>
      max (improvedVectorDepth (width / 2))
        (improvedVectorDepth ((width + 1) / 2)) + 1
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

@[simp] theorem summaryNodes_small :
    summaryNodes 1 = 4 ∧ summaryNodes 2 = 20 ∧ summaryNodes 3 = 63 := by
  norm_num [summaryNodes]

@[simp] theorem partialHNodes_small :
    partialHNodes 1 = 0 ∧ partialHNodes 2 = 6 ∧ partialHNodes 3 = 24 := by
  norm_num [partialHNodes]

@[simp] theorem improvedVectorNodes_small :
    improvedVectorNodes .positive 1 = 6 ∧
      improvedVectorNodes .negative 1 = 6 ∧
      improvedVectorNodes .positive 2 = 20 ∧
      improvedVectorNodes .negative 2 = 21 ∧
      improvedVectorNodes .positive 3 = 66 ∧
      improvedVectorNodes .negative 3 = 67 := by
  norm_num [improvedVectorNodes, summaryNodes, partialHNodes, reusableCount,
    parityCounts]

/-- Scaled form of `A(w) <= (7/3)3^w`, avoiding rational arithmetic. -/
theorem summaryNodes_scaled_bound (width : Nat) :
    3 * summaryNodes width ≤ 7 * 3 ^ width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 4
      · interval_cases width <;> norm_num [summaryNodes]
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
        have leftBound' :
            3 * summaryNodes ((rest + 2) / 2) ≤ 7 * 3 ^ rest :=
          leftBound.trans (Nat.mul_le_mul_left 7 leftPower)
        have rightBound' :
            3 * summaryNodes ((rest + 2 + 1) / 2) ≤ 7 * 3 ^ rest :=
          rightBound.trans (Nat.mul_le_mul_left 7 rightPower)
        have halfBound :
            2 * ((3 ^ ((rest + 2 + 1) / 2) - 1) / 2) ≤
              3 ^ ((rest + 2 + 1) / 2) := by
          omega
        have scaledHalf :=
          Nat.mul_le_mul_left (3 * 3 ^ ((rest + 2) / 2)) halfBound
        have gainBound :
            6 * (3 ^ ((rest + 2) / 2) *
              ((3 ^ ((rest + 2 + 1) / 2) - 1) / 2)) ≤
              3 * 3 ^ (rest + 2) := by
          calc
            6 * (3 ^ ((rest + 2) / 2) *
                ((3 ^ ((rest + 2 + 1) / 2) - 1) / 2)) =
                (3 * 3 ^ ((rest + 2) / 2)) *
                  (2 * ((3 ^ ((rest + 2 + 1) / 2) - 1) / 2)) := by
                    ring
            _ ≤ (3 * 3 ^ ((rest + 2) / 2)) *
                  3 ^ ((rest + 2 + 1) / 2) := scaledHalf
            _ = 3 * 3 ^ (rest + 2) := by
              rw [← ternary_cross_product (rest + 2)]
              ring
        have powerStep : 3 ^ (rest + 2) = 9 * 3 ^ rest := by
          rw [pow_add]
          norm_num
          omega
        have doubled :
            6 * summaryNodes (rest + 2) ≤ 14 * 3 ^ (rest + 2) := by
          rw [summaryNodes_recurrence (rest + 2) (by omega)]
          rw [powerStep] at gainBound ⊢
          omega
        omega

/-- Partial upper-root packages are strictly below one full ternary layer. -/
theorem partialHNodes_le_pow_sub_three (width : Nat) (positive : 1 ≤ width) :
    partialHNodes width ≤ 3 ^ width - 3 := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 2
      · interval_cases width
        norm_num [partialHNodes]
      · have widthAtLeast : 2 ≤ width := by omega
        obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
          ⟨width - 2, by omega⟩
        have rightLess : (rest + 2 + 1) / 2 < rest + 2 := by omega
        have rightPositive : 1 ≤ (rest + 2 + 1) / 2 := by omega
        have rightBound :=
          ih ((rest + 2 + 1) / 2) rightLess rightPositive
        have exponentBound : (rest + 2 + 1) / 2 ≤ rest + 1 := by omega
        have powerBound :
            3 ^ ((rest + 2 + 1) / 2) ≤ 3 ^ (rest + 1) :=
          Nat.pow_le_pow_right (by omega) exponentBound
        have rightBound' :
            partialHNodes ((rest + 2 + 1) / 2) ≤
              3 ^ (rest + 1) - 3 :=
          rightBound.trans (Nat.sub_le_sub_right powerBound 3)
        have powerStep : 3 ^ (rest + 2) = 3 * 3 ^ (rest + 1) := by
          rw [pow_succ]
          omega
        have powerAtLeast : 3 ≤ 3 ^ (rest + 1) := by
          calc
            3 = 3 ^ 1 := by norm_num
            _ ≤ 3 ^ (rest + 1) := Nat.pow_le_pow_right (by omega) (by omega)
        rw [partialHNodes_recurrence (rest + 2) (by omega)]
        rw [show rest + 2 - 1 = rest + 1 by omega]
        rw [powerStep]
        omega

/-- Closed scaled parity counts for the roots saved at the final merge. -/
theorem reusableCount_positive_scaled (tail : Nat) :
    6 * reusableCount .positive (tail + 1) = 3 ^ (tail + 1) + 3 := by
  have sumRule := parityCounts_sum tail
  have differenceRule := parityCounts_even_eq_odd_add_one tail
  simp only [reusableCount]
  rw [pow_succ]
  omega

theorem reusableCount_negative_scaled (tail : Nat) :
    6 * reusableCount .negative (tail + 1) = 3 ^ (tail + 1) - 3 := by
  have sumRule := parityCounts_sum tail
  have differenceRule := parityCounts_even_eq_odd_add_one tail
  simp only [reusableCount]
  rw [pow_succ]
  omega

/-- Root sign changes the exact construction by one node from width two on. -/
theorem negative_eq_positive_add_one (width : Nat) (atLeastTwo : 2 ≤ width) :
    improvedVectorNodes .negative width =
      improvedVectorNodes .positive width + 1 := by
  obtain ⟨tail, rfl⟩ : ∃ tail, width = tail + 2 :=
    ⟨width - 2, by omega⟩
  have differenceRule := parityCounts_even_eq_odd_add_one (tail + 1)
  have sumRule := parityCounts_sum (tail + 1)
  have summaryLower : 3 ^ (tail + 2) ≤ summaryNodes (tail + 2) := by
    rw [summaryNodes_recurrence (tail + 2) (by omega)]
    omega
  rw [pow_succ] at summaryLower
  rw [improvedVectorNodes_recurrence .negative (tail + 2) (by omega),
    improvedVectorNodes_recurrence .positive (tail + 2) (by omega)]
  simp only [reusableCount]
  omega

/-- Explicit uniform improvement over the historical `7q` ledger. -/
theorem improvedVectorNodes_uniform_bound (root : Sign) (width : Nat)
    (positive : 1 ≤ width) :
    2 * improvedVectorNodes root width ≤ 5 * 3 ^ width - 1 := by
  by_cases oneWidth : width = 1
  · subst width
    cases root <;>
      norm_num [improvedVectorNodes]
  · have atLeastTwo : 2 ≤ width := by omega
    obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
      ⟨width - 2, by omega⟩
    have summaryBound := summaryNodes_scaled_bound (rest + 2)
    have rightPositive : 1 ≤ (rest + 2 + 1) / 2 := by omega
    have rightPowerPositive : 0 < 3 ^ ((rest + 2 + 1) / 2) := by positivity
    have partialBound :=
      partialHNodes_le_pow_sub_three ((rest + 2 + 1) / 2) rightPositive
    have exponentBound : (rest + 2 + 1) / 2 ≤ rest + 1 := by omega
    have powerBound :
        3 ^ ((rest + 2 + 1) / 2) ≤ 3 ^ (rest + 1) :=
      Nat.pow_le_pow_right (by omega) exponentBound
    have partialBound' :
        partialHNodes ((rest + 2 + 1) / 2) ≤ 3 ^ (rest + 1) - 3 :=
      partialBound.trans (Nat.sub_le_sub_right powerBound 3)
    have powerStep : 3 ^ (rest + 2) = 3 * 3 ^ (rest + 1) := by
      rw [pow_succ]
      omega
    cases root with
    | positive =>
        have saved := reusableCount_positive_scaled (rest + 1)
        change 6 * reusableCount .positive (rest + 2) = 3 ^ (rest + 2) + 3 at saved
        rw [improvedVectorNodes_recurrence .positive (rest + 2) (by omega)]
        rw [powerStep] at summaryBound saved ⊢
        omega
    | negative =>
        have saved := reusableCount_negative_scaled (rest + 1)
        change 6 * reusableCount .negative (rest + 2) = 3 ^ (rest + 2) - 3 at saved
        rw [improvedVectorNodes_recurrence .negative (rest + 2) (by omega)]
        rw [powerStep] at summaryBound saved ⊢
        omega

/-- One balanced split adds one dependency layer. -/
theorem improvedVectorDepth_le_three_add_clog (width : Nat)
    (positive : 1 ≤ width) :
    improvedVectorDepth width ≤ 3 + Nat.clog 2 width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 2
      · interval_cases width
        norm_num [improvedVectorDepth]
      · have widthAtLeast : 2 ≤ width := by omega
        obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
          ⟨width - 2, by omega⟩
        have leftLess : (rest + 2) / 2 < rest + 2 := by omega
        have rightLess : (rest + 2 + 1) / 2 < rest + 2 := by omega
        have leftPositive : 1 ≤ (rest + 2) / 2 := by omega
        have rightPositive : 1 ≤ (rest + 2 + 1) / 2 := by omega
        have leftBound := ih ((rest + 2) / 2) leftLess leftPositive
        have rightBound := ih ((rest + 2 + 1) / 2) rightLess rightPositive
        have halvesOrdered :
            (rest + 2) / 2 ≤ (rest + 2 + 1) / 2 := by omega
        have logsOrdered :
            Nat.clog 2 ((rest + 2) / 2) ≤
              Nat.clog 2 ((rest + 2 + 1) / 2) :=
          Nat.clog_mono_right 2 halvesOrdered
        have leftBound' :
            improvedVectorDepth ((rest + 2) / 2) ≤
              3 + Nat.clog 2 ((rest + 2 + 1) / 2) := by
          omega
        have maximumBound :
            max (improvedVectorDepth ((rest + 2) / 2))
                (improvedVectorDepth ((rest + 2 + 1) / 2)) ≤
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
          improvedVectorDepth (rest + 2) =
              max (improvedVectorDepth ((rest + 2) / 2))
                (improvedVectorDepth ((rest + 2 + 1) / 2)) + 1 := by
                  rw [improvedVectorDepth]
          _ ≤ (3 + Nat.clog 2 ((rest + 2 + 1) / 2)) + 1 :=
            Nat.add_le_add_right maximumBound 1
          _ = 3 + Nat.clog 2 (rest + 2) := by
            rw [clogStep]
            omega

/-- Main checked ledger: the new vector is below `5q/2` and has one-logarithm
preprocessing depth. -/
theorem improved_balanced_materialization_bounds (root : Sign) (width : Nat)
    (positive : 1 ≤ width) :
    2 * improvedVectorNodes root width ≤ 5 * 3 ^ width - 1 ∧
      improvedVectorDepth width ≤ 3 + Nat.clog 2 width :=
  ⟨improvedVectorNodes_uniform_bound root width positive,
    improvedVectorDepth_le_three_add_clog width positive⟩

end OrbitSynthesis.StrongSignedRouter.OrderPairProgramVector
