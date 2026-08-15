#!/usr/bin/env python3
"""Fail-closed audit of the external SAT/MaxSAT process adapter."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import compile_quasi_primal_domain_model
from orbitsynthesis.domain_solver import (
    literals_for_witness,
    maximum_weight_domain_exhaustive,
)
from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.safety import FiniteSafetyGame
from orbitsynthesis.solver_adapter import (
    SolverAdapterError,
    SolverCommand,
    SolverTimeoutError,
    run_cnf_solver,
    run_weighted_maxsat_solver,
)

Q = (0, 1, 2)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def qunary(x: int) -> int:
    return (1, 0, 1)[x]


def algebra() -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        Q,
        {"d": (3, discriminator), "u": (1, qunary)},
    )


FAKE_SOLVER = r'''#!/usr/bin/env python3
import pathlib
import sys
import time

problem = pathlib.Path(sys.argv[1])
mode = sys.argv[2]
model_path = pathlib.Path(sys.argv[3])
objective = int(sys.argv[4])
header = problem.read_text(encoding="utf-8").splitlines()[0]
model = model_path.read_text(encoding="utf-8").strip()

if mode == "timeout":
    time.sleep(5)
    raise SystemExit(0)
if mode == "noise":
    print("X" * 5000)
    raise SystemExit(0)
if mode == "bad-return":
    print("s UNKNOWN")
    raise SystemExit(7)
if mode == "unsat":
    print("s UNSATISFIABLE")
    raise SystemExit(20)
if mode == "cnf":
    assert header.startswith("p cnf ")
    print("c fake solver")
    print("s SATISFIABLE")
    print(model)
    raise SystemExit(10)
if mode in {"wcnf", "bad-objective"}:
    assert header.startswith("p wcnf ")
    print("c fake optimizer")
    print("s OPTIMUM FOUND")
    print(f"o {objective + (1 if mode == 'bad-objective' else 0)}")
    print(model)
    raise SystemExit(0)
raise SystemExit(9)
'''


def command(
    script: Path,
    mode: str,
    model_path: Path,
    objective: int,
    *,
    timeout: float = 5.0,
    max_output: int = 100_000,
    extra: str | None = None,
) -> SolverCommand:
    argv = [
        sys.executable,
        str(script),
        "{input}",
        mode,
        str(model_path),
        str(objective),
    ]
    if extra is not None:
        argv.append(extra)
    return SolverCommand(
        argv=tuple(argv),
        timeout_seconds=timeout,
        max_output_bytes=max_output,
    )


def make_receipt() -> dict[str, object]:
    A = algebra()
    game = FiniteSafetyGame(
        A,
        1,
        0,
        {
            ((0,), (), (0,)),
            ((1,), (), (0,)),
            ((2,), (), (2,)),
        },
    )
    model = compile_quasi_primal_domain_model(game)
    required = frozenset(((0,),))
    weights = {(0,): 5, (1,): 3, (2,): 1}
    optimum = maximum_weight_domain_exhaustive(
        model,
        required_states=required,
        state_weights=weights,
        exhaustive_state_limit=3,
    )
    require(optimum is not None, "missing reference optimum")
    require(optimum.total_weight == 6, "reference optimum drift")

    hard = model.cnf(required_states=required)
    weighted = model.weighted_cnf(
        required_states=required,
        state_weights=weights,
    )
    literals = literals_for_witness(model, hard, optimum.witness)
    total_soft = sum(weight for _, weight in weighted.soft_state_units)
    optimum_cost = total_soft - optimum.total_weight
    require(optimum_cost == 3, "objective convention drift")

    with tempfile.TemporaryDirectory(prefix="orbit-fake-solver-") as directory:
        directory_path = Path(directory)
        script = directory_path / "fake_solver.py"
        script.write_text(FAKE_SOLVER, encoding="utf-8")
        model_path = directory_path / "model.txt"
        model_path.write_text(
            "v " + " ".join(map(str, literals)) + " 0\n",
            encoding="utf-8",
        )

        sentinel = directory_path / "SHELL_WOULD_HAVE_CREATED_THIS"
        cnf = run_cnf_solver(
            model,
            hard,
            command(
                script,
                "cnf",
                model_path,
                0,
                extra=f";touch {sentinel}",
            ),
        )
        require(cnf.witness.domain == optimum.witness.domain, "CNF domain")
        require(cnf.witness.strategy == optimum.witness.strategy, "CNF strategy")
        require(not sentinel.exists(), "solver command unexpectedly invoked a shell")

        weighted_claim = run_weighted_maxsat_solver(
            model,
            hard,
            weighted,
            command(script, "wcnf", model_path, optimum_cost),
        )
        require(weighted_claim.receipt.solver_claimed_optimum, "missing claim")
        require(
            not weighted_claim.receipt.optimality_verified,
            "unproved solver claim was promoted to verified optimum",
        )
        require(
            weighted_claim.receipt.expected_objective_cost == optimum_cost,
            "weighted objective arithmetic",
        )

        weighted_verified = run_weighted_maxsat_solver(
            model,
            hard,
            weighted,
            command(script, "wcnf", model_path, optimum_cost),
            known_optimum_cost=optimum_cost,
        )
        require(
            weighted_verified.receipt.optimality_verified,
            "known optimum was not verified",
        )
        require(
            weighted_verified.witness.domain == optimum.witness.domain,
            "weighted domain",
        )

        bad_objective_rejected = False
        try:
            run_weighted_maxsat_solver(
                model,
                hard,
                weighted,
                command(script, "bad-objective", model_path, optimum_cost),
            )
        except SolverAdapterError:
            bad_objective_rejected = True
        require(bad_objective_rejected, "bad objective mutation escaped")

        unsat_rejected = False
        try:
            run_cnf_solver(
                model,
                hard,
                command(script, "unsat", model_path, 0),
            )
        except SolverAdapterError:
            unsat_rejected = True
        require(unsat_rejected, "UNSAT mutation escaped")

        timeout_rejected = False
        try:
            run_cnf_solver(
                model,
                hard,
                command(script, "timeout", model_path, 0, timeout=0.05),
            )
        except SolverTimeoutError:
            timeout_rejected = True
        require(timeout_rejected, "timeout mutation escaped")

        output_limit_rejected = False
        try:
            run_cnf_solver(
                model,
                hard,
                command(script, "noise", model_path, 0, max_output=100),
            )
        except SolverAdapterError:
            output_limit_rejected = True
        require(output_limit_rejected, "output-limit mutation escaped")

        return_code_rejected = False
        try:
            run_cnf_solver(
                model,
                hard,
                command(script, "bad-return", model_path, 0),
            )
        except SolverAdapterError:
            return_code_rejected = True
        require(return_code_rejected, "return-code mutation escaped")

        placeholder_rejected = False
        try:
            SolverCommand(argv=(sys.executable, str(script)))
        except ValueError:
            placeholder_rejected = True
        require(placeholder_rejected, "missing-input placeholder escaped")

    result = {
        "schema": "orbit-synthesis/external-solver-adapter/v1",
        "reference": {
            "optimum_weight": optimum.total_weight,
            "optimum_cost": optimum_cost,
            "domain": [list(state) for state in sorted(optimum.witness.domain)],
            "variables": hard.variable_count,
            "hard_clauses": len(hard.clauses),
        },
        "cnf": {
            "status": cnf.receipt.status,
            "return_code": cnf.receipt.return_code,
            "model_literals": cnf.receipt.model_literal_count,
            "problem_sha256": cnf.receipt.problem_sha256,
            "stdout_sha256": cnf.receipt.stdout_sha256,
            "shell_metacharacters_inert": True,
        },
        "weighted_claim": {
            "status": weighted_claim.receipt.status,
            "reported_cost": weighted_claim.receipt.objective_cost,
            "expected_cost": weighted_claim.receipt.expected_objective_cost,
            "claimed_optimum": weighted_claim.receipt.solver_claimed_optimum,
            "optimality_verified": weighted_claim.receipt.optimality_verified,
        },
        "weighted_verified": {
            "optimality_verified": weighted_verified.receipt.optimality_verified,
            "known_optimum_cost": optimum_cost,
        },
        "mutations": {
            "bad_objective_rejected": bad_objective_rejected,
            "unsat_rejected": unsat_rejected,
            "timeout_rejected": timeout_rejected,
            "output_limit_rejected": output_limit_rejected,
            "return_code_rejected": return_code_rejected,
            "missing_placeholder_rejected": placeholder_rejected,
        },
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main() -> int:
    result = make_receipt()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
