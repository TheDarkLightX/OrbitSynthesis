"""External exact-optimization adapters for OrbitSynthesis WCNF models.

OrbitSynthesis treats an external optimizer as an untrusted search oracle.  A
returned assignment is normalized, checked against every hard clause, decoded
into the selected state domain, and replayed into one complete compatible
controller table.  The model/controller certificate is therefore checked even
when the backend itself is optional or out of process.

The adapters currently support:

* SciPy's HiGHS MILP wrapper (optional dependency);
* PySAT RC2 weighted MaxSAT (optional dependency); and
* arbitrary Open-WBO-style command-line solvers through a no-shell subprocess
  interface.

The assignment is a checkable feasibility certificate.  Global optimality and
infeasibility remain backend claims unless a proof-producing solver, bounded
exhaustive check, native OrbitSynthesis replay, or another independent backend
is used as an additional authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from typing import Iterable, Mapping, Sequence

from .domain_model import (
    CNFEncoding,
    CompiledDomainWitness,
    QuasiPrimalDomainModel,
    WeightedCNFEncoding,
)
from .domain_solver import (
    ParsedBooleanModel,
    decode_cnf_model,
    normalize_boolean_model,
    parse_dimacs_model,
)

State = tuple[object, ...]
_MAX_EXACT_FLOAT_INTEGER = (1 << 53) - 1


class ExternalOptimizationError(RuntimeError):
    """An external backend failed, timed out, or returned invalid evidence."""


@dataclass(frozen=True)
class ParsedMaxSATOutput:
    """Normalized MaxSAT Evaluation/Open-WBO style output."""

    status: str
    reported_cost: int | None
    model_literals: tuple[int, ...]


@dataclass(frozen=True)
class ExternalOptimizationResult:
    """An external result after OrbitSynthesis model-certificate checking.

    ``certificate_verified`` concerns the returned assignment and reconstructed
    controller.  ``optimality_authority`` records where the optimum/infeasible
    claim came from; it is deliberately separate because a model by itself is
    not a compact proof that no better model exists.
    """

    backend: str
    status: str
    certificate_verified: bool
    optimality_authority: str
    witness: CompiledDomainWitness | None
    model_literals: tuple[int, ...]
    soft_reward: int | None
    unsatisfied_cost: int | None
    reported_cost: int | None
    signed_utility: int | None
    wall_seconds: float
    metadata_items: tuple[tuple[str, object], ...] = ()

    @property
    def metadata(self) -> dict[str, object]:
        return dict(self.metadata_items)

    @property
    def semantic_sha256(self) -> str:
        """Hash semantic output while excluding machine-dependent timing."""

        payload = {
            "backend": self.backend,
            "status": self.status,
            "certificate_verified": self.certificate_verified,
            "optimality_authority": self.optimality_authority,
            "domain": (
                [list(state) for state in sorted(self.witness.domain, key=repr)]
                if self.witness is not None
                else None
            ),
            "component_choices": (
                list(self.witness.component_choices)
                if self.witness is not None
                else None
            ),
            "model_literals": list(self.model_literals),
            "soft_reward": self.soft_reward,
            "unsatisfied_cost": self.unsatisfied_cost,
            "reported_cost": self.reported_cost,
            "signed_utility": self.signed_utility,
        }
        return hashlib.sha256(
            json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                default=repr,
            ).encode()
        ).hexdigest()


def parse_maxsat_output(text: str) -> ParsedMaxSATOutput:
    """Parse conventional ``s``, ``o`` and ``v`` MaxSAT output lines."""

    status = "unknown"
    reported_cost: int | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        marker = line[:1].lower()
        if marker == "s":
            body = line[1:].strip().upper()
            if "UNSATISFIABLE" in body:
                status = "infeasible"
            elif "OPTIMUM" in body:
                status = "optimal"
            elif "SATISFIABLE" in body:
                status = "satisfiable"
            elif "UNKNOWN" in body:
                status = "unknown"
        elif marker == "o":
            fields = line[1:].strip().split()
            if not fields:
                raise ExternalOptimizationError("empty MaxSAT objective line")
            try:
                reported_cost = int(fields[0])
            except ValueError as error:
                raise ExternalOptimizationError(
                    f"invalid MaxSAT objective line: {line!r}"
                ) from error

    return ParsedMaxSATOutput(
        status=status,
        reported_cost=reported_cost,
        model_literals=parse_dimacs_model(text),
    )


def _validate_encodings(cnf: CNFEncoding, wcnf: WeightedCNFEncoding) -> None:
    if cnf.variable_count != wcnf.variable_count:
        raise ValueError("CNF and WCNF variable counts disagree")
    if cnf.clauses != wcnf.hard_clauses:
        raise ValueError("WCNF hard clauses do not match the decoding CNF")


def _full_model(variable_count: int, literals: Iterable[int]) -> tuple[int, ...]:
    assignment = normalize_boolean_model(variable_count, literals)
    return tuple(
        variable if assignment.value(variable) else -variable
        for variable in range(1, variable_count + 1)
    )


def _literal_satisfied(literal: int, assignment: ParsedBooleanModel) -> bool:
    return assignment.value(abs(literal)) == (literal > 0)


def weighted_soft_reward(
    encoding: WeightedCNFEncoding,
    literals: Iterable[int],
) -> int:
    assignment = normalize_boolean_model(encoding.variable_count, literals)
    return sum(
        weight
        for literal, weight in encoding.soft_state_units
        if _literal_satisfied(literal, assignment)
    )


def weighted_unsatisfied_cost(
    encoding: WeightedCNFEncoding,
    literals: Iterable[int],
) -> int:
    total = sum(weight for _literal, weight in encoding.soft_state_units)
    return total - weighted_soft_reward(encoding, literals)


def domain_signed_utility(
    states: Sequence[State],
    domain: Iterable[State],
    state_weights: Mapping[State, int] | None = None,
    *,
    default_weight: int = 1,
) -> int:
    if not isinstance(default_weight, int):
        raise TypeError("default_weight must be an integer")
    supplied = {} if state_weights is None else dict(state_weights)
    unknown = set(supplied) - set(states)
    if unknown:
        raise ValueError(f"state weight outside model: {min(unknown, key=repr)!r}")
    if any(not isinstance(weight, int) for weight in supplied.values()):
        raise TypeError("all state weights must be integers")
    selected = frozenset(domain)
    return sum(
        supplied.get(state, default_weight)
        for state in states
        if state in selected
    )


def _checked_result(
    *,
    backend: str,
    model: QuasiPrimalDomainModel,
    cnf: CNFEncoding,
    wcnf: WeightedCNFEncoding,
    literals: Iterable[int],
    reported_cost: int | None,
    wall_seconds: float,
    state_weights: Mapping[State, int] | None,
    default_weight: int,
    status: str,
    optimality_authority: str,
    metadata: Mapping[str, object] | None = None,
) -> ExternalOptimizationResult:
    _validate_encodings(cnf, wcnf)
    full = _full_model(wcnf.variable_count, literals)
    try:
        witness = decode_cnf_model(model, cnf, full)
    except (TypeError, ValueError) as error:
        raise ExternalOptimizationError(
            f"backend assignment failed OrbitSynthesis certificate replay: {error}"
        ) from error
    reward = weighted_soft_reward(wcnf, full)
    cost = sum(weight for _literal, weight in wcnf.soft_state_units) - reward
    if reported_cost is not None and reported_cost != cost:
        raise ExternalOptimizationError(
            f"solver reported cost {reported_cost}, certificate has cost {cost}"
        )
    utility = domain_signed_utility(
        model.states,
        witness.domain,
        state_weights,
        default_weight=default_weight,
    )
    return ExternalOptimizationResult(
        backend=backend,
        status=status,
        certificate_verified=True,
        optimality_authority=optimality_authority,
        witness=witness,
        model_literals=full,
        soft_reward=reward,
        unsatisfied_cost=cost,
        reported_cost=reported_cost,
        signed_utility=utility,
        wall_seconds=wall_seconds,
        metadata_items=tuple(sorted((metadata or {}).items())),
    )


def solve_weighted_cnf_command(
    model: QuasiPrimalDomainModel,
    cnf: CNFEncoding,
    wcnf: WeightedCNFEncoding,
    command: Sequence[str],
    *,
    timeout: float | None = 60.0,
    require_optimum: bool = True,
    require_reported_cost: bool = True,
    state_weights: Mapping[State, int] | None = None,
    default_weight: int = 1,
    env: Mapping[str, str] | None = None,
    cwd: str | os.PathLike[str] | None = None,
    accepted_returncodes: Iterable[int] = (0,),
) -> ExternalOptimizationResult:
    """Run an Open-WBO-style executable without invoking a shell.

    ``{wcnf}`` or ``{input}`` in any command argument is replaced by the
    temporary WCNF path.  When no placeholder is present, the path is appended.
    The returned model is always decoded and checked before it is exposed.
    """

    _validate_encodings(cnf, wcnf)
    if not command:
        raise ValueError("external MaxSAT command must be nonempty")
    accepted = frozenset(int(code) for code in accepted_returncodes)
    if not accepted:
        raise ValueError("accepted_returncodes must be nonempty")

    with tempfile.TemporaryDirectory(prefix="orbit-maxsat-") as directory:
        input_path = Path(directory) / "instance.wcnf"
        input_path.write_text(wcnf.wdimacs(), encoding="utf-8")
        rendered: list[str] = []
        replaced = False
        for argument in command:
            value = str(argument)
            if "{wcnf}" in value or "{input}" in value:
                value = value.replace("{wcnf}", str(input_path))
                value = value.replace("{input}", str(input_path))
                replaced = True
            rendered.append(value)
        if not replaced:
            rendered.append(str(input_path))

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                rendered,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=(None if env is None else {**os.environ, **dict(env)}),
            )
        except subprocess.TimeoutExpired as error:
            raise ExternalOptimizationError(
                f"external MaxSAT solver timed out after {timeout} seconds"
            ) from error
        except OSError as error:
            raise ExternalOptimizationError(
                f"could not start external MaxSAT solver: {error}"
            ) from error
        elapsed = time.perf_counter() - started

        if completed.returncode not in accepted:
            raise ExternalOptimizationError(
                "external MaxSAT solver exited with code "
                f"{completed.returncode}: {completed.stderr.strip()}"
            )
        parsed = parse_maxsat_output(completed.stdout)
        sanitized_command = tuple(
            argument.replace(str(input_path), "<wcnf>")
            for argument in rendered
        )
        metadata = {
            "command": sanitized_command,
            "returncode": completed.returncode,
            "stdout_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest(),
            "stderr_sha256": hashlib.sha256(completed.stderr.encode()).hexdigest(),
        }

        if parsed.status == "infeasible":
            return ExternalOptimizationResult(
                backend="command",
                status="infeasible",
                certificate_verified=False,
                optimality_authority="backend_status",
                witness=None,
                model_literals=(),
                soft_reward=None,
                unsatisfied_cost=None,
                reported_cost=parsed.reported_cost,
                signed_utility=None,
                wall_seconds=elapsed,
                metadata_items=tuple(sorted(metadata.items())),
            )
        if require_optimum and parsed.status != "optimal":
            raise ExternalOptimizationError(
                f"solver did not report an optimum: status={parsed.status!r}"
            )
        if require_reported_cost and parsed.reported_cost is None:
            raise ExternalOptimizationError("solver returned no objective-cost line")
        if not parsed.model_literals:
            raise ExternalOptimizationError("solver returned no model literals")
        return _checked_result(
            backend="command",
            model=model,
            cnf=cnf,
            wcnf=wcnf,
            literals=parsed.model_literals,
            reported_cost=parsed.reported_cost,
            wall_seconds=elapsed,
            state_weights=state_weights,
            default_weight=default_weight,
            status=parsed.status,
            optimality_authority=(
                "backend_status" if parsed.status == "optimal" else "not_claimed"
            ),
            metadata=metadata,
        )


def solve_weighted_cnf_highs(
    model: QuasiPrimalDomainModel,
    cnf: CNFEncoding,
    wcnf: WeightedCNFEncoding,
    *,
    state_weights: Mapping[State, int] | None = None,
    default_weight: int = 1,
    time_limit: float | None = None,
) -> ExternalOptimizationResult:
    """Solve the WCNF through SciPy's deterministic HiGHS MILP wrapper.

    HiGHS uses floating-point coefficient storage.  To retain exact integer
    objective comparison, this adapter rejects objective magnitudes above the
    largest integer exactly representable by binary64.
    """

    _validate_encodings(cnf, wcnf)
    try:
        import numpy as np
        from scipy.optimize import Bounds, LinearConstraint, milp
        from scipy.sparse import csc_array
    except ImportError as error:
        raise ExternalOptimizationError(
            "SciPy with scipy.optimize.milp is required for the HiGHS backend"
        ) from error

    total_soft_weight = sum(weight for _literal, weight in wcnf.soft_state_units)
    if total_soft_weight > _MAX_EXACT_FLOAT_INTEGER:
        raise ExternalOptimizationError(
            "HiGHS adapter requires total soft weight <= 2^53-1 for exact "
            "objective replay; use an integer MaxSAT backend for larger weights"
        )

    variable_count = wcnf.variable_count
    rows: list[int] = []
    columns: list[int] = []
    data: list[float] = []
    lower: list[float] = []
    for row_index, clause in enumerate(wcnf.hard_clauses):
        if not clause:
            return ExternalOptimizationResult(
                backend="highs",
                status="infeasible",
                certificate_verified=False,
                optimality_authority="backend_status",
                witness=None,
                model_literals=(),
                soft_reward=None,
                unsatisfied_cost=None,
                reported_cost=None,
                signed_utility=None,
                wall_seconds=0.0,
            )
        coefficients: dict[int, int] = {}
        negative_count = 0
        for literal in clause:
            variable = abs(literal)
            if not 1 <= variable <= variable_count:
                raise ValueError(f"hard-clause variable outside model: {literal}")
            coefficient = 1 if literal > 0 else -1
            negative_count += int(literal < 0)
            coefficients[variable - 1] = coefficients.get(variable - 1, 0) + coefficient
        for column, coefficient in coefficients.items():
            if coefficient:
                rows.append(row_index)
                columns.append(column)
                data.append(float(coefficient))
        lower.append(float(1 - negative_count))

    objective = np.zeros(variable_count, dtype=float)
    positive_constant = 0
    for literal, weight in wcnf.soft_state_units:
        variable = abs(literal)
        if not 1 <= variable <= variable_count:
            raise ValueError(f"soft-clause variable outside model: {literal}")
        if weight <= 0:
            raise ValueError("soft weights must be positive")
        if literal > 0:
            objective[variable - 1] -= weight
            positive_constant += weight
        else:
            objective[variable - 1] += weight

    if wcnf.hard_clauses:
        matrix = csc_array(
            (data, (rows, columns)),
            shape=(len(wcnf.hard_clauses), variable_count),
        )
        constraints = LinearConstraint(
            matrix,
            np.asarray(lower, dtype=float),
            np.full(len(lower), np.inf),
        )
    else:
        constraints = ()

    options: dict[str, object] = {"presolve": True, "mip_rel_gap": 0.0}
    if time_limit is not None:
        options["time_limit"] = float(time_limit)
    started = time.perf_counter()
    result = milp(
        c=objective,
        integrality=np.ones(variable_count, dtype=int),
        bounds=Bounds(np.zeros(variable_count), np.ones(variable_count)),
        constraints=constraints,
        options=options,
    )
    elapsed = time.perf_counter() - started

    if result.status == 2:
        return ExternalOptimizationResult(
            backend="highs",
            status="infeasible",
            certificate_verified=False,
            optimality_authority="backend_status",
            witness=None,
            model_literals=(),
            soft_reward=None,
            unsatisfied_cost=None,
            reported_cost=None,
            signed_utility=None,
            wall_seconds=elapsed,
            metadata_items=(("message", str(result.message)),),
        )
    if result.status != 0 or result.x is None:
        raise ExternalOptimizationError(
            f"HiGHS did not report an optimum: status={result.status}, "
            f"message={result.message}"
        )

    rounded = np.rint(result.x).astype(int)
    if rounded.size and np.max(np.abs(result.x - rounded)) > 1e-6:
        raise ExternalOptimizationError("HiGHS returned a nonintegral Boolean model")
    literals = tuple(
        index + 1 if value else -(index + 1)
        for index, value in enumerate(rounded)
    )
    exact_cost = weighted_unsatisfied_cost(wcnf, literals)
    milp_cost = int(round(float(result.fun) + positive_constant))
    if exact_cost != milp_cost:
        raise ExternalOptimizationError(
            f"HiGHS objective mismatch: milp={milp_cost}, exact={exact_cost}"
        )
    metadata = {
        "message": str(result.message),
        "mip_node_count": int(getattr(result, "mip_node_count", 0) or 0),
        "mip_gap": float(getattr(result, "mip_gap", 0.0) or 0.0),
    }
    return _checked_result(
        backend="highs",
        model=model,
        cnf=cnf,
        wcnf=wcnf,
        literals=literals,
        reported_cost=milp_cost,
        wall_seconds=elapsed,
        state_weights=state_weights,
        default_weight=default_weight,
        status="optimal",
        optimality_authority="backend_status",
        metadata=metadata,
    )


def solve_weighted_cnf_pysat_rc2(
    model: QuasiPrimalDomainModel,
    cnf: CNFEncoding,
    wcnf: WeightedCNFEncoding,
    *,
    state_weights: Mapping[State, int] | None = None,
    default_weight: int = 1,
    solver: str = "g3",
) -> ExternalOptimizationResult:
    """Solve through PySAT's RC2 backend when ``python-sat`` is installed."""

    _validate_encodings(cnf, wcnf)
    try:
        from pysat.examples.rc2 import RC2
        from pysat.formula import WCNF
    except ImportError as error:
        raise ExternalOptimizationError(
            "python-sat is required for the PySAT RC2 backend"
        ) from error

    formula = WCNF()
    for clause in wcnf.hard_clauses:
        formula.append(list(clause))
    for literal, weight in wcnf.soft_state_units:
        formula.append([literal], weight=weight)

    started = time.perf_counter()
    with RC2(formula, solver=solver) as optimizer:
        literals = optimizer.compute()
        reported_cost = optimizer.cost
    elapsed = time.perf_counter() - started
    if literals is None:
        return ExternalOptimizationResult(
            backend="pysat-rc2",
            status="infeasible",
            certificate_verified=False,
            optimality_authority="backend_status",
            witness=None,
            model_literals=(),
            soft_reward=None,
            unsatisfied_cost=None,
            reported_cost=None,
            signed_utility=None,
            wall_seconds=elapsed,
            metadata_items=(("solver", solver),),
        )
    return _checked_result(
        backend="pysat-rc2",
        model=model,
        cnf=cnf,
        wcnf=wcnf,
        literals=literals,
        reported_cost=int(reported_cost),
        wall_seconds=elapsed,
        state_weights=state_weights,
        default_weight=default_weight,
        status="optimal",
        optimality_authority="backend_status",
        metadata={"solver": solver},
    )
