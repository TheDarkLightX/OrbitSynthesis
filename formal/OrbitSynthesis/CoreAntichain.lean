import Mathlib.Data.Set.Lattice

open Set

namespace OrbitSynthesis

universe u v

variable {α : Type u} {β : Type v}

/-- Inclusion-minimality of one feasible parameter core for one target. -/
def MinimalCore
    (Allowed : Set α → β → Prop) (target : β) (core : Set α) : Prop :=
  Allowed core target ∧
    ∀ other, Allowed other target → other ⊆ core → core ⊆ other

/-- Inclusion-minimal feasible cores are pairwise incomparable. -/
theorem minimalCore_eq_of_subset
    (Allowed : Set α → β → Prop) (target : β)
    {left right : Set α}
    (hleft : MinimalCore Allowed target left)
    (hright : MinimalCore Allowed target right)
    (hsubset : left ⊆ right) :
    left = right := by
  apply Set.Subset.antisymm hsubset
  exact hright.2 left hleft.1 hsubset

/-- A pair-collapse law forbids two distinct singleton cores from both being
minimal: their joint feasibility would make the empty core feasible. -/
theorem no_two_singleton_minimal
    (Allowed : Set α → β → Prop) (target : β)
    {a b : α} (hne : a ≠ b)
    (pairCollapse :
      a ≠ b → Allowed {a} target → Allowed {b} target → Allowed ∅ target)
    (ha : MinimalCore Allowed target {a})
    (hb : MinimalCore Allowed target {b}) :
    False := by
  have hempty : Allowed ∅ target := pairCollapse hne ha.1 hb.1
  have hback : ({a} : Set α) ⊆ ∅ :=
    ha.2 ∅ hempty (Set.empty_subset {a})
  have haempty : a ∈ (∅ : Set α) := hback (Set.mem_singleton a)
  simpa using haempty

/-- Equivalently, under pair collapse a minimal-core family contains at most one
singleton core. -/
theorem singleton_minimal_unique
    (Allowed : Set α → β → Prop) (target : β)
    (pairCollapse :
      ∀ {a b : α}, a ≠ b →
        Allowed {a} target → Allowed {b} target → Allowed ∅ target)
    {a b : α}
    (ha : MinimalCore Allowed target {a})
    (hb : MinimalCore Allowed target {b}) :
    a = b := by
  by_contra hne
  exact no_two_singleton_minimal Allowed target hne
    (pairCollapse hne) ha hb

end OrbitSynthesis
