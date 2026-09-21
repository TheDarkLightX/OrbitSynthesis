#!/usr/bin/env python3
"""Exact small checks for conservative Quackenbush-Q term-operation counts."""
from __future__ import annotations

import hashlib
import json
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.orbit_term_compile import (
    Q,
    compile_orbit_coordinate_selector,
    complement,
    evaluate,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def formula_exponents(arity: int) -> tuple[int, int]:
    require(arity >= 1, "arity must be positive")
    exponent_two = 5 * 2 ** (arity - 1) - 5
    exponent_three = 3**arity - 3 * 2**arity + 3
    return exponent_two, exponent_three


def conservative_term_count(arity: int) -> int:
    exponent_two, exponent_three = formula_exponents(arity)
    return 2**exponent_two * 3**exponent_three


def direct_category_counts(arity: int) -> dict[str, int]:
    points = tuple(product(Q, repeat=arity))
    binary_nonconstant = sum(
        1
        for point in product((0, 1), repeat=arity)
        if point[0] == 0 and len(set(point)) == 2
    )
    nonbinary_two_value = sum(
        1 for point in points if 2 in point and len(set(point)) == 2
    )
    all_three = sum(1 for point in points if len(set(point)) == 3)
    return {
        "binary_nonconstant_complement_orbits": binary_nonconstant,
        "nonbinary_two_value_tuples": nonbinary_two_value,
        "all_three_value_tuples": all_three,
    }


def enumerate_semantic_functions(arity: int):
    """Enumerate conservative complement-equivariant functions at small arity."""

    binary_representatives = tuple(
        point for point in product((0, 1), repeat=arity) if point[0] == 0
    )
    nonbinary = tuple(point for point in product(Q, repeat=arity) if 2 in point)
    option_sets = tuple(tuple(sorted(set(point))) for point in binary_representatives)
    option_sets += tuple(tuple(sorted(set(point))) for point in nonbinary)
    for choices in product(*option_sets):
        values: dict[tuple[int, ...], int] = {}
        offset = 0
        for point in binary_representatives:
            value = choices[offset]
            values[point] = value
            values[complement(point)] = 1 - value
            offset += 1
        for point in nonbinary:
            values[point] = choices[offset]
            offset += 1
        yield values


def selector_for_function(
    values: dict[tuple[int, ...], int],
) -> dict[tuple[int, ...], int]:
    return {
        point: next(index for index, value in enumerate(point) if value == output)
        for point, output in values.items()
    }


def dag_description_lower_bound(arity: int, function_count: int) -> int:
    """Pigeonhole lower bound on worst-case operation nodes in a term DAG."""

    # With t topologically ordered operation nodes, node i has at most
    # (r+i)+(r+i)^3 choices (u or d plus predecessor choices), and the root
    # has r+t choices. This deliberately overcounts malformed/unreachable and
    # extensionally duplicate DAGs, so it is safe for a lower bound.
    descriptions_at_most = arity
    if descriptions_at_most >= function_count:
        return 0
    product_of_node_choices = 1
    operation_nodes = 0
    while descriptions_at_most < function_count:
        prior_nodes = arity + operation_nodes
        product_of_node_choices *= prior_nodes + prior_nodes**3
        operation_nodes += 1
        descriptions_at_most += (
            arity + operation_nodes
        ) * product_of_node_choices
    return operation_nodes


def main() -> None:
    exhaustive_rows = []
    for arity in (1, 2):
        seen: set[tuple[int, ...]] = set()
        points = tuple(product(Q, repeat=arity))
        for values in enumerate_semantic_functions(arity):
            output_table = tuple(values[point] for point in points)
            require(output_table not in seen, "semantic enumerator duplicated a function")
            seen.add(output_table)
            selector = selector_for_function(values)
            term = compile_orbit_coordinate_selector(arity, selector)
            for point in points:
                require(
                    evaluate(term, point) == values[point],
                    f"compiled semantic function disagrees at {point}",
                )
        expected = conservative_term_count(arity)
        require(len(seen) == expected, f"exact function count failed at {arity}")
        exhaustive_rows.append(
            {
                "arity": arity,
                "functions_enumerated_and_compiled": len(seen),
                "expected_functions": expected,
            }
        )

    count_rows = []
    for arity in range(1, 9):
        direct = direct_category_counts(arity)
        exponent_two, exponent_three = formula_exponents(arity)
        require(
            direct["binary_nonconstant_complement_orbits"]
            == 2 ** (arity - 1) - 1,
            f"binary orbit count failed at {arity}",
        )
        require(
            direct["nonbinary_two_value_tuples"] == 2 * (2**arity - 2),
            f"two-value nonbinary count failed at {arity}",
        )
        require(
            direct["all_three_value_tuples"]
            == 3**arity - 3 * 2**arity + 3,
            f"three-value count failed at {arity}",
        )
        count = conservative_term_count(arity)
        count_rows.append(
            {
                "arity": arity,
                **direct,
                "formula_base_2_exponent": exponent_two,
                "formula_base_3_exponent": exponent_three,
                "count_decimal_digits": len(str(count)),
                "count_log2_floor": count.bit_length() - 1,
                "dag_operation_nodes_pigeonhole_lower_bound": (
                    dag_description_lower_bound(arity, count)
                ),
            }
        )

    r3_count = conservative_term_count(3)
    require(r3_count == 23_887_872, "arity-3 closed form regression")
    r3_all_three = formula_exponents(3)[1]
    forgot_binary_quotient = (
        2 ** (3 * (2**3 - 2)) * 3**r3_all_three
    )
    gave_all_two_three_choices = 3 * (
        2 ** formula_exponents(3)[0] * 3**r3_all_three
    )
    mutation_checks = {
        "forgetting_binary_orbit_quotient_changes_r3_count": (
            forgot_binary_quotient != r3_count
        ),
        "giving_all_two_tuple_three_choices_changes_r3_count": (
            gave_all_two_three_choices != r3_count
        ),
    }
    require(all(mutation_checks.values()), "count mutation was not detected")

    summary = {
        "schema": "orbit-synthesis/quasiprimal-conservative-term-count/v1",
        "algebra": "Quackenbush Q=({0,1,2};d,u)",
        "exact_formula": (
            "2^(5*2^(r-1)-5) * 3^(3^r-3*2^r+3), for r>=1"
        ),
        "exhaustive_rows": exhaustive_rows,
        "count_rows": count_rows,
        "arity_3_exact_count": r3_count,
        "mutation_checks": mutation_checks,
        "claim_boundary": (
            "The finite checks validate category counts, small exhaustive semantics, "
            "compilation, and a syntax-description lower-bound calculation. The all-r "
            "count and asymptotic lower bound rest on the separate manuscript proof."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS quasi-primal conservative term count")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
