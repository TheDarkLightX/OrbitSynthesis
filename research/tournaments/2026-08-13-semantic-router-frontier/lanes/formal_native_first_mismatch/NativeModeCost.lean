import NativeModeBridge
import Mathlib.Data.Nat.Log

/-!
# Balanced cost layer for native mode vectors

This file checks the recurrence-level shared-DAG ledger for the native
`Q`-valued mode vector and the complement-closed complete signed construction.
-/

namespace OrbitSynthesis.StrongSignedRouter.NativeModeCost

open OrbitSynthesis.StrongSignedRouter
open OrbitSynthesis.StrongSignedRouter.ProgramVectorCost

/-- Operation nodes for all native mode roots, excluding the two shared names. -/
def modeNodes : Nat → Nat
  | 0 => 0
  | 1 => 3
  | width@ (_ + 2) =>
      modeNodes (width / 2) + modeNodes ((width + 1) / 2) +
        3 ^ width
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

/-- Maximum depth of a native mode root above raw anchor/address inputs. -/
def modeDepth : Nat → Nat
  | 0 => 0
  | 1 => 3
  | width@ (_ + 2) =>
      max (modeDepth (width / 2)) (modeDepth ((width + 1) / 2)) + 1
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

/-- Complete mode-vector ledger, including `u(A)` and `u(u(A))`. -/
def modeVectorNodes (width : Nat) : Nat :=
  if width = 0 then 2 else modeNodes width + 2

theorem modeNodes_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    modeNodes width =
      modeNodes (width / 2) + modeNodes ((width + 1) / 2) +
        3 ^ width := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [modeNodes]

theorem modeDepth_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    modeDepth width =
      max (modeDepth (width / 2)) (modeDepth ((width + 1) / 2)) + 1 := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [modeDepth]

theorem modeNodes_small :
    modeNodes 1 = 3 ∧ modeNodes 2 = 15 ∧ modeNodes 3 = 45 := by
  norm_num [modeNodes]

/-- Uniform recurrence bound, written without division. -/
theorem three_mul_modeNodes_le_five_mul_pow (width : Nat) :
    3 * modeNodes width ≤ 5 * 3 ^ width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 4
      · interval_cases width <;> norm_num [modeNodes]
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
            3 * modeNodes ((rest + 2) / 2) ≤ 5 * 3 ^ rest :=
          leftBound.trans (Nat.mul_le_mul_left 5 leftPower)
        have rightBound' :
            3 * modeNodes ((rest + 2 + 1) / 2) ≤ 5 * 3 ^ rest :=
          rightBound.trans (Nat.mul_le_mul_left 5 rightPower)
        calc
          3 * modeNodes (rest + 2) =
              3 * modeNodes ((rest + 2) / 2) +
                3 * modeNodes ((rest + 2 + 1) / 2) +
                  3 * 3 ^ (rest + 2) := by
                    rw [modeNodes_recurrence (rest + 2) (by omega)]
                    omega
          _ ≤ 5 * 3 ^ rest + 5 * 3 ^ rest + 3 * 3 ^ (rest + 2) := by
                omega
          _ ≤ 5 * 3 ^ (rest + 2) := by
                rw [pow_add]
                norm_num
                omega

/-- Exact finite constant used in the paper: all roots plus both shared names
fit below `17q/9`. -/
theorem nine_mul_modeVectorNodes_le_seventeen_mul_pow
    (width : Nat) (positive : 1 ≤ width) :
    9 * modeVectorNodes width ≤ 17 * 3 ^ width := by
  by_cases one : width = 1
  · subst width
    norm_num [modeVectorNodes, modeNodes]
  · have widthAtLeast : 2 ≤ width := by omega
    have nodeBound := three_mul_modeNodes_le_five_mul_pow width
    have powerAtLeast : 9 ≤ 3 ^ width := by
      calc
        9 = 3 ^ 2 := by norm_num
        _ ≤ 3 ^ width := Nat.pow_le_pow_right (by omega) widthAtLeast
    have nonzero : width ≠ 0 := by omega
    simp only [modeVectorNodes, nonzero, ite_false]
    omega

/-- Logarithmic balanced preprocessing depth. -/
theorem modeDepth_le_three_add_clog (width : Nat) :
    modeDepth width ≤ 3 + Nat.clog 2 width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 2
      · interval_cases width <;> norm_num [modeDepth]
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
            modeDepth ((rest + 2) / 2) ≤
              3 + Nat.clog 2 ((rest + 2 + 1) / 2) := by
          omega
        have maximumBound :
            max (modeDepth ((rest + 2) / 2))
                (modeDepth ((rest + 2 + 1) / 2)) ≤
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
          modeDepth (rest + 2) =
              max (modeDepth ((rest + 2) / 2))
                (modeDepth ((rest + 2 + 1) / 2)) + 1 := by
                rw [modeDepth]
          _ ≤ (3 + Nat.clog 2 ((rest + 2 + 1) / 2)) + 1 :=
            Nat.add_le_add_right maximumBound 1
          _ = 3 + (Nat.clog 2 ((rest + 2 + 1) / 2) + 1) := by
            omega
          _ = 3 + Nat.clog 2 (rest + 2) := by
            rw [clogStep]

/-- Complement-closed signed selection uses the frozen signed skeleton plus one
native mode vector. -/
def complementClosedNodes (width : Nat) : Nat :=
  (router .positive width).discCount + modeVectorNodes width

/-- Complete complement-closed construction bound. -/
theorem three_mul_complementClosedNodes_le_ten_mul_pow
    (width : Nat) (positive : 1 ≤ width) :
    3 * complementClosedNodes width ≤ 10 * 3 ^ width := by
  by_cases one : width = 1
  · subst width
    norm_num [complementClosedNodes, modeVectorNodes, modeNodes, router,
      DTerm.discCount]
  · have widthAtLeast : 2 ≤ width := by omega
    have skeletonIdentity := router_discCount_identity .positive width
    have nodeBound := three_mul_modeNodes_le_five_mul_pow width
    have powerAtLeast : 9 ≤ 3 ^ width := by
      calc
        9 = 3 ^ 2 := by norm_num
        _ ≤ 3 ^ width := Nat.pow_le_pow_right (by omega) widthAtLeast
    have nonzero : width ≠ 0 := by omega
    simp only [complementClosedNodes, modeVectorNodes, nonzero, ite_false]
    rw [pow_succ] at skeletonIdentity
    omega

/-- Consolidated checkpoint. -/
theorem native_mode_cost_bounds (width : Nat) (positive : 1 ≤ width) :
    9 * modeVectorNodes width ≤ 17 * 3 ^ width ∧
      modeDepth width ≤ 3 + Nat.clog 2 width ∧
        3 * complementClosedNodes width ≤ 10 * 3 ^ width :=
  ⟨nine_mul_modeVectorNodes_le_seventeen_mul_pow width positive,
    modeDepth_le_three_add_clog width,
    three_mul_complementClosedNodes_le_ten_mul_pow width positive⟩

end OrbitSynthesis.StrongSignedRouter.NativeModeCost
