import ProgramVectorCost
import NativeFirstMismatch

/-!
# Original-signature bridge for native comparison modes

This layer uses the frozen `QTerm`, signed-tree, and address-summary interfaces.
It proves exact one-digit mode terms, one-node segment composition, fused bottom
cells, and the complete signed-tree semantics.
-/

namespace OrbitSynthesis.StrongSignedRouter.NativeModeBridge

open OrbitSynthesis.StrongSignedRouter
open OrbitSynthesis.StrongSignedRouter.ProgramVector
open OrbitSynthesis.StrongSignedRouter.ProgramVectorCost

/-- Encode the three reachable `(equal,gain)` states directly as `2,1,0`. -/
def summaryCode (summary : SegmentSummary) : Q :=
  if summary.eqFlag then .two else if summary.gain then .one else .zero

/-- Segment composition becomes one native discriminator node.  The premise
excludes the unreachable flag pattern `(true,true)`. -/
theorem summaryCode_comp (left right : SegmentSummary)
    (leftDisjoint : (left.eqFlag && left.gain) = false) :
    summaryCode (left.comp right) =
      qDisc (summaryCode left) .two (summaryCode right) := by
  rcases left with ⟨leftEqual, leftGain⟩
  rcases right with ⟨rightEqual, rightGain⟩
  cases leftEqual <;> cases leftGain <;>
    cases rightEqual <;> cases rightGain <;>
    simp_all [summaryCode, SegmentSummary.comp, qDisc]

/-- One-digit native roots in the original constant-free `d/u` grammar. -/
def digitModeTerm {Var : Type} (anchor digit : Var) : Digit → QTerm Var
  | .left =>
      .disc (anchorZero anchor) (.variable digit) (anchorTwo anchor)
  | .middle =>
      .disc
        (.disc (anchorOne anchor) (.variable digit) (anchorTwo anchor))
        (anchorOne anchor)
        (anchorZero anchor)
  | .right => .variable digit

/-- All nine target/physical one-digit cases. -/
theorem digitModeTerm_correct {Var : Type} (environment : Var → Q)
    (anchor digit : Var) (target physical : Digit)
    (anchorValue : environment anchor = .two)
    (digitValue : environment digit = digitQ target) :
    (digitModeTerm anchor digit physical).eval environment =
      summaryCode (digitSummary target physical) := by
  cases target <;> cases physical <;>
    simp [digitModeTerm, summaryCode, digitSummary, anchorZero, anchorOne,
      anchorTwo, QTerm.eval, qDisc, qUnary, digitQ, anchorValue, digitValue]

@[simp] theorem digitModeTerm_originalSignature {Var : Type}
    (anchor digit : Var) (physical : Digit) :
    (digitModeTerm anchor digit physical).OriginalSignature := by
  cases physical <;> simp [digitModeTerm]

theorem digitModeTerm_depth_le_three {Var : Type}
    (anchor digit : Var) (physical : Digit) :
    (digitModeTerm anchor digit physical).depth ≤ 3 := by
  cases physical <;>
    norm_num [digitModeTerm, anchorZero, anchorOne, anchorTwo, QTerm.depth]

/-- One discriminator node composes two segment roots. -/
def composeModeTerm {Var : Type} (anchor : Var)
    (left right : QTerm Var) : QTerm Var :=
  .disc left (anchorTwo anchor) right

theorem composeModeTerm_correct {Var : Type} (environment : Var → Q)
    (anchor : Var) (anchorValue : environment anchor = .two)
    (left right : QTerm Var) (leftSummary rightSummary : SegmentSummary)
    (leftDisjoint : (leftSummary.eqFlag && leftSummary.gain) = false)
    (leftCorrect : left.eval environment = summaryCode leftSummary)
    (rightCorrect : right.eval environment = summaryCode rightSummary) :
    (composeModeTerm anchor left right).eval environment =
      summaryCode (leftSummary.comp rightSummary) := by
  rw [summaryCode_comp leftSummary rightSummary leftDisjoint]
  simp [composeModeTerm, QTerm.eval, anchorTwo, anchorValue, leftCorrect,
    rightCorrect]

@[simp] theorem composeModeTerm_originalSignature {Var : Type}
    (anchor : Var) (left right : QTerm Var) :
    (composeModeTerm anchor left right).OriginalSignature := by
  simp [composeModeTerm]

@[simp] theorem composeModeTerm_depth {Var : Type}
    (anchor : Var) (left right : QTerm Var) :
    (composeModeTerm anchor left right).depth =
      max left.depth right.depth + 1 := by
  simp [composeModeTerm, anchorTwo, QTerm.depth]

/-- Existing base modes encoded by native values. -/
def baseModeCode : Mode 0 → Q
  | .constant false => .zero
  | .constant true => .one
  | .project _ => .two

def signedPayload : Sign → Bool → Bool
  | .positive, value => value
  | .negative, value => !value

def nativeBaseEval (sign : Sign) (mode : Mode 0) (payload : Bool) : Q :=
  qDisc (baseModeCode mode) .two (qBit (signedPayload sign payload))

theorem nativeBaseEval_correct (sign : Sign) (mode : Mode 0)
    (branches : Address 0 → Bool) :
    nativeBaseEval sign mode (branches PUnit.unit) =
      qBit (expected sign mode branches) := by
  cases sign <;> cases mode with
  | constant value =>
      cases value <;>
        simp [nativeBaseEval, baseModeCode, qDisc, qBit,
          expected]
  | project address =>
      rcases address with ⟨⟩
      generalize h : branches PUnit.unit = value
      cases value <;>
        simp [nativeBaseEval, baseModeCode, signedPayload, qDisc, qBit,
          expected, h]

/-- Term-level fused bottom cell. -/
def fusedBottomTerm {Var : Type} (anchor : Var) (sign : Sign)
    (mode payload : QTerm Var) : QTerm Var :=
  match sign with
  | .positive => .disc mode (anchorTwo anchor) payload
  | .negative => .disc mode (anchorTwo anchor) (.unary payload)

theorem fusedBottomTerm_correct {Var : Type} (environment : Var → Q)
    (anchor : Var) (anchorValue : environment anchor = .two)
    (sign : Sign) (mode : Mode 0) (modeTerm payloadTerm : QTerm Var)
    (payload : Bool)
    (modeCorrect : modeTerm.eval environment = baseModeCode mode)
    (payloadCorrect : payloadTerm.eval environment = qBit payload) :
    (fusedBottomTerm anchor sign modeTerm payloadTerm).eval environment =
      nativeBaseEval sign mode payload := by
  cases sign <;> cases mode with
  | constant value =>
      cases value <;> cases payload <;>
        simp_all [fusedBottomTerm, nativeBaseEval, baseModeCode,
          anchorTwo, QTerm.eval, qDisc, qBit]
  | project address =>
      rcases address with ⟨⟩
      cases payload <;>
        simp_all [fusedBottomTerm, nativeBaseEval, baseModeCode, signedPayload,
          anchorTwo, QTerm.eval, qDisc, qUnary, qBit]

@[simp] theorem qDisc_qBit (x y z : Bool) :
    qDisc (qBit x) (qBit y) (qBit z) = qBit (disc x y z) := by
  cases x <;> cases y <;> cases z <;> rfl

/-- Semantic evaluation of the complete signed tree with native fused bottoms. -/
def evalNative : (n : Nat) → Sign → Mode n → (Address n → Bool) → Q
  | 0, sign, mode, branches =>
      nativeBaseEval sign mode (branches PUnit.unit)
  | n + 1, sign, mode, branches =>
      qDisc
        (evalNative n (childSign sign .left) (childMode mode .left)
          (fun address => branches (.left, address)))
        (evalNative n (childSign sign .middle) (childMode mode .middle)
          (fun address => branches (.middle, address)))
        (evalNative n (childSign sign .right) (childMode mode .right)
          (fun address => branches (.right, address)))

/-- Exact fused signed-tree induction for every width, sign, projection, and
constant mode. -/
theorem evalNative_correct :
    ∀ n (sign : Sign) (mode : Mode n) (branches : Address n → Bool),
      evalNative n sign mode branches = qBit (expected sign mode branches)
  | 0, sign, mode, branches => nativeBaseEval_correct sign mode branches
  | n + 1, .positive, mode, branches => by
      simp only [evalNative, childSign]
      rw [evalNative_correct n .positive (childMode mode .left)
            (fun address => branches (.left, address))]
      rw [evalNative_correct n .negative (childMode mode .middle)
            (fun address => branches (.middle, address))]
      rw [evalNative_correct n .positive (childMode mode .right)
            (fun address => branches (.right, address))]
      rw [qDisc_qBit]
      cases mode with
      | constant value => cases value <;> simp [expected, childMode]
      | project address =>
          rcases address with ⟨digit, address⟩
          cases digit <;> simp [expected, childMode]
  | n + 1, .negative, mode, branches => by
      simp only [evalNative, childSign]
      rw [evalNative_correct n .negative (childMode mode .left)
            (fun address => branches (.left, address))]
      rw [evalNative_correct n .positive (childMode mode .middle)
            (fun address => branches (.middle, address))]
      rw [evalNative_correct n .negative (childMode mode .right)
            (fun address => branches (.right, address))]
      rw [qDisc_qBit]
      cases mode with
      | constant value => cases value <;> simp [expected, childMode]
      | project address =>
          rcases address with ⟨digit, address⟩
          cases digit <;> simp [expected, childMode]

@[simp] theorem projects_positive (n : Nat) (target : Address n)
    (branches : Address n → Bool) :
    evalNative n .positive (.project target) branches = qBit (branches target) := by
  simpa [expected] using
    evalNative_correct n .positive (.project target) branches

@[simp] theorem projects_negative (n : Nat) (target : Address n)
    (branches : Address n → Bool) :
    evalNative n .negative (.project target) branches = qBit (!(branches target)) := by
  simpa [expected] using
    evalNative_correct n .negative (.project target) branches

@[simp] theorem forces_constant (n : Nat) (sign : Sign) (value : Bool)
    (branches : Address n → Bool) :
    evalNative n sign (.constant value) branches = qBit value := by
  simpa [expected] using
    evalNative_correct n sign (.constant value) branches

end OrbitSynthesis.StrongSignedRouter.NativeModeBridge
