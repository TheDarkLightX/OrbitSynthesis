#!/usr/bin/env python3
"""Audit that learned clauses are bound to the compiled component model."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import (
    CompiledDomainFailure,
    ComponentCandidateRule,
    ComponentRuleSet,
    QuasiPrimalDomainModel,
)
from orbitsynthesis.domain_nogood import (
    minimize_domain_failure,
    verify_domain_conflict_core,
    verify_domain_conflict_core_against_model,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def make_receipt() -> dict[str, object]:
    s0, s1 = (0,), (1,)
    model = QuasiPrimalDomainModel(
        states=(s0, s1),
        observations=(),
        components=(
            ComponentRuleSet(
                representative=("component",),
                observations=(),
                candidates=(
                    ComponentCandidateRule(
                        representative_output=(),
                        assignment_items=(),
                        forbidden_states=frozenset((s0,)),
                        closure_edges=frozenset(),
                    ),
                ),
            ),
        ),
    )
    domain = frozenset((s0, s1))
    actual = model.solve_domain(domain)
    require(isinstance(actual, CompiledDomainFailure), "actual domain should fail")
    actual_core = minimize_domain_failure(actual)
    require(
        verify_domain_conflict_core_against_model(
            model,
            actual,
            actual_core,
            require_minimal=True,
        ),
        "actual conflict did not replay against the model",
    )

    # This forged failure is internally self-consistent: state 1 is included,
    # so its fabricated forbidden-state condition and derived core both verify
    # against the forged object.  It is nevertheless false for the compiled
    # component, whose only forbidden state is state 0.
    forged = CompiledDomainFailure(
        domain=domain,
        component_index=actual.component_index,
        representative=actual.representative,
        forbidden_hits=((0, (s1,)),),
        missing_closure_edges=((0, ()),),
    )
    forged_core = minimize_domain_failure(forged)
    require(
        verify_domain_conflict_core(
            forged,
            forged_core,
            require_minimal=True,
        ),
        "forged conflict should be self-consistent with its forged failure",
    )
    require(
        not verify_domain_conflict_core_against_model(
            model,
            forged,
            forged_core,
            require_minimal=True,
        ),
        "model-aware verifier accepted a stale/forged failure",
    )

    feasible = frozenset((s1,))
    require(model.domain_feasible(feasible), "control domain should be feasible")
    require(
        not actual_core.holds(feasible),
        "actual learned core would block a feasible control domain",
    )

    result = {
        "schema": "orbit-synthesis/domain-conflict-model-replay/v1",
        "actual_core": [
            {"state": list(literal.state), "included": literal.included}
            for literal in actual_core.literals
        ],
        "forged_core": [
            {"state": list(literal.state), "included": literal.included}
            for literal in forged_core.literals
        ],
        "raw_forged_core_verifies": True,
        "model_aware_forged_core_rejected": True,
        "feasible_control_preserved": True,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main() -> int:
    print(json.dumps(make_receipt(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
