#!/usr/bin/env python3
"""No-import reconstruction of the structural benchmark authorities."""

from __future__ import annotations

import hashlib
from itertools import product
import json

Q = (0, 1, 2)
B = (0, 1)


def complement(state):
    return tuple(1 - value for value in state)


def complement_pairs(state_arity):
    seen = set()
    pairs = []
    for state in product(B, repeat=state_arity):
        if state in seen:
            continue
        other = complement(state)
        seen.add(state)
        seen.add(other)
        pairs.append((state, other))
    return tuple(pairs)


def antichain_row(state_arity):
    states = tuple(product(Q, repeat=state_arity))
    pairs = complement_pairs(state_arity)
    live, dead = pairs[0]
    variable_pairs = pairs[2:]
    variable_states = {
        state for pair in variable_pairs for state in pair
    }
    common = frozenset(states) - {dead} - variable_states
    maxima = tuple(
        common
        | frozenset(
            pair[choice]
            for pair, choice in zip(variable_pairs, orientation, strict=True)
        )
        for orientation in product((0, 1), repeat=len(variable_pairs))
    )
    expected_count = 1 << (2 ** (state_arity - 1) - 2)
    expected_size = 3**state_arity - 2 ** (state_arity - 1) + 1
    if len(maxima) != expected_count:
        raise AssertionError("antichain count")
    if any(len(domain) != expected_size for domain in maxima):
        raise AssertionError("antichain size")
    if any(dead in domain for domain in maxima):
        raise AssertionError("dead state")
    if any(
        len(domain & frozenset(pair)) != 1
        for domain in maxima
        for pair in variable_pairs
    ):
        raise AssertionError("one-per-pair geometry")

    weights = {state: 1 for state in states}
    for index, (preferred, _alternate) in enumerate(variable_pairs):
        weights[preferred] += 1 << (index + 1)
    scored = tuple(
        (sum(weights[state] for state in domain), domain)
        for domain in maxima
    )
    best = max(score for score, _domain in scored)
    optimum = tuple(domain for score, domain in scored if score == best)
    preferred = common | frozenset(pair[0] for pair in variable_pairs)
    if optimum != (preferred,):
        raise AssertionError("antichain weighted optimum")
    return {
        "state_arity": state_arity,
        "states": len(states),
        "orientation_variables": len(variable_pairs),
        "maximal_domains": len(maxima),
        "maximal_domain_size": expected_size,
        "preferred_score": best,
        "preferred_domain_sha256": hashlib.sha256(
            json.dumps(
                [list(state) for state in sorted(preferred)],
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
    }


# Generic principal witness specialized independently to Quackenbush Q.
SOURCE_OUTPUT_ZERO = (0, 1, 0, 0)
SOURCE_OUTPUT_ONE = (0, 1, 0, 1)
SOURCE_STATE = (0, 1, 1, 0)
TARGET_OUTPUT_ZERO = complement(SOURCE_OUTPUT_ZERO)
TARGET_OUTPUT_ONE = complement(SOURCE_OUTPUT_ONE)
TARGET_STATE = complement(SOURCE_STATE)
SOURCE_OBSERVATION = SOURCE_STATE + (0,)
TARGET_OBSERVATION = TARGET_STATE + (1,)
DEAD_OBSERVATIONS = {
    SOURCE_OUTPUT_ONE + (2,),
    TARGET_OUTPUT_ZERO + (2,),
}
CRITICAL = {
    SOURCE_OBSERVATION: {SOURCE_OUTPUT_ZERO, SOURCE_OUTPUT_ONE},
    TARGET_OBSERVATION: {TARGET_OUTPUT_ZERO, TARGET_OUTPUT_ONE},
}
LEFT = frozenset((SOURCE_STATE, SOURCE_OUTPUT_ZERO))
RIGHT = frozenset((TARGET_STATE, TARGET_OUTPUT_ONE))
UNION = LEFT | RIGHT
STATES4 = tuple(product(Q, repeat=4))
BINARY_STATES4 = tuple(product(B, repeat=4))
BINARY_OBSERVATIONS5 = tuple(product(B, repeat=5))


def principal_safe(state, input_value, output):
    observation = state + (input_value,)
    if observation in DEAD_OBSERVATIONS:
        return False
    if observation in CRITICAL:
        return output in CRITICAL[observation]
    return True


def principal_domain_feasible(domain):
    domain = frozenset(domain)

    # Observations containing 2 form singleton groupoid components.  Their
    # generated subalgebra is Q, so a live state needs one safe output in the
    # candidate domain.
    for state in domain:
        for input_value in Q:
            observation = state + (input_value,)
            if 2 in observation and not any(
                output in domain
                and principal_safe(state, input_value, output)
                for output in STATES4
            ):
                return False

    # Binary observations occur in complement pairs.  One binary output fixes
    # the complementary output at the paired observation.
    seen = set()
    for observation in BINARY_OBSERVATIONS5:
        if observation in seen:
            continue
        paired = complement(observation)
        seen.add(observation)
        seen.add(paired)
        state, input_value = observation[:4], observation[4]
        paired_state, paired_input = paired[:4], paired[4]
        if not any(
            (
                state not in domain
                or (
                    output in domain
                    and principal_safe(state, input_value, output)
                )
            )
            and (
                paired_state not in domain
                or (
                    complement(output) in domain
                    and principal_safe(
                        paired_state,
                        paired_input,
                        complement(output),
                    )
                )
            )
            for output in BINARY_STATES4
        ):
            return False
    return True


def principal_row():
    allowed = tuple(sorted(UNION))
    rows = []
    for mask in range(1 << len(allowed)):
        domain = frozenset(
            state
            for index, state in enumerate(allowed)
            if mask & (1 << index)
        )
        rows.append((domain, principal_domain_feasible(domain)))

    if not principal_domain_feasible(LEFT):
        raise AssertionError("left domain")
    if not principal_domain_feasible(RIGHT):
        raise AssertionError("right domain")
    if principal_domain_feasible(UNION):
        raise AssertionError("union domain")

    weights = {
        state: 1 << index
        for index, state in enumerate(allowed)
    }
    scored = tuple(
        (sum(weights[state] for state in domain), domain)
        for domain, feasible in rows
        if feasible
    )
    best = max(score for score, _domain in scored)
    optimum = tuple(domain for score, domain in scored if score == best)
    if len(optimum) != 1:
        raise AssertionError("principal optimum is not unique")
    forced_union_feasible = next(
        feasible for domain, feasible in rows if domain == UNION
    )
    return {
        "allowed_states": len(allowed),
        "assignments_checked": len(rows),
        "feasible_domains": sum(feasible for _domain, feasible in rows),
        "left_feasible": principal_domain_feasible(LEFT),
        "right_feasible": principal_domain_feasible(RIGHT),
        "union_feasible": forced_union_feasible,
        "optimum_score": best,
        "optimum_domain": [list(state) for state in sorted(optimum[0])],
    }


def make_receipt():
    result = {
        "schema": "orbit-synthesis/structural-families-independent/v1",
        "antichain": [antichain_row(3), antichain_row(4)],
        "principal": principal_row(),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main():
    print(json.dumps(make_receipt(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
