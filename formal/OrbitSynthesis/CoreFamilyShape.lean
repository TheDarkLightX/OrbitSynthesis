import Mathlib.Data.Set.Lattice
import OrbitSynthesis.CoreIntersection

open Set

namespace OrbitSynthesis

universe u v

variable {α : Type u} {β : Type v}

/-- Distinct members of the family jointly cover the carrier. -/
def PairwiseCoverFamily (family : Set (Set α)) : Prop :=
  ∀ left ∈ family, ∀ right ∈ family, left ≠ right →
    left ∪ right = Set.univ

/-- Carrier complements of distinct members are disjoint. -/
def ComplementBlocksPairwiseDisjoint (family : Set (Set α)) : Prop :=
  ∀ left ∈ family, ∀ right ∈ family, left ≠ right →
    leftᶜ ∩ rightᶜ = (∅ : Set α)

/-- Pairwise cover is exactly disjointness of the complement blocks. -/
theorem pairwiseCover_iff_complementBlocksDisjoint
    (family : Set (Set α)) :
    PairwiseCoverFamily family ↔
      ComplementBlocksPairwiseDisjoint family := by
  constructor
  · intro hcover left hleft right hright hne
    have hunion : left ∪ right = Set.univ :=
      hcover left hleft right hright hne
    have hcomplement := congrArg (fun S : Set α => Sᶜ) hunion
    simpa using hcomplement
  · intro hdisjoint left hleft right hright hne
    have hinter : leftᶜ ∩ rightᶜ = (∅ : Set α) :=
      hdisjoint left hleft right hright hne
    have hcomplement := congrArg (fun S : Set α => Sᶜ) hinter
    simpa only [Set.compl_inter, compl_compl, Set.compl_empty] using hcomplement

/-- The abstract meet-collapse theorem gives the partial-partition shape. -/
theorem minimalCore_family_complementBlocksDisjoint
    (Allowed : Set α → β → Prop) (target : β)
    (hcollapse : MeetCollapseAwayFromCovers Allowed target)
    (family : Set (Set α))
    (hminimal : ∀ core ∈ family, MinimalCore Allowed target core) :
    ComplementBlocksPairwiseDisjoint family := by
  intro left hleft right hright hne
  exact minimalCore_compl_inter_eq_empty Allowed target hcollapse
    (hminimal left hleft) (hminimal right hright) hne

end OrbitSynthesis
