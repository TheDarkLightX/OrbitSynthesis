import Mathlib.Data.Set.Basic

open Set

namespace OrbitSynthesis

universe u

variable {α : Type u}

/--
An upward predicate on a restriction fiber needs only the fiber's greatest
extension.  The theorem is deliberately representation-agnostic: ABA later
instantiates `≤` with support inclusion and `topE` with the maximal allowed
refinement support.
-/
theorem exists_iff_greatest_witness
    [Preorder α]
    (E : Set α)
    (Good : α → Prop)
    (topE : α)
    (htop_mem : topE ∈ E)
    (htop : ∀ e ∈ E, e ≤ topE)
    (hup : ∀ ⦃a b : α⦄, a ∈ E → b ∈ E → a ≤ b → Good a → Good b) :
    (∃ e ∈ E, Good e) ↔ Good topE := by
  constructor
  · rintro ⟨e, he, hgood⟩
    exact hup he htop_mem (htop e he) hgood
  · intro hgood
    exact ⟨topE, htop_mem, hgood⟩

/--
If every environment extension lies above one member of a chosen minimal/test
family, an upward goodness predicate needs to be checked only on that family.
Finiteness is not required once the cofinal-from-below property is supplied.
-/
theorem forall_iff_minimal_tests
    [Preorder α]
    (D M : Set α)
    (Good : α → Prop)
    (hM : M ⊆ D)
    (hcover : ∀ d ∈ D, ∃ m ∈ M, m ≤ d)
    (hup : ∀ ⦃a b : α⦄, a ∈ D → b ∈ D → a ≤ b → Good a → Good b) :
    (∀ d ∈ D, Good d) ↔ ∀ m ∈ M, Good m := by
  constructor
  · intro hall m hm
    exact hall m (hM hm)
  · intro hmin d hd
    rcases hcover d hd with ⟨m, hm, hmd⟩
    exact hup (hM hm) hd hmd (hmin m hm)

/--
The two extremal reductions compose: first replace system existential search by
its greatest response, then reduce universal environment checking to a
cofinal-from-below test family.
-/
theorem extremal_quantifier_collapse
    [Preorder α]
    (D M : Set α)
    (Good : α → Prop)
    (hM : M ⊆ D)
    (hcover : ∀ d ∈ D, ∃ m ∈ M, m ≤ d)
    (hup : ∀ ⦃a b : α⦄, a ∈ D → b ∈ D → a ≤ b → Good a → Good b) :
    (∀ d ∈ D, Good d) ↔ ∀ m ∈ M, Good m :=
  forall_iff_minimal_tests D M Good hM hcover hup

end OrbitSynthesis
