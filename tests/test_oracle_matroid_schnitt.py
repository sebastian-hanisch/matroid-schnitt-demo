"""Orakel (ORACLE-PLAYBOOK §5): anderer Rechenweg als der der Demo.

1. Optimum und gemeinsame Mengen: Regenbogen mit networkx (is_forest, verschiedene Farben), Zuordnung mit networkx (bipartites Matching auf dem Doppelgraphen),
   Arboreszenz mit networkx (maximales Branching ohne Bögen in die Wurzel); jeweils gegen Aufzählung mit eigener Unabhängigkeitsprüfung.
2. Austauschgraph und Weg: Pfeile aus Mengenoperationen neu berechnet, Länge des kürzesten Weges mit networkx.
3. Min-Max: Rang durch Aufzählung der unabhängigen Teilmengen (ohne die Rangtabelle der App).
4. Greedy ≥ ½ Optimum auf allen Paaren von Matroiden mit höchstens 4 Elementen, mit einfachen Schleifen.
5. Literatur: Matroide 2, 5, 16, 68, 406."""

import itertools
import random

import numpy as np
import pytest

import msc_algorithm as A
import msc_constants as C
import msc_systems as S

nx = pytest.importorskip("networkx")


def _forest(v, edges, mask):
    g = nx.MultiGraph()
    g.add_nodes_from(range(v))
    g.add_edges_from(edges[e] for e in range(len(edges)) if mask >> e & 1)
    return nx.is_forest(g)


def _common_by_definition(pair, member1, member2):
    return [mask for mask in range(1 << pair.m) if member1(mask) and member2(mask)]


def _brute_summary(common, m):
    cs = set(common)
    opt = max(bin(c).count("1") for c in cs)
    maximal = [c for c in cs if not any(c | 1 << e in cs for e in range(m) if not c >> e & 1)]
    return opt, sorted(bin(c).count("1") for c in maximal), len(cs)


def test_regenbogen_equals_the_networkx_definition_on_several_plans():
    for n, seed, k in ((6, 0, 5), (6, 3, 3), (7, 8, 6), (7, 2, 4)):
        p = S.get_pair("regenbogen", n, seed, k)
        edges = [(u, w) for u, w, _ in p.inst.edges]
        common = _common_by_definition(p, lambda mask: _forest(n, edges, mask), lambda mask: len({p.colors[e] for e in range(p.m) if mask >> e & 1}) == bin(mask).count("1"))
        opt, maximal_sizes, count = _brute_summary(common, p.m)
        assert (p.opt, sorted(map(int, A.pc_table()[p.maximal])), p.n_common) == (opt, maximal_sizes, count), (n, seed, k)


def test_zuordnung_equals_the_maximum_bipartite_matching_of_networkx():
    for n, seed in ((6, 0), (6, 4), (7, 8), (7, 1), (8, 2)):
        p = S.get_pair("zuordnung", n, seed, 0)
        edges = [(u, w) for u, w, _ in p.inst.edges]
        g = nx.Graph()
        left = [("L", u) for u in range(n)]
        g.add_nodes_from(left, bipartite=0)
        g.add_nodes_from([("R", u) for u in range(n)], bipartite=1)
        g.add_edges_from((("L", u), ("R", w)) for u, w in edges)
        matching = nx.bipartite.maximum_matching(g, top_nodes=left)
        assert p.opt == len(matching) // 2, (n, seed)
        # jede gemeinsame Menge ist ein Matching im Doppelgraphen
        for mask in random.Random(seed).sample(range(1 << p.m), 200):
            used_l = [edges[e][0] for e in range(p.m) if mask >> e & 1]
            used_r = [edges[e][1] for e in range(p.m) if mask >> e & 1]
            assert bool(p.common[mask]) == (len(set(used_l)) == len(used_l) and len(set(used_r)) == len(used_r))


def test_arboreszenz_equals_the_maximum_branching_of_networkx_and_the_brute_force():
    arcs = C.ARBORESCENCE_ARCS
    p = S.get_pair("arboreszenz", 6, 8, 6)
    g = nx.DiGraph()
    g.add_nodes_from(range(6))
    g.add_edges_from((a, b) for a, b in arcs if b != 0)
    branching = nx.maximum_branching(g)
    assert p.opt == branching.number_of_edges() == 5
    common = _common_by_definition(p, lambda mask: _forest(6, list(arcs), mask), lambda mask: all(arcs[e][1] != 0 for e in range(p.m) if mask >> e & 1) and
                                   len({arcs[e][1] for e in range(p.m) if mask >> e & 1}) == bin(mask).count("1"))
    assert _brute_summary(common, p.m) == (p.opt, sorted(map(int, A.pc_table()[p.maximal])), p.n_common)


def _explicit_graph(pair, cur):
    """Austauschgraph zu I = cur aus Mengenoperationen, ohne exchange_graph der App."""
    ins = {e for e in range(pair.m) if cur >> e & 1}
    outs = set(range(pair.m)) - ins
    arcs = []
    x1 = [x for x in outs if pair.ok1[cur | 1 << x]]
    x2 = [x for x in outs if pair.ok2[cur | 1 << x]]
    for y in ins:
        for x in outs:
            swapped = (cur - (1 << y)) | (1 << x)
            if pair.ok1[swapped]:
                arcs.append((y, x))
            if pair.ok2[swapped]:
                arcs.append((x, y))
    return x1, x2, arcs


def test_exchange_graph_and_shortest_path_agree_with_networkx():
    rng = random.Random(1)
    for key, n, seed, k in (("regenbogen", 6, 1, 5), ("zuordnung", 6, 2, 0), ("arboreszenz", 6, 8, 6)):
        p = S.get_pair(key, n, seed, k)
        commons = np.nonzero(p.common)[0].tolist()
        for cur in rng.sample(commons, min(40, len(commons))):
            g = A.exchange_graph(p, cur)
            x1, x2, arcs = _explicit_graph(p, cur)
            assert sorted(g["x1"]) == sorted(x1) and sorted(g["x2"]) == sorted(x2) and sorted((a, b) for a, b, _ in g["arcs"]) == sorted(arcs)
            d = nx.DiGraph()
            d.add_nodes_from(range(p.m))
            d.add_edges_from(arcs)
            d.add_node("S")
            d.add_edges_from(("S", x) for x in x1)
            lengths = [nx.shortest_path_length(d, "S", x) for x in x2 if nx.has_path(d, "S", x)]
            adj = {v: [] for v in range(p.m)}
            for a, b in arcs:
                adj[a].append(b)
            path, _ = A.bfs_path(x1, lambda v: v in set(x2), lambda v: adj[v])
            if lengths:
                assert path is not None and len(path) == min(lengths)                      # Knotenzahl = Pfeile von S ohne S: gleich
            else:
                assert path is None
            if path:
                assert all((a, b) in set(arcs) for a, b in zip(path, path[1:])) and path[0] in x1 and path[-1] in x2


def _brute_rank(ok_member, m, subset):
    best = 0
    sub = subset
    while True:
        if ok_member(sub):
            best = max(best, bin(sub).count("1"))
        if sub == 0:
            return best
        sub = (sub - 1) & subset


def test_min_max_with_ranks_by_enumeration_equals_the_optimum():
    p = S.get_pair("zuordnung", 6, 3, 0)
    ok1, ok2, full = p.ok1.tolist(), p.ok2.tolist(), p.full
    value = min(_brute_rank(lambda s: ok1[s], p.m, a) + _brute_rank(lambda s: ok2[s], p.m, full ^ a) for a in range(1 << p.m))
    assert value == p.opt == A.min_max(p)["value"]


def _matroid_tables(n):
    return [np.array(ok, dtype=bool) for ok in A.all_systems(n) if A.System("x", n, list(ok)).exchange_scan()[1] == 0]


def test_greedy_reaches_at_least_half_on_all_pairs_up_to_four_elements_by_simple_loops():
    for n in range(1, 5):
        mats = _matroid_tables(n)
        worst = 1.0
        fails = pairs = 0
        for t1, t2 in itertools.product(mats, mats):
            common = {mask for mask in range(1 << n) if t1[mask] and t2[mask]}
            opt, sizes, _ = _brute_summary(common, n)
            ratio = min(sizes) / opt if opt else 1.0
            worst = min(worst, ratio)
            fails += min(sizes) < opt
            pairs += 1
        assert worst >= 0.5 and (n < 3 or worst == 0.5) and pairs == len(mats) ** 2
        assert fails == {1: 0, 2: 0, 3: 6, 4: 360}[n]


def test_matroid_counts_up_to_five_elements():
    assert [len(_matroid_tables(n)) for n in range(1, 6)] == [2, 5, 16, 68, 406]
