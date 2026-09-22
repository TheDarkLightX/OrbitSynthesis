"""Fixed-Q safety via viability envelopes and binary symmetry obstructions.

Original research prototype; stdlib only. Q=(0,1,2; d,u),
d(x,y,z)=z if x==y else x, u=(1,0,1). One Q-valued environment input.
A semantic controller table is certified by the classical quasi-primal
characterization, NOT an emitted d/u term DAG. No Tau code or dependency.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from typing import Iterable


def bits(mask: int):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def digest(obj) -> str:
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class QGame:
    k: int
    rows: tuple[int, ...]  # three successor bitsets per lexicographic Q^k state

    def __post_init__(self):
        if type(self.k) is not int or self.k < 1:
            raise ValueError("positive integer state arity required")
        n = 3 ** self.k
        if len(self.rows) != 3*n or any(type(x) is not int or x < 0 or x.bit_length() > n for x in self.rows):
            raise ValueError("invalid successor bitsets")

    @property
    def n(self):
        return 3 ** self.k

    def wire(self):
        return {"schema": "orbit-synthesis/q-obstruction-game/v1", "k": self.k,
                "rows": [list(bits(row)) for row in self.rows]}


class Engine:
    def __init__(self, game: QGame):
        self.game = game
        self.states = tuple(product(range(3), repeat=game.k))
        self.index = {s: j for j, s in enumerate(self.states)}
        self.full = (1 << game.n)-1
        self.boolean = tuple(j for j,s in enumerate(self.states) if 2 not in s)
        self.bmask = sum(1 << j for j in self.boolean)
        self.bar = {j: self.index[tuple(1-x for x in self.states[j])] for j in self.boolean}
        self.pairs = tuple((j,self.bar[j]) for j in self.boolean if j < self.bar[j])
        # Generated-subalgebra admissibility. No safety-symmetry premise needed.
        self.local = tuple(row & self.bmask if s in self.bar and i < 2 else row
                           for s in range(game.n) for i,row in enumerate(game.rows[3*s:3*s+3]))

    def validate_mask(self, mask: int):
        if type(mask) is not int or mask < 0 or mask & ~self.full:
            raise ValueError("invalid state mask")

    def envelope(self, allowed: int):
        """Largest locally admissible safety invariant contained in allowed."""
        self.validate_mask(allowed)
        w, rounds = allowed, []
        while True:
            dead = sum(1 << s for s in bits(w)
                       if any(not (self.local[3*s+i] & w) for i in range(3)))
            if not dead:
                return w, rounds
            rounds.append(dead)
            w &= ~dead

    def conflict(self, w: int):
        """A pair in W whose paired Boolean observations have no shared seed."""
        for s,t in self.pairs:
            if not (w >> s & 1 and w >> t & 1):
                continue
            for i in (0,1):
                left = self.local[3*s+i] & w
                right = self.local[3*t+1-i] & w
                if not any(right >> self.bar[y] & 1 for y in bits(left)):
                    return s,t,i
        return None

    def strategy(self, w: int):
        """Complete total Q-term-compatible table, including inactive rows."""
        if self.envelope(w)[0] != w or self.conflict(w) is not None:
            raise ValueError("domain is not Q-term winning")
        table = [-1]*(3*self.game.n)
        for s,t in self.pairs:
            for i in (0,1):
                candidates = self.bmask
                if w >> s & 1:
                    candidates &= self.local[3*s+i] & w
                if w >> t & 1:
                    right = self.local[3*t+1-i] & w
                    candidates &= sum(1 << self.bar[y] for y in bits(right))
                if not candidates:
                    raise ValueError("empty paired response")
                y = next(bits(candidates))
                table[3*s+i], table[3*t+1-i] = y, self.bar[y]
        for s in range(self.game.n):
            for i in range(3):
                if table[3*s+i] >= 0:
                    continue
                choices = self.local[3*s+i] & w if w >> s & 1 else (1 << s)
                if not choices:
                    raise ValueError("empty independent response")
                table[3*s+i] = next(bits(choices))
        return table

    def solve(self, *, required: int = 0, forbidden: int = 0,
              weights: Iterable[int] | None = None, decision: bool = False):
        """Exact feasibility / nonnegative utility optimization.

        Exponential only in initially viable complementary state pairs d.
        Negative utilities are rejected: maximal-envelope search is not sound
        for signed optimization. Feasibility uses explicit required states.
        """
        self.validate_mask(required); self.validate_mask(forbidden)
        ws = tuple(weights) if weights is not None else (1,)*self.game.n
        if len(ws) != self.game.n or any(type(v) is not int or v < 0 for v in ws):
            raise ValueError("weights must be nonnegative integers")
        allowed = self.full & ~forbidden
        root_env = self.envelope(allowed)[0]
        d = sum(bool(root_env >> a & 1 and root_env >> b & 1) for a,b in self.pairs)
        stats = {"nodes":0,"splits":0,"feasible_leaves":0,"required_rejections":0,
                 "max_depth":0,"initial_pairs":d,"root_envelope_size":root_env.bit_count()}
        leaves = []

        def visit(a,depth):
            stats["nodes"] += 1; stats["max_depth"] = max(stats["max_depth"],depth)
            w, rounds = self.envelope(a)
            node = {"allowed":hex(a),"envelope":hex(w),"removed":[hex(x) for x in rounds]}
            if required & ~w:
                stats["required_rejections"] += 1
                node["kind"] = "required_missing"
                return node, False
            bad = self.conflict(w)
            if bad is None:
                stats["feasible_leaves"] += 1
                leaves.append(w); node["kind"] = "feasible"
                return node, True
            s,t,i = bad
            stats["splits"] += 1
            node.update(kind="split",pair=[s,t],input=i,children=[])
            found = False
            for removed in (s,t):
                child, ok = visit(w & ~(1 << removed),depth+1)
                node["children"].append(child); found |= ok
                if decision and ok:
                    node["short_circuit"] = True
                    break
            return node, found

        tree, _ = visit(allowed,0)
        best = max(leaves, key=lambda w:(sum(ws[s] for s in bits(w)), w.bit_count(),w)) if leaves else None
        result = {"schema":"orbit-synthesis/q-obstruction-result/v1",
                  "game_sha256":digest(self.game.wire()),"required":hex(required),
                  "forbidden":hex(forbidden),"weights":list(ws),"decision":decision,
                  "status":"feasible" if best is not None else "infeasible", "stats":stats,
                  "domain":hex(best) if best is not None else None,
                  "score":sum(ws[s] for s in bits(best)) if best is not None else None,
                  "strategy":self.strategy(best) if best is not None else None,"proof":tree}
        return result


def cnf_game(clauses: Iterable[Iterable[int]], nvars: int, *, min_k: int = 1,
             live_rigid_padding: bool = False):
    """Polynomial SAT reduction: one initial state, one Q input, Q fixed.

    Literal states are complementary Boolean pairs. A dead complement of the
    live sink turns internal equivariance into mutual exclusion. An environment
    selector tree forces every clause. Nonbinary clause states choose literals.
    """
    clauses = tuple(tuple(c) for c in clauses)
    if type(nvars) is not int or nvars < 0 or type(min_k) is not int or min_k < 1:
        raise ValueError("invalid dimensions")
    if any(type(x) is not int or x == 0 or abs(x) > nvars for c in clauses for x in c):
        raise ValueError("invalid literal")
    m = len(clauses)
    needed = max(1,2*m-1)
    k = min_k
    while 2**(k-1) < nvars+1 or 3**k-2**k < needed:
        k += 1
    states = tuple(product(range(3),repeat=k)); idx = {s:j for j,s in enumerate(states)}
    bs = [j for j,s in enumerate(states) if 2 not in s]
    bar = {j:idx[tuple(1-x for x in states[j])] for j in bs}
    reps = [s for s in bs if s < bar[s]]
    sink, dead = reps[0],bar[reps[0]]
    literals = {i+1:s for i,s in enumerate(reps[1:nvars+1])}
    literals.update({-v:bar[s] for v,s in tuple(literals.items())})
    rigid = [j for j,s in enumerate(states) if 2 in s]
    rows = [0]*(3*len(states))
    def setrow(s,i,targets):
        rows[3*s+i] = sum(1 << y for y in set(targets))
    for i in range(3): setrow(sink,i,[sink])
    for i in (0,1): setrow(dead,i,[dead])
    for s in literals.values():
        for i in (0,1): setrow(s,i,[sink,dead])
        setrow(s,2,[sink])
    used = 0
    def alloc():
        nonlocal used
        s=rigid[used]; used += 1
        return s
    clause_states=[]
    for c in clauses:
        s=alloc(); clause_states.append(s)
        for i in range(3): setrow(s,i,[literals[v] for v in c])
    def tree(nodes):
        if len(nodes)==1: return nodes[0]
        mid=len(nodes)//2
        left,right=tree(nodes[:mid]),tree(nodes[mid:])
        s=alloc()
        setrow(s,0,[left]); setrow(s,1,[right]); setrow(s,2,[sink])
        return s
    if clause_states:
        root=tree(clause_states)
    else:
        root=alloc()
        for i in range(3): setrow(root,i,[sink])
    if live_rigid_padding:
        for s in rigid[used:]:
            for i in range(3): setrow(s,i,[sink])
    return QGame(k,tuple(rows)), {"root":root,"sink":sink,"dead":dead,
                                 "literals":literals,"clause_states":clause_states,
                                 "nvars":nvars,"clauses":[list(c) for c in clauses]}


if __name__ == "__main__":
    # Minimal semantic falsifier of independent local action selection.
    game, meta = cnf_game([(1,),(-1,)],1)
    engine = Engine(game)
    result = engine.solve(required=1 << meta["root"])
    print(json.dumps({"game":game.wire(),"meta":meta,"result":result},sort_keys=True))
