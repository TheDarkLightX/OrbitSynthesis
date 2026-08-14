"""Exact optimizer for balanced recursive-library group counts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def balanced_table_sum(rows: int, groups: int) -> tuple[int, int, int]:
    quotient, remainder = divmod(rows, groups)
    require(quotient >= 1, "group count exceeds rows")
    value = (groups + remainder) * 2**quotient
    return value, quotient, remainder


def variable_cost(rows: int, width: int, prefix_capacity: int,
                  groups: int) -> tuple[int, int, int, int]:
    table_sum, quotient, remainder = balanced_table_sum(rows, groups)
    value = (
        4 * width * table_sum
        + 5 * width
        + groups * (3 * prefix_capacity - 1)
    )
    return value, table_sum, quotient, remainder


def endpoint_optimum(rows: int, width: int,
                     prefix_capacity: int) -> dict[str, int]:
    """Minimize over all groups by testing quotient-interval endpoints."""
    best = None
    left = 1
    intervals = 0
    while left <= rows:
        quotient = rows // left
        right = rows // quotient
        intervals += 1
        endpoints = (left,) if left == right else (left, right)
        for groups in endpoints:
            value, table_sum, checked_quotient, remainder = variable_cost(
                rows, width, prefix_capacity, groups
            )
            require(checked_quotient == quotient, "quotient interval drift")
            key = (value, groups)
            if best is None or key < best[0]:
                best = (
                    key,
                    table_sum,
                    quotient,
                    remainder,
                )
        left = right + 1

    require(best is not None, "empty optimizer")
    (value, groups), table_sum, quotient, remainder = best
    return {
        "g": groups,
        "variable_cost": value,
        "table_sum": table_sum,
        "row_quotient": quotient,
        "row_remainder": remainder,
        "max_rows": quotient + (1 if remainder else 0),
        "intervals": intervals,
    }


def audit_endpoint_optimizer() -> dict[str, object]:
    checked = 0
    for rows in range(1, 201):
        for width in range(1, 5):
            for prefix_capacity in (1, 3, 9, 27, 81):
                result = endpoint_optimum(rows, width, prefix_capacity)
                brute = min(
                    (
                        variable_cost(rows, width, prefix_capacity, groups)[0],
                        groups,
                    )
                    for groups in range(1, rows + 1)
                )
                require(
                    (result["variable_cost"], result["g"]) == brute,
                    "endpoint optimizer mismatch",
                )
                checked += 1

    mutation = None
    for rows in range(2, 80):
        for width in range(1, 5):
            for prefix_capacity in (3, 9, 27, 81):
                correct = endpoint_optimum(rows, width, prefix_capacity)
                lower_only = []
                left = 1
                while left <= rows:
                    quotient = rows // left
                    right = rows // quotient
                    lower_only.append(
                        (
                            variable_cost(
                                rows, width, prefix_capacity, left
                            )[0],
                            left,
                        )
                    )
                    left = right + 1
                wrong = min(lower_only)
                if wrong != (correct["variable_cost"], correct["g"]):
                    mutation = {
                        "N": rows,
                        "t": width,
                        "P": prefix_capacity,
                        "correct_g": correct["g"],
                        "correct": correct["variable_cost"],
                        "lower_only_g": wrong[1],
                        "lower_only": wrong[0],
                    }
                    break
            if mutation is not None:
                break
        if mutation is not None:
            break
    require(mutation is not None, "lower-endpoint mutation ineffective")

    return {
        "bruteforce_instances": checked,
        "identity": "E_N(g)=(N-(q-1)g)2^q on floor(N/g)=q",
        "method": "test both endpoints of every quotient interval",
        "mutation_lower_endpoints_only": mutation,
    }
