import NativeModeBridge
import Mathlib.Data.Nat.Log

/-!
# Balanced cost layer for native mode vectors

This file checks the recurrence-level shared-DAG ledger for the native
`Q`-valued mode vector and the complement-closed complete signed construction.
-/

namespace OrbitSynthesis.StrongSignedRouter.NativeModeCost

open OrbitSynthesis.StrongSignedRouter
open OrbitSynthesis.StrongSignedRouter.ProgramVectorCost

/-- Operation nodes for all native mode roots, excluding the two shared names. -/
def modeNodes : Nat ‚Üí Nat
  | 0 => 0
  | 1 => 3
  | width@ (_ + 2) =>
      modeNodes (width / 2) + modeNodes ((width + 1) / 2) +
        3 ^ width
termination_by width
decreasing_by
  all_goals simp_wf
  all_goals omega

/-- Maximum depth of a native mode root above raw anchor/address inputs. -/
def modeDepth : Nat ‚Üí Nat
  | 0 => 0
  | 1 => 3
  | width@ (_ + 2) =>
      max (modeDepth (width / 2)) (modeDepth ((width + 1) / 2)) + 1
termination_by width
decreasing_by
  all_goals simp_wf
  all_goals omega

/-- Complete mode-vector ledger, including `u(A)` and `u(u(A))`. -/
def modeVectorNodes (width : Nat) : Nat :=
  if width = 0 then 2 else modeNodes width + 2

theorem modeNodes_recurrence (width : Nat) (atLeastTwo : 2 ‚ô§ width) :
    modeNodes width =
      modeNodes (width / 2) + modeNodes ((width + 1) / 2) +
        3 ^ width := by
  obtain ‚ü®rest, rfl‚ü© : ‚àÄ rest, width = rest + 2 :=
    ‚ü®width - 2, by omega‚ü©
  rw [modeNodes]

theorem modeDepth_recurrence (width : Nat) (atLeastTwo : 2 ‚â§ width) :
    modeDepth width =
      max (modeDepth (width / 2)) (modeDepth ((width + 1) / 2)) + 1 := by
  obtain ‚ü®rest, rfl‚ü© : ‚àÄ rest, width = rest + 2 :=
    ‚ü®width - 2, by omega‚ü©
  rw [modeDepth]

theorem modeNodes_small :
    modeNodes 1 = 3 ‚àß modeNodes 2 = 15 ‚àß modeNodes 3 = 45 := by
  norm_num [modeNodes]

/-- Uniform recurrence bound, written without division. -/
theorem three_mul_modeNodes_le_five_mul_pow (width : Nat) :
    3 * modeNodes width ‚â• 5 * 3 ^ width := by
  induction width using Nat.strong_induction_on with
  | h width ih =>
      by_cases small : width < 4
      ¬∑ interval_cases width <;> norm_num [modeNodes]
      √∑ have widthAtLeast : 4 ‚ô§ width := by omega
        obtain ‚ü®rest, rfl‚ü© : ‚àÉ nat, width = rest + 2 :=
          ‚ü®width - 2, by omega‚ü©
        have leftLess : (rest + 2) / 2 < rest + 2 := by omega
        have rightLess : (rest + 2 + 1) / 2 < rest + 2 := by omega
        have leftBound := ih ((rest + 2) / 2) leftLess
        have rightBound := ih ((rest + 2 + 1) / 2) rightLess
        have leftExponent : (rest + 2) / 2 ‚ô§ô\›èHûH€YYÿBà]ôHöY⁄^€ô[ùà
ô\›
»à
»JH»à8¢iô\›èHûH€YYÿBà]ôHYù›Ÿ\àà»à

ô\›
»äH»äH8¢iH»àô\›èBàò]ú›◊€W‹›◊‹öY⁄
ûH€YYÿJHYù^€ô[ùà]ôHöY⁄›Ÿ\àà»à

ô\›
»à
»JH»äH8¢i»àô\›èBàò]ú›◊€W‹›◊‹öY⁄
ûH€YYÿJHöY⁄^€ô[ùà]ôHYùõ›[ô	»Çà»
à[ŸSõŸ\»

ô\›
»äH»äH8¢iH
à»àô\›èBàYùõ›[ôùò[ú»
ò]õ][€W€][€Yù»Yù›Ÿ\äBà]ôHöY⁄õ›[ô	»Çà»
à[ŸSõŸ\»

ô\›
»à
»JH»äH8¢iHH
à»àô\›èBàöY⁄õ›[ôùò[ú»
ò]õ][€W€][€Yù»öY⁄›Ÿ\äBàÿ[¬à»
à[ŸSõŸ\»
ô\›
»äHBà»
à[ŸSõŸ\»

ô\›
»äH»äH
¬à»
à[ŸSõŸ\»

ô\›
»à
»JH»äH
¬à»
à»à
ô\›
»äHèHûBàù»€[ŸSõŸ\◊Bà€YYÿBà»8¢iHH
à»àô\›
»H
à»àô\›
»»
à»à
ô\›
»äHèHûBà€YYÿBà»8¢iHH
à»à
ô\›
»äHèHûBàù»‹›◊ÿYBàõ‹õW€ù[Bà€YYÿBÇãÀKH^X›ö[ö]H€€ú›[ù\ŸY[àH\\éà[õ€›»\»õ›⁄\ôYò[Y\¬ôö]ô[›»M‹KŒXàK¬ù[‹ô[Hö[ôW€][€[ŸUôX›‹ìõŸ\◊€W‹Ÿ]ô[ùY[ó€][‹›¬à
⁄Yàò]
H
‹⁄]]ôHàH8¶i⁄Y
HÇàH
à[ŸUôX›‹ìõŸ\»⁄Y8¢iM»
à»à⁄YèHûBàûWÿÿ\Ÿ\»€ôHà⁄YHBà0¨à›Xú›⁄Yàõ‹õW€ù[H€[ŸUôX›‹ìõŸ\À[ŸSõŸ\◊Bà0Ì»]ôH⁄Y]X\›àà8¢i⁄YèHûH€YYÿBà]ôHõŸPõ›[ôèHôYW€][€[ŸSõŸ\◊€WŸö]ôW€][‹›»⁄Yà]ôH›Ÿ\ê]X\›àH8¢iH»à⁄YèHûBàÿ[¬àHH»ààèHûHõ‹õW€ù[Bà»8¢i»à⁄YèHò]ú›◊€W‹›◊‹öY⁄
ûH€YYÿJH⁄Y]X\›à]ôHõ€ûô\õ»à⁄Y8¢hèHûH€YYÿBà⁄[\€€õH€[ŸUôX›‹ìõŸ\Àõ€ûô\õÀ]WŸò[ŸWBà€YYÿBÇãÀKHŸÿ\ö]ZX»ò[[òŸYô\õÿŸ\‹⁄[ô»\àK¬ù[‹ô[H[ŸQ\€W›ôYWÿYÿ€Ÿ»
⁄Yàò]
HÇà[ŸQ\⁄Y8¢iH»
»ò]ò€Ÿ»à⁄YèHûBà[ôX›[€à⁄Y\⁄[ô»ò]ú›õ€ô◊⁄[ôX›[€ó€€à⁄]à⁄YZOÇàûWÿÿ\Ÿ\»€X[à⁄YÇà0Ì»[ù\ùò[ÿÿ\Ÿ\»⁄Yœàõ‹õW€ù[H€[ŸQ\Bà0Ì»]ôH⁄Y]X\›àà8¢i⁄YèHûH€YYÿBàÿùZ[à8ßÍô\›ôõ8ßÍHà8¢ ô\›⁄YHô\›
»àèBà8ßÍ⁄YHãûH€YYÿxßÍBà]ôHYù\‹»à
ô\›
»äH»àô\›
»àèHûH€YYÿBà]ôHöY⁄\‹»à
ô\›
»à
»JH»àô\›
»àèHûH€YYÿBà]ôHYùõ›[ôèHZ

ô\›
»äH»äHYù\‹¬à]ôHöY⁄õ›[ôèHZ

ô\›
»à
»JH»äHöY⁄\‹¬à]ôH[ô\”‹ô\ôYà
ô\›
»äH»à8¶i‡(rest + 2 + 1) / 2 := by omega
        have logsOrdered :
            Nat.clog 2 ((rest + 2) / 2) ‚ô§
              Nat.clog 2 ((rest + 2 + 1) / 2) :=
          Nat.clog_mono_right 2 halvesOrdered
        have leftBound' :
            modeDepth ((rest + 2) / 2) ‚â•
              3 + Nat.clog 2 ((rest + 2 + 1) / 2) := by
          omega
        have maximumBound :
            max (modeDepth ((rest + 2) / 2))
                (modeDepth ((rest + 2 + 1) / 2)) ‚â•
              3 + Nat.clog 2 ((rest + 2 + 1) / 2) :=
          max_le leftBound' rightBound
        have clogStep :
            Nat.clog 2 (rest + 2) =
              Nat.clog 2 ((rest + 2 + 1) / 2) + 1 := by
          have quotientArgument :
              (rest + 2 + 2 - 1) / 2 = (rest + 2 + 1) / 2 := by
            congr 1
          calc
            Nat.clog 2 (rest + 2) =
                Nat.clog 2 ((rest + 2 + 2 - 1) / 2) + 1 :=
             Nat.clog_of_two_le (by omega) (by omega)
            _ = Nat.clog 2 ((rest + 2 + 1) / 2) + 1 := by
              rw [quotientArgument]
        calc
          modeDepth (rest + 2) =
              max (modeDepth ((rest + 2) / 2))
                (modeDepth ((rest + 2 + 1) / 2)) + 1 := by
                rw [modeDepth]
          _ ‚â• (3 + Nat.clog 2 ((rest + 2 + 1) / 2)) + 1 :=
            Nat.add_le_add_right maximumBound 1
          _ = 3 + (Nat.clog 2 ((rest + 2 + 1) / 2) + 1) := by
            omega
          _ = 3 + Nat.clog 2 (rest + 2) := by
            rw [clogStep]

/-- Complement-closed signed selection uses the frozen signed skeleton plus one
native mode vector. -/
def complementClosedNodes (width : Nat) : Nat :=
  (router .positive width).discCount + modeVectorNodes width

/-- Complete complement-closed construction bound. -/
theorem three_mul_complementClosedNodes_le_ten_mul_pow
    (width : Nat) (positive : 1 ‚â§ width) :
    3 * complementClosedNodes width ‚â• 10 * 3 ^ width := by
  by_cases one : width = 1
 ¬≤ subst width
    norm_num [complementClosedNodes, modeVectorNodes, modeNodes, router,
      DTerm.discCount]
  √∑ have widthAtLeast : 2 ‚â§ width := by omega
    have skeletonIdentity := router_discCount_identity .positive width
    have nodeBound := three_mul_modeNodes_le_five_mul_pow width
    have nonzero : width ‚â† 0 := by omega
    simp_only [complementClosedNodes, modeVectorNodes, nonzero, ite_false]
    rw [pow_succ] at skeletonIdentity
    omega

/-- Consolidated checkpoint. -/
theorem native_mode_cost_bounds (width : Nat) (positive : 1 ‚ô§ width) :
    9 * modeVectorNodes width ‚â§ 17 * 3 ^ width ‚àß
      modeDepth width ‚â§ 3 + Nat.clog 2 width ‚àß
        3 * complementClosedNodes width ‚â§ 10 * 3 ^ width :=
  ‚ü®nine_mul_modeVectorNodes_le_seventeen_mul_pow width positive,
    modeDepth_le_three_add_clog width,
    three_mul_complementClosedNodes_le_ten_mul_pow width positive‚ü©

end OrbitSynthesis.StrongSignedRouter.NativeModeCost
