import Mathlib.Data.Set.Function

open Set

namespace OrbitSynthesis

universe u v w

/--
An abstract pointed-class product.  `classOf` selects the independent seed
coordinate used at an observation, while `transport` reconstructs the table
value at that observation.  The representative laws make seed recovery exact.
-/
structure PointedProduct (ι : Type u) (Obs : Type v) (α : Type w) where
  classOf : Obs → ι
  representative : ι → Obs
  representative_class : ∀ i, classOf (representative i) = i
  admissible : ι → Set α
  transport : Obs → α → α
  transport_representative : ∀ i a, transport (representative i) a = a

namespace PointedProduct

variable {ι : Type u} {Obs : Type v} {α : Type w}

/-- One admissible seed in every pointed class. -/
def SeedAssignment (P : PointedProduct ι Obs α) :=
  ∀ i, {a : α // a ∈ P.admissible i}

/-- Decode a seed assignment to its complete observation table. -/
def decode (P : PointedProduct ι Obs α)
    (a : P.SeedAssignment) : Obs → α :=
  fun z => P.transport z (a (P.classOf z)).1

/-- Representative evaluation recovers every seed coordinate. -/
theorem decode_at_representative
    (P : PointedProduct ι Obs α) (a : P.SeedAssignment) (i : ι) :
    P.decode a (P.representative i) = (a i).1 := by
  change P.transport (P.representative i) (a (P.classOf (P.representative i))).1 = _
  rw [P.transport_representative]
  exact congrArg (fun j => (a j).1) (P.representative_class i)

/-- No two distinct seed assignments decode to the same table. -/
theorem decode_injective (P : PointedProduct ι Obs α) :
    Function.Injective P.decode := by
  intro a b hab
  funext i
  apply Subtype.ext
  have hrep := congrFun hab (P.representative i)
  calc
    (a i).1 = P.decode a (P.representative i) :=
      (P.decode_at_representative a i).symm
    _ = P.decode b (P.representative i) := hrep
    _ = (b i).1 := P.decode_at_representative b i

/-- The tables represented by the pointed product. -/
def CoherentTable (P : PointedProduct ι Obs α) :=
  {t : Obs → α // t ∈ Set.range P.decode}

/-- The seed product is exactly equivalent to the coherent table space. -/
noncomputable def seedEquivCoherent (P : PointedProduct ι Obs α) :
    P.SeedAssignment ≃ P.CoherentTable where
  toFun a := ⟨P.decode a, ⟨a, rfl⟩⟩
  invFun t := Classical.choose t.2
  left_inv a := by
    apply P.decode_injective
    have h := Classical.choose_spec
      (show P.decode a ∈ Set.range P.decode from ⟨a, rfl⟩)
    exact h
  right_inv t := by
    apply Subtype.ext
    exact Classical.choose_spec t.2

/-- A seed meets every allowed list in its pointed class. -/
def SeedFeasible (P : PointedProduct ι Obs α)
    (allowed : Obs → Set α) (i : ι)
    (seed : {a : α // a ∈ P.admissible i}) : Prop :=
  ∀ z, P.classOf z = i → P.transport z seed.1 ∈ allowed z

/--
Global list interpolation factorizes into one independent seed-existence test
per pointed class.
-/
theorem exists_decoded_table_iff_classwise
    (P : PointedProduct ι Obs α) (allowed : Obs → Set α) :
    (∃ a : P.SeedAssignment, ∀ z, P.decode a z ∈ allowed z) ↔
      ∀ i, ∃ seed : {a : α // a ∈ P.admissible i},
        P.SeedFeasible allowed i seed := by
  constructor
  · rintro ⟨a, ha⟩ i
    refine ⟨a i, ?_⟩
    intro z hz
    have hvalue := congrArg (fun j => (a j).1) hz
    change P.transport z (a i).1 ∈ allowed z
    rw [← hvalue]
    exact ha z
  · intro h
    classical
    let a : P.SeedAssignment := fun i => Classical.choose (h i)
    refine ⟨a, ?_⟩
    intro z
    have hz := Classical.choose_spec (h (P.classOf z)) z rfl
    simpa [decode, a] using hz

end PointedProduct

end OrbitSynthesis
