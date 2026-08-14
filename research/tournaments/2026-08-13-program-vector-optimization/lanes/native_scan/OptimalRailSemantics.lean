import Mathlib

/-!
# Exact absorbing rails and sibling sharing

This file formalizes the semantic core of the optimized program-vector
construction.  It stays deliberately independent of the asymptotic ledger:
the latter is audited by an exact integer recurrence in `check_optimal_scan.py`.
-/

namespace OrbitSynthesis.OptimalRail

inductive Q where
  | zero | one | two
  deriving DecidableEq, Repr

def disc (x y z : Q) : Q := if x = y then z else x

def unary : Q → Q
  | .zero => .one
  | .one => .zero
  | .two => .one

def bit : Bool → Q
  | false => .zero
  | true => .one

/-- Three first-mismatch modes: equality is the unique nonabsorbing state. -/
inductive Mode where
  | equal | zero | one
  deriving DecidableEq, Repr

def Mode.comp : Mode → Mode → Mode
  | .equal, right => right
  | left, _ => left

def zeroRail : Mode → Bool
  | .zero => true
  | _ => false

def oneRail : Mode → Bool
  | .one => true
  | _ => false

def notZeroRail : Mode → Bool
  | .zero => false
  | _ => true

theorem rail_disjoint (mode : Mode) :
    (zeroRail mode && oneRail mode) = false := by
  cases mode <;> rfl

/-- Both absorbing rails compose in one discriminator layer. -/
theorem zeroRail_comp (left right : Mode) :
    bit (zeroRail (left.comp right)) =
      disc (bit (zeroRail left)) (bit (oneRail left))
        (bit (zeroRail right)) := by
  cases left <;> cases right <;> rfl

theorem oneRail_comp (left right : Mode) :
    bit (oneRail (left.comp right)) =
      disc (bit (oneRail left)) (bit (zeroRail left))
        (bit (oneRail right)) := by
  cases left <;> cases right <;> rfl

theorem notZeroRail_comp (left right : Mode) :
    bit (notZeroRail (left.comp right)) =
      disc (bit (oneRail left)) (bit (zeroRail left))
        (bit (notZeroRail right)) := by
  cases left <;> cases right <;> rfl

/-- A right segment incapable of producing mode one contributes no new one
rail: the composed rail is literally the left rail. -/
theorem oneRail_comp_right_zero (left right : Mode)
    (rightZero : oneRail right = false) :
    oneRail (left.comp right) = oneRail left := by
  cases left <;> cases right <;> simp_all [Mode.comp, oneRail]

inductive Digit where
  | left | middle | right
  deriving DecidableEq, Repr

def digitMode : Digit → Digit → Mode
  | target, physical =>
      if target = physical then .equal
      else if target = .middle ∧ physical = .right then .one
      else .zero

def prependMode (target physical : Digit) (suffix : Mode) : Mode :=
  (digitMode target physical).comp suffix

/-- Load-bearing sibling identity: for every earlier segment summary, the
not-zero control at physical middle is the one-mode control at physical right.
This is exactly `N_(a1)=O_(a2)` after the common prefix `a` is composed. -/
theorem sibling_notZero_eq_one (prior : Mode) (target : Digit) :
    notZeroRail (prior.comp (digitMode target .middle)) =
      oneRail (prior.comp (digitMode target .right)) := by
  cases prior <;> cases target <;> rfl

def qDigit : Digit → Q
  | .left => .zero
  | .middle => .one
  | .right => .two

def baseZero0 (target : Digit) : Q := disc (qDigit target) .two .one
def baseZero1 (target : Digit) : Q := disc .one (qDigit target) .zero
def baseZero2 (target : Digit) : Q := disc .zero (qDigit target) .one
def baseOne2 (target : Digit) : Q := disc (qDigit target) .two .zero

/-- The four one-digit original-signature terms realize all six rails. -/
theorem one_digit_rails (target physical : Digit) :
    let z := match physical with
      | .left => baseZero0 target
      | .middle => baseZero1 target
      | .right => baseZero2 target
    let o := match physical with
      | .left => .zero
      | .middle => .zero
      | .right => baseOne2 target
    z = bit (zeroRail (digitMode target physical)) ∧
      o = bit (oneRail (digitMode target physical)) := by
  cases target <;> cases physical <;> decide

def firstControl (negative : Bool) (mode : Mode) : Bool :=
  if negative then oneRail mode else zeroRail mode

def secondControl (negative : Bool) (mode : Mode) : Bool :=
  if negative then notZeroRail mode else oneRail mode

/-- Final controls require no decoding on positive cells and only Boolean
complementation of the zero rail on negative cells. -/
theorem final_controls (negative : Bool) (mode : Mode) :
    (bit (firstControl negative mode), bit (secondControl negative mode)) =
      if negative then
        (bit (oneRail mode), unary (bit (zeroRail mode)))
      else
        (bit (zeroRail mode), bit (oneRail mode)) := by
  cases negative <;> cases mode <;> rfl

/-- Swapping the absorbing guards is not harmless. -/
theorem reversed_guard_counterexample :
    disc (bit (oneRail Mode.zero)) (bit (zeroRail Mode.zero))
        (bit (zeroRail Mode.one)) ≠
      bit (zeroRail (Mode.zero.comp Mode.one)) := by
  decide

end OrbitSynthesis.OptimalRail
