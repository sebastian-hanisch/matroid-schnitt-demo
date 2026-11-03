"""Eigenschaftstests (Schicht „Eigenschaften“, siehe Eigenschaftstests-Pilot): Invarianten auf Zufallspaaren mit festem Seed."""

import random

import numpy as np

import msc_algorithm as A
from msc_algorithm import Pair

SEED = 20261109


def _random_matroid(rng, n):
    kind = rng.choice(["uniform", "partition", "graphic", "gf2"])
    if kind == "uniform":
        k = rng.randint(0, n)
        return np.array([bin(mask).count("1") <= k for mask in range(1 << n)])
    if kind == "partition":
        return A.partition_table(n, [rng.randint(0, 2) for _ in range(n)], {c: rng.randint(1, 2) for c in range(3)})
    if kind == "graphic":
        v = rng.randint(2, 5)
        return A.graphic_table(v, [(rng.randrange(v), rng.randrange(v)) for _ in range(n)])
    vec = [rng.getrandbits(3) for _ in range(n)]

    def indep(mask):
        basis = []
        for e in range(n):
            if mask >> e & 1:
                x = vec[e]
                for b in basis:
                    x = min(x, x ^ b)
                if not x:
                    return False
                basis.append(x)
        return True

    return np.array([indep(mask) for mask in range(1 << n)])


def _pairs(count=60):
    rng = random.Random(SEED)
    out = []
    for _ in range(count):
        n = rng.randint(2, 6)
        out.append(Pair("zufall", n, _random_matroid(rng, n), _random_matroid(rng, n), tuple(str(i) for i in range(n)), "kanten"))
    return out


def test_every_variant_finds_the_optimum_and_the_certificate_matches():
    for p in _pairs():
        for v in A.VARIANTS:
            r = A.intersect(p, v)
            assert A.popcount(r["set"]) == p.opt and p.common[r["set"]]
        r = A.intersect(p, "faul")
        assert A.certificate(p, r["reach"])[2] == p.opt == A.min_max(p)["value"]


def test_each_round_adds_exactly_one_element_with_an_odd_alternating_path():
    for p in _pairs():
        rounds = A.steps(p, "leer")
        for rd, nxt in zip(rounds, rounds[1:]):
            assert A.popcount(nxt["set"]) == A.popcount(rd["set"]) + 1 and p.common[nxt["set"]]
            path = rd["path"]
            assert len(path) % 2 == 1 and all(not rd["set"] >> v & 1 for v in path[::2]) and all(rd["set"] >> v & 1 for v in path[1::2])
            assert nxt["set"] == rd["set"] ^ sum(1 << v for v in path)
        assert rounds[-1]["path"] is None and len(rounds) == p.opt + 1


def test_greedy_reaches_at_least_half_of_the_optimum_for_every_maximal_set():
    for p in _pairs():
        sizes = A.pc_table()[p.maximal]
        assert (2 * sizes >= p.opt).all()
        rng = random.Random(1)
        for _ in range(10):
            order = list(range(p.m))
            rng.shuffle(order)
            assert 2 * A.popcount(A.greedy_common(p, order)) >= p.opt


def test_lazy_never_needs_more_oracle_calls_than_naive_and_greedy_start_saves_rounds():
    for p in _pairs():
        naiv, faul, greedy = (A.intersect(p, v) for v in A.VARIANTS)
        assert faul["calls"] <= naiv["calls"] and naiv["rounds"] == faul["rounds"] == p.opt
        assert greedy["rounds"] == p.opt - greedy["start"] and greedy["start"] >= (p.opt + 1) // 2


def test_swapping_the_matroids_and_relabeling_keep_the_optimum_and_the_maximal_sizes():
    rng = random.Random(SEED + 1)
    for p in _pairs(30):
        swapped = Pair("v", p.m, p.ok2, p.ok1, p.labels, "kanten")
        perm = list(range(p.m))
        rng.shuffle(perm)
        idx = np.arange(1 << p.m)
        new = np.zeros(1 << p.m, dtype=np.int64)
        for e in range(p.m):
            new |= ((idx >> e) & 1) << perm[e]
        ok1, ok2 = np.zeros(1 << p.m, dtype=bool), np.zeros(1 << p.m, dtype=bool)
        ok1[new], ok2[new] = p.ok1, p.ok2
        relabeled = Pair("r", p.m, ok1, ok2, p.labels, "kanten")
        for q in (swapped, relabeled):
            assert q.opt == p.opt and A.maximal_sizes(q) == A.maximal_sizes(p) and A.min_max(q)["value"] == p.opt


def test_weak_duality_holds_for_every_subset_a():
    for p in _pairs(30):
        idx = np.arange(1 << p.m)
        assert (p.ur1[idx] + p.ur2[p.full ^ idx] >= p.opt).all()


def test_the_intersection_of_a_matroid_with_a_free_matroid_is_that_matroid():
    rng = random.Random(SEED + 2)
    for _ in range(15):
        n = rng.randint(2, 6)
        t = _random_matroid(rng, n)
        p = Pair("m", n, t, np.ones(1 << n, dtype=bool), tuple(str(i) for i in range(n)), "kanten")
        assert A.maximal_sizes(p) == {int(p.opt): len(p.maximal)} and A.intersection_is_matroid(p) is True
