"""Randfälle (DEMO-PLAYBOOK §4): kleinste Paare, Nullmatroid, gleiche Matroide, Reglergrenzen, Spielwiese."""

import numpy as np

import msc_algorithm as A
import msc_constants as C
import msc_evaluation as ev
import msc_systems as S
from msc_algorithm import Pair


def _pair(m, ok1, ok2):
    return Pair("x", m, np.array(ok1, dtype=bool), np.array(ok2, dtype=bool), tuple(str(i) for i in range(m)), "kanten")


def test_single_element_pairs():
    p = _pair(1, [True, True], [True, True])
    assert p.opt == 1 and [r["path"] for r in A.steps(p, "leer")] == [[0], None] and A.maximal_sizes(p) == {1: 1}
    q = _pair(1, [True, True], [True, False])                    # M2: das Element ist eine Schleife
    assert q.opt == 0 and A.steps(q, "leer")[-1]["path"] is None and A.certificate(q, A.steps(q, "leer")[-1]["reach"])[2] == 0


def test_the_zero_matroid_as_one_side_gives_optimum_zero_and_a_trivial_certificate():
    p = _pair(3, [True] * 8, [mask == 0 for mask in range(8)])
    rd = A.steps(p, "leer")[-1]
    assert p.opt == 0 and rd["path"] is None and rd["set"] == 0 and A.certificate(p, rd["reach"]) == (0, 0, 0) and A.min_max(p)["value"] == 0
    assert A.maximal_sizes(p) == {0: 1} and A.intersect(p, "faul+greedy")["set"] == 0


def test_identical_matroids_have_optimum_equal_to_the_rank_and_greedy_never_fails():
    t = A.partition_table(4, [0, 0, 1, 1])
    p = Pair("gleich", 4, t, t.copy(), ("a", "b", "c", "d"), "kanten")
    assert p.opt == 2 and A.maximal_sizes(p) == {2: 4} and all(A.popcount(A.greedy_common(p, o)) == 2 for o in ([0, 1, 2, 3], [3, 2, 1, 0], [1, 3, 0, 2]))


def test_swapping_the_two_matroids_keeps_the_optimum_and_the_certificate_value(weg):
    swapped = Pair("vertauscht", weg.m, weg.ok2, weg.ok1, weg.labels, "kanten")
    assert swapped.opt == weg.opt and A.min_max(swapped)["value"] == weg.opt
    rd = A.steps(swapped, "schlecht")[-1]
    assert A.certificate(swapped, rd["reach"])[2] == weg.opt


def test_empty_start_set_in_the_playground_is_valid_and_gets_a_path():
    s = ev.Settings(system="regenbogen")
    a = ev.analyse(s)
    v = ev.play_view(s, 0)
    assert v["ok1"] and v["ok2"] and v["path"] is not None and ev.verdict_play(a, ev.pair_of(s), v)[0] == "info"


def test_playground_branches():
    s = ev.Settings(system="regenbogen")
    a, p = ev.analyse(s), ev.pair_of(s)
    bad1 = next(m for m in range(1 << p.m) if not p.ok1[m] and p.ok2[m])
    bad2 = next(m for m in range(1 << p.m) if p.ok1[m] and not p.ok2[m])
    both = next(m for m in range(1 << p.m) if not p.ok1[m] and not p.ok2[m])
    for mask, needle in ((bad1, "in M1 nicht unabhängig"), (bad2, "in M2 nicht unabhängig"), (both, "in beiden Matroiden nicht unabhängig")):
        kind, text = ev.verdict_play(a, p, ev.play_view(s, mask))
        assert kind == "info" and needle in text
    final = ev.run_view(s, "leer")[-1]["set"]
    kind, text = ev.verdict_play(a, p, ev.play_view(s, final))
    assert kind == "success" and "Kein Weg" in text and "Zertifikat" in text


def test_every_example_at_the_slider_limits_builds_and_reaches_the_brute_force_optimum():
    for key in C.SYSTEMS:
        for n in (C.N_MIN, C.N_MAX):
            for k in (C.K_MIN, C.K_MAX):
                if key != "regenbogen" and k != C.K_MIN:
                    continue
                s = ev.Settings(n, C.DEFAULT_SEED, key, k)
                p = ev.pair_of(s)
                assert all(A.popcount(r["set"]) == p.opt for r in [A.intersect(p, "faul+greedy")]), (key, n, k)
                assert p.m == (12 if key == "arboreszenz" else 2 * n - 2)


def test_regenbogen_with_two_colors_has_optimum_two_and_greedy_never_fails():
    p = S.get_pair("regenbogen", 7, 8, 2)
    assert p.opt == 2 and set(A.maximal_sizes(p)) == {2} and ev.greedy_view(ev.Settings(7, 8, "regenbogen", 2), 200)["worst"] == 2


def test_three_colors_example_shows_no_greedy_failure_but_six_colors_do():
    assert set(A.maximal_sizes(S.get_pair("regenbogen", 7, 8, 3))) == {3}
    assert min(A.maximal_sizes(S.get_pair("regenbogen", 7, 8, 6))) < S.get_pair("regenbogen", 7, 8, 6).opt


def test_oracle_series_is_unavailable_only_by_ui_but_computes_for_both_plan_examples():
    rows = ev.oracle_series("zuordnung")
    assert [r["n"] for r in rows] == list(C.SERIES_N) and all(r["naiv"] > r["faul"] > r["faul+greedy"] for r in rows)


def test_greedy_view_is_reproducible_and_counts_every_trial():
    s = ev.Settings(system="zuordnung")
    a, b = ev.greedy_view(s, 300), ev.greedy_view(s, 300)
    assert a["sizes"] == b["sizes"] and len(a["sizes"]) == 300 and set(a["sizes"]) <= set(a["maximal"])


def test_set_formatting_helpers():
    a = ev.analyse(ev.Settings(system="arboreszenz"))
    assert ev.setstr(a, 0) == "∅" and ev.setstr(a, 3) == "{0→1, 0→2}" and ev.seq(a, [0, 2]) == "0→1 → 1→2"
