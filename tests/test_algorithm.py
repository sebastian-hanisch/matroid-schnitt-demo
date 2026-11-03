"""Einheiten des Kerns an Mini-Instanzen von Hand (DEMO-PLAYBOOK §1b, §4)."""

import numpy as np
import pytest

import msc_algorithm as A
import msc_constants as C
import msc_systems as S


def test_tables_of_the_path_pair(weg):
    assert weg.ok1.tolist() == [True, True, True, False, True, True, True, False]            # {a, b} und {a, b, c} gehören nicht dazu
    assert weg.ok2.tolist() == [True, True, True, True, True, True, False, False]
    assert int(weg.common.sum()) == weg.n_common == 5 and weg.opt == 2 and weg.opt_set == 5 and weg.worst_set == 2
    assert weg.maximal.tolist() == [2, 5] and A.maximal_sizes(weg) == {1: 1, 2: 1}


def test_ranks_and_the_min_max_value_of_the_path_pair(weg):
    assert weg.ur1[7] == 2 and weg.ur2[7] == 2 and weg.ur1[3] == 1 and weg.ur2[6] == 1
    mm = A.min_max(weg)
    assert mm["value"] == 2 and mm["count"] == 4 and mm["first"] == [0, 1, 3, 7]               # ∅, {a}, {a, b}, E


def test_greedy_by_hand(weg):
    assert A.greedy_common(weg, [1, 0, 2]) == 2                    # b zuerst blockiert a (M1) und c (M2)
    assert A.greedy_common(weg, [0, 1, 2]) == 5
    assert A.popcount(A.greedy_common(weg, [1, 0, 2])) * 2 == weg.opt                        # genau die Hälfte


def test_exchange_graph_at_the_bad_set(weg):
    g = A.exchange_graph(weg, 2)                                 # I = {b}
    assert g["out"] == [0, 2] and g["inn"] == [1] and g["x1"] == [2] and g["x2"] == [0]
    assert sorted(g["arcs"]) == [(0, 1, 2), (1, 0, 1), (1, 2, 1), (2, 1, 2)]


def test_steps_from_the_bad_set_and_from_the_empty_set(weg):
    bad = A.steps(weg, "schlecht")
    assert [r["set"] for r in bad] == [2, 5] and bad[0]["path"] == [2, 1, 0] and bad[1]["path"] is None and bad[1]["reach"] == 0
    assert A.certificate(weg, bad[1]["reach"]) == (2, 0, 2)                                    # r1(E) + r2(∅) = 2
    empty = A.steps(weg, "leer")
    assert [r["set"] for r in empty] == [0, 1, 5] and [r["path"] for r in empty] == [[0], [2], None]
    assert [r["set"] for r in A.steps(weg, "greedy")] == [5]


def test_the_three_variants_count_oracle_calls_by_hand(weg):
    naiv, faul, greedy = (A.intersect(weg, v) for v in A.VARIANTS)
    assert (naiv["calls"], faul["calls"], greedy["calls"]) == (20, 8, 6)          # Handrechnung in PLAN-07: 6 + 8 + 6, 4 + 3 + 1, 5 + 1
    assert [A.popcount(r["set"]) for r in (naiv, faul, greedy)] == [2, 2, 2]
    assert (naiv["rounds"], faul["rounds"], greedy["rounds"]) == (2, 2, 0) and greedy["start"] == 2 and naiv["lengths"] == [1, 1]


def test_oracle_counts_every_question():
    o = A.Oracle([True, False])
    assert (o(0), o(1), o.calls) == (True, False, 2)


def test_certificate_is_the_weak_duality_bound_for_every_a(weg):
    for a in range(8):
        assert int(weg.ur1[a] + weg.ur2[7 ^ a]) >= weg.opt


def test_triangle_with_two_equal_colors(dreieck_farben):
    p = dreieck_farben
    assert p.opt == 2 and A.maximal_sizes(p) == {2: 2} and sorted(p.maximal.tolist()) == [5, 6]       # {a, c}, {b, c}
    assert [A.popcount(A.greedy_common(p, o)) for o in ([0, 1, 2], [1, 0, 2], [2, 0, 1])] == [2, 2, 2]


def test_free_pair_has_optimum_m_and_no_path_needed(frei):
    assert frei.opt == 3 and A.maximal_sizes(frei) == {3: 1} and [r["path"] for r in A.steps(frei, "leer")] == [[0], [1], [2], None]
    assert A.intersection_is_matroid(frei) is True


def test_the_intersection_of_the_path_pair_is_not_a_matroid(weg):
    assert A.intersection_is_matroid(weg) is False
    assert A.intersection_is_matroid(S.get_pair("regenbogen", 9, 8, 6)) is None                # 16 Elemente: nicht gerechnet


def test_partition_and_graphic_tables():
    assert A.partition_table(3, [0, 0, 1]).tolist() == [True, True, True, False, True, True, True, False]
    assert A.partition_table(3, ["wurzel", 1, 1], {"wurzel": 0}).tolist() == [True, False, True, False, True, False, False, False]
    assert A.graphic_table(3, [(0, 1), (1, 2), (0, 2)]).tolist() == [True, True, True, True, True, True, True, False]
    assert A.graphic_table(2, [(0, 0), (0, 1)]).tolist() == [True, False, True, False]                 # Schleife nie unabhängig


def test_rank_table_matches_the_definition():
    ok = np.array([True, True, True, False, True, True, False, False])
    assert A.rank_table(ok, 3).tolist() == [0, 1, 1, 1, 1, 2, 1, 2]


def test_small_pairs_row_for_three_elements():
    r = A.small_pairs_row(3, 6000, 1)
    assert (r["matroids"], r["pairs"], r["fail"], r["half"], r["below_half"], r["minmax"], r["checked"], r["alg_ok"], r["cert_ok"]) == (16, 256, 6, 6, 0, 256, 256, 256, 256) and r["worst"] == 0.5
    assert A.small_pairs_row(5 - 4, 10, 1)["pairs"] == 4


def test_all_systems_counts():
    assert [len(A.all_systems(n)) for n in range(1, 5)] == [2, 5, 19, 167]


def test_build_pair_examples_and_errors():
    arb = S.get_pair("arboreszenz", 9, 123, 8)
    assert arb is S.get_pair("arboreszenz", 6, 1, 3) and arb.m == 12 and arb.kind == "boegen" and arb.opt == 5 and arb.labels[0] == "0→1"
    zu = S.get_pair("zuordnung", 6, 8, 2)
    assert zu is S.get_pair("zuordnung", 6, 8, 7) and zu.kind == "kanten" and zu.m == 10
    rg = S.get_pair("regenbogen", 6, 8, 5)
    assert len(rg.colors) == rg.m and set(rg.colors) <= set(range(5)) and rg.opt <= 5
    with pytest.raises(ValueError):
        S.build_pair("gibtsnicht", 6, 1, 3)


def test_edge_colors_are_deterministic_and_inside_the_range():
    inst = S.make_instance(7, 8)
    assert S.edge_colors(inst, 8, 4) == S.edge_colors(inst, 8, 4) and set(S.edge_colors(inst, 8, 4)) <= {0, 1, 2, 3} and S.color_name(2) == "F3"
    assert C.K_MIN <= C.DEFAULT_K <= C.K_MAX
