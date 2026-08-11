#!/usr/bin/env python3
"""Reference ROBDD prototype for support-level ABA quantifier elimination.

This is deliberately dependency-free and small enough to audit.  It is not a
production BDD package.  Its purpose is to test the semantic translation in
`notes/ABA_SUPPORT_BOOLEANIZATION.md`.

For k retained Boolean-algebra variables there are n=2^k coarse minterm cells.
When eliminating one new BA variable y, each coarse cell i has three BDD vars:

    z_i       : coarse cell is nonzero
    w_i0      : fine cell with y=0 is nonzero
    w_i1      : fine cell with y=1 is nonzero

ordered locally as `(z_i,w_i0,w_i1)` and then cell-by-cell.  The exact ABA
extension relation is

    z_i <-> (w_i0 OR w_i1)

for every cell i.
"""

from __future__ import annotations

import random
from itertools import product


class ROBDD:
    """Minimal reduced ordered BDD manager with Boolean apply and abstraction."""

    def __init__(self) -> None:
        self.nodes: dict[int, tuple[int, int, int] | None] = {0: None, 1: None}
        self.unique: dict[tuple[int, int, int], int] = {}
        self.next_id = 2
        self.apply_cache: dict[tuple[str, int, int], int] = {}
        self.neg_cache: dict[int, int] = {0: 1, 1: 0}

    def mk(self, var: int, low: int, high: int) -> int:
        if low == high:
            return low
        key = (var, low, high)
        if key in self.unique:
            return self.unique[key]
        out = self.next_id
        self.next_id += 1
        self.unique[key] = out
        self.nodes[out] = key
        return out

    def var(self, var: int) -> int:
        return self.mk(var, 0, 1)

    def _top(self, node: int) -> int:
        return 10**18 if node < 2 else self.nodes[node][0]  # type: ignore[index]

    def _cofactor(self, node: int, var: int) -> tuple[int, int]:
        if node < 2:
            return node, node
        node_var, low, high = self.nodes[node]  # type: ignore[misc]
        return (low, high) if node_var == var else (node, node)

    def neg(self, node: int) -> int:
        if node in self.neg_cache:
            return self.neg_cache[node]
        var, low, high = self.nodes[node]  # type: ignore[misc]
        out = self.mk(var, self.neg(low), self.neg(high))
        self.neg_cache[node] = out
        self.neg_cache[out] = node
        return out

    def apply(self, op: str, left: int, right: int) -> int:
        if op in {"and", "or", "xor", "eq"} and left > right:
            left, right = right, left
        key = (op, left, right)
        if key in self.apply_cache:
            return self.apply_cache[key]

        if op == "and":
            if left == 0 or right == 0:
                return 0
            if left == 1:
                return right
            if right == 1:
                return left
            if left == right:
                return left
        elif op == "or":
            if left == 1 or right == 1:
                return 1
            if left == 0:
                return right
            if right == 0:
                return left
            if left == right:
                return left
        elif op == "xor":
            if left == right:
                return 0
            if left == 0:
                return right
            if right == 0:
                return left
            if left == 1:
                return self.neg(right)
            if right == 1:
                return self.neg(left)
        elif op == "eq":
            if left == right:
                return 1
            if left == 0:
                return self.neg(right)
            if right == 0:
                return self.neg(left)
            if left == 1:
                return right
            if right == 1:
                return left
        else:
            raise ValueError(f"unknown Boolean op {op!r}")

        var = min(self._top(left), self._top(right))
        ll, lh = self._cofactor(left, var)
        rl, rh = self._cofactor(right, var)
        out = self.mk(var, self.apply(op, ll, rl), self.apply(op, lh, rh))
        self.apply_cache[key] = out
        return out

    def conjunction(self, *nodes: int) -> int:
        out = 1
        for node in nodes:
            out = self.apply("and", out, node)
        return out

    def disjunction(self, *nodes: int) -> int:
        out = 0
        for node in nodes:
            out = self.apply("or", out, node)
        return out

    def exists(self, node: int, variables: set[int]) -> int:
        cache: dict[int, int] = {}

        def visit(current: int) -> int:
            if current < 2:
                return current
            if current in cache:
                return cache[current]
            var, low, high = self.nodes[current]  # type: ignore[misc]
            low2, high2 = visit(low), visit(high)
            out = (
                self.apply("or", low2, high2)
                if var in variables
                else self.mk(var, low2, high2)
            )
            cache[current] = out
            return out

        return visit(node)

    def evaluate(self, node: int, assignment: dict[int, bool]) -> bool:
        while node >= 2:
            var, low, high = self.nodes[node]  # type: ignore[misc]
            node = high if assignment.get(var, False) else low
        return bool(node)

    def reachable_nonterminals(self, root: int) -> int:
        seen: set[int] = set()
        stack = [root]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            if node >= 2:
                _, low, high = self.nodes[node]  # type: ignore[misc]
                stack.extend((low, high))
        return sum(node >= 2 for node in seen)


def layout(n_cells: int) -> tuple[list[int], list[int], list[int]]:
    coarse = [3 * i for i in range(n_cells)]
    fine0 = [3 * i + 1 for i in range(n_cells)]
    fine1 = [3 * i + 2 for i in range(n_cells)]
    return coarse, fine0, fine1


def extension_relation(manager: ROBDD, n_cells: int) -> int:
    coarse, fine0, fine1 = layout(n_cells)
    clauses = []
    for i in range(n_cells):
        rhs = manager.apply("or", manager.var(fine0[i]), manager.var(fine1[i]))
        clauses.append(manager.apply("eq", manager.var(coarse[i]), rhs))
    return manager.conjunction(*clauses)


def valid_coarse_support(manager: ROBDD, n_cells: int) -> int:
    coarse, _, _ = layout(n_cells)
    return manager.disjunction(*(manager.var(v) for v in coarse))


def eq0(manager: ROBDD, n_cells: int, fine_term_mask: int) -> int:
    """Compile `term=0`; fine bit positions are `(2*i+ybit)`."""
    _, fine0, fine1 = layout(n_cells)
    literals = []
    for i in range(n_cells):
        if fine_term_mask & (1 << (2 * i)):
            literals.append(manager.neg(manager.var(fine0[i])))
        if fine_term_mask & (1 << (2 * i + 1)):
            literals.append(manager.neg(manager.var(fine1[i])))
    return manager.conjunction(*literals)


def neq0(manager: ROBDD, n_cells: int, fine_term_mask: int) -> int:
    """Compile `term!=0`; fine bit positions are `(2*i+ybit)`."""
    _, fine0, fine1 = layout(n_cells)
    literals = []
    for i in range(n_cells):
        if fine_term_mask & (1 << (2 * i)):
            literals.append(manager.var(fine0[i]))
        if fine_term_mask & (1 << (2 * i + 1)):
            literals.append(manager.var(fine1[i]))
    return manager.disjunction(*literals)


def existentially_eliminate_new_ba_var(
    manager: ROBDD, n_cells: int, fine_formula: int
) -> int:
    coarse, fine0, fine1 = layout(n_cells)
    del coarse
    constrained = manager.conjunction(
        extension_relation(manager, n_cells), fine_formula
    )
    projected = manager.exists(constrained, set(fine0 + fine1))
    return manager.conjunction(valid_coarse_support(manager, n_cells), projected)


def coarse_assignment(n_cells: int, support_mask: int) -> dict[int, bool]:
    coarse, _, _ = layout(n_cells)
    return {var: bool(support_mask & (1 << i)) for i, var in enumerate(coarse)}


def enumerate_extensions(coarse_support: int, n_cells: int) -> list[int]:
    active = [i for i in range(n_cells) if coarse_support & (1 << i)]
    out = []
    for choices in product((1, 2, 3), repeat=len(active)):
        fine = 0
        for cell, choice in zip(active, choices):
            if choice & 1:
                fine |= 1 << (2 * cell)
            if choice & 2:
                fine |= 1 << (2 * cell + 1)
        out.append(fine)
    return out


# Tiny expression language used for differential tests.
Expression = tuple


def evaluate_expression(expr: Expression, fine_support: int) -> bool:
    op = expr[0]
    if op == "atom":
        _, kind, term_mask = expr
        intersects = bool(fine_support & term_mask)
        return (not intersects) if kind == "eq0" else intersects
    if op == "not":
        return not evaluate_expression(expr[1], fine_support)
    if op == "and":
        return evaluate_expression(expr[1], fine_support) and evaluate_expression(
            expr[2], fine_support
        )
    if op == "or":
        return evaluate_expression(expr[1], fine_support) or evaluate_expression(
            expr[2], fine_support
        )
    raise ValueError(op)


def compile_expression(manager: ROBDD, n_cells: int, expr: Expression) -> int:
    op = expr[0]
    if op == "atom":
        _, kind, term_mask = expr
        return (
            eq0(manager, n_cells, term_mask)
            if kind == "eq0"
            else neq0(manager, n_cells, term_mask)
        )
    if op == "not":
        return manager.neg(compile_expression(manager, n_cells, expr[1]))
    if op in {"and", "or"}:
        return manager.apply(
            op,
            compile_expression(manager, n_cells, expr[1]),
            compile_expression(manager, n_cells, expr[2]),
        )
    raise ValueError(op)


def random_expression(rng: random.Random, n_cells: int, depth: int) -> Expression:
    if depth <= 0 or rng.random() < 0.35:
        term_mask = rng.randrange(0, 1 << (2 * n_cells))
        return ("atom", rng.choice(("eq0", "neq0")), term_mask)
    if rng.random() < 0.2:
        return ("not", random_expression(rng, n_cells, depth - 1))
    return (
        rng.choice(("and", "or")),
        random_expression(rng, n_cells, depth - 1),
        random_expression(rng, n_cells, depth - 1),
    )


def self_test() -> None:
    # Under the local interleaved variable order the reduced BDD for Ext has
    # exactly five nonterminal nodes per coarse minterm cell.
    for k in range(5):
        n_cells = 1 << k
        manager = ROBDD()
        ext = extension_relation(manager, n_cells)
        assert manager.reachable_nonterminals(ext) == 5 * n_cells

    # Semantic identities for k=2 retained BA variables.
    k = 2
    n_cells = 1 << k
    manager = ROBDD()
    y_mask = sum(1 << (2 * i + 1) for i in range(n_cells))
    not_y_mask = sum(1 << (2 * i) for i in range(n_cells))

    exists_y_eq_0 = existentially_eliminate_new_ba_var(
        manager, n_cells, eq0(manager, n_cells, y_mask)
    )
    exists_nontrivial_y = existentially_eliminate_new_ba_var(
        manager,
        n_cells,
        manager.apply(
            "and",
            neq0(manager, n_cells, y_mask),
            neq0(manager, n_cells, not_y_mask),
        ),
    )
    impossible = existentially_eliminate_new_ba_var(
        manager,
        n_cells,
        manager.apply(
            "and",
            eq0(manager, n_cells, y_mask),
            eq0(manager, n_cells, not_y_mask),
        ),
    )

    # y = x_0 is `(y XOR x_0)=0`.
    xor_mask = 0
    for coarse_cell in range(n_cells):
        x0 = coarse_cell & 1
        for y in (0, 1):
            if x0 != y:
                xor_mask |= 1 << (2 * coarse_cell + y)
    exists_y_eq_x0 = existentially_eliminate_new_ba_var(
        manager, n_cells, eq0(manager, n_cells, xor_mask)
    )

    for support in range(1, 1 << n_cells):
        assignment = coarse_assignment(n_cells, support)
        assert manager.evaluate(exists_y_eq_0, assignment)
        assert manager.evaluate(exists_nontrivial_y, assignment)
        assert not manager.evaluate(impossible, assignment)
        assert manager.evaluate(exists_y_eq_x0, assignment)

    # Differential test: BDD projection versus exhaustive ternary refinement.
    rng = random.Random(7)
    for k in (1, 2):
        n_cells = 1 << k
        for _ in range(200):
            expr = random_expression(rng, n_cells, depth=4)
            manager = ROBDD()
            fine_bdd = compile_expression(manager, n_cells, expr)
            projected = existentially_eliminate_new_ba_var(
                manager, n_cells, fine_bdd
            )
            for coarse_support in range(1, 1 << n_cells):
                expected = any(
                    evaluate_expression(expr, fine_support)
                    for fine_support in enumerate_extensions(
                        coarse_support, n_cells
                    )
                )
                actual = manager.evaluate(
                    projected, coarse_assignment(n_cells, coarse_support)
                )
                assert actual == expected


def main() -> None:
    self_test()
    print("support-level ABA ROBDD self-tests passed")
    for k in range(5):
        n_cells = 1 << k
        manager = ROBDD()
        ext = extension_relation(manager, n_cells)
        print(
            f"k={k}: coarse cells={n_cells:2d}, "
            f"Ext ROBDD nonterminals={manager.reachable_nonterminals(ext):3d}"
        )


if __name__ == "__main__":
    main()
