import OrbitSynthesis.CoreAntichain

open Set

namespace OrbitSynthesis

universe u v
variable {α : Type u} {β : Type v}

/-- Explicit abstract premise: joint feasibility descends to the intersection
when the two cores do not jointly cover the carrier. This declaration does not
establish the premise for any particular algebra or implementation. -/
def MeetCollapseAwayFromCovers
    (Allowed : Set α → β → Prop) (target : β) : Prop :=
  ∀ {left right : Set α}, left ∪ right ≠ Set.univ →
    Allowed left target → Allowed right target → Allowed (left ∩ right) target

/-- Under meet collapse, two distinct minimal cores must cover the carrier. -/
theorem minimalCore_union_eq_univ
    (Allowed : Set α → β → Prop) (target : β)
    (hcollapse : MeetCollapseAwayFromCovers Allowed target)
    {left right : Set α}
    (hleft : MinimalCore Allowed target left)
    (hright : MinimalCore Allowed target right)
    (hne : left ≠ right) :
    left ∪ right = Set.univ := by
  by_contra hnot
  have hmeet := hcollapse hnot hleft.1 hright.1
  have hl := hleft.2 (left ∩ right) hmeet Set.inter_subset_left
  have hr := hright.2 (left ∩ right) hmeet Set.inter_subset_right
  apply hne
  exact Set.Subset.antisymm (fun _ hx => (hl hx).2) (fun _ hx => (hr hx).1)

/-- Equivalent disjointness statement used by the existing family-shape leaf. -/
theorem minimalCore_compl_inter_eq_empty
    (Allowed : Set α → β → Prop) (target : β)
    (hcollapse : MeetCollapseAwayFromCovers Allowed target)
    {left right : Set α}
    (hleft : MinimalCore Allowed target left)
    (hright : MinimalCore Allowed target right)
    (hne : left ≠ right) :
    leftᶜ ∩ rightᶜ = (∅ : Set α) := by
  have h := congrArg (fun S : Set α => Sᶜ)
    (minimalCore_union_eq_univ Allowed target hcollapse hleft hright hne)
  simpa only [Set.compl_union, Set.compl_univ] using h

end OrbitSynthesis
