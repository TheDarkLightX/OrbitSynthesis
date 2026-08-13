"""Concrete original-signature DAG for the order-pair program vector."""

from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

Word = Tuple[int, ...]


def d(x: int, y: int, z: int) -> int:
    return z if x == y else x


def u(x: int) -> int:
    if x == 1:
        return 0
    if x in (0, 2):
        return 1
    raise ValueError(x)


@dataclass(frozen=True)
class Node:
    op: str
    args: Tuple[int, ...]


class DAG:
    def __init__(self, width: int) -> None:
        self.width = width
        self.nodes: List[Node] = []
        self.index: Dict[Node, int] = {}
        self.inputs: Dict[Tuple[object, ...], int] = {}
        self.anchor = self.var(("A",))
        self.targets = tuple(self.var(("t", i)) for i in range(width))
        self.one = self.unary(self.anchor)
        self.zero = self.unary(self.one)

    def var(self, name: Tuple[object, ...]) -> int:
        key = ("var",) + name
        if key not in self.inputs:
            self.inputs[key] = -(len(self.inputs) + 1)
        return self.inputs[key]

    def intern(self, node: Node) -> int:
        old = self.index.get(node)
        if old is not None:
            return old
        ref = len(self.nodes)
        self.nodes.append(node)
        self.index[node] = ref
        return ref

    def unary(self, child: int) -> int:
        return self.intern(Node("u", (child,)))

    def disc(self, x: int, y: int, z: int) -> int:
        return self.intern(Node("d", (x, y, z)))

    def evaluate(self, target: Word) -> Tuple[List[int], Mapping[int, int]]:
        inputs = {self.anchor: 2}
        inputs.update({ref: value for ref, value in zip(self.targets, target)})
        values: List[int] = []

        def get(ref: int) -> int:
            return inputs[ref] if ref < 0 else values[ref]

        for node in self.nodes:
            if node.op == "u":
                values.append(u(get(node.args[0])))
            else:
                values.append(d(*(get(arg) for arg in node.args)))
        return values, inputs

    @staticmethod
    def value(ref: int, values: Sequence[int], inputs: Mapping[int, int]) -> int:
        return inputs[ref] if ref < 0 else values[ref]

    @lru_cache(maxsize=None)
    def depth(self, ref: int) -> int:
        if ref < 0:
            return 0
        return 1 + max(self.depth(arg) for arg in self.nodes[ref].args)

    def reachable_count(self, roots: Iterable[int]) -> int:
        seen: set[int] = set()

        def visit(ref: int) -> None:
            if ref < 0 or ref in seen:
                return
            seen.add(ref)
            for arg in self.nodes[ref].args:
                visit(arg)

        for root in roots:
            visit(root)
        return len(seen)


@dataclass
class Package:
    width: int
    outputs: Dict[Word, Tuple[int, int]]
    left: "Package | None" = None
    right: "Package | None" = None


def words(width: int) -> List[Word]:
    return list(product(range(3), repeat=width))


def build_package(dag: DAG, variables: Tuple[int, ...]) -> Package:
    """All physical-word summaries, encoded as E=(0,0), L=(1,0), G=(0,1)."""
    width = len(variables)
    if width == 1:
        x = variables[0]
        a = dag.unary(x)
        g = dag.unary(a)
        l2 = dag.disc(dag.zero, x, a)
        l0 = dag.disc(x, dag.anchor, a)
        return Package(1, {
            (0,): (l0, dag.zero),
            (1,): (a, dag.zero),
            (2,): (l2, g),
        })
    if width < 1:
        raise ValueError("positive width required")

    split = width // 2
    left = build_package(dag, variables[:split])
    right = build_package(dag, variables[split:])
    outputs: Dict[Word, Tuple[int, int]] = {}
    for pa, (la, ga) in left.outputs.items():
        for pb, (lb, gb) in right.outputs.items():
            loss = dag.disc(la, ga, lb)
            gain = ga if gb == dag.zero else dag.disc(ga, la, gb)
            outputs[pa + pb] = (loss, gain)
    return Package(width, outputs, left, right)


def h_value(package: Package, partial_h: Mapping[Word, int], physical: Word) -> int:
    if physical[-1] == 1:
        return package.outputs[physical[:-1] + (2,)][1]
    return partial_h[physical]


def build_partial_h(dag: DAG, package: Package) -> Dict[Word, int]:
    """H=not L for words ending 0/2; H_(a1)=G_(a2) is reused."""
    if package.width == 1:
        return {
            (0,): package.outputs[(2,)][0],
            (2,): package.outputs[(0,)][0],
        }
    assert package.left is not None and package.right is not None
    right_h = build_partial_h(dag, package.right)
    outputs: Dict[Word, int] = {}
    for pa, (la, ga) in package.left.outputs.items():
        for pb in package.right.outputs:
            if pb[-1] == 1:
                continue
            outputs[pa + pb] = dag.disc(
                ga, la, h_value(package.right, right_h, pb)
            )
    return outputs


def parity(physical: Word) -> int:
    return sum(digit == 1 for digit in physical) & 1


def expected_pair(target: Word, physical: Word, root_negative: bool) -> Tuple[int, int]:
    equal = target == physical
    gain = False
    if not equal:
        for x, p in zip(target, physical):
            if x != p:
                gain = x == 1 and p == 2
                break
    loss = not equal and not gain
    negative = root_negative ^ bool(parity(physical))
    return (int(gain), int(equal or gain)) if negative else (int(loss), int(gain))


def build_vector(width: int, root_negative: bool) -> Tuple[DAG, Dict[Word, Tuple[int, int]], int, int]:
    """Exact sign-aware 2*3^w-output projection program."""
    if width < 1:
        raise ValueError("positive width required")
    dag = DAG(width)

    if width == 1:
        package = build_package(dag, dag.targets)
        partial_h = build_partial_h(dag, package)
        outputs = {}
        for p, (loss, gain) in package.outputs.items():
            if root_negative ^ bool(parity(p)):
                outputs[p] = (gain, h_value(package, partial_h, p))
            else:
                outputs[p] = (loss, gain)
    else:
        split = width // 2
        left = build_package(dag, dag.targets[:split])
        right = build_package(dag, dag.targets[split:])
        right_h = build_partial_h(dag, right)

        root_gain: Dict[Word, int] = {}
        for pa, (la, ga) in left.outputs.items():
            for pb, (_, gb) in right.outputs.items():
                p = pa + pb
                root_gain[p] = ga if gb == dag.zero else dag.disc(ga, la, gb)

        outputs = {}
        for pa, (la, ga) in left.outputs.items():
            for pb, (lb, _) in right.outputs.items():
                p = pa + pb
                gain = root_gain[p]
                negative = root_negative ^ bool(parity(p))
                if not negative:
                    outputs[p] = (dag.disc(la, ga, lb), gain)
                elif p[-1] == 1:
                    outputs[p] = (gain, root_gain[p[:-1] + (2,)])
                else:
                    outputs[p] = (
                        gain,
                        dag.disc(ga, la, h_value(right, right_h, pb)),
                    )

    roots = [root for pair in outputs.values() for root in pair]
    return (
        dag,
        outputs,
        dag.reachable_count(roots),
        max(dag.depth(root) for root in roots),
    )


@lru_cache(maxsize=None)
def summary_nodes(width: int) -> int:
    if width == 0:
        return 0
    if width == 1:
        return 4
    a = width // 2
    b = width - a
    return (
        summary_nodes(a)
        + summary_nodes(b)
        + 3**width
        + 3**a * ((3**b - 1) // 2)
    )


@lru_cache(maxsize=None)
def partial_h_nodes(width: int) -> int:
    if width <= 1:
        return 0
    return partial_h_nodes((width + 1) // 2) + 2 * 3 ** (width - 1)


def overlap(width: int, root_negative: bool) -> int:
    q = 3**width
    return (q - 3) // 6 if root_negative else (q + 3) // 6


def vector_nodes(width: int, root_negative: bool) -> int:
    if width == 1:
        return 6
    return (
        2
        + summary_nodes(width)
        + partial_h_nodes((width + 1) // 2)
        - overlap(width, root_negative)
    )


def vector_depth(width: int) -> int:
    import math
    return 3 + math.ceil(math.log2(width))


def output_lower_bound(width: int, root_negative: bool) -> int:
    q = 3**width
    return 4 * q // 3 if root_negative else 4 * q // 3 - 1
