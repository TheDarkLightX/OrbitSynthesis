import ProgramVectorCost

/-!
# Formal repairs for manuscript-facing claims

This file leaves the frozen formal lanes unchanged. It replaces their
native-evaluator cardinality checkpoints by kernel-reduced `decide` proofs,
states the constant-free constructor catalogs directly, and proves the outer
glue and two-plane decoder identities in the original three-element algebra.
-/

namespace OrbitSynthesis.StrongSignedRouter.ManuscriptRepairs

open OrbitSynthesis.StrongSignedRouter
open OrbitSynthesis.StrongSignedRouter.ProgramVectorCost

theorem card_digit_kernel : Fintype.card Digit = 3 := by
  decide

theorem card_slot_kernel : Fintype.card Slot = 2 := by
  decide

theorem card_address_kernel (n : Nat) : Fintype.card (Address n) = 3 ^ n := by
  induction n with
  | zero => decide
  | succ n ih =>
      calc
        Fintype.card (Address (n + 1)) =
            Fintype.card (Digit × Address n) :=
          Fintype.card_congr (Equiv.refl (Digit × Address n))
        _ = Fintype.card Digit * Fintype.card (Address n) :=
          Fintype.card_prod _ _
        _ = 3 ^ (n + 1) := by
          rw [card_digit_kernel, ih, pow_succ]
          omega

theorem card_control_kernel (n : Nat) :
    Fintype.card (Control n) = 2 * 3 ^ n := by
  simp only [Control, Fintype.card_prod, card_slot_kernel, card_address_kernel]

theorem capacity_at_depth_kernel (h : Nat) :
    Fintype.card (Address (h - 1)) = 3 ^ (h - 1) :=
  card_address_kernel (h - 1)

/-- The constructor catalog is the substantive constant-free grammar fact:
there is no fourth, nullary constructor to consider. -/
theorem dterm_constructor_catalog {Branch Control : Type}
    (term : DTerm Branch Control) :
    (∃ branch, term = .branch branch) ∨
      (∃ control, term = .control control) ∨
      (∃ left middle right, term = .disc left middle right) := by
  cases term with
  | branch branch => exact Or.inl ⟨branch, rfl⟩
  | control control => exact Or.inr (Or.inl ⟨control, rfl⟩)
  | disc left middle right =>
      exact Or.inr (Or.inr ⟨left, middle, right, rfl⟩)

theorem qterm_constructor_catalog {Var : Type} (term : QTerm Var) :
    (∃ variableId, term = .variable variableId) ∨
      (∃ child, term = .unary child) ∨
      (∃ left middle right, term = .disc left middle right) := by
  cases term with
  | «variable» variableId => exact Or.inl ⟨variableId, rfl⟩
  | unary child => exact Or.inr (Or.inl ⟨child, rfl⟩)
  | disc left middle right =>
      exact Or.inr (Or.inr ⟨left, middle, right, rfl⟩)

def anchorFoldCell (x y : Q) : Q :=
  qDisc x (qUnary (qUnary x)) (qDisc y (qUnary x) x)

theorem anchorFoldCell_semantics (x y : Q) :
    anchorFoldCell x y = .two ↔ x = .two ∨ y = .two := by
  cases x <;> cases y <;> decide

theorem anchorFoldCell_binary_left (x y : Q)
    (xBinary : x = .zero ∨ x = .one)
    (yBinary : y = .zero ∨ y = .one) :
    anchorFoldCell x y = x := by
  rcases xBinary with rfl | rfl <;> rcases yBinary with rfl | rfl <;> rfl

def glue (anchor binary nonbinary : Q) : Q :=
  let selector := qUnary (qUnary anchor)
  qDisc (qDisc selector anchor binary)
    (qDisc selector anchor nonbinary) nonbinary

theorem glue_binary_zero (binary nonbinary : Q) :
    glue .zero binary nonbinary = binary := by
  cases binary <;> cases nonbinary <;> rfl

theorem glue_binary_one (binary nonbinary : Q) :
    glue .one binary nonbinary = binary := by
  cases binary <;> cases nonbinary <;> rfl

theorem glue_nonbinary (binary nonbinary : Q) :
    glue .two binary nonbinary = nonbinary := by
  cases binary <;> cases nonbinary <;> rfl

def twoPlaneDecode (high low : Q) : Q :=
  qDisc (qDisc high .one .two) .zero low

theorem twoPlaneDecode_zero : twoPlaneDecode .zero .zero = .zero := by rfl
theorem twoPlaneDecode_one : twoPlaneDecode .zero .one = .one := by rfl
theorem twoPlaneDecode_two : twoPlaneDecode .one .zero = .two := by rfl

theorem twoPlaneDecode_unused : twoPlaneDecode .one .one = .two := by rfl

end OrbitSynthesis.StrongSignedRouter.ManuscriptRepairs
