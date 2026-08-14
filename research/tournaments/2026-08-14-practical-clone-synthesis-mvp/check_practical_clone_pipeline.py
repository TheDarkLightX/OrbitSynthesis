#!/usr/bin/env python3
"""Deterministic gate for the practical clone-synthesis vertical slice."""

from __future__ import annotations

from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.practical import (
    game_from_model,
    game_to_model,
    synthesize_model,
    verify_certificate,
)
from orbitsynthesis.practical_examples import (
    coupling_counterexample_model,
    discriminator_policy_model,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def contains_failure(value: object, kind: str) -> bool:
    if isinstance(value, dict):
        return value.get("kind") == kind or any(
            contains_failure(child, kind) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_failure(child, kind) for child in value)
    return False


def normalized_semantics(certificate: dict[str, object]) -> dict[str, object]:
    analysis = dict(certificate["analysis"])
    analysis.pop("quasi_search", None)
    return {
        "analysis": analysis,
        "modes": certificate["modes"],
        "selected_controller": certificate["selected_controller"],
        "compilation": certificate["compilation"],
        "diagnostic_kind": (
            certificate["diagnostic"].get("kind")
            if isinstance(certificate.get("diagnostic"), dict)
            else None
        ),
    }


def roundtrip(model: dict[str, object]) -> None:
    game, initial, name = game_from_model(model)
    rebuilt = game_to_model(game, initial, name=name)
    require(rebuilt == model, "model JSON roundtrip drift")


def build_receipt(output_dir: Path | None) -> dict[str, object]:
    positive_model = discriminator_policy_model()
    negative_model = coupling_counterexample_model()
    roundtrip(positive_model)
    roundtrip(negative_model)

    positive = synthesize_model(positive_model, quasi_search="bitset_nogood")
    positive_reference = synthesize_model(positive_model, quasi_search="exhaustive")
    require(
        normalized_semantics(positive) == normalized_semantics(positive_reference),
        "positive bitset/exhaustive disagreement",
    )
    verify_certificate(positive_model, positive)

    positive_modes = positive["modes"]
    require(
        all(positive_modes[mode]["initial_realizable"] for mode in positive_modes),
        "positive hierarchy unexpectedly unrealizable",
    )
    require(
        all(positive_modes[mode]["winning_state_count"] == 3 for mode in positive_modes),
        "positive winning-domain census",
    )
    compilation = positive["compilation"]
    require(compilation["status"] == "compiled", "positive strategy not compiled")
    require(
        compilation["backend_per_output"] == ["single_discriminator"],
        "positive peephole backend drift",
    )
    require(compilation["dag"]["operation_count"] == 1, "positive operation count")
    require(compilation["dag"]["depth"] == 1, "positive depth")
    require(compilation["replay_rows"] == 27, "positive replay row count")

    negative = synthesize_model(negative_model, quasi_search="bitset_nogood")
    negative_reference = synthesize_model(negative_model, quasi_search="exhaustive")
    require(
        normalized_semantics(negative) == normalized_semantics(negative_reference),
        "negative bitset/exhaustive disagreement",
    )
    verify_certificate(negative_model, negative)

    negative_modes = negative["modes"]
    for mode in ("ordinary", "semi_primal", "demi_semi_primal"):
        require(negative_modes[mode]["initial_realizable"], f"{mode} relaxation failed")
        require(
            negative_modes[mode]["winning_state_count"] == 3,
            f"{mode} winning-domain census",
        )
    require(
        not negative_modes["quasi_primal"]["initial_realizable"],
        "negative quasi-primal false positive",
    )
    require(
        negative["compilation"]["status"] == "not_realizable",
        "negative instance reached compiler",
    )
    require(
        negative["diagnostic"]["kind"] == "groupoid_component_unsatisfiable",
        "negative diagnostic kind",
    )
    require(
        contains_failure(negative["diagnostic"], "transported_output_forbidden"),
        "negative diagnostic missed transported-output conflict",
    )

    mutated = deepcopy(positive)
    mutated["compilation"]["dag"]["nodes"][-1]["args"] = [0, 1, 0]
    mutation_rejected = False
    try:
        verify_certificate(positive_model, mutated)
    except ValueError:
        mutation_rejected = True
    require(mutation_rejected, "mutated compiled DAG certificate was accepted")

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        artifacts = {
            "positive_model.json": positive_model,
            "positive_certificate.json": positive,
            "negative_model.json": negative_model,
            "negative_certificate.json": negative,
        }
        for filename, value in artifacts.items():
            (output_dir / filename).write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

    result = {
        "schema": "orbit-synthesis/practical-clone-synthesis-gate/v1",
        "positive": {
            "model_sha256": positive["model_sha256"],
            "mode_winning_counts": {
                mode: positive_modes[mode]["winning_state_count"]
                for mode in sorted(positive_modes)
            },
            "backend": compilation["backend_per_output"],
            "operation_count": compilation["dag"]["operation_count"],
            "depth": compilation["dag"]["depth"],
            "semantic_rows": compilation["replay_rows"],
            "certificate_verified": True,
        },
        "negative": {
            "model_sha256": negative["model_sha256"],
            "relaxation_winning_counts": {
                mode: negative_modes[mode]["winning_state_count"]
                for mode in ("ordinary", "semi_primal", "demi_semi_primal")
            },
            "quasi_realizable": negative_modes["quasi_primal"]["initial_realizable"],
            "diagnostic_kind": negative["diagnostic"]["kind"],
            "transported_output_conflict": True,
            "certificate_verified": True,
        },
        "cross_checks": {
            "bitset_equals_exhaustive": True,
            "model_roundtrip": True,
            "compiled_dag_mutation_rejected": mutation_rejected,
        },
    }
    result["semantic_sha256"] = canonical_hash(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--expected", type=Path)
    args = parser.parse_args()

    receipt = build_receipt(args.artifact_dir)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.expected:
        require(receipt == json.loads(args.expected.read_text()), "receipt drift")
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
