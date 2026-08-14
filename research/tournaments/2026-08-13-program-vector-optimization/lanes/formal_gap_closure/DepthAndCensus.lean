import SiblingShared

/-!
# Sharp depth and all-width output census

This file closes two local gaps left explicit by the optimized formal lane:

* the sibling-shared construction depth recurrence has depth at most
  `3 + Nat.clog 2 width` for positive widths;
* the distinct scalar Boolean projection controls are counted all-width.

The census uses a recursive truth-table syntax whose three children are the
target-left, target-middle, and target-right blocks.  An injective evaluation
map connects those structural tables to actual Boolean functions on the
frozen `Address` type.
-/

namespace OrbitSynthesis.StrongSignedRouter.FormalGapClosure

open OrbitSynthesis.StrongSignedRouter
open OrbitSynthesis.StrongSignedRouter.ProgramVector
open OrbitSynthesis.StrongSignedRouter.ProgramVectorCost
open OrbitSynthesis.StrongSignedRouter.FormalOptimized

/-! ## Exact sharp-depth ledger -/

/-- Depth of either recursively built generic BG or extended BGN library.
The one-digit original-signature library has depth three; every balanced
composition layer adds exactly one possible discriminator layer. -/
def siblingLibraryDepth : Nat → Nat
  | 0 => 0
  | 1 => 3
  | width@(_ + 2) =>
      max (siblingLibraryDepth ((width + 1) / 2))
        (siblingLibraryDepth (width / 2)) + 1
termination_by width => width
decreasing_by
  all_goals simp_wf
  all_goals omega

/-- The sign-specialized terminal merge has the same recurrence: it adds one
parallel discriminator layer above the longer-left BG and shorter-right BGN
libraries.  Width one uses the direct legal base; width zero uses the two
anchor names. -/
def siblingSharedDepth : Nat → Nat
  | 0 => 2
  | 1 => 3
  | width@(_ + 2) =>
      max (siblingLibraryDepth ((width + 1) / 2))
        (siblingLibraryDepth (width / 2)) + 1

theorem siblingLibraryDepth_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    siblingLibraryDepth width =
      max (siblingLibraryDepth ((width + 1) / 2))
        (siblingLibraryDepth (width / 2)) + 1 := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [siblingLibraryDepth]

theorem siblingSharedDepth_recurrence (width : Nat) (atLeastTwo : 2 ≤ width) :
    siblingSharedDepth width =
      max (siblingLibraryDepth ((width + 1) / 2))
        (siblingLibraryDepth (width / 2)) + 1 := by
  obtain ⟨rest, rfl⟩ : ∃ rest, width = rest + 2 :=
    ⟨width - 2, by omega⟩
  rw [siblingSharedDepth]

theorem siblingLibraryDepth_le_three_add_clog (width : Nat) :
    siblingLibraryDepth width ≤ 3 + Nat.clog 2 width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 2
      · interval_cases width <;> norm_num [siblingLibraryDepth]
      · have widthAtLeast : 2 ≤ width := by omega
        let leftWidth := (width + 1) / 2
        let rightWidth := width / 2
        have leftLess : leftWidth < width := by
          dsimp [leftWidth]
          omega
        have rightLess : rightWidth < width := by
          dsimp [rightWidth]
          omega
        have leftBound := ih leftWidth leftLess
        have rightBound := ih rightWidth rightLess
        have widthsOrdered : rightWidth ≤ leftWidth := by
          dsimp [leftWidth, rightWidth]
          omega
        have logsOrdered : Nat.clog 2 rightWidth ≤ Nat.clog 2 leftWidth :=
          Nat.clog_mono_right 2 widthsOrdered
        have rightBound' :
            siblingLibraryDepth rightWidth ≤ 3 + Nat.clog 2 leftWidth := by
          omega
        have maximumBound :
            max (siblingLibraryDepth leftWidth)
                (siblingLibraryDepth rightWidth) ≤
              3 + Nat.clog 2 leftWidth :=
          max_le leftBound rightBound'
        have clogStep :
            Nat.clog 2 width = Nat.clog 2 leftWidth + 1 := by
          dsimp [leftWidth]
          have quotientArgument :
              (width + 2 - 1) / 2 = (width + 1) / 2 := by
            congr 1
          calc
            Nat.clog 2 width = Nat.clog 2 ((width + 2 - 1) / 2) + 1 :=
              Nat.clog_of_two_le (by omega) (by omega)
            _ = Nat.clog 2 ((width + 1) / 2) + 1 := by
              rw [quotientArgument]
        calc
          siblingLibraryDepth width =
              max (siblingLibraryDepth leftWidth)
                (siblingLibraryDepth rightWidth) + 1 := by
            simpa [leftWidth, rightWidth] using
              siblingLibraryDepth_recurrence width widthAtLeast
          _ ≤ (3 + Nat.clog 2 leftWidth) + 1 :=
            Nat.add_le_add_right maximumBound 1
          _ = 3 + Nat.clog 2 width := by omega

theorem siblingSharedDepth_le_three_add_clog (width : Nat)
    (positive : 1 ≤ width) :
    siblingSharedDepth width ≤ 3 + Nat.clog 2 width := by
  by_cases one : width = 1
  · subst width
    norm_num [siblingSharedDepth]
  · have atLeastTwo : 2 ≤ width := by omega
    rw [siblingSharedDepth_recurrence width atLeastTwo]
    rw [← siblingLibraryDepth_recurrence width atLeastTwo]
    exact siblingLibraryDepth_le_three_add_clog width

/-- The exact size and sharp depth recurrences share the same longer-left,
shorter-right split. -/
theorem siblingShared_size_depth_checkpoint (root : Sign) (width : Nat)
    (positive : 1 ≤ width) :
    3 * siblingSharedNodes root width ≤
        4 * 3 ^ width + 15 * 3 ^ ((width + 1) / 2) ∧
      siblingSharedDepth width ≤ 3 + Nat.clog 2 width :=
  ⟨siblingSharedNodes_scaled_envelope root width,
    siblingSharedDepth_le_three_add_clog width positive⟩

/-! ## Structural ternary truth tables -/

inductive TruthTable : Nat → Type
  | leaf : Bool → TruthTable 0
  | node : TruthTable n → TruthTable n → TruthTable n → TruthTable (n + 1)
  deriving DecidableEq, Repr

namespace TruthTable

def eval : {n : Nat} → TruthTable n → Address n → Bool
  | 0, .leaf value, _ => value
  | _ + 1, .node left middle right, (digit, tail) =>
      match digit with
      | .left => left.eval tail
      | .middle => middle.eval tail
      | .right => right.eval tail

def falseTable : (n : Nat) → TruthTable n
  | 0 => .leaf false
  | n + 1 => .node (falseTable n) (falseTable n) (falseTable n)

def trueTable : (n : Nat) → TruthTable n
  | 0 => .leaf true
  | n + 1 => .node (trueTable n) (trueTable n) (trueTable n)

@[simp] theorem eval_falseTable (n : Nat) (address : Address n) :
    (falseTable n).eval address = false := by
  induction n with
  | zero => rfl
  | succ n ih =>
      rcases address with ⟨digit, tail⟩
      cases digit <;> exact ih tail

@[simp] theorem eval_trueTable (n : Nat) (address : Address n) :
    (trueTable n).eval address = true := by
  induction n with
  | zero => rfl
  | succ n ih =>
      rcases address with ⟨digit, tail⟩
      cases digit <;> exact ih tail

theorem eval_injective (n : Nat) :
    Function.Injective (eval : TruthTable n → Address n → Bool) := by
  induction n with
  | zero =>
      intro left right equality
      rcases left with ⟨leftValue⟩
      rcases right with ⟨rightValue⟩
      have := congr_fun equality PUnit.unit
      simp [eval] at this
      subst rightValue
      rfl
  | succ n ih =>
      intro left right equality
      rcases left with ⟨leftLeft, leftMiddle, leftRight⟩
      rcases right with ⟨rightLeft, rightMiddle, rightRight⟩
      congr
      · apply ih
        funext tail
        exact congr_fun equality (.left, tail)
      · apply ih
        funext tail
        exact congr_fun equality (.middle, tail)
      · apply ih
        funext tail
        exact congr_fun equality (.right, tail)

theorem false_ne_true (n : Nat) : falseTable n ≠ trueTable n := by
  induction n with
  | zero => decide
  | succ n ih =>
      intro equality
      have leftEquality : falseTable n = trueTable n := by
        injection equality
      exact ih leftEquality

end TruthTable

/-! ## First-mismatch table families -/

def gainTable : (n : Nat) → Address n → TruthTable n
  | 0, _ => .leaf false
  | n + 1, (physical, tail) =>
      match physical with
      | .left => .node (gainTable n tail)
          (TruthTable.falseTable n) (TruthTable.falseTable n)
      | .middle => .node (TruthTable.falseTable n)
          (gainTable n tail) (TruthTable.falseTable n)
      | .right => .node (TruthTable.falseTable n)
          (TruthTable.trueTable n) (gainTable n tail)

def badTable : (n : Nat) → Address n → TruthTable n
  | 0, _ => .leaf false
  | n + 1, (physical, tail) =>
      match physical with
      | .left => .node (badTable n tail)
          (TruthTable.trueTable n) (TruthTable.trueTable n)
      | .middle => .node (TruthTable.trueTable n)
          (badTable n tail) (TruthTable.trueTable n)
      | .right => .node (TruthTable.trueTable n)
          (TruthTable.falseTable n) (badTable n tail)

def notBadTable : (n : Nat) → Address n → TruthTable n
  | 0, _ => .leaf true
  | n + 1, (physical, tail) =>
      match physical with
      | .left => .node (notBadTable n tail)
          (TruthTable.falseTable n) (TruthTable.falseTable n)
      | .middle => .node (TruthTable.falseTable n)
          (notBadTable n tail) (TruthTable.falseTable n)
      | .right => .node (TruthTable.falseTable n)
          (TruthTable.trueTable n) (notBadTable n tail)

theorem gainTable_eval :
    ∀ n (physical target : Address n),
      (gainTable n physical).eval target =
        (addressSummary n target physical).gain
  | 0, physical, target => by
      rcases physical with ⟨⟩
      rcases target with ⟨⟩
      rfl
  | n + 1, (physicalDigit, physicalTail), (targetDigit, targetTail) => by
      cases physicalDigit <;> cases targetDigit <;>
        simp [gainTable, TruthTable.eval, addressSummary, digitSummary,
          SegmentSummary.comp, gainTable_eval n]

theorem badTable_eval :
    ∀ n (physical target : Address n),
      (badTable n physical).eval target =
        ((!((addressSummary n target physical).eqFlag)) &&
          !((addressSummary n target physical).gain))
  | 0, physical, target => by
      rcases physical with ⟨⟩
      rcases target with ⟨⟩
      rfl
  | n + 1, (physicalDigit, physicalTail), (targetDigit, targetTail) => by
      cases physicalDigit <;> cases targetDigit <;>
        simp [badTable, TruthTable.eval, addressSummary, digitSummary,
          SegmentSummary.comp, badTable_eval n]

theorem notBadTable_eval :
    ∀ n (physical target : Address n),
      (notBadTable n physical).eval target =
        ((addressSummary n target physical).eqFlag ||
          (addressSummary n target physical).gain)
  | 0, physical, target => by
      rcases physical with ⟨⟩
      rcases target with ⟨⟩
      rfl
  | n + 1, (physicalDigit, physicalTail), (targetDigit, targetTail) => by
      cases physicalDigit <;> cases targetDigit <;>
        simp [notBadTable, TruthTable.eval, addressSummary, digitSummary,
          SegmentSummary.comp, notBadTable_eval n]

theorem notBadTable_is_complement (n : Nat) (physical target : Address n) :
    (notBadTable n physical).eval target =
      !((badTable n physical).eval target) := by
  rw [badTable_eval, notBadTable_eval]
  have disjoint := addressSummary_disjoint n target physical
  rcases summaryValue : addressSummary n target physical with ⟨equal, gain⟩
  simp only [summaryValue] at disjoint ⊢
  cases equal <;> cases gain <;> simp_all

theorem addressSummary_self :
    ∀ n (physical : Address n),
      addressSummary n physical physical = SegmentSummary.nil
  | 0, physical => by
      rcases physical with ⟨⟩
      rfl
  | n + 1, (digit, tail) => by
      cases digit <;>
        simp [addressSummary, digitSummary, SegmentSummary.nil,
          SegmentSummary.comp, addressSummary_self n]

theorem gainTable_ne_true (n : Nat) (physical : Address n) :
    gainTable n physical ≠ TruthTable.trueTable n := by
  intro equality
  have evaluated := congr_arg
    (fun table => table.eval physical) equality
  rw [gainTable_eval, TruthTable.eval_trueTable, addressSummary_self] at evaluated
  contradiction

theorem badTable_ne_true (n : Nat) (physical : Address n) :
    badTable n physical ≠ TruthTable.trueTable n := by
  intro equality
  have evaluated := congr_arg
    (fun table => table.eval physical) equality
  rw [badTable_eval, TruthTable.eval_trueTable, addressSummary_self] at evaluated
  contradiction

theorem notBadTable_ne_false (n : Nat) (physical : Address n) :
    notBadTable n physical ≠ TruthTable.falseTable n := by
  intro equality
  have evaluated := congr_arg
    (fun table => table.eval physical) equality
  rw [notBadTable_eval, TruthTable.eval_falseTable, addressSummary_self] at evaluated
  contradiction

/-- A target that forces a bad first mismatch at the first digit. -/
def badWitnessTarget {n : Nat} : Address (n + 1) → Address (n + 1)
  | (.left, tail) => (.middle, tail)
  | (.middle, tail) => (.left, tail)
  | (.right, tail) => (.left, tail)

theorem badTable_witness_true {n : Nat} (physical : Address (n + 1)) :
    (badTable (n + 1) physical).eval (badWitnessTarget physical) = true := by
  rcases physical with ⟨digit, tail⟩
  cases digit <;>
    simp [badWitnessTarget, badTable, TruthTable.eval]

theorem notBadTable_witness_false {n : Nat} (physical : Address (n + 1)) :
    (notBadTable (n + 1) physical).eval (badWitnessTarget physical) = false := by
  rw [notBadTable_is_complement, badTable_witness_true]
  rfl

theorem badTable_ne_false {n : Nat} (physical : Address (n + 1)) :
    badTable (n + 1) physical ≠ TruthTable.falseTable (n + 1) := by
  intro equality
  have evaluated := congr_arg
    (fun table => table.eval (badWitnessTarget physical)) equality
  rw [badTable_witness_true, TruthTable.eval_falseTable] at evaluated
  contradiction

theorem notBadTable_ne_true {n : Nat} (physical : Address (n + 1)) :
    notBadTable (n + 1) physical ≠ TruthTable.trueTable (n + 1) := by
  intro equality
  have evaluated := congr_arg
    (fun table => table.eval (badWitnessTarget physical)) equality
  rw [notBadTable_witness_false, TruthTable.eval_trueTable] at evaluated
  contradiction

theorem badTable_injective :
    ∀ n, Function.Injective (badTable n)
  | 0, left, right, _ => by
      rcases left with ⟨⟩
      rcases right with ⟨⟩
      rfl
  | n + 1, (leftDigit, leftTail), (rightDigit, rightTail), equality => by
      cases leftDigit <;> cases rightDigit <;>
        simp only [badTable, TruthTable.node.injEq] at equality
      · congr
        exact badTable_injective n equality.1
      · exfalso
        exact badTable_ne_true n _ equality.1
      · exfalso
        exact badTable_ne_true n _ equality.1
      · exfalso
        exact badTable_ne_true n _ equality.1.symm
      · congr
        exact badTable_injective n equality.2.1
      · exfalso
        exact badTable_ne_true n _ equality.2.2.symm
      · exfalso
        exact TruthTable.false_ne_true n equality.2.1
      · exfalso
        exact badTable_ne_true n _ equality.2.2
      · congr
        exact badTable_injective n equality.2.2

theorem notBadTable_injective :
    ∀ n, Function.Injective (notBadTable n)
  | 0, left, right, _ => by
      rcases left with ⟨⟩
      rcases right with ⟨⟩
      rfl
  | n + 1, (leftDigit, leftTail), (rightDigit, rightTail), equality => by
      cases leftDigit <;> cases rightDigit <;>
        simp only [notBadTable, TruthTable.node.injEq] at equality
      · congr
        exact notBadTable_injective n equality.1
      · exfalso
        exact notBadTable_ne_false n _ equality.1
      · exfalso
        exact TruthTable.false_ne_true n equality.2.1
      · exfalso
        exact notBadTable_ne_false n _ equality.1.symm
      · congr
        exact notBadTable_injective n equality.2.1
      · exfalso
        exact notBadTable_ne_false n _ equality.2.2.symm
      · exfalso
        exact TruthTable.false_ne_true n equality.2.1.symm
      · exfalso
        exact notBadTable_ne_false n _ equality.2.2
      · congr
        exact notBadTable_injective n equality.2.2

end OrbitSynthesis.StrongSignedRouter.FormalGapClosure
