import Mathlib.Logic.Function.Basic

namespace OrbitSynthesis

universe u v w

variable {σ : Type u} {ι : Type v} {κ : Type w}

/-- The deterministic safety relation whose only legal output is `target s i`. -/
def graphSafe (target : σ → ι → σ) (s : σ) (i : ι) (out : σ) : Prop :=
  out = target s i

/-- A positional controller wins the full-domain graph game exactly when it is
pointwise equal to the target operation. -/
theorem wins_graphSafe_iff
    (target controller : σ → ι → σ) :
    (∀ s i, graphSafe target s i (controller s i)) ↔ controller = target := by
  constructor
  · intro h
    funext s i
    exact h s i
  · intro h s i
    simpa [graphSafe, h]

/-- Parameter-core feasibility of the graph game is exactly membership of the
target operation in the corresponding controller language. -/
theorem exists_allowed_graphSafe_controller_iff
    (Allowed : κ → (σ → ι → σ) → Prop)
    (core : κ) (target : σ → ι → σ) :
    (∃ controller, Allowed core controller ∧
      ∀ s i, graphSafe target s i (controller s i)) ↔
      Allowed core target := by
  constructor
  · rintro ⟨controller, hallowed, hwins⟩
    have hcontroller : controller = target :=
      (wins_graphSafe_iff target controller).mp hwins
    simpa [hcontroller] using hallowed
  · intro htarget
    exact ⟨target, htarget, (wins_graphSafe_iff target target).mpr rfl⟩

/-- The entire feasible-core predicate is preserved by the reduction, so all
least-core, minimal-core, and minimum-budget antichains transfer unchanged. -/
theorem graphSafe_feasibleCore_ext
    (Allowed : κ → (σ → ι → σ) → Prop)
    (target : σ → ι → σ) :
    (fun core => ∃ controller, Allowed core controller ∧
      ∀ s i, graphSafe target s i (controller s i)) =
      (fun core => Allowed core target) := by
  funext core
  exact propext (exists_allowed_graphSafe_controller_iff Allowed core target)

end OrbitSynthesis
