import ProgramVectorCost

/-!
# Five-node direct Q multiplexer

This file formalizes the two local gadgets used by the direct-Q Pareto compiler:

* a five-discriminator selector for three arbitrary Q-valued payloads; and
* a two-node Boolean encoding with a one-node decoder.

The value names are variables in this scoped grammar.  In the integrated
compiler they are supplied once by the nonbinary anchor and shared freely.
-/

namespace OrbitSynthesis.StrongSignedRouter.DirectQMux

open OrbitSynthesis.StrongSignedRouter.ProgramVectorCost

inductive MuxVar where
  | selector
  | zero
  | one
  | two
  | branch0
  | branch1
  | branch2
  deriving DecidableEq, Repr

/-- Five discriminator nodes, with maximum payload depth three. -/
def muxTerm : QTerm MuxVar :=
  .disc
    (.disc (.variable .zero) (.variable .selector) (.variable .branch0))
    (.variable .zero)
    (.disc
      (.disc (.variable .one) (.variable .selector) (.variable .branch1))
      (.variable .one)
      (.disc (.variable .selector) (.variable .two) (.variable .branch2)))

def muxEnvironment (selector branch0 branch1 branch2 : Q) : MuxVar → Q
  | .selector => selector
  | .zero => .zero
  | .one => .one
  | .two => .two
  | .branch0 => branch0
  | .branch1 => branch1
  | .branch2 => branch2

theorem muxTerm_correct (selector branch0 branch1 branch2 : Q) :
    muxTerm.eval (muxEnvironment selector branch0 branch1 branch2) =
      match selector with
      | .zero => branch0
      | .one => branch1
      | .two => branch2 := by
  cases selector <;>
    simp [muxTerm, muxEnvironment, QTerm.eval, qDisc]

@[simp] theorem muxTerm_operationCount : muxTerm.operationCount = 5 := by
  norm_num [muxTerm, QTerm.operationCount]

@[simp] theorem muxTerm_depth : muxTerm.depth = 3 := by
  norm_num [muxTerm, QTerm.depth]

@[simp] theorem muxTerm_originalSignature : muxTerm.OriginalSignature := by
  simp [muxTerm]

inductive CodeVar where
  | value
  | zero
  | one
  | two
  | first
  | second
  deriving DecidableEq, Repr

/-- First rail: values `0,1,2` map to `1,0,0`. -/
def firstRailTerm : QTerm CodeVar :=
  .disc (.variable .zero) (.variable .value) (.variable .one)

/-- Second rail: values `0,1,2` map to `0,1,0`. -/
def secondRailTerm : QTerm CodeVar :=
  .disc (.variable .value) (.variable .two) (.variable .zero)

/-- Decode the legal codes `10,01,00` as `0,1,2`. -/
def decoderTerm : QTerm CodeVar :=
  .disc (.variable .second) (.variable .first) (.variable .two)

def codeEnvironment (value : Q) : CodeVar → Q
  | .value => value
  | .zero => .zero
  | .one => .one
  | .two => .two
  | .first => qDisc .zero value .one
  | .second => qDisc value .two .zero

theorem firstRail_correct (value : Q) :
    firstRailTerm.eval (codeEnvironment value) =
      match value with
      | .zero => .one
      | .one => .zero
      | .two => .zero := by
  cases value <;>
    simp [firstRailTerm, codeEnvironment, QTerm.eval, qDisc]

theorem secondRail_correct (value : Q) :
    secondRailTerm.eval (codeEnvironment value) =
      match value with
      | .zero => .zero
      | .one => .one
      | .two => .zero := by
  cases value <;>
    simp [secondRailTerm, codeEnvironment, QTerm.eval, qDisc]

theorem decoder_correct (value : Q) :
    decoderTerm.eval (codeEnvironment value) = value := by
  cases value <;>
    simp [decoderTerm, codeEnvironment, QTerm.eval, qDisc]

@[simp] theorem firstRail_operationCount :
    firstRailTerm.operationCount = 1 := by
  rfl

@[simp] theorem secondRail_operationCount :
    secondRailTerm.operationCount = 1 := by
  rfl

@[simp] theorem decoder_operationCount : decoderTerm.operationCount = 1 := by
  rfl

@[simp] theorem firstRail_depth : firstRailTerm.depth = 1 := by
  rfl

@[simp] theorem secondRail_depth : secondRailTerm.depth = 1 := by
  rfl

@[simp] theorem decoder_depth : decoderTerm.depth = 1 := by
  rfl

@[simp] theorem codeTerms_originalSignature :
    firstRailTerm.OriginalSignature ∧
      secondRailTerm.OriginalSignature ∧
      decoderTerm.OriginalSignature := by
  simp [firstRailTerm, secondRailTerm, decoderTerm]

end OrbitSynthesis.StrongSignedRouter.DirectQMux
