import Mathlib.Data.Set.Lattice

open Set

namespace OrbitSynthesis

universe u v

/-- One pointed-class seed compiled to state-domain obligations. -/
structure DomainSeedRule (σ : Type u) where
  unsafe : Set σ
  requires : σ → Set σ

namespace DomainSeedRule

variable {σ : Type u} {ι : Type v}

/-- A complete state domain satisfies one seed rule. -/
def Valid (rule : DomainSeedRule σ) (W : Set σ) : Prop :=
  (∀ p ∈ W, p ∉ rule.unsafe) ∧
    ∀ p ∈ W, rule.requires p ⊆ W

/-- A seed has not yet been killed by a partial include/exclude assignment. -/
def PartialViable (rule : DomainSeedRule σ) (included excluded : Set σ) : Prop :=
  (∀ p ∈ included, p ∉ rule.unsafe) ∧
    ∀ p ∈ included, ∀ q ∈ excluded, q ∉ rule.requires p

/-- The positive and negative literals defining one learned conflict cone. -/
structure Nogood (σ : Type u) where
  include : Set σ
  exclude : Set σ

namespace Nogood

/-- A complete domain lies in the cone rejected by a nogood. -/
def Covers (N : Nogood σ) (W : Set σ) : Prop :=
  N.include ⊆ W ∧ ∀ q ∈ N.exclude, q ∉ W

/-- The nogood contains a concrete reason killing this seed rule. -/
def Kills (N : Nogood σ) (rule : DomainSeedRule σ) : Prop :=
  (∃ p ∈ N.include, p ∈ rule.unsafe) ∨
    ∃ p ∈ N.include, ∃ q ∈ N.exclude, q ∈ rule.requires p

end Nogood

/-- Every complete extension of a valid seed is partially viable. -/
theorem partialViable_of_valid_of_covers
    (rule : DomainSeedRule σ) {included excluded W : Set σ}
    (hvalid : rule.Valid W)
    (hincluded : included ⊆ W)
    (hexcluded : ∀ q ∈ excluded, q ∉ W) :
    rule.PartialViable included excluded := by
  constructor
  · intro p hp
    exact hvalid.1 p (hincluded hp)
  · intro p hp q hq hreq
    exact hexcluded q hq (hvalid.2 p (hincluded hp) hreq)

/-- A killed seed cannot satisfy any complete domain covered by the nogood. -/
theorem not_valid_of_killed_of_covers
    (rule : DomainSeedRule σ) (N : Nogood σ) (W : Set σ)
    (hkilled : N.Kills rule) (hcovers : N.Covers W) :
    ¬ rule.Valid W := by
  intro hvalid
  rcases hkilled with hunsafe | hmissing
  · rcases hunsafe with ⟨p, hpN, hpUnsafe⟩
    exact hvalid.1 p (hcovers.1 hpN) hpUnsafe
  · rcases hmissing with ⟨p, hpN, q, hqN, hqReq⟩
    exact hcovers.2 q hqN (hvalid.2 p (hcovers.1 hpN) hqReq)

/--
If one nogood kills every seed of a pointed class, every covered domain makes
that class infeasible.
-/
theorem nogood_sound
    (rules : ι → DomainSeedRule σ) (N : Nogood σ)
    (hkills : ∀ i, N.Kills (rules i)) :
    ∀ W, N.Covers W → ¬ ∃ i, (rules i).Valid W := by
  intro W hcover hfeasible
  rcases hfeasible with ⟨i, hi⟩
  exact not_valid_of_killed_of_covers (rules i) N W (hkills i) hcover hi

/--
If no seed remains partially viable after including `p`, every feasible
completion of the current assignment must exclude `p`.
-/
theorem forced_exclude_of_no_partial_seed
    (rules : ι → DomainSeedRule σ)
    (included excluded : Set σ) (p : σ)
    (hno : ∀ i, ¬ (rules i).PartialViable (insert p included) excluded)
    {W : Set σ}
    (hincluded : included ⊆ W)
    (hexcluded : ∀ q ∈ excluded, q ∉ W)
    (hfeasible : ∃ i, (rules i).Valid W) :
    p ∉ W := by
  intro hpW
  rcases hfeasible with ⟨i, hi⟩
  apply hno i
  apply partialViable_of_valid_of_covers (rules i) hi
  · intro x hx
    rcases hx with rfl | hx
    · exact hpW
    · exact hincluded hx
  · exact hexcluded

/--
If every partially viable seed requires `q` from an already included source,
then every feasible completion must include `q`.
-/
theorem forced_include_of_common_requirement
    (rules : ι → DomainSeedRule σ)
    (included excluded : Set σ) (q : σ)
    (hrequires : ∀ i, (rules i).PartialViable included excluded →
      ∃ p ∈ included, q ∈ (rules i).requires p)
    {W : Set σ}
    (hincluded : included ⊆ W)
    (hexcluded : ∀ x ∈ excluded, x ∉ W)
    (hfeasible : ∃ i, (rules i).Valid W) :
    q ∈ W := by
  rcases hfeasible with ⟨i, hi⟩
  have hpartial : (rules i).PartialViable included excluded :=
    partialViable_of_valid_of_covers (rules i) hi hincluded hexcluded
  rcases hrequires i hpartial with ⟨p, hp, hq⟩
  exact hi.2 p (hincluded hp) hq

end DomainSeedRule

end OrbitSynthesis
