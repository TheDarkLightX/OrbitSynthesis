"""Thin, solver-neutral process adapter for OrbitSynthesis CNF/WCNF models.

External SAT/MaxSAT software is treated as an untrusted search oracle.  This
module never invokes a shell.  It writes one temporary problem file, runs an
explicit argv template containing ``{input}``, bounds runtime/output, parses
the returned model, rechecks every hard clause, and reconstructs the complete
algebraic controller certificate.

For weighted MaxSAT, the reported objective is checked against the decoded
state assignment.  A solver status such as ``OPTIMUM FOUND`` is recorded as a
claim, not independently promoted to an optimality proof.  ``optimality_verified``
is true only when the caller supplies a separately established optimum cost.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
from typing import Iterable, Sequence

from .domain_model import (
    CNFEncoding,
    CompiledDomainWitness,
    QuasiPrimalDomainModel,
    WeightedCNFEncoding,
)
from .domain_solver import (
    decode_cnf_model,
    normalize_boolean_model,
    parse_dimacs_model,
)


class SolverAdapterError(RuntimeError):
    """Base class for fail-closed external-solver failures."""


class SolverTimeoutError(SolverAdapterError):
    """The configured external solver exceeded its deadline."""


@dataclass(frozen=True)
class SolverCommand:
    """An explicit, shell-free command template.

    At least one argv item must contain ``{input}``.  The placeholder is
    replaced by the temporary CNF/WCNF file path.  Other arguments are passed
    literally, including spaces and shell metacharacters.
    """

    argv: tuple[str, ...]
    timeout_seconds: float = 60.0
    accepted_return_codes: tuple[int, ...] = (0, 10, 20, 30)
    max_output_bytes: int = 4_000_000

    def __post_init__(self) -> None:
        if not self.argv:
            raise ValueError("solver command must not be empty")
        if not any("{input}" in argument for argument in self.argv):
            raise ValueError("solver command must contain an {input} placeholder")
        if self.timeout_seconds <= 0:
            raise ValueError("solver timeout must be positive")
        if self.max_output_bytes <= 0:
            raise ValueError("solver output limit must be positive")

    def render(self, input_path: Path) -> tuple[str, ...]:
        return tuple(
            argument.replace("{input}", str(input_path))
            for argument in self.argv
        )


@dataclass(frozen=True)
class SolverExecutionReceipt:
    """Portable evidence about one verified external model."""

    return_code: int
    elapsed_milliseconds: int
    status: str | None
    objective_cost: int | None
    expected_objective_cost: int | None
    solver_claimed_optimum: bool
    optimality_verified: bool
    model_literal_count: int
    problem_sha256: str
    stdout_sha256: str
    stderr_sha256: str
    stderr_excerpt: str


@dataclass(frozen=True)
class VerifiedExternalModel:
    """A decoded controller witness plus its process receipt."""

    witness: CompiledDomainWitness
    receipt: SolverExecutionReceipt


@dataclass(frozen=True)
class _RawSolverOutput:
    return_code: int
    elapsed_milliseconds: int
    stdout: str
    stderr: str
    problem_sha256: str


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _terminate_process_group(process: subprocess.Popen[str]) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass


def _run_problem(
    problem_text: str,
    suffix: str,
    command: SolverCommand,
) -> _RawSolverOutput:
    encoded_problem = problem_text.encode("utf-8")
    problem_sha256 = hashlib.sha256(encoded_problem).hexdigest()

    with tempfile.TemporaryDirectory(prefix="orbitsynthesis-solver-") as directory:
        input_path = Path(directory) / f"problem{suffix}"
        input_path.write_bytes(encoded_problem)
        argv = command.render(input_path)
        started = time.monotonic()
        process = subprocess.Popen(
            argv,
            cwd=directory,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            start_new_session=(os.name == "posix"),
        )
        try:
            stdout, stderr = process.communicate(timeout=command.timeout_seconds)
        except subprocess.TimeoutExpired as error:
            _terminate_process_group(process)
            stdout, stderr = process.communicate()
            raise SolverTimeoutError(
                f"solver exceeded {command.timeout_seconds} seconds"
            ) from error
        elapsed = int(round((time.monotonic() - started) * 1000))

    output_size = len(stdout.encode("utf-8")) + len(stderr.encode("utf-8"))
    if output_size > command.max_output_bytes:
        raise SolverAdapterError(
            "solver output exceeded configured limit: "
            f"{output_size}>{command.max_output_bytes} bytes"
        )
    if process.returncode not in command.accepted_return_codes:
        raise SolverAdapterError(
            f"solver returned unaccepted code {process.returncode}; "
            f"stderr={stderr[:500]!r}"
        )
    return _RawSolverOutput(
        return_code=process.returncode,
        elapsed_milliseconds=elapsed,
        stdout=stdout,
        stderr=stderr,
        problem_sha256=problem_sha256,
    )


def parse_solver_status(text: str) -> str | None:
    """Return the final conventional ``s ...`` status line, if any."""

    status = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.lower().startswith("s "):
            status = line[2:].strip()
    return status


def parse_solver_objective(text: str) -> int | None:
    """Return the final conventional integer ``o ...`` objective, if any."""

    objective = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.lower().startswith("o "):
            continue
        token = line[2:].strip().split()[0]
        try:
            objective = int(token)
        except ValueError as error:
            raise SolverAdapterError(
                f"non-integer solver objective: {token!r}"
            ) from error
    return objective


def _reject_unsat_status(status: str | None) -> None:
    if status is not None and "UNSAT" in status.upper():
        raise SolverAdapterError(
            f"solver returned {status!r}; no controller model is available"
        )


def _receipt(
    raw: _RawSolverOutput,
    *,
    status: str | None,
    objective_cost: int | None,
    expected_objective_cost: int | None,
    solver_claimed_optimum: bool,
    optimality_verified: bool,
    model_literal_count: int,
) -> SolverExecutionReceipt:
    return SolverExecutionReceipt(
        return_code=raw.return_code,
        elapsed_milliseconds=raw.elapsed_milliseconds,
        status=status,
        objective_cost=objective_cost,
        expected_objective_cost=expected_objective_cost,
        solver_claimed_optimum=solver_claimed_optimum,
        optimality_verified=optimality_verified,
        model_literal_count=model_literal_count,
        problem_sha256=raw.problem_sha256,
        stdout_sha256=_sha256_text(raw.stdout),
        stderr_sha256=_sha256_text(raw.stderr),
        stderr_excerpt=raw.stderr[:500],
    )


def run_cnf_solver(
    model: QuasiPrimalDomainModel,
    encoding: CNFEncoding,
    command: SolverCommand,
) -> VerifiedExternalModel:
    """Run a SAT command and verify/decode its returned controller model."""

    raw = _run_problem(encoding.dimacs(), ".cnf", command)
    status = parse_solver_status(raw.stdout)
    _reject_unsat_status(status)
    literals = parse_dimacs_model(raw.stdout)
    if not literals:
        raise SolverAdapterError("solver output contains no model literals")
    try:
        witness = decode_cnf_model(model, encoding, literals)
    except ValueError as error:
        raise SolverAdapterError(f"invalid SAT model: {error}") from error
    return VerifiedExternalModel(
        witness=witness,
        receipt=_receipt(
            raw,
            status=status,
            objective_cost=None,
            expected_objective_cost=None,
            solver_claimed_optimum=False,
            optimality_verified=False,
            model_literal_count=len(literals),
        ),
    )


def run_weighted_maxsat_solver(
    model: QuasiPrimalDomainModel,
    hard_encoding: CNFEncoding,
    weighted_encoding: WeightedCNFEncoding,
    command: SolverCommand,
    *,
    require_objective: bool = True,
    known_optimum_cost: int | None = None,
) -> VerifiedExternalModel:
    """Run WCNF search and verify its feasible model and objective arithmetic.

    ``objective_cost`` follows the standard weighted-MaxSAT convention: the
    sum of unsatisfied soft-clause weights.  The model's objective is checked
    exactly.  Solver-reported optimality is not independently trusted unless
    ``known_optimum_cost`` is supplied by another proof/reference computation.
    """

    if hard_encoding.variable_count != weighted_encoding.variable_count:
        raise ValueError("hard and weighted encodings use different variables")

    raw = _run_problem(weighted_encoding.wdimacs(), ".wcnf", command)
    status = parse_solver_status(raw.stdout)
    _reject_unsat_status(status)
    objective = parse_solver_objective(raw.stdout)
    if require_objective and objective is None:
        raise SolverAdapterError("weighted solver output lacks an objective line")
    literals = parse_dimacs_model(raw.stdout)
    if not literals:
        raise SolverAdapterError("weighted solver output contains no model literals")

    try:
        assignment = normalize_boolean_model(
            hard_encoding.variable_count,
            literals,
        )
        witness = decode_cnf_model(model, hard_encoding, literals)
    except ValueError as error:
        raise SolverAdapterError(f"invalid weighted model: {error}") from error

    expected_cost = sum(
        weight
        for variable, weight in weighted_encoding.soft_state_units
        if not assignment.value(variable)
    )
    if objective is not None and objective != expected_cost:
        raise SolverAdapterError(
            "solver objective disagrees with decoded model: "
            f"reported {objective}, expected {expected_cost}"
        )
    if known_optimum_cost is not None and expected_cost != known_optimum_cost:
        raise SolverAdapterError(
            "decoded objective disagrees with independently known optimum: "
            f"{expected_cost}!={known_optimum_cost}"
        )

    claimed_optimum = status is not None and "OPTIMUM" in status.upper()
    return VerifiedExternalModel(
        witness=witness,
        receipt=_receipt(
            raw,
            status=status,
            objective_cost=objective,
            expected_objective_cost=expected_cost,
            solver_claimed_optimum=claimed_optimum,
            optimality_verified=(
                known_optimum_cost is not None
                and expected_cost == known_optimum_cost
            ),
            model_literal_count=len(literals),
        ),
    )
