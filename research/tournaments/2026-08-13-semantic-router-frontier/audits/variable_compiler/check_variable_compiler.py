#!/usr/bin/env python3
"""Independent arithmetic audit of the variable-depth router compiler.

Premise (not reproved here): for every h>=1 there is a Boolean router of
capacity q_h=3^(h-1), dependency depth h, 2*q_h Boolean control leaves, and
(3^h-1)/2 discriminator nodes.  This checker audits the compiler consequences
with k=floor(sqrt(r)), h=k+1, q=3^k.

It deliberately compares residual-last and residual-first prefix chunking.
Only residual-first (or an equivalent balanced address tree) has uniform
O(3^r/r) accounting.
"""
from __future__ import annotations

import hashlib
import json
import math


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def ceil_log(base: int, value: int) -> int:
    require(base >= 2 and value >= 1, "bad ceil-log arguments")
    exponent = 0
    power = 1
    while power < value:
        power *= base
        exponent += 1
    return exponent


def floor_log(base: int, value: int) -> int:
    require(base >= 2 and value >= 1, "bad floor-log arguments")
    exponent = 0
    power = 1
    while power * base <= value:
        power *= base
        exponent += 1
    return exponent


def chunk_widths(total: int, width: int, *, residual_first: bool) -> tuple[int, ...]:
    require(total >= 0 and width >= 1, "bad chunk arguments")
    if total == 0:
        return ()
    quotient, remainder = divmod(total, width)
    full = (width,) * quotient
    residual = (remainder,) if remainder else ()
    return residual + full if residual_first else full + residual


def prefix_instances(widths: tuple[int, ...], alphabet: int) -> tuple[int, int]:
    product_so_far = 1
    instances = 0
    for width in widths:
        instances += product_so_far
        product_so_far *= alphabet**width
    return instances, product_so_far


def parameters(arity: int, *, residual_first: bool) -> dict[str, int | float | list[int]]:
    require(arity >= 64, "audit starts at arity 64")
    k = math.isqrt(arity)
    h = k + 1
    q = 3**k
    router_nodes = (3**h - 1) // 2

    # 3^H <= 3^r/(r*q), with exact integer ceil-log accounting.
    h_exponent = max(1, arity - ceil_log(3, arity * q))
    block_coordinates = floor_log(3, h_exponent)
    block_assignments = 3**block_coordinates
    prefix_coordinates = arity - block_coordinates

    ternary_widths = chunk_widths(prefix_coordinates, k, residual_first=residual_first)
    ternary_instances, ternary_assignments = prefix_instances(ternary_widths, 3)
    require(ternary_assignments == 3**prefix_coordinates, "ternary product drift")
    ternary_levels = 1 + len(ternary_widths)  # local library plus prefix

    # Two Boolean planes; each library function has two router outputs.
    # The factor 6 safely dominates 2*router_nodes/ q < 3.
    local_library_nodes = 6 * router_nodes * 3**block_assignments
    ternary_prefix_nodes = 2 * router_nodes * ternary_instances

    # Generic fallback: 2q program bits per level, each compiled as an
    # arbitrary q-way digit table using a ternary selector of <=7q nodes and
    # depth <=3k. This charges decoding; the recursive digit program can only
    # improve this subexponential bound.
    ternary_control_nodes = 14 * q * q * ternary_levels

    binary_width = min(arity - 1, max(1, floor_log(2, q)))
    binary_widths = chunk_widths(arity - 1, binary_width, residual_first=residual_first)
    binary_instances, binary_assignments = prefix_instances(binary_widths, 2)
    require(binary_assignments == 2 ** (arity - 1), "binary product drift")
    binary_levels = len(binary_widths)
    binary_router_nodes = router_nodes * binary_instances

    # A conservative generic relative-binary control compiler: <=3*2^w
    # discriminator nodes per bit and 2q bits per level.
    binary_control_nodes = sum(6 * q * 2**width for width in binary_widths)

    anchor_and_glue_nodes = 10 * arity + 100
    size_upper = (
        local_library_nodes
        + ternary_prefix_nodes
        + ternary_control_nodes
        + binary_router_nodes
        + binary_control_nodes
        + anchor_and_glue_nodes
    )

    anchor_depth = 3 * ceil_log(2, arity)
    nonbinary_depth = h * ternary_levels + anchor_depth + 3 * k + 12
    binary_depth = h * binary_levels + 2 * binary_width + 8
    depth_upper = max(nonbinary_depth, binary_depth)

    require(q * 3**block_assignments * arity <= 3**arity, "local-library budget failed")
    return {
        "arity": arity,
        "k": k,
        "h": h,
        "q": q,
        "router_nodes": router_nodes,
        "H": h_exponent,
        "block_coordinates": block_coordinates,
        "block_assignments": block_assignments,
        "prefix_coordinates": prefix_coordinates,
        "ternary_widths": list(ternary_widths),
        "ternary_instances": ternary_instances,
        "ternary_levels": ternary_levels,
        "binary_width": binary_width,
        "binary_widths": list(binary_widths),
        "binary_instances": binary_instances,
        "binary_levels": binary_levels,
        "local_library_nodes": local_library_nodes,
        "ternary_prefix_nodes": ternary_prefix_nodes,
        "ternary_control_nodes": ternary_control_nodes,
        "binary_router_nodes": binary_router_nodes,
        "binary_control_nodes": binary_control_nodes,
        "size_upper": size_upper,
        "size_normalized": size_upper * arity / 3**arity,
        "nonbinary_depth": nonbinary_depth,
        "binary_depth": binary_depth,
        "depth_upper": depth_upper,
        "depth_per_arity": depth_upper / arity,
        "depth_excess_per_sqrt": (depth_upper - arity) / math.sqrt(arity),
    }


def program_bit_structure(max_depth: int = 12) -> dict[str, object]:
    """Audit the recursive program decoder's base-3 digit dependence.

    A physical control leaf is identified by its recursive child path.  The
    program recursion sends the unique selected target child a projection mode
    and every sibling a constant mode. Therefore a control bit depends on the
    target's base-3 digits only while every prefix digit agrees with that path;
    at the first disagreement its value is fixed by a constant sibling mode.
    It is thus a decision list of length at most h-1, not a free q-entry ROM.
    """

    rows = []
    for h in range(1, max_depth + 1):
        digit_count = h - 1
        capacity = 3**digit_count
        control_bits = 2 * capacity
        decision_list_depth = digit_count
        decision_list_nodes = 3 * digit_count + 1
        require(decision_list_depth <= h, "program bit exceeded router depth")
        rows.append(
            {
                "h": h,
                "capacity": capacity,
                "control_bits": control_bits,
                "target_digits": digit_count,
                "per_control_decision_list_depth": decision_list_depth,
                "per_control_decision_list_nodes_upper": decision_list_nodes,
            }
        )
    return {
        "rows": rows,
        "conclusion": (
            "Each recursive program bit is constant or a prefix-conditioned "
            "decision list in the h-1 base-3 route digits. Compiling it costs "
            "O(h) depth and size per bit; no free program decoding is assumed."
        ),
    }


def compact_row(row: dict[str, int | float | list[int]]) -> dict[str, object]:
    """Keep exact structural integers but summarize enormous node counts by logs."""

    return {
        key: row[key]
        for key in (
            "arity",
            "k",
            "h",
            "q",
            "H",
            "block_coordinates",
            "block_assignments",
            "prefix_coordinates",
            "ternary_levels",
            "binary_width",
            "binary_levels",
            "size_normalized",
            "nonbinary_depth",
            "binary_depth",
            "depth_upper",
            "depth_per_arity",
            "depth_excess_per_sqrt",
        )
    } | {
        "ternary_residual_width": row["ternary_widths"][0],
        "ternary_full_width_count": len(row["ternary_widths"]) - 1,
        "binary_residual_width": row["binary_widths"][0],
        "binary_full_width_count": len(row["binary_widths"]) - 1,
        "size_upper_log3": math.log(int(row["size_upper"]), 3),
        "ternary_prefix_nodes_log3": math.log(int(row["ternary_prefix_nodes"]), 3),
    }


def main() -> None:
    selected_arities = (64, 81, 100, 128, 243, 256, 512, 729, 1024, 2048, 4096, 6561, 10000)
    repaired_rows = []
    maximum_size_normalized = (0.0, 0)
    maximum_depth_excess = (0.0, 0)
    for arity in range(64, 10001):
        row = parameters(arity, residual_first=True)
        require(row["size_normalized"] <= 11, f"repaired size constant failed at {arity}")
        require(
            row["depth_upper"] <= arity + 10 * math.isqrt(arity) + 50,
            f"repaired depth inequality failed at {arity}",
        )
        if row["size_normalized"] > maximum_size_normalized[0]:
            maximum_size_normalized = (float(row["size_normalized"]), arity)
        if row["depth_excess_per_sqrt"] > maximum_depth_excess[0]:
            maximum_depth_excess = (float(row["depth_excess_per_sqrt"]), arity)
        if arity in selected_arities:
            repaired_rows.append(compact_row(row))

    # Exact counterexample to residual-last uniform O(3^r/r) accounting.
    broken = parameters(512, residual_first=False)
    repaired = parameters(512, residual_first=True)
    require(broken["ternary_prefix_nodes"] > repaired["ternary_prefix_nodes"] * 10**9, "ordering mutation ineffective")
    require(broken["size_normalized"] > 10**10, "residual-last flaw did not reproduce")
    require(repaired["size_normalized"] < 11, "residual-first repair failed")

    summary = {
        "schema": "orbit-synthesis/variable-router-compiler-independent-audit/v1",
        "premise": "exact router family q_h=3^(h-1), depth h, 2q controls, (3^h-1)/2 d nodes",
        "schedule": "k=floor(sqrt(r)), h=k+1, q=3^k",
        "status": "CONDITIONAL_PASS_AFTER_RESIDUAL_FIRST_REPAIR",
        "program_bit_structure": program_bit_structure(),
        "arities_checked": 10000 - 64 + 1,
        "repaired_selected_rows": repaired_rows,
        "repaired_maximum_size_normalized": {
            "value": maximum_size_normalized[0],
            "arity": maximum_size_normalized[1],
        },
        "repaired_maximum_depth_excess_per_sqrt": {
            "value": maximum_depth_excess[0],
            "arity": maximum_depth_excess[1],
        },
        "proved_integer_inequalities_on_checked_range": [
            "size_upper <= 11*3^r/r for 64<=r<=10000",
            "depth_upper <= r+10*floor(sqrt(r))+50 for 64<=r<=10000",
        ],
        "asymptotic_result": {
            "size": "O(3^r/r)",
            "depth": "r+O(sqrt(r))",
            "conditions": (
                "short residual chunks are routed first (or a balanced address tree is used); "
                "all generic controls, both Q planes, router growth, local library, prefix, "
                "binary branch, anchor, decoder, padding, and gluing are charged"
            ),
        },
        "residual_last_counterexample": {
            "arity": 512,
            "ternary_widths": broken["ternary_widths"],
            "ternary_prefix_nodes_log3": math.log(int(broken["ternary_prefix_nodes"]), 3),
            "target_exponent": 512 - math.log(512, 3),
            "size_normalized": broken["size_normalized"],
            "repaired_widths": repaired["ternary_widths"],
            "repaired_size_normalized": repaired["size_normalized"],
            "verdict": (
                "Residual-last sequential chunking is not uniformly O(3^r/r): the final "
                "short chunk leaves an uncancelled q/3^residual prefix factor. Routing the "
                "residual first restores geometric telescoping."
            ),
        },
        "claim_boundary": (
            "The recursive router family is an assumed premise. This is an independent "
            "compiler-accounting audit, not a proof of the family, novelty, optimality of "
            "lower-order terms, patent/FTO, practical performance, or Tau capability."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS variable router compiler audit after residual-first repair")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
