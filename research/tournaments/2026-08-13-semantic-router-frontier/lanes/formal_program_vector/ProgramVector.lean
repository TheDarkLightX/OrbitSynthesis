import StrongSignedRouter

/-!
# Exact address-only program vectors for strong signed routers

This file refines the frozen `StrongSignedRouter.program` construction.  It
computes the two control bits at a base leaf from a two-bit summary of the
target word and the branch word.  The summary records equality and the unique
"gain" mismatch `(target, branch) = (middle, right)` when all earlier digits
agree.

The imported term grammar remains unchanged: this file adds no term
constructor and does not add a free Boolean negation operation.
-/

namespace OrbitSynthesis.StrongSignedRouter.ProgramVector

open OrbitSynthesis.StrongSignedRouter

/-- Summary of a target/branch segment.  `eqFlag` says that the whole segment
matches.  `gain` says that its first mismatch is target `middle`, branch
`right`. -/
structure SegmentSummary where
  eqFlag : Bool
  gain : Bool
  deriving DecidableEq, Repr

/-- Empty-segment summary. -/
def SegmentSummary.nil : SegmentSummary := ⟨true, false⟩

/-- Left-to-right segment composition. -/
def SegmentSummary.comp (a b : SegmentSummary) : SegmentSummary :=
  ⟨a.eqFlag && b.eqFlag, a.gain || (a.eqFlag && b.gain)⟩

@[simp] theorem SegmentSummary.comp_matches (a b : SegmentSummary) :
    (a.comp b).eqFlag = (a.eqFlag && b.eqFlag) := rfl

@[simp] theorem SegmentSummary.comp_gain (a b : SegmentSummary) :
    (a.comp b).gain = (a.gain || (a.eqFlag && b.gain)) := rfl

@[simp] theorem SegmentSummary.nil_comp (a : SegmentSummary) :
    SegmentSummary.nil.comp a = a := by
  rcases a with ⟨eqFlag, gain⟩
  cases eqFlag <;> cases gain <;> rfl

@[simp] theorem SegmentSummary.comp_nil (a : SegmentSummary) :
    a.comp SegmentSummary.nil = a := by
  rcases a with ⟨eqFlag, gain⟩
  cases eqFlag <;> cases gain <;> rfl

theorem SegmentSummary.comp_assoc (a b c : SegmentSummary) :
    (a.comp b).comp c = a.comp (b.comp c) := by
  rcases a with ⟨am, ag⟩
  rcases b with ⟨bm, bg⟩
  rcases c with ⟨cm, cg⟩
  cases am <;> cases ag <;> cases bm <;> cases bg <;>
    cases cm <;> cases cg <;> rfl

/-- One-digit summary. -/
def digitSummary : Digit → Digit → SegmentSummary
  | .left, .left => ⟨true, false⟩
  | .left, .middle => ⟨false, false⟩
  | .left, .right => ⟨false, false⟩
  | .middle, .left => ⟨false, false⟩
  | .middle, .middle => ⟨true, false⟩
  | .middle, .right => ⟨false, true⟩
  | .right, .left => ⟨false, false⟩
  | .right, .middle => ⟨false, false⟩
  | .right, .right => ⟨true, false⟩

/-- Summary of two equal-length ternary addresses. -/
def addressSummary : (n : Nat) → Address n → Address n → SegmentSummary
  | 0, _, _ => SegmentSummary.nil
  | n + 1, (targetDigit, targetTail), (branchDigit, branchTail) =>
      (digitSummary targetDigit branchDigit).comp
        (addressSummary n targetTail branchTail)

/-- The exact first-mismatch predicate represented by `SegmentSummary.gain`. -/
def FirstGain : (n : Nat) → Address n → Address n → Prop
  | 0, _, _ => False
  | n + 1, (targetDigit, targetTail), (branchDigit, branchTail) =>
      (targetDigit = .middle ∧ branchDigit = .right) ∨
        (targetDigit = branchDigit ∧ FirstGain n targetTail branchTail)

theorem addressSummary_matches_iff :
    ∀ n (target branch : Address n),
      (addressSummary n target branch).eqFlag = true ↔ target = branch
  | 0, target, branch => by
      rcases target with ⟨⟩
      rcases branch with ⟨⟩
      constructor <;> intro _ <;> rfl
  | n + 1, (targetDigit, targetTail), (branchDigit, branchTail) => by
      change
        ((digitSummary targetDigit branchDigit).comp
            (addressSummary n targetTail branchTail)).eqFlag = true ↔
          ((targetDigit, targetTail) : Digit × Address n) =
            (branchDigit, branchTail)
      cases targetDigit <;> cases branchDigit <;>
        simp [digitSummary, SegmentSummary.comp, Prod.mk.injEq,
          addressSummary_matches_iff n]

theorem addressSummary_gain_iff :
    ∀ n (target branch : Address n),
      (addressSummary n target branch).gain = true ↔
        FirstGain n target branch
  | 0, target, branch => by
      rcases target with ⟨⟩
      rcases branch with ⟨⟩
      simp [addressSummary, SegmentSummary.nil, FirstGain]
  | n + 1, (targetDigit, targetTail), (branchDigit, branchTail) => by
      cases targetDigit <;> cases branchDigit <;>
        simp [addressSummary, digitSummary, SegmentSummary.comp, FirstGain,
          addressSummary_gain_iff n]

theorem addressSummary_disjoint :
    ∀ n (target branch : Address n),
      ((addressSummary n target branch).eqFlag &&
        (addressSummary n target branch).gain) = false
  | 0, target, branch => by
      rcases target with ⟨⟩
      rcases branch with ⟨⟩
      rfl
  | n + 1, (targetDigit, targetTail), (branchDigit, branchTail) => by
      cases targetDigit <;> cases branchDigit <;>
        simp [addressSummary, digitSummary, SegmentSummary.comp,
          addressSummary_disjoint n]

/-- A segment represented directly as aligned `(target, branch)` digit pairs. -/
def summarizePairs : List (Digit × Digit) → SegmentSummary
  | [] => SegmentSummary.nil
  | pair :: pairs => (digitSummary pair.1 pair.2).comp (summarizePairs pairs)

/-- Exact segment-concatenation law.  Associativity permits any balanced
parenthesization of consecutive segment summaries. -/
theorem summarizePairs_append (xs ys : List (Digit × Digit)) :
    summarizePairs (xs ++ ys) =
      (summarizePairs xs).comp (summarizePairs ys) := by
  induction xs with
  | nil => simp [summarizePairs]
  | cons pair xs ih =>
      simp only [List.cons_append, summarizePairs, ih]
      exact (SegmentSummary.comp_assoc
        (digitSummary pair.1 pair.2) (summarizePairs xs)
          (summarizePairs ys)).symm

/-- Aligned pair-list view of two addresses. -/
def addressPairs : (n : Nat) → Address n → Address n → List (Digit × Digit)
  | 0, _, _ => []
  | n + 1, (targetDigit, targetTail), (branchDigit, branchTail) =>
      (targetDigit, branchDigit) :: addressPairs n targetTail branchTail

theorem addressSummary_eq_summarizePairs :
    ∀ n (target branch : Address n),
      addressSummary n target branch =
        summarizePairs (addressPairs n target branch)
  | 0, target, branch => by
      rcases target with ⟨⟩
      rcases branch with ⟨⟩
      rfl
  | n + 1, (targetDigit, targetTail), (branchDigit, branchTail) => by
      simp [addressSummary, addressPairs, summarizePairs,
        addressSummary_eq_summarizePairs n]

/-- Follow one branch address down a mode until the base router. -/
def descendMode : (n : Nat) → Mode n → Address n → Mode 0
  | 0, mode, _ => mode
  | n + 1, mode, (digit, tail) =>
      descendMode n (childMode mode digit) tail

@[simp] theorem descendMode_constant :
    ∀ n (value : Bool) (branch : Address n),
      descendMode n (.constant value) branch = .constant value
  | 0, value, branch => by
      rcases branch with ⟨⟩
      rfl
  | n + 1, value, (digit, tail) => by
      simp [descendMode, childMode, descendMode_constant n]

/-- Decode a summary into the exact base mode: equality projects, otherwise
`gain` selects constant one and its absence selects constant zero. -/
def modeOfSummary (summary : SegmentSummary) : Mode 0 :=
  if summary.eqFlag then .project PUnit.unit else .constant summary.gain

theorem descendMode_project_summary :
    ∀ n (target branch : Address n),
      descendMode n (.project target) branch =
        modeOfSummary (addressSummary n target branch)
  | 0, target, branch => by
      rcases target with ⟨⟩
      rcases branch with ⟨⟩
      rfl
  | n + 1, (targetDigit, targetTail), (branchDigit, branchTail) => by
      cases targetDigit <;> cases branchDigit <;>
        simp [descendMode, childMode, addressSummary, digitSummary,
          SegmentSummary.comp, modeOfSummary,
          descendMode_project_summary n]

theorem descendMode_project_iff (n : Nat) (target branch : Address n) :
    descendMode n (.project target) branch = .project PUnit.unit ↔
      target = branch := by
  rw [descendMode_project_summary, ← addressSummary_matches_iff]
  generalize addressSummary n target branch = summary
  rcases summary with ⟨eqFlag, gain⟩
  cases eqFlag <;> cases gain <;> simp [modeOfSummary]

theorem descendMode_one_iff (n : Nat) (target branch : Address n) :
    descendMode n (.project target) branch = .constant true ↔
      FirstGain n target branch := by
  rw [descendMode_project_summary, ← addressSummary_gain_iff]
  have disjoint := addressSummary_disjoint n target branch
  generalize addressSummary n target branch = summary at disjoint ⊢
  rcases summary with ⟨eqFlag, gain⟩
  cases eqFlag <;> cases gain <;> simp [modeOfSummary] at disjoint ⊢

theorem descendMode_zero_iff (n : Nat) (target branch : Address n) :
    descendMode n (.project target) branch = .constant false ↔
      target ≠ branch ∧ ¬ FirstGain n target branch := by
  rw [descendMode_project_summary]
  have eqSpec := addressSummary_matches_iff n target branch
  have gainSpec := addressSummary_gain_iff n target branch
  generalize addressSummary n target branch = summary at eqSpec gainSpec ⊢
  rcases summary with ⟨eqFlag, gain⟩
  cases eqFlag <;> cases gain <;> simp_all [modeOfSummary]

/-- Follow one branch address down the signed router. -/
def descendSign : (n : Nat) → Sign → Address n → Sign
  | 0, sign, _ => sign
  | n + 1, sign, (digit, tail) =>
      descendSign n (childSign sign digit) tail

def middleBit : Digit → Bool
  | .left => false
  | .middle => true
  | .right => false

def boolXor : Bool → Bool → Bool
  | false, value => value
  | true, value => !value

def middleParity : (n : Nat) → Address n → Bool
  | 0, _ => false
  | n + 1, (digit, tail) => boolXor (middleBit digit) (middleParity n tail)

def signXor : Sign → Bool → Sign
  | sign, false => sign
  | .positive, true => .negative
  | .negative, true => .positive

def isNegative : Sign → Bool
  | .positive => false
  | .negative => true

theorem descendSign_eq_signXor :
    ∀ n (root : Sign) (branch : Address n),
      descendSign n root branch = signXor root (middleParity n branch)
  | 0, root, branch => by
      rcases branch with ⟨⟩
      cases root <;> rfl
  | n + 1, root, (digit, tail) => by
      rw [descendSign]
      rw [descendSign_eq_signXor n]
      cases root <;> cases digit <;>
        cases parity : middleParity n tail <;>
        simp [middleParity, middleBit, boolXor, childSign, signXor, parity]

theorem isNegative_signXor (root : Sign) (parity : Bool) :
    isNegative (signXor root parity) =
      boolXor (isNegative root) parity := by
  cases root <;> cases parity <;> rfl

theorem descendSign_isNegative (n : Nat) (root : Sign)
    (branch : Address n) :
    isNegative (descendSign n root branch) =
      boolXor (isNegative root) (middleParity n branch) := by
  rw [descendSign_eq_signXor, isNegative_signXor]

/-- Reduce a recursive program lookup to the selected base leaf. -/
theorem program_eq_base :
    ∀ n (sign : Sign) (mode : Mode n) (slot : Slot) (branch : Address n),
      program sign n mode (slot, branch) =
        baseProgram (descendSign n sign branch)
          (descendMode n mode branch) slot
  | 0, sign, mode, slot, branch => by
      rcases branch with ⟨⟩
      rfl
  | n + 1, sign, mode, slot, (digit, tail) => by
      exact program_eq_base n (childSign sign digit) (childMode mode digit)
        slot tail

/-- First control bit as a Boolean function of equality, first-gain, and the
base sign (`negative = true`). -/
def firstControlBit (eqFlag gain negative : Bool) : Bool :=
  (!eqFlag) && (gain == negative)

/-- Second control bit as a Boolean function of equality, first-gain, and the
base sign (`negative = true`). -/
def secondControlBit (eqFlag gain negative : Bool) : Bool :=
  (negative && eqFlag) || ((!eqFlag) && gain)

theorem baseProgram_modeOfSummary_first (sign : Sign)
    (summary : SegmentSummary) :
    baseProgram sign (modeOfSummary summary) .first =
      firstControlBit summary.eqFlag summary.gain (isNegative sign) := by
  rcases summary with ⟨eqFlag, gain⟩
  cases sign <;> cases eqFlag <;> cases gain <;> rfl

theorem baseProgram_modeOfSummary_second (sign : Sign)
    (summary : SegmentSummary) :
    baseProgram sign (modeOfSummary summary) .second =
      secondControlBit summary.eqFlag summary.gain (isNegative sign) := by
  rcases summary with ⟨eqFlag, gain⟩
  cases sign <;> cases eqFlag <;> cases gain <;> rfl

theorem projection_program_first (n : Nat) (root : Sign)
    (target branch : Address n) :
    program root n (.project target) (.first, branch) =
      firstControlBit
        (addressSummary n target branch).eqFlag
        (addressSummary n target branch).gain
        (boolXor (isNegative root) (middleParity n branch)) := by
  rw [program_eq_base, descendMode_project_summary]
  rw [baseProgram_modeOfSummary_first, descendSign_isNegative]

theorem projection_program_second (n : Nat) (root : Sign)
    (target branch : Address n) :
    program root n (.project target) (.second, branch) =
      secondControlBit
        (addressSummary n target branch).eqFlag
        (addressSummary n target branch).gain
        (boolXor (isNegative root) (middleParity n branch)) := by
  rw [program_eq_base, descendMode_project_summary]
  rw [baseProgram_modeOfSummary_second, descendSign_isNegative]

/-- The exact two-bit projection program at one base leaf. -/
theorem projection_program_pair (n : Nat) (root : Sign)
    (target branch : Address n) :
    (program root n (.project target) (.first, branch),
      program root n (.project target) (.second, branch)) =
    (firstControlBit
        (addressSummary n target branch).eqFlag
        (addressSummary n target branch).gain
        (boolXor (isNegative root) (middleParity n branch)),
      secondControlBit
        (addressSummary n target branch).eqFlag
        (addressSummary n target branch).gain
        (boolXor (isNegative root) (middleParity n branch))) := by
  rw [projection_program_first, projection_program_second]

end OrbitSynthesis.StrongSignedRouter.ProgramVector
