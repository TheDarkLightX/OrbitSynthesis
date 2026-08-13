import Mathlib.Tactic

/-!
# Native first-mismatch algebra

The three reachable comparison outcomes are `loss`, `gain`, and `equal`.
Composition returns the first outcome that is not `equal`. Under the encoding
`loss -> 0`, `gain -> 1`, and `equal -> 2`, this product is exactly the
ternary discriminator operation `d(x,2,y)`.
-/

namespace OrbitSynthesis.NativeFirstMismatch

inductive Q where
  | zero
  | one
  | two
  deriving DecidableEq, Repr

/-- Ternary discriminator: use the third argument when the first two agree,
and otherwise retain the first. -/
def disc (x y z : Q) : Q :=
  if x = y then z else x

inductive Outcome where
  | loss
  | gain
  | equal
  deriving DecidableEq, Repr

/-- First-non-equal composition. -/
def Outcome.comp : Outcome → Outcome → Outcome
  | .equal, right => right
  | .gain, _ => .gain
  | .loss, _ => .loss

@[simp] theorem Outcome.equal_comp (x : Outcome) :
    Outcome.equal.comp x = x := rfl

@[simp] theorem Outcome.comp_equal (x : Outcome) :
    x.comp Outcome.equal = x := by
  cases x <;> rfl

@[simp] theorem Outcome.loss_comp (x : Outcome) :
    Outcome.loss.comp x = .loss := rfl

@[simp] theorem Outcome.gain_comp (x : Outcome) :
    Outcome.gain.comp x = .gain := rfl

theorem Outcome.comp_assoc (a b c : Outcome) :
    (a.comp b).comp c = a.comp (b.comp c) := by
  cases a <;> rfl

/-- Native carrier encoding. -/
def Outcome.encode : Outcome → Q
  | .loss => .zero
  | .gain => .one
  | .equal => .two

/-- The discriminator is exactly first-non-equal multiplication. -/
@[simp] theorem Outcome.encode_comp (a b : Outcome) :
    (a.comp b).encode = disc a.encode .two b.encode := by
  cases a <;> cases b <;> rfl

theorem Outcome.encode_injective : Function.Injective Outcome.encode := by
  intro a b h
  cases a <;> cases b <;> simp_all [Outcome.encode]

inductive Digit where
  | left
  | middle
  | right
  deriving DecidableEq, Repr

/-- One aligned digit pair. The only gain mismatch is `(middle,right)`. -/
def digitOutcome : Digit → Digit → Outcome
  | .left, .left => .equal
  | .middle, .middle => .equal
  | .right, .right => .equal
  | .middle, .right => .gain
  | _, _ => .loss

/-- Fixed-width ternary addresses. -/
def Address : Nat → Type
  | 0 => PUnit
  | n + 1 => Digit × Address n

/-- Outcome of comparing two addresses from left to right. -/
def addressOutcome : (n : Nat) → Address n → Address n → Outcome
  | 0, _, _ => .equal
  | n + 1, (targetDigit, targetTail), (physicalDigit, physicalTail) =>
      (digitOutcome targetDigit physicalDigit).comp
        (addressOutcome n targetTail physicalTail)

/-- Exact first-gain predicate. -/
def FirstGain : (n : Nat) → Address n → Address n → Prop
  | 0, _, _ => False
  | n + 1, (targetDigit, targetTail), (physicalDigit, physicalTail) =>
      (targetDigit = .middle ∧ physicalDigit = .right) ∨
        (targetDigit = physicalDigit ∧
          FirstGain n targetTail physicalTail)

theorem addressOutcome_equal_iff :
    ∀ n (target physical : Address n),
      addressOutcome n target physical = .equal ↔ target = physical
  | 0, target, physical => by
      rcases target with ⟨⟩
      rcases physical with ⟨⟩
      simp [addressOutcome]
  | n + 1, (targetDigit, targetTail), (physicalDigit, physicalTail) => by
      cases targetDigit <;> cases physicalDigit <;>
        simp [addressOutcome, digitOutcome, Outcome.comp, Prod.mk.injEq,
          addressOutcome_equal_iff n]

theorem addressOutcome_gain_iff :
    ∀ n (target physical : Address n),
      addressOutcome n target physical = .gain ↔
        FirstGain n target physical
  | 0, target, physical => by
      rcases target with ⟨⟩
      rcases physical with ⟨⟩
      simp [addressOutcome, FirstGain]
  | n + 1, (targetDigit, targetTail), (physicalDigit, physicalTail) => by
      cases targetDigit <;> cases physicalDigit <;>
        simp [addressOutcome, digitOutcome, Outcome.comp, FirstGain,
          addressOutcome_gain_iff n]

theorem addressOutcome_loss_iff (n : Nat)
    (target physical : Address n) :
    addressOutcome n target physical = .loss ↔
      target ≠ physical ∧ ¬ FirstGain n target physical := by
  have hEqual := addressOutcome_equal_iff n target physical
  have hGain := addressOutcome_gain_iff n target physical
  generalize hMode : addressOutcome n target physical = mode at hEqual hGain ⊢
  cases mode <;> simp_all

/-- One `Q`-valued root for every physical address. -/
def root (n : Nat) (physical target : Address n) : Q :=
  (addressOutcome n target physical).encode

@[simp] theorem root_self (n : Nat) (physical : Address n) :
    root n physical physical = .two := by
  have h := (addressOutcome_equal_iff n physical physical).2 rfl
  simp [root, h, Outcome.encode]

theorem root_ne_two_of_ne (n : Nat) (physical target : Address n)
    (h : target ≠ physical) :
    root n physical target ≠ .two := by
  have hNotEqual : addressOutcome n target physical ≠ .equal := by
    intro hEqual
    exact h ((addressOutcome_equal_iff n target physical).1 hEqual)
  cases hMode : addressOutcome n target physical <;>
    simp_all [root, Outcome.encode]

/-- The complete family of roots is pairwise distinct. -/
theorem roots_injective (n : Nat) :
    Function.Injective
      (fun physical : Address n => fun target => root n physical target) := by
  intro left right hRoots
  by_contra hDifferent
  have hValue := congrFun hRoots left
  have hLeft := root_self n left
  have hRight := root_ne_two_of_ne n right left hDifferent
  apply hRight
  rw [← hValue]
  exact hLeft

end OrbitSynthesis.NativeFirstMismatch
