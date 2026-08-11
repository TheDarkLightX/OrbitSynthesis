import Mathlib.Data.Set.Image

open Set

namespace OrbitSynthesis

universe u v

variable {α : Type u} {β : Type v}

/--
The right-adjoint image of a set along a function: a target point belongs
exactly when every point in its fiber belongs to the source set.
-/
def forallImage (f : α → β) (A : Set α) : Set β :=
  { b | ∀ a, f a = b → a ∈ A }

/-- Direct image is left adjoint to inverse image on powersets. -/
theorem image_subset_iff_preimage_subset
    (f : α → β) (A : Set α) (B : Set β) :
    f '' A ⊆ B ↔ A ⊆ f ⁻¹' B := by
  constructor
  · intro h a ha
    exact h ⟨a, ha, rfl⟩
  · intro h b hb
    rcases hb with ⟨a, ha, rfl⟩
    exact h ha

/-- Inverse image is left adjoint to the all-fibers-contained image. -/
theorem preimage_subset_iff_subset_forallImage
    (f : α → β) (A : Set α) (B : Set β) :
    f ⁻¹' B ⊆ A ↔ B ⊆ forallImage f A := by
  constructor
  · intro h b hb
    change ∀ a, f a = b → a ∈ A
    intro a hfa
    apply h
    change f a ∈ B
    simpa [hfa] using hb
  · intro h a ha
    have hfa : f a ∈ forallImage f A := h ha
    exact hfa a rfl

/--
The right-adjoint image is complement of the direct image of the complement.
No surjectivity assumption is needed: points outside the range satisfy the
fiber condition vacuously.
-/
theorem forallImage_eq_compl_image_compl
    (f : α → β) (A : Set α) :
    forallImage f A = (f '' Aᶜ)ᶜ := by
  ext b
  constructor
  · intro hb
    change b ∉ f '' Aᶜ
    rintro ⟨a, ha, hfa⟩
    change ∀ x, f x = b → x ∈ A at hb
    exact ha (hb a hfa)
  · intro hb
    change ∀ a, f a = b → a ∈ A
    intro a hfa
    by_contra ha
    apply hb
    exact ⟨a, ha, hfa⟩

/-- The two adjunction laws packaged together. -/
theorem powerset_quantifier_adjoint_triple
    (f : α → β) (A : Set α) (B : Set β) :
    (f '' A ⊆ B ↔ A ⊆ f ⁻¹' B) ∧
      (f ⁻¹' B ⊆ A ↔ B ⊆ forallImage f A) := by
  exact ⟨image_subset_iff_preimage_subset f A B,
    preimage_subset_iff_subset_forallImage f A B⟩

end OrbitSynthesis
