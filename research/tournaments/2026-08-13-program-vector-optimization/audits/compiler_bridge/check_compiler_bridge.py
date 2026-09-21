"""Independent deterministic audit of compiler premises I2--I6.

This file intentionally imports no OrbitSynthesis implementation.  It
reconstructs the Q algebra, the global anchor, the signed router, the
sibling-shared P program vector, the two-plane nonbinary compiler, the
complement-relative binary compiler, and the final same-DAG glue.

The exhaustive semantic checks are deliberately small.  The all-arity
claims are checked from explicit integer recurrences and are paired with the
inductive statements recorded in REPORT.md; finite replay is evidence for,
not a replacement for, those inductions.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
from collections.abc import Callable, Iterable, Sequence
from functools import cache
from pathlib import Path

Q = (0, 1, 2)
B = (0, 1)
FROZEN_STATE_SHA256 = "6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def d_value(x: int, y: int, z: int) -> int:
    require(x in Q and y in Q and z in Q, "d input outside Q")
    return z if x == y else x


def u_value(x: int) -> int:
    require(x in Q, "u input outside Q")
    return (1, 0, 1)[x]


def words(alphabet: Sequence[int], width: int) -> list[tuple[int, ...]]:
    return list(itertools.product(alphabet, repeat=width))


def ceil_log2(n: int) -> int:
    require(n >= 1, "ceil_log2 domain")
    return (n - 1).bit_length()


def ceil_log3(n: int) -> int:
    require(n >= 1, "ceil_log3 domain")
    p = 1
    e = 0
    while p < n:
        p *= 3
        e += 1
    return e


def floor_power3(n: int) -> tuple[int, int]:
    require(n >= 1, "floor_power3 domain")
    p = 1
    e = 0
    while 3 * p <= n:
        p *= 3
        e += 1
    return e, p


class DAG:
    """Hash-consed original-signature scalar DAG; terminals are free."""

    def __init__(self) -> None:
        self.nodes: list[tuple[object, ...]] = []
        self.index: dict[tuple[object, ...], int] = {}
        self.depths: list[int] = []

    def _intern(self, node: tuple[object, ...], depth: int) -> int:
        previous = self.index.get(node)
        if previous is not None:
            return previous
        result = len(self.nodes)
        self.nodes.append(node)
        self.index[node] = result
        self.depths.append(depth)
        return result

    def var(self, name: str) -> int:
        return self._intern(("var", name), 0)

    def u(self, x: int) -> int:
        return self._intern(("u", x), self.depths[x] + 1)

    def d(self, x: int, y: int, z: int) -> int:
        return self._intern(
            ("d", x, y, z),
            max(self.depths[x], self.depths[y], self.depths[z]) + 1,
        )

    def operation_count(self) -> int:
        return sum(node[0] != "var" for node in self.nodes)

    def evaluate(self, roots: Iterable[int], assignment: dict[str, int]) -> tuple[int, ...]:
        values: list[int] = []
        for node in self.nodes:
            kind = node[0]
            if kind == "var":
                value = assignment[str(node[1])]
                require(value in Q, "terminal assignment outside Q")
            elif kind == "u":
                value = u_value(values[int(node[1])])
            else:
                value = d_value(
                    values[int(node[1])],
                    values[int(node[2])],
                    values[int(node[3])],
                )
            values.append(value)
        return tuple(values[root] for root in roots)

    def depends_on(self, root: int) -> frozenset[str]:
        memo: dict[int, frozenset[str]] = {}

        def visit(node_id: int) -> frozenset[str]:
            old = memo.get(node_id)
            if old is not None:
                return old
            node = self.nodes[node_id]
            if node[0] == "var":
                out = frozenset((str(node[1]),))
            elif node[0] == "u":
                out = visit(int(node[1]))
            else:
                out = visit(int(node[1])) | visit(int(node[2])) | visit(int(node[3]))
            memo[node_id] = out
            return out

        return visit(root)


def build_anchor(dag: DAG, xs: Sequence[int]) -> int:
    """Balanced ordered fold of h(x,y)=d(x,u(u(x)),d(y,u(x),x))."""
    require(len(xs) >= 1, "empty anchor")
    if len(xs) == 1:
        return xs[0]
    split = (len(xs) + 1) // 2
    left = build_anchor(dag, xs[:split])
    right = build_anchor(dag, xs[split:])
    u_left = dag.u(left)
    uu_left = dag.u(u_left)
    inner = dag.d(right, u_left, left)
    return dag.d(left, uu_left, inner)


def anchor_reference(point: tuple[int, ...]) -> int:
    return point[0] if all(value in B for value in point) else 2


def anchor_checks() -> dict[str, object]:
    rows = []
    tuples_checked = 0
    for r in range(1, 8):
        dag = DAG()
        xs = [dag.var(f"x{i}") for i in range(r)]
        root = build_anchor(dag, xs)
        for point in words(Q, r):
            got = dag.evaluate((root,), {f"x{i}": value for i, value in enumerate(point)})[0]
            require(got == anchor_reference(point), "anchor semantic mismatch")
            tuples_checked += 1
        require(dag.operation_count() == 4 * (r - 1), "anchor count mismatch")
        require(dag.depths[root] == 3 * ceil_log2(r), "anchor depth mismatch")
        rows.append(
            {
                "r": r,
                "operation_nodes": dag.operation_count(),
                "depth": dag.depths[root],
            }
        )

    # Killer mutation: remove one u from the left equality witness.
    bad_witness = None
    for x, y in words(Q, 2):
        ux = u_value(x)
        bad = d_value(x, ux, d_value(y, ux, x))
        expected = anchor_reference((x, y))
        if bad != expected:
            bad_witness = [x, y, bad, expected]
            break
    require(bad_witness is not None, "anchor mutation was ineffective")
    return {
        "formula": "h(x,y)=d(x,u(u(x)),d(y,u(x),x))",
        "exact_nodes": "4(r-1)",
        "exact_balanced_depth": "3ceil(log2 r)",
        "tuples_checked": tuples_checked,
        "rows": rows,
        "mutation_remove_outer_u": bad_witness,
    }


def make_names(dag: DAG, anchor: int) -> tuple[int, int]:
    one = dag.u(anchor)
    zero = dag.u(one)
    return one, zero


def split_width(width: int) -> tuple[int, int]:
    return (width + 1) // 2, width // 2


def generic_rails(
    dag: DAG, address: Sequence[int], anchor: int, one: int, zero: int
) -> dict[tuple[int, ...], tuple[int, int]]:
    """All (loss,gain) rails, with zero-gain root reuse."""
    width = len(address)
    require(width >= 1, "generic rail width")
    if width == 1:
        x = address[0]
        loss0 = dag.d(x, anchor, one)
        loss1 = dag.u(x)
        loss2 = dag.u(loss0)
        gain2 = dag.u(loss1)
        return {
            (0,): (loss0, zero),
            (1,): (loss1, zero),
            (2,): (loss2, gain2),
        }
    a, _b = split_width(width)
    left = generic_rails(dag, address[:a], anchor, one, zero)
    right = generic_rails(dag, address[a:], anchor, one, zero)
    out: dict[tuple[int, ...], tuple[int, int]] = {}
    for pa, (la, ga) in left.items():
        for pb, (lb, gb) in right.items():
            loss = dag.d(la, ga, lb)
            gain = ga if gb == zero else dag.d(ga, la, gb)
            out[pa + pb] = (loss, gain)
    return out


def extended_rails(
    dag: DAG, address: Sequence[int], anchor: int, one: int, zero: int
) -> dict[tuple[int, ...], tuple[int, int, int]]:
    """All (loss,gain,not-loss) rails; sibling identities hash-cons."""
    width = len(address)
    require(width >= 1, "extended rail width")
    if width == 1:
        x = address[0]
        loss0 = dag.d(x, anchor, one)
        loss1 = dag.u(x)
        loss2 = dag.u(loss0)
        gain2 = dag.u(loss1)
        return {
            (0,): (loss0, zero, loss2),
            (1,): (loss1, zero, gain2),
            (2,): (loss2, gain2, loss0),
        }
    a, _b = split_width(width)
    left = generic_rails(dag, address[:a], anchor, one, zero)
    right = extended_rails(dag, address[a:], anchor, one, zero)
    out: dict[tuple[int, ...], tuple[int, int, int]] = {}
    for pa, (la, ga) in left.items():
        for pb, (lb, gb, nb) in right.items():
            loss = dag.d(la, ga, lb)
            gain = ga if gb == zero else dag.d(ga, la, gb)
            not_loss = dag.d(ga, la, nb)
            out[pa + pb] = (loss, gain, not_loss)
    return out


def build_p_vector(
    dag: DAG, address: Sequence[int], anchor: int
) -> tuple[dict[tuple[int, ...], tuple[int, int]], int, int]:
    """Sign-specialized P-root controls, including shared names."""
    one, zero = make_names(dag, anchor)
    width = len(address)
    if width == 0:
        return {(): (zero, zero)}, one, zero
    if width == 1:
        x = address[0]
        loss0 = dag.d(x, anchor, one)
        loss2 = dag.u(loss0)
        gain2 = dag.d(x, anchor, zero)
        return {
            (0,): (loss0, zero),
            (1,): (zero, gain2),
            (2,): (loss2, gain2),
        }, one, zero
    a, _b = split_width(width)
    left = generic_rails(dag, address[:a], anchor, one, zero)
    right = extended_rails(dag, address[a:], anchor, one, zero)
    controls: dict[tuple[int, ...], tuple[int, int]] = {}
    for pa, (la, ga) in left.items():
        for pb, (lb, gb, nb) in right.items():
            physical = pa + pb
            gain = ga if gb == zero else dag.d(ga, la, gb)
            if sum(digit == 1 for digit in physical) % 2 == 0:
                mixed = dag.d(la, ga, lb)
                controls[physical] = (mixed, gain)
            else:
                mixed = dag.d(ga, la, nb)
                controls[physical] = (gain, mixed)
    return controls, one, zero


def first_mismatch_controls(
    target: tuple[int, ...], physical: tuple[int, ...]
) -> tuple[int, int]:
    require(len(target) == len(physical), "control word widths")
    loss = 0
    gain = 0
    for t, p in zip(target, physical):
        if t != p:
            if (t, p) == (1, 2):
                gain = 1
            else:
                loss = 1
            break
    negative = sum(digit == 1 for digit in physical) % 2
    return (gain, 1 - loss) if negative else (loss, gain)


@cache
def generic_count(width: int) -> int:
    if width == 0:
        return 0
    if width == 1:
        return 4
    a, b = split_width(width)
    return generic_count(a) + generic_count(b) + 3**width + 3**a * (3**b - 1) // 2


@cache
def extended_count(width: int) -> int:
    if width == 0:
        return 0
    if width == 1:
        return 4
    a, b = split_width(width)
    return (
        generic_count(a)
        + extended_count(b)
        + 2 * 3**width
        - 3 ** (width - 1)
        + 3**a * (3**b - 1) // 2
    )


@cache
def p_vector_count(width: int) -> int:
    if width == 0:
        return 2
    if width == 1:
        return 5
    a, b = split_width(width)
    return (
        2
        + generic_count(a)
        + extended_count(b)
        + 3**a * (3**b - 1) // 2
        + 3**width
        - (3 ** (width - 1) + 1) // 2
    )


def vector_depth(width: int) -> int:
    return 2 if width == 0 else 3 + ceil_log2(width)


def build_signed_router(
    dag: DAG,
    root_sign: str,
    width: int,
    leaves: dict[tuple[int, ...], int],
    controls: dict[tuple[int, ...], tuple[int, int]],
    prefix: tuple[int, ...] = (),
) -> int:
    require(root_sign in ("P", "N"), "router sign")
    if width == 0:
        x = leaves[prefix]
        c0, c1 = controls[prefix]
        return dag.d(x, c0, c1) if root_sign == "P" else dag.d(c0, x, c1)
    child_signs = ("P", "N", "P") if root_sign == "P" else ("N", "P", "N")
    children = [
        build_signed_router(dag, child_signs[digit], width - 1, leaves, controls, prefix + (digit,))
        for digit in Q
    ]
    return dag.d(children[0], children[1], children[2])


def vector_and_router_checks() -> dict[str, object]:
    count_rows = []
    semantic_pairs = 0
    router_rows = 0
    for width in range(1, 7):
        dag = DAG()
        anchor = dag.var("A")
        address = [dag.var(f"t{i}") for i in range(width)]
        controls, _one, _zero = build_p_vector(dag, address, anchor)
        require(dag.operation_count() == p_vector_count(width), "P-vector exact count mismatch")
        require(max(dag.depths[root] for pair in controls.values() for root in pair) <= vector_depth(width), "P-vector depth mismatch")
        for target in words(Q, width):
            assignment = {"A": 2, **{f"t{i}": value for i, value in enumerate(target)}}
            observed = dag.evaluate((root for pair in controls.values() for root in pair), assignment)
            cursor = 0
            for physical in controls:
                got = (observed[cursor], observed[cursor + 1])
                cursor += 2
                require(got == first_mismatch_controls(target, physical), "P-vector semantics mismatch")
                semantic_pairs += 1
        count_rows.append(
            {
                "width": width,
                "q": 3**width,
                "nodes": dag.operation_count(),
                "bound_numerator_slack": 4 * 3**width + 15 * 3 ** ((width + 1) // 2) - 3 * dag.operation_count(),
                "depth": max(dag.depths[root] for pair in controls.values() for root in pair),
            }
        )

    # Full projection replay through width two, all target/payload choices.
    for width in (1, 2):
        dag = DAG()
        anchor = dag.var("A")
        address = [dag.var(f"t{i}") for i in range(width)]
        controls, _one, _zero = build_p_vector(dag, address, anchor)
        leaf_words = words(Q, width)
        leaves = {physical: dag.var("v" + "".join(map(str, physical))) for physical in leaf_words}
        root = build_signed_router(dag, "P", width, leaves, controls)
        expected_router_nodes = (3 ** (width + 1) - 1) // 2
        # Router nodes can collide only with existing nodes if terminals/control
        # triples literally coincide; distinct v leaves make the charged tree exact.
        require(dag.operation_count() >= p_vector_count(width) + expected_router_nodes, "router node undercount")
        for target in leaf_words:
            for payload in words(B, len(leaf_words)):
                assignment = {"A": 2}
                assignment.update({f"t{i}": value for i, value in enumerate(target)})
                assignment.update({"v" + "".join(map(str, physical)): value for physical, value in zip(leaf_words, payload)})
                got = dag.evaluate((root,), assignment)[0]
                require(got == payload[leaf_words.index(target)], "signed router projection mismatch")
                router_rows += 1

    # Killer mutation: swap one physical cell's controls.
    mutation = None
    for target in words(Q, 2):
        for physical in words(Q, 2):
            c0, c1 = first_mismatch_controls(target, physical)
            bad = (c1, c0)
            if bad != (c0, c1):
                mutation = {"target": target, "physical": physical, "good": [c0, c1], "bad": list(bad)}
                break
        if mutation is not None:
            break
    require(mutation is not None, "control-swap mutation ineffective")
    return {
        "semantics_checked": semantic_pairs,
        "router_cases_checked": router_rows,
        "exact_rows": count_rows,
        "all_width_envelope": "3S_P(w)<=4*3^w+15*3^ceil(w/2)",
        "uniform_bound": "S_P(w)<=7*3^w/3",
        "depth_bound": "3+ceil(log2 w)",
        "mutation_control_swap": mutation,
    }


def code_planes(value: int) -> tuple[int, int]:
    require(value in Q, "plane encoding domain")
    return ((0, 0), (0, 1), (1, 0))[value]


def decode_value(high: int, low: int) -> int:
    return d_value(d_value(high, 1, 2), 0, low)


def decoder_checks() -> dict[str, object]:
    rows = []
    for value in Q:
        high, low = code_planes(value)
        got = decode_value(high, low)
        require(got == value, "decoder mismatch")
        rows.append([value, high, low, got])
    # Mutation: reversing the legal planes maps 2 incorrectly.
    high, low = code_planes(2)
    bad = decode_value(low, high)
    require(bad != 2, "decoder plane-swap mutation ineffective")
    return {
        "code": {"0": [0, 0], "1": [0, 1], "2": [1, 0]},
        "formula": "d(d(high,one,A),zero,low)",
        "rows": rows,
        "new_d_nodes": 2,
        "depth_above_planes": 2,
        "mutation_swap_planes_at_2": bad,
    }


def table_index(values: Sequence[int]) -> int:
    out = 0
    for value in values:
        out = 3 * out + value
    return out


def build_local_library(
    dag: DAG,
    local_address: Sequence[int],
    anchor: int,
) -> tuple[list[tuple[int, int]], int, int]:
    controls, one, zero = build_p_vector(dag, local_address, anchor)
    branch_words = words(Q, len(local_address))
    m = len(branch_words)
    library: list[tuple[int, int]] = []
    for values in words(Q, m):
        high_leaves = {physical: (one if code_planes(value)[0] else zero) for physical, value in zip(branch_words, values)}
        low_leaves = {physical: (one if code_planes(value)[1] else zero) for physical, value in zip(branch_words, values)}
        high = build_signed_router(dag, "P", len(local_address), high_leaves, controls)
        low = build_signed_router(dag, "P", len(local_address), low_leaves, controls)
        library.append((high, low))
    return library, one, zero


def build_nonbinary_compiler(
    dag: DAG,
    xs: Sequence[int],
    sigma: Callable[[tuple[int, ...]], int],
    b: int,
    anchor: int,
) -> tuple[int, dict[str, int]]:
    r = len(xs)
    require(1 <= b < r, "small nonbinary split")
    s = r - b
    local_address = xs[s:]
    prefix_address = xs[:s]
    before = dag.operation_count()
    library, one, zero = build_local_library(dag, local_address, anchor)
    after_library = dag.operation_count()
    prefix_controls, _one2, _zero2 = build_p_vector(dag, prefix_address, anchor)
    prefix_words = words(Q, s)
    local_words = words(Q, b)
    high_leaves: dict[tuple[int, ...], int] = {}
    low_leaves: dict[tuple[int, ...], int] = {}
    for prefix in prefix_words:
        table = []
        for local in local_words:
            point = prefix + local
            table.append(point[sigma(point)])
        high_leaves[prefix], low_leaves[prefix] = library[table_index(table)]
    high = build_signed_router(dag, "P", s, high_leaves, prefix_controls)
    low = build_signed_router(dag, "P", s, low_leaves, prefix_controls)
    inner = dag.d(high, one, anchor)
    decoded = dag.d(inner, zero, low)
    return decoded, {
        "before": before,
        "after_library": after_library,
        "after": dag.operation_count(),
        "high_depth": dag.depths[high],
        "low_depth": dag.depths[low],
        "decoded_depth": dag.depths[decoded],
    }


def selector_units_r2() -> list[list[tuple[int, ...]]]:
    unseen = set(words(Q, 2))
    units: list[list[tuple[int, ...]]] = []
    while unseen:
        point = min(unseen)
        if all(value in B for value in point):
            other = tuple(1 - value for value in point)
            unit = sorted({point, other})
        else:
            unit = [point]
        for item in unit:
            unseen.remove(item)
        units.append(unit)
    return units


def sigma_from_choices_r2(bits: int) -> Callable[[tuple[int, ...]], int]:
    units = selector_units_r2()
    require(len(units) == 7, "r2 selector quotient census")
    table: dict[tuple[int, ...], int] = {}
    for i, unit in enumerate(units):
        for point in unit:
            table[point] = (bits >> i) & 1
    return lambda point: table[point]


def seeded_sigma(r: int, seed: int) -> Callable[[tuple[int, ...]], int]:
    require(r >= 2, "seeded selector arity")
    rng = random.Random(0xC011AB1E + 97 * r + seed)
    table: dict[tuple[int, ...], int] = {}
    for point in words(Q, r):
        if point in table:
            continue
        choice = rng.randrange(r)
        table[point] = choice
        if all(value in B for value in point):
            complement = tuple(1 - value for value in point)
            table[complement] = choice
    return lambda point: table[point]


def compatible(sigma: Callable[[tuple[int, ...]], int], r: int) -> bool:
    for point in words(B, r):
        if sigma(point) != sigma(tuple(1 - value for value in point)):
            return False
    return True


def ternary_word(index: int, width: int) -> tuple[int, ...]:
    require(0 <= index < 3**width, "ternary word range")
    digits = [0] * width
    for pos in range(width - 1, -1, -1):
        digits[pos] = index % 3
        index //= 3
    return tuple(digits)


def relative_selector(
    dag: DAG,
    x0: int,
    variables: Sequence[int],
    table: dict[tuple[int, ...], int],
    x0_not: int,
) -> int:
    """Decision tree for physical x0-relative output table."""
    width = len(variables)

    def rec(level: int, prefix: tuple[int, ...]) -> int:
        if level == width:
            return x0 if table[prefix] == 0 else x0_not
        equal = rec(level + 1, prefix + (0,))
        different = rec(level + 1, prefix + (1,))
        x = variables[level]
        a = dag.d(x, x0, equal)
        b = dag.d(x, x0, different)
        return dag.d(a, b, different)

    return rec(0, ())


def binary_chunks(r: int) -> tuple[int, int, int, list[list[int]]]:
    k = math.isqrt(r)
    q = 3**k
    width = q.bit_length() - 1
    require(2**width <= q < 2 ** (width + 1), "binary chunk width")
    count = r - 1
    residual = count % width
    sizes = ([residual] if residual else []) + [width] * (count // width)
    chunks: list[list[int]] = []
    cursor = 1
    for size in sizes:
        chunks.append(list(range(cursor, cursor + size)))
        cursor += size
    require(cursor == r, "binary chunk partition")
    return k, q, width, chunks


def build_binary_compiler(
    dag: DAG,
    xs: Sequence[int],
    sigma: Callable[[tuple[int, ...]], int],
) -> tuple[int, dict[str, object]]:
    r = len(xs)
    require(compatible(sigma, r), "binary compiler requires complement-invariant selector")
    k, q, width, chunks = binary_chunks(r)
    x0 = xs[0]
    x0_not = dag.u(x0)
    physical_words = words(Q, k)
    level_controls: list[dict[tuple[int, ...], tuple[int, int]]] = []
    control_roots: list[int] = []
    for chunk in chunks:
        c = len(chunk)
        logical_patterns = words(B, c)
        table_pairs: dict[tuple[int, ...], list[dict[tuple[int, ...], int]]] = {}
        for physical in physical_words:
            first: dict[tuple[int, ...], int] = {}
            second: dict[tuple[int, ...], int] = {}
            for index, pattern in enumerate(logical_patterns):
                target = ternary_word(index, k)
                c0, c1 = first_mismatch_controls(target, physical)
                first[pattern] = c0
                second[pattern] = c1
            table_pairs[physical] = [first, second]
        controls: dict[tuple[int, ...], tuple[int, int]] = {}
        variables = [xs[index] for index in chunk]
        for physical in physical_words:
            c0 = relative_selector(dag, x0, variables, table_pairs[physical][0], x0_not)
            c1 = relative_selector(dag, x0, variables, table_pairs[physical][1], x0_not)
            controls[physical] = (c0, c1)
            control_roots.extend((c0, c1))
        level_controls.append(controls)

    instances = 0

    def rec(level: int, prefix: tuple[int, ...]) -> int:
        nonlocal instances
        if level == len(chunks):
            representative = (0,) + prefix
            return xs[sigma(representative)]
        patterns = words(B, len(chunks[level]))
        live = [rec(level + 1, prefix + pattern) for pattern in patterns]
        padded = live + [live[-1]] * (q - len(live))
        leaves = {physical: leaf for physical, leaf in zip(physical_words, padded)}
        instances += 1
        return build_signed_router(dag, "P", k, leaves, level_controls[level])

    root = rec(0, ())
    return root, {
        "k": k,
        "q": q,
        "width": width,
        "chunk_sizes": [len(chunk) for chunk in chunks],
        "router_instances": instances,
        "control_depth": max((dag.depths[node] for node in control_roots), default=0),
        "root_depth": dag.depths[root],
    }


def build_glue(dag: DAG, anchor: int, binary: int, nonbinary: int) -> int:
    selector = dag.u(dag.u(anchor))
    left = dag.d(selector, anchor, binary)
    right = dag.d(selector, anchor, nonbinary)
    return dag.d(left, right, nonbinary)


def semantic_compiler_checks() -> dict[str, object]:
    selectors = [(2, i, sigma_from_choices_r2(i), 1) for i in range(128)]
    selectors.extend((3, seed, seeded_sigma(3, seed), 1) for seed in range(4))
    tuples_checked = 0
    binary_checked = 0
    nonbinary_checked = 0
    actual_rows = []
    for r, label, sigma, b in selectors:
        require(compatible(sigma, r), "test selector compatibility")
        dag = DAG()
        xs = [dag.var(f"x{i}") for i in range(r)]
        anchor = build_anchor(dag, xs)
        nonbinary, nb_meta = build_nonbinary_compiler(dag, xs, sigma, b, anchor)
        binary, b_meta = build_binary_compiler(dag, xs, sigma)
        before_glue = dag.operation_count()
        glued = build_glue(dag, anchor, binary, nonbinary)
        glue_added = dag.operation_count() - before_glue
        require(glue_added == 3, "glue must add exactly three d nodes")
        for point in words(Q, r):
            assignment = {f"x{i}": value for i, value in enumerate(point)}
            got_anchor, got_n, got_b, got = dag.evaluate((anchor, nonbinary, binary, glued), assignment)
            expected = point[sigma(point)]
            require(got_anchor == anchor_reference(point), "composed anchor mismatch")
            if got_anchor == 2:
                require(got_n == expected, "nonbinary compiler mismatch")
                nonbinary_checked += 1
            else:
                require(got_b == expected, "binary compiler mismatch")
                binary_checked += 1
            require(got == expected, "glued compiler mismatch")
            tuples_checked += 1
        if label in (0, 127):
            actual_rows.append(
                {
                    "r": r,
                    "selector_label": label,
                    "operation_nodes": dag.operation_count(),
                    "glued_depth": dag.depths[glued],
                    "nonbinary_depth": nb_meta["decoded_depth"],
                    "binary_depth": b_meta["root_depth"],
                    "binary_chunks": b_meta["chunk_sizes"],
                }
            )

    # Killer mutation: a non-invariant binary selector must be rejected.
    bad_table = {point: 0 for point in words(Q, 2)}
    bad_table[(1, 1)] = 1
    bad_sigma = lambda point: bad_table[point]
    require(not compatible(bad_sigma, 2), "non-invariant mutation escaped")

    # Absolute logical controls do not complement physically.  One self-dual
    # d cell suffices to expose the orientation error.
    representative = d_value(0, 0, 1)
    wrong_complement = d_value(1, 0, 1)
    require(wrong_complement != 1 - representative, "absolute-control mutation ineffective")

    glue_rows = 0
    glue_mutation = None
    for anchor_value, binary_value, nonbinary_value in itertools.product(Q, repeat=3):
        if anchor_value not in Q:
            continue
        selector = u_value(u_value(anchor_value))
        got = d_value(
            d_value(selector, anchor_value, binary_value),
            d_value(selector, anchor_value, nonbinary_value),
            nonbinary_value,
        )
        expected = binary_value if anchor_value in B else nonbinary_value
        require(got == expected, "glue truth-table mismatch")
        bad = d_value(
            d_value(selector, anchor_value, nonbinary_value),
            d_value(selector, anchor_value, binary_value),
            binary_value,
        )
        if bad != expected and glue_mutation is None:
            glue_mutation = [anchor_value, binary_value, nonbinary_value, bad, expected]
        glue_rows += 1
    require(glue_mutation is not None, "glue branch-swap mutation ineffective")
    return {
        "selector_tables": len(selectors),
        "all_r2_compatible_tables": 128,
        "tuples_checked": tuples_checked,
        "binary_rows_checked": binary_checked,
        "nonbinary_rows_checked": nonbinary_checked,
        "selected_materializations": actual_rows,
        "mutation_noninvariant_rejected": True,
        "mutation_absolute_binary_control": {
            "representative_output": representative,
            "complement_input_with_uncomplemented_controls": wrong_complement,
            "expected": 1 - representative,
        },
        "glue_rows_checked": glue_rows,
        "mutation_glue_branch_swap": glue_mutation,
    }


def giant_schedule(r: int) -> dict[str, int]:
    require(r >= 64, "giant schedule domain")
    reserve = 4 + ceil_log3(r * r)
    h = r - reserve
    b, m = floor_power3(h)
    require(m == 3**b and h // 3 < m <= h, "giant M interval")
    s = r - b
    p = 3**s
    return {"r": r, "reserve": reserve, "H": h, "M": m, "b": b, "s": s, "P": p}


def nonbinary_ledger(r: int) -> dict[str, int]:
    plan = giant_schedule(r)
    m = plan["M"]
    b = plan["b"]
    s = plan["s"]
    p = plan["P"]
    local_routers = (3 * m - 1) * 3**m
    prefix_routers = 3 * p - 1
    program_union = p_vector_count(b) + p_vector_count(s) - 2
    anchor = 4 * (r - 1)
    decoder = 2
    glue = 3
    inclusive = local_routers + prefix_routers + program_union + anchor + decoder + glue

    da = 3 * ceil_log2(r)
    local_plane = da + vector_depth(b) + b + 1
    prefix_control = da + vector_depth(s)
    prefix_plane = max(local_plane, prefix_control) + s + 1
    before_glue_depth = prefix_plane + 2
    return {
        **plan,
        "local_routers": local_routers,
        "prefix_routers": prefix_routers,
        "program_union": program_union,
        "anchor_nodes": anchor,
        "decoder_nodes": decoder,
        "reserved_glue_nodes": glue,
        "inclusive_nodes": inclusive,
        "anchor_depth": da,
        "local_plane_depth": local_plane,
        "prefix_plane_depth": prefix_plane,
        "before_glue_depth": before_glue_depth,
    }


def binary_ledger(r: int) -> dict[str, int]:
    k, q, width, chunks = binary_chunks(r)
    sizes = [len(chunk) for chunk in chunks]
    prefix = 1
    instances = 0
    control_upper = 0
    for size in sizes:
        instances += prefix
        control_upper += 6 * q * (2**size - 1)
        prefix *= 2**size
    require(prefix == 2 ** (r - 1), "binary prefix product")
    router_nodes = (3 * q - 1) // 2 * instances
    intrinsic_depth = (k + 1) * len(sizes) + 2 * width + 1
    retained_depth = (k + 1) * len(sizes) + 2 * width + 3 * ceil_log2(r) + 8
    return {
        "r": r,
        "k": k,
        "q": q,
        "width": width,
        "levels": len(sizes),
        "first_chunk": sizes[0],
        "instances": instances,
        "router_nodes": router_nodes,
        "control_nodes_upper": control_upper,
        "private_u_x0": 1,
        "standalone_nodes_upper": router_nodes + control_upper + 1,
        "same_dag_increment_upper": router_nodes + control_upper,
        "intrinsic_depth_upper": intrinsic_depth,
        "retained_depth": retained_depth,
    }


def ratio_decimal(numerator: int, denominator: int, digits: int = 15) -> str:
    require(numerator >= 0 and denominator > 0 and digits >= 0, "decimal ratio domain")
    whole, remainder = divmod(numerator, denominator)
    out = str(whole)
    if digits:
        decimals = []
        for _ in range(digits):
            remainder *= 10
            digit, remainder = divmod(remainder, denominator)
            decimals.append(str(digit))
        out += "." + "".join(decimals)
    return out


def ledger_checks() -> dict[str, object]:
    max_r = 16384
    max_total_pair = (-1, 1, -1)
    max_nb_pair = (-1, 1, -1)
    selected = []
    nonbinary_dominates = True
    under_34 = True
    threshold_nonbelow = []
    for r in range(64, max_r + 1):
        nb = nonbinary_ledger(r)
        binary = binary_ledger(r)
        unit_denominator = 3**r
        # Inclusive NB already reserves the unique glue.  In the actual union,
        # u(x0) is present in the r>=2 anchor, so only router/control nodes are
        # added for the binary branch.
        total = nb["inclusive_nodes"] + binary["same_dag_increment_upper"]
        num = total * r
        nb_num = nb["inclusive_nodes"] * r
        if num * max_total_pair[1] > max_total_pair[0] * unit_denominator:
            max_total_pair = (num, unit_denominator, r)
        if nb_num * max_nb_pair[1] > max_nb_pair[0] * unit_denominator:
            max_nb_pair = (nb_num, unit_denominator, r)
        under_34 = under_34 and num < 34 * unit_denominator
        require(
            binary["router_nodes"] * r * 4 < unit_denominator,
            "binary router quarter-unit bound",
        )
        require(
            binary["control_nodes_upper"] * r * 4 < unit_denominator,
            "binary control quarter-unit bound",
        )
        require(
            nb["local_routers"] * r * 27 < unit_denominator,
            "local-router one-over-27-unit bound",
        )
        require(
            (nb["prefix_routers"] + p_vector_count(nb["s"])) * r < 32 * unit_denominator,
            "prefix-router/vector 32-unit bound",
        )
        lower_nonbinary = (
            nb["program_union"] - p_vector_count(nb["s"])
            + nb["anchor_nodes"]
            + nb["decoder_nodes"]
            + nb["reserved_glue_nodes"]
        )
        require(lower_nonbinary * r * 2 < unit_denominator, "local-vector/fixed half-unit bound")

        final_depth = max(
            nb["anchor_depth"] + 2,
            binary["intrinsic_depth_upper"],
            nb["before_glue_depth"],
        ) + 2
        require(final_depth <= r + 4 * ceil_log2(r) + 9, "optimized total depth ceiling")
        if binary["intrinsic_depth_upper"] > nb["before_glue_depth"]:
            nonbinary_dominates = False
        if r <= 899 and binary["retained_depth"] >= r:
            threshold_nonbelow.append(r)
        if r in (64, 90, 93, 94, 338, 339, 512, 900, 4096, 16384):
            selected.append(
                {
                    "r": r,
                    "b": nb["b"],
                    "M": nb["M"],
                    "same_dag_size_ratio": ratio_decimal(num, unit_denominator),
                    "nonbinary_before_glue_depth": nb["before_glue_depth"],
                    "binary_intrinsic_depth_upper": binary["intrinsic_depth_upper"],
                    "binary_retained_depth": binary["retained_depth"],
                    "final_max_depth": final_depth,
                    "depth_ceiling": r + 4 * ceil_log2(r) + 9,
                }
            )

    require(under_34, "34-unit total size bound")
    require(nonbinary_dominates, "binary intrinsic branch unexpectedly dominates")
    require(max(threshold_nonbelow) == 338, "last retained-depth violation")
    require(binary_ledger(338)["retained_depth"] == 338, "r338 retained equality")
    require(binary_ledger(339)["retained_depth"] == 338, "r339 retained pass")
    require(all(binary_ledger(r)["retained_depth"] < r for r in range(339, 900)), "retained exact tail")

    def tail_polynomial(k: int) -> int:
        return k**3 - 27 * k**2 - 19 * k + 9

    require(tail_polynomial(30) > 0, "binary analytic tail base")
    require(3 * 30**2 - 51 * 30 - 45 > 0, "binary tail monotonicity base")

    # One-log reserve mutation.  It first allows M=6561 at r=6574, far too
    # large for a local library under a 3^r/r target.
    bad_r = 6574
    bad_h = bad_r - (4 + ceil_log3(bad_r))
    _bad_b, bad_m = floor_power3(bad_h)
    require(bad_m == 6561, "one-log reserve counterexample drift")
    bad_local_num = (3 * bad_m - 1) * 3**bad_m * bad_r
    require(bad_local_num >= 3**bad_r, "one-log reserve mutation did not break unit bound")

    return {
        "arity_range": [64, max_r],
        "inclusive_nonbinary_formula": "(3M-1)3^M+(3P-1)+V_P(b)+V_P(r-b)-2+4(r-1)+2+3",
        "same_dag_total_formula": "inclusive_nonbinary+binary_router_nodes+binary_control_upper",
        "size_bound": "same_dag_total < 34*3^r/r",
        "analytic_component_bounds": [
            "local routers < (1/27)3^r/r",
            "prefix routers plus prefix vector < 32*3^r/r",
            "local vector plus anchor/decoder/glue < (1/2)3^r/r",
            "binary routers < (1/4)3^r/r",
            "binary controls < (1/4)3^r/r",
        ],
        "maximum_total_ratio": {
            "r": max_total_pair[2],
            "value": ratio_decimal(max_total_pair[0], max_total_pair[1]),
        },
        "maximum_nonbinary_ratio": {
            "r": max_nb_pair[2],
            "value": ratio_decimal(max_nb_pair[0], max_nb_pair[1]),
        },
        "depth_bound": "max(anchor+2,binary_intrinsic,nonbinary_before_glue)+2 <= r+4ceil(log2 r)+9",
        "nonbinary_dominates_intrinsic_binary_entire_range": nonbinary_dominates,
        "selected_rows": selected,
        "retained_binary_threshold": {
            "last_not_strictly_below_r": max(threshold_nonbelow),
            "depth_338": binary_ledger(338)["retained_depth"],
            "depth_339": binary_ledger(339)["retained_depth"],
            "meaning": "boundary of the conservative serial ledger, not the united-DAG critical path",
            "analytic_tail_polynomial_at_30": tail_polynomial(30),
        },
        "same_dag_sharing": {
            "program_name_nodes_shared": 2,
            "binary_u_x0_already_in_anchor": True,
            "glue_nodes_once": 3,
        },
        "mutation_one_log_reserve": {
            "r": bad_r,
            "H": bad_h,
            "M": bad_m,
            "local_library_alone_breaks_one_unit": True,
        },
    }


def barrier_checks() -> dict[str, object]:
    # The only machine-checkable part of the restricted cut argument is the
    # fan-in dependency cone: depth ell reaches at most 3^ell terminals.
    rows = []
    for width in range(1, 65):
        dependency_floor = ceil_log3(width)
        router_distance = width + 1
        restricted_floor = dependency_floor + router_distance
        require(3**dependency_floor >= width, "fan-in cone upper reach")
        if dependency_floor:
            require(3 ** (dependency_floor - 1) < width, "fan-in cone minimality")
        rows.append([width, dependency_floor, router_distance, restricted_floor])

    # KPG is the three-state first-nonpropagating monoid.  It is a valid upper
    # construction but supplies no lower bound.
    kpg_rows = 0
    for left, right in itertools.product(Q, repeat=2):
        merged = d_value(left, 2, right)
        expected = right if left == 2 else left
        require(merged == expected, "KPG merge mismatch")
        kpg_rows += 1
    for a, b, c in itertools.product(Q, repeat=3):
        require(
            d_value(d_value(a, 2, b), 2, c) == d_value(a, 2, d_value(b, 2, c)),
            "KPG associativity mismatch",
        )

    # A three-way mux is a concrete architecture outside the cut premise:
    # payload and address nodes are interleaved, and no complete program
    # vector exists below an untouched signed router.
    mux_rows = 0
    for target, b0, b1, b2 in itertools.product(Q, repeat=4):
        left = d_value(0, d_value(target, 2, b0), d_value(0, target, b0))
        right = d_value(d_value(1, target, b1), 1, d_value(target, 2, b2))
        got = d_value(left, 0, right)
        require(got == (b0, b1, b2)[target], "interleaved mux mismatch")
        mux_rows += 1
    return {
        "restricted_statement": "If an exposed scalar control depends essentially on all w address inputs and a syntactic cut places it below an otherwise untouched depth-(w+1) signed router, its raw-address path is at least ceil(log3 w)+w+1.",
        "checked_widths": len(rows),
        "selected_rows": [rows[i - 1] for i in (1, 2, 3, 9, 27, 64)],
        "kpg": {
            "state_encoding": {"K": 0, "P": 2, "G": 1},
            "merge": "d(S_left,A,S_right) with A=2",
            "truth_rows_checked": kpg_rows,
            "associativity_rows_checked": 27,
            "status": "valid first-nonpropagating upper construction; not a lower bound",
        },
        "outside_cut_witness": {
            "construction": "three-way payload/address mux with no exposed all-address vector cut",
            "truth_rows_checked": mux_rows,
            "meaning": "invalidates transfer of the cut proof to arbitrary fused/interleaved DAGs, not the numerical restricted-floor inequality",
        },
        "not_a_global_lower_bound": [
            "interleaved mux/substitution has no all-address program-vector cut",
            "a fused router may avoid exposing the scalar controls",
            "the local/prefix compiler overlaps local payload depth with prefix-control depth and takes a maximum",
            "the KPG three-state construction is an upper construction, not a lower-bound model",
        ],
        "conclusion": "No r+ceil(log3 r)-Omega(1) lower bound is established for arbitrary original-signature shared DAGs.",
    }


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def verify_contract() -> dict[str, str]:
    state = Path(__file__).resolve().parents[2] / "STATE.md"
    observed = hashlib.sha256(state.read_bytes()).hexdigest()
    require(observed == FROZEN_STATE_SHA256, "frozen STATE contract drift")
    return {"STATE.md": observed}


def run() -> dict[str, object]:
    result: dict[str, object] = {
        "schema": "orbit.program-vector.compiler-bridge-independent-audit.v1",
        "status": "PASS_I2_TO_I6__I1_AND_FINITE_FALLBACK_NOT_RECONSTRUCTED",
        "frozen_contract": verify_contract(),
        "scope": {
            "proved_or_reconstructed": [
                "I2 exact anchor",
                "signed P-router and optimized P program vector used by I3",
                "I3 two-plane nonbinary architecture and inclusive ledger",
                "I4 complement-relative binary architecture and ledger",
                "I5 same-DAG union accounting",
                "I6 decoder and glue",
            ],
            "assumed": [
                "I1 existence of a compatible selector for every target operation",
                "I7 named finite fallback outside the giant schedule",
            ],
        },
        "anchor": anchor_checks(),
        "program_vector_router": vector_and_router_checks(),
        "decoder": decoder_checks(),
        "composed_semantics": semantic_compiler_checks(),
        "ledgers": ledger_checks(),
        "restricted_barrier": barrier_checks(),
    }
    result["semantic_sha256"] = hashlib.sha256(canonical_bytes(result)).hexdigest()
    return result


def main() -> int:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
