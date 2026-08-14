#!/usr/bin/env python3
"""Focused gate for command adapter status and return-code options."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import (
    CompiledDomainWitness,
    ComponentCandidateRule,
    ComponentRuleSet,
    QuasiPrimalDomainModel,
)
from orbitsynthesis.domain_solver import literals_for_witness
from orbitsynthesis.external_optimization import (
    ExternalOptimizationResult,
    solve_weighted_cnf_command,
)


def model_and_encoding():
    states = ((0,), (1,))
    observations = states
    candidates = (
        ComponentCandidateRule(
            representative_output=(0,),
            assignment_items=tuple((observation, (0,)) for observation in observations),
            forbidden_states=frozenset({(1,)}),
            closure_edges=frozenset(),
        ),
        ComponentCandidateRule(
            representative_output=(1,),
            assignment_items=tuple((observation, (1,)) for observation in observations),
            forbidden_states=frozenset({(0,)}),
            closure_edges=frozenset(),
        ),
    )
    model = QuasiPrimalDomainModel(
        states=states,
        observations=observations,
        components=(
            ComponentRuleSet(
                representative=(0,),
                observations=observations,
                candidates=candidates,
            ),
        ),
    )
    cnf = model.cnf()
    wcnf = model.weighted_cnf(
        state_weights={(0,): 5, (1,): 3},
        default_weight=0,
    )
    witness = model.solve_domain({(0,)})
    if not isinstance(witness, CompiledDomainWitness):
        raise AssertionError("expected a concrete component-domain witness")
    literals = literals_for_witness(model, cnf, witness)
    return model, cnf, wcnf, literals


def main() -> int:
    model, cnf, wcnf, literals = model_and_encoding()
    model_text = " ".join(map(str, literals))

    returncode = solve_weighted_cnf_command(
        model,
        cnf,
        wcnf,
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                f"print('o 3\\ns OPTIMUM FOUND\\nv {model_text} 0'); "
                "sys.exit(10)"
            ),
            "{wcnf}",
        ],
        accepted_returncodes=(0, 10),
        state_weights={(0,): 5, (1,): 3},
        default_weight=0,
    )
    if returncode.status != "optimal" or returncode.metadata["returncode"] != 10:
        raise AssertionError("configured return code was not preserved")

    satisfiable = solve_weighted_cnf_command(
        model,
        cnf,
        wcnf,
        [
            sys.executable,
            "-c",
            f"print('s SATISFIABLE\\nv {model_text} 0')",
            "{wcnf}",
        ],
        require_optimum=False,
        require_reported_cost=False,
        state_weights={(0,): 5, (1,): 3},
        default_weight=0,
    )
    if satisfiable.status != "satisfiable":
        raise AssertionError("non-optimal model status was overwritten")
    if satisfiable.optimality_authority != "not_claimed":
        raise AssertionError("non-optimal model incorrectly claimed optimum authority")
    if not satisfiable.certificate_verified or satisfiable.witness is None:
        raise AssertionError("satisfiable model was not certificate checked")

    rejected_empty_returncodes = False
    try:
        solve_weighted_cnf_command(
            model,
            cnf,
            wcnf,
            [sys.executable, "-c", "print('s UNKNOWN')", "{wcnf}"],
            accepted_returncodes=(),
        )
    except ValueError:
        rejected_empty_returncodes = True
    if not rejected_empty_returncodes:
        raise AssertionError("empty accepted-returncode set was accepted")

    unusual = ExternalOptimizationResult(
        backend="test",
        status="optimal",
        certificate_verified=True,
        optimality_authority="bounded_exhaustive",
        witness=CompiledDomainWitness(
            domain=frozenset({(frozenset({1, 2}),)}),
            component_choices=(),
            strategy_items=(),
        ),
        model_literals=(),
        soft_reward=0,
        unsatisfied_cost=0,
        reported_cost=0,
        signed_utility=0,
        wall_seconds=0.0,
    )
    if len(unusual.semantic_sha256) != 64:
        raise AssertionError("semantic hash did not support non-JSON carrier values")

    result = {
        "schema": "orbit-synthesis/command-adapter-options/v1",
        "accepted_returncode": returncode.metadata["returncode"],
        "satisfiable_status": satisfiable.status,
        "satisfiable_authority": satisfiable.optimality_authority,
        "unusual_semantic_sha256": unusual.semantic_sha256,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
