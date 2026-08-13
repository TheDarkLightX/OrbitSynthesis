import Mathlib.Data.Set.Lattice

open Set

namespace OrbitSynthesis

universe u v

/--
A task-relative closure operator, stated explicitly so the formal theorem does
not depend on implementation details of universal-algebra term evaluation.
-/
structure SemanticClosure (α : Type u) where
  cl : Set α → Set α
  extensive : ∀ S, S ⊆ cl S
  monotone : Monotone cl
  idempotent : ∀ S, cl (cl S) = cl S

namespace SemanticClosure

variable {α : Type u} {β : Type v}

/-- A set is closed when applying the abstraction changes nothing. -/
def Closed (K : SemanticClosure α) (S : Set α) : Prop := K.cl S = S

/-- Every abstract state produced by the closure operator is closed. -/
theorem closed_cl (K : SemanticClosure α) (S : Set α) :
    K.Closed (K.cl S) := by
  exact K.idempotent S

/-- Adding two raw parameter sets descends to join of their closures. -/
theorem cl_union_cl_eq_cl_union
    (K : SemanticClosure α) (S T : Set α) :
    K.cl (K.cl S ∪ K.cl T) = K.cl (S ∪ T) := by
  apply Set.Subset.antisymm
  · have hUnion : K.cl S ∪ K.cl T ⊆ K.cl (S ∪ T) := by
      intro x hx
      rcases hx with hxS | hxT
      · exact K.monotone Set.subset_union_left hxS
      · exact K.monotone Set.subset_union_right hxT
    calc
      K.cl (K.cl S ∪ K.cl T) ⊆ K.cl (K.cl (S ∪ T)) :=
        K.monotone hUnion
      _ = K.cl (S ∪ T) := K.idempotent (S ∪ T)
  · apply K.monotone
    intro x hx
    rcases hx with hxS | hxT
    · exact Or.inl (K.extensive S hxS)
    · exact Or.inr (K.extensive T hxT)

/--
For a closed obstruction `F`, a raw set is below `F` exactly when its closure
is below `F`.  This is the formal operation-descent fact used by parameter
patchability.
-/
theorem subset_closed_iff_closure_subset
    (K : SemanticClosure α) {S F : Set α} (hF : K.Closed F) :
    S ⊆ F ↔ K.cl S ⊆ F := by
  constructor
  · intro hSF
    have h := K.monotone hSF
    simpa [Closed, hF] using h
  · intro hKS x hx
    exact hKS (K.extensive S hx)

/-- The obstruction-avoidance form of `subset_closed_iff_closure_subset`. -/
theorem not_subset_closed_iff_not_closure_subset
    (K : SemanticClosure α) {S F : Set α} (hF : K.Closed F) :
    (¬ S ⊆ F) ↔ ¬ K.cl S ⊆ F := by
  exact not_congr (K.subset_closed_iff_closure_subset hF)

/-- Hitting the complement of `F` is equivalent to not lying below `F`. -/
theorem inter_compl_nonempty_iff_not_subset (S F : Set α) :
    (S ∩ Fᶜ).Nonempty ↔ ¬ S ⊆ F := by
  constructor
  · rintro ⟨x, hxS, hxF⟩ hSF
    exact hxF (hSF hxS)
  · intro h
    by_contra hnone
    apply h
    intro x hxS
    by_contra hxF
    apply hnone
    exact ⟨x, hxS, show x ∈ Fᶜ from hxF⟩

/--
A whole family of closed obstructions can be tested on raw parameter sets or
on their abstract closures with exactly the same answer.
-/
theorem avoids_closed_family_iff_closure_avoids
    (K : SemanticClosure α) (S : Set α) (𝓕 : Set (Set α))
    (hclosed : ∀ F ∈ 𝓕, K.Closed F) :
    (∀ F ∈ 𝓕, ¬ S ⊆ F) ↔
      ∀ F ∈ 𝓕, ¬ K.cl S ⊆ F := by
  constructor
  · intro h F hF
    exact (K.not_subset_closed_iff_not_closure_subset (hclosed F hF)).mp
      (h F hF)
  · intro h F hF
    exact (K.not_subset_closed_iff_not_closure_subset (hclosed F hF)).mpr
      (h F hF)

/--
The complement-hypergraph and closed-fixed-core formulations are equivalent.
This is the formal core of the OrbitSynthesis patchability quotient.
-/
theorem hits_complements_iff_closure_avoids
    (K : SemanticClosure α) (S : Set α) (𝓕 : Set (Set α))
    (hclosed : ∀ F ∈ 𝓕, K.Closed F) :
    (∀ F ∈ 𝓕, (S ∩ Fᶜ).Nonempty) ↔
      ∀ F ∈ 𝓕, ¬ K.cl S ⊆ F := by
  constructor
  · intro h F hF
    have hraw : ¬ S ⊆ F :=
      (inter_compl_nonempty_iff_not_subset S F).mp (h F hF)
    exact (K.not_subset_closed_iff_not_closure_subset (hclosed F hF)).mp hraw
  · intro h F hF
    have hraw : ¬ S ⊆ F :=
      (K.not_subset_closed_iff_not_closure_subset (hclosed F hF)).mpr
        (h F hF)
    exact (inter_compl_nonempty_iff_not_subset S F).mpr hraw

/--
A generic Morph-style full-abstraction theorem.  If all queries factor through
`cl`, and distinct closed states are separated by the query interface, then
query equality is exactly closure equality.
-/
theorem query_full_abstraction
    (K : SemanticClosure α) (query : Set α → β)
    (hfactor : ∀ S, query S = query (K.cl S))
    (hseparate : ∀ {A B}, K.Closed A → K.Closed B → query A = query B → A = B)
    (S T : Set α) :
    query S = query T ↔ K.cl S = K.cl T := by
  constructor
  · intro h
    apply hseparate (K.closed_cl S) (K.closed_cl T)
    calc
      query (K.cl S) = query S := (hfactor S).sym
      _ = query T := h
      _ = query (K.cl T) := hfactor T
  · intro h
    calc
      query S = query (K.cl S) := hfactor S
      _ = query (K.cl T) := congrArg query h
      _ = query T := (hfactor T).sym

end SemanticClosure

end OrbitSynthesis
