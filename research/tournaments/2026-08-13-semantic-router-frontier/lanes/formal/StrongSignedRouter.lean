import Mathlib.Data.Fintype.Card
import Mathlib.Tactic

/-!
# Strong signed discriminator routers

This file formalizes the Boolean induction underlying the frozen strong-router
family.  `DTerm` is the original-signature grammar used here: it has branch
leaves, address-control leaves, and the ternary discriminator only.  In
particular it has no Boolean constant constructor and no unary/NOT constructor.

Programs are external assignments to the control leaves.  Their type contains
the route target but no branch valuation, making the address-only boundary
explicit.
-/

namespace OrbitSynthesis.StrongSignedRouter

/-- Boolean restriction of the discriminator: if `x=y`, return `z`; otherwise
return `x`. -/
def disc (x y z : Bool) : Bool :=
  if x = y then z else x

@[simp] theorem disc_same (x : Bool) : disc x x x = x := by
  simp [disc]

@[simp] theorem disc_pos_project_left (x : Bool) : disc x false false = x := by
  cases x <;> rfl

@[simp] theorem disc_project_right (x : Bool) : disc false false x = x := by
  rfl

@[simp] theorem disc_pos_zero (x : Bool) : disc x true false = false := by
  cases x <;> rfl

@[simp] theorem disc_pos_one (x : Bool) : disc x false true = true := by
  cases x <;> rfl

@[simp] theorem disc_neg_project (x : Bool) : disc false x true = !x := by
  cases x <;> rfl

@[simp] theorem disc_neg_zero (x : Bool) : disc false x false = false := by
  cases x <;> rfl

@[simp] theorem disc_neg_one (x : Bool) : disc true x true = true := by
  cases x <;> rfl

@[simp] theorem disc_complement (x y z : Bool) :
    disc (!x) (!y) (!z) = !(disc x y z) := by
  cases x <;> cases y <;> cases z <;> rfl

/-- Original-signature discriminator terms.  There is intentionally no `not`
or constant constructor. -/
inductive DTerm (Branch Control : Type) where
  | branch : Branch → DTerm Branch Control
  | control : Control → DTerm Branch Control
  | disc : DTerm Branch Control → DTerm Branch Control → DTerm Branch Control →
      DTerm Branch Control

namespace DTerm

def eval {Branch Control : Type} (branches : Branch → Bool)
    (controls : Control → Bool) : DTerm Branch Control → Bool
  | .branch branchId => branches branchId
  | .control controlId => controls controlId
  | .disc left middle right =>
      StrongSignedRouter.disc
        (eval branches controls left)
        (eval branches controls middle)
        (eval branches controls right)

def rename {Branch Control Branch' Control' : Type}
    (branchMap : Branch → Branch') (controlMap : Control → Control') :
    DTerm Branch Control → DTerm Branch' Control'
  | .branch branchId => .branch (branchMap branchId)
  | .control controlId => .control (controlMap controlId)
  | .disc left middle right =>
      .disc (rename branchMap controlMap left)
        (rename branchMap controlMap middle)
        (rename branchMap controlMap right)

@[simp] theorem eval_rename {Branch Control Branch' Control' : Type}
    (branchMap : Branch → Branch') (controlMap : Control → Control')
    (term : DTerm Branch Control) (branches : Branch' → Bool)
    (controls : Control' → Bool) :
    eval branches controls (rename branchMap controlMap term) =
      eval (fun branch => branches (branchMap branch))
        (fun control => controls (controlMap control)) term := by
  induction term <;> simp [rename, eval, *]

def branchCount {Branch Control : Type} : DTerm Branch Control → Nat
  | .branch _ => 1
  | .control _ => 0
  | .disc left middle right =>
      branchCount left + branchCount middle + branchCount right

def controlCount {Branch Control : Type} : DTerm Branch Control → Nat
  | .branch _ => 0
  | .control _ => 1
  | .disc left middle right =>
      controlCount left + controlCount middle + controlCount right

def discCount {Branch Control : Type} : DTerm Branch Control → Nat
  | .branch _ => 0
  | .control _ => 0
  | .disc left middle right =>
      1 + discCount left + discCount middle + discCount right

def depth {Branch Control : Type} : DTerm Branch Control → Nat
  | .branch _ => 0
  | .control _ => 0
  | .disc left middle right =>
      1 + max (depth left) (max (depth middle) (depth right))

@[simp] theorem branchCount_rename {Branch Control Branch' Control' : Type}
    (branchMap : Branch → Branch') (controlMap : Control → Control')
    (term : DTerm Branch Control) :
    branchCount (rename branchMap controlMap term) = branchCount term := by
  induction term <;> simp [rename, branchCount, *]

@[simp] theorem controlCount_rename {Branch Control Branch' Control' : Type}
    (branchMap : Branch → Branch') (controlMap : Control → Control')
    (term : DTerm Branch Control) :
    controlCount (rename branchMap controlMap term) = controlCount term := by
  induction term <;> simp [rename, controlCount, *]

@[simp] theorem discCount_rename {Branch Control Branch' Control' : Type}
    (branchMap : Branch → Branch') (controlMap : Control → Control')
    (term : DTerm Branch Control) :
    discCount (rename branchMap controlMap term) = discCount term := by
  induction term <;> simp [rename, discCount, *]

@[simp] theorem depth_rename {Branch Control Branch' Control' : Type}
    (branchMap : Branch → Branch') (controlMap : Control → Control')
    (term : DTerm Branch Control) :
    depth (rename branchMap controlMap term) = depth term := by
  induction term <;> simp [rename, depth, *]

/-- Syntactic certificate for the declared original signature. -/
def OriginalSignature {Branch Control : Type} : DTerm Branch Control → Prop
  | .branch _ => True
  | .control _ => True
  | .disc left middle right =>
      OriginalSignature left ∧ OriginalSignature middle ∧ OriginalSignature right

@[simp] theorem originalSignature_rename
    {Branch Control Branch' Control' : Type}
    (branchMap : Branch → Branch') (controlMap : Control → Control')
    (term : DTerm Branch Control) :
    OriginalSignature (rename branchMap controlMap term) ↔
      OriginalSignature term := by
  induction term <;> simp [rename, OriginalSignature, *]

end DTerm

inductive Sign where
  | positive
  | negative
  deriving DecidableEq, Repr

inductive Digit where
  | left
  | middle
  | right
  deriving DecidableEq, Repr

instance : Fintype Digit where
  elems := {.left, .middle, .right}
  complete value := by cases value <;> simp

inductive Slot where
  | first
  | second
  deriving DecidableEq, Repr

instance : Fintype Slot where
  elems := {.first, .second}
  complete value := by cases value <;> simp

/-- A route address with `n` ternary digits.  The associated router has depth
`n+1`. -/
def Address : Nat → Type
  | 0 => PUnit
  | n + 1 => Digit × Address n

instance addressFintype : (n : Nat) → Fintype (Address n)
  | 0 => inferInstanceAs (Fintype PUnit)
  | n + 1 => by
      letI : Fintype (Address n) := addressFintype n
      exact inferInstanceAs (Fintype (Digit × Address n))

abbrev Control (n : Nat) := Slot × Address n

@[simp] theorem card_digit : Fintype.card Digit = 3 := by
  native_decide

@[simp] theorem card_slot : Fintype.card Slot = 2 := by
  native_decide

@[simp] theorem card_address (n : Nat) : Fintype.card (Address n) = 3 ^ n := by
  induction n with
  | zero => native_decide
  | succ n ih =>
      calc
        Fintype.card (Address (n + 1)) =
            Fintype.card (Digit × Address n) :=
          Fintype.card_congr (Equiv.refl (Digit × Address n))
        _ = Fintype.card Digit * Fintype.card (Address n) := Fintype.card_prod _ _
        _ = 3 ^ (n + 1) := by rw [card_digit, ih, pow_succ]; omega

@[simp] theorem card_control (n : Nat) :
    Fintype.card (Control n) = 2 * 3 ^ n := by
  simp [Control, card_address]

def branchInto {n : Nat} (digit : Digit) (address : Address n) : Address (n + 1) :=
  (digit, address)

def controlInto {n : Nat} (digit : Digit) (control : Control n) : Control (n + 1) :=
  (control.1, (digit, control.2))

def childSign : Sign → Digit → Sign
  | .positive, .left => .positive
  | .positive, .middle => .negative
  | .positive, .right => .positive
  | .negative, .left => .negative
  | .negative, .middle => .positive
  | .negative, .right => .negative

/-- The signed full discriminator tree.  Index `n` means capacity `3^n` and
depth `n+1`. -/
def router : (sign : Sign) → (n : Nat) → DTerm (Address n) (Control n)
  | .positive, 0 =>
      .disc (.branch PUnit.unit)
        (.control (.first, PUnit.unit))
        (.control (.second, PUnit.unit))
  | .negative, 0 =>
      .disc (.control (.first, PUnit.unit))
        (.branch PUnit.unit)
        (.control (.second, PUnit.unit))
  | .positive, n + 1 =>
      .disc
        ((router .positive n).rename (branchInto .left) (controlInto .left))
        ((router .negative n).rename (branchInto .middle) (controlInto .middle))
        ((router .positive n).rename (branchInto .right) (controlInto .right))
  | .negative, n + 1 =>
      .disc
        ((router .negative n).rename (branchInto .left) (controlInto .left))
        ((router .positive n).rename (branchInto .middle) (controlInto .middle))
        ((router .negative n).rename (branchInto .right) (controlInto .right))

inductive Mode (n : Nat) where
  | constant : Bool → Mode n
  | project : Address n → Mode n

def childMode {n : Nat} : Mode (n + 1) → Digit → Mode n
  | .constant value, _ => .constant value
  | .project (.left, address), .left => .project address
  | .project (.left, _), .middle => .constant false
  | .project (.left, _), .right => .constant false
  | .project (.middle, _), .left => .constant false
  | .project (.middle, address), .middle => .project address
  | .project (.middle, _), .right => .constant true
  | .project (.right, _), .left => .constant false
  | .project (.right, _), .middle => .constant false
  | .project (.right, address), .right => .project address

def baseProgram : Sign → Mode 0 → Slot → Bool
  | .positive, .project _, .first => false
  | .positive, .project _, .second => false
  | .positive, .constant false, .first => true
  | .positive, .constant false, .second => false
  | .positive, .constant true, .first => false
  | .positive, .constant true, .second => true
  | .negative, .project _, .first => false
  | .negative, .project _, .second => true
  | .negative, .constant false, .first => false
  | .negative, .constant false, .second => false
  | .negative, .constant true, .first => true
  | .negative, .constant true, .second => true

/-- Address-only control program.  Its arguments include no payload
valuation. -/
def program : (sign : Sign) → (n : Nat) → Mode n → Control n → Bool
  | sign, 0, mode, (slot, _) => baseProgram sign mode slot
  | sign, n + 1, mode, (slot, (digit, address)) =>
      program (childSign sign digit) n (childMode mode digit) (slot, address)

def expected {n : Nat} (sign : Sign) (mode : Mode n)
    (branches : Address n → Bool) : Bool :=
  match mode with
  | .constant value => value
  | .project address =>
      match sign with
      | .positive => branches address
      | .negative => !(branches address)

/-- Exact strong-router realization theorem. -/
theorem eval_router :
    ∀ n (sign : Sign) (mode : Mode n) (branches : Address n → Bool),
      (router sign n).eval branches (program sign n mode) =
        expected sign mode branches
  | 0, sign, mode, branches => by
      cases sign <;> cases mode with
      | constant value => cases value <;> simp [router, DTerm.eval, program,
          baseProgram, expected]
      | project address =>
          rcases address with ⟨⟩
          generalize branches PUnit.unit = value
          cases value <;> simp [router, DTerm.eval, program, baseProgram, expected]
  | n + 1, .positive, mode, branches => by
      simp only [router, DTerm.eval, DTerm.eval_rename, program, controlInto,
        childSign, branchInto]
      rw [eval_router n .positive (childMode mode .left)
            (fun address => branches (.left, address))]
      rw [eval_router n .negative (childMode mode .middle)
            (fun address => branches (.middle, address))]
      rw [eval_router n .positive (childMode mode .right)
            (fun address => branches (.right, address))]
      cases mode with
      | constant value => cases value <;> simp [expected, childMode]
      | project address =>
          rcases address with ⟨digit, address⟩
          cases digit <;> simp [expected, childMode]
  | n + 1, .negative, mode, branches => by
      simp only [router, DTerm.eval, DTerm.eval_rename, program, controlInto,
        childSign, branchInto]
      rw [eval_router n .negative (childMode mode .left)
            (fun address => branches (.left, address))]
      rw [eval_router n .positive (childMode mode .middle)
            (fun address => branches (.middle, address))]
      rw [eval_router n .negative (childMode mode .right)
            (fun address => branches (.right, address))]
      cases mode with
      | constant value => cases value <;> simp [expected, childMode]
      | project address =>
          rcases address with ⟨digit, address⟩
          cases digit <;> simp [expected, childMode]

theorem projects_positive (n : Nat) (target : Address n)
    (branches : Address n → Bool) :
    (router .positive n).eval branches
        (program .positive n (.project target)) = branches target := by
  simpa [expected] using eval_router n .positive (.project target) branches

theorem projects_negative (n : Nat) (target : Address n)
    (branches : Address n → Bool) :
    (router .negative n).eval branches
        (program .negative n (.project target)) = !(branches target) := by
  simpa [expected] using eval_router n .negative (.project target) branches

theorem forces_constant (sign : Sign) (n : Nat) (value : Bool)
    (branches : Address n → Bool) :
    (router sign n).eval branches (program sign n (.constant value)) = value := by
  simpa [expected] using eval_router n sign (.constant value) branches

@[simp] theorem router_branchCount (sign : Sign) (n : Nat) :
    (router sign n).branchCount = 3 ^ n := by
  induction n generalizing sign with
  | zero => cases sign <;> simp [router, DTerm.branchCount]
  | succ n ih =>
      cases sign <;> simp [router, DTerm.branchCount, ih, pow_succ]
      <;> omega

@[simp] theorem router_controlCount (sign : Sign) (n : Nat) :
    (router sign n).controlCount = 2 * 3 ^ n := by
  induction n generalizing sign with
  | zero => cases sign <;> simp [router, DTerm.controlCount]
  | succ n ih =>
      cases sign <;> simp [router, DTerm.controlCount, ih, pow_succ]
      <;> ring

@[simp] theorem router_depth (sign : Sign) (n : Nat) :
    (router sign n).depth = n + 1 := by
  induction n generalizing sign with
  | zero => cases sign <;> simp [router, DTerm.depth]
  | succ n ih =>
      cases sign <;> simp [router, DTerm.depth, ih]
      <;> omega

theorem router_discCount_identity (sign : Sign) (n : Nat) :
    2 * (router sign n).discCount + 1 = 3 ^ (n + 1) := by
  induction n generalizing sign with
  | zero => cases sign <;> simp [router, DTerm.discCount]
  | succ n ih =>
      have positiveIH := ih .positive
      have negativeIH := ih .negative
      cases sign <;> simp only [router, DTerm.discCount, DTerm.discCount_rename]
      all_goals rw [pow_succ]
      all_goals omega

@[simp] theorem router_originalSignature (sign : Sign) (n : Nat) :
    (router sign n).OriginalSignature := by
  induction n generalizing sign with
  | zero => cases sign <;> simp [router, DTerm.OriginalSignature]
  | succ n ih =>
      cases sign <;> simp [router, DTerm.OriginalSignature, ih]

/-- Depth-indexed form of the capacity statement `q_h=3^(h-1)`. -/
theorem capacity_at_depth (h : Nat) (_positive : 1 ≤ h) :
    Fintype.card (Address (h - 1)) = 3 ^ (h - 1) := by
  exact card_address (h - 1)

/-- The signed router whose externally stated depth is `h`. -/
def routerAtDepth (sign : Sign) (h : Nat) :
    DTerm (Address (h - 1)) (Control (h - 1)) :=
  router sign (h - 1)

@[simp] theorem routerAtDepth_branchCount (sign : Sign) (h : Nat) :
    (routerAtDepth sign h).branchCount = 3 ^ (h - 1) := by
  simp [routerAtDepth]

@[simp] theorem routerAtDepth_controlCount (sign : Sign) (h : Nat) :
    (routerAtDepth sign h).controlCount = 2 * 3 ^ (h - 1) := by
  simp [routerAtDepth]

theorem routerAtDepth_depth (sign : Sign) (h : Nat) (positive : 1 ≤ h) :
    (routerAtDepth sign h).depth = h := by
  simp [routerAtDepth, Nat.sub_add_cancel positive]

theorem positive_realization_at_depth (h : Nat) (_positive : 1 ≤ h)
    (target : Address (h - 1)) (branches : Address (h - 1) → Bool) :
    (routerAtDepth .positive h).eval branches
        (program .positive (h - 1) (.project target)) = branches target := by
  exact projects_positive (h - 1) target branches

theorem negative_realization_at_depth (h : Nat) (_positive : 1 ≤ h)
    (target : Address (h - 1)) (branches : Address (h - 1) → Bool) :
    (routerAtDepth .negative h).eval branches
        (program .negative (h - 1) (.project target)) = !(branches target) := by
  exact projects_negative (h - 1) target branches

end OrbitSynthesis.StrongSignedRouter
