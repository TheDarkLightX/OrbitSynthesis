import Lake
open Lake DSL

package orbitSynthesis where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @
  "9aa55045016ce35bb2379a8fc3d7f268995fb99a"

@[default_target]
lean_lib OrbitSynthesis where
  srcDir := "formal"
