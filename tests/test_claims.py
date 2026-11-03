"""Jede Zahl der README („Befunde“) wird hier mit den Funktionen der App nachgerechnet (DEMO-PLAYBOOK §4)."""

import re
import statistics
from pathlib import Path

import msc_algorithm as A
import msc_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")

EXAMPLES = {  # Name in der README -> (Einstellungen, Optimum, gemeinsame Mengen, maximale Mengen, Greedy scheitert, im Mittel, schlechteste, Min-Max-Mengen, Orakelaufrufe)
    "Regenbogen-Spannbaum mit 6 Farben": (ev.Settings(7, 8, "regenbogen", 6), 5, 303, ((4, 41), (5, 18)), "47,1", "90,6", "80,0", 4, (364, 150, 119)),
    "Regenbogen mit 3 Farben": (ev.Settings(7, 8, "regenbogen", 3), 3, 94, ((3, 40),), "0,0", "100,0", "100,0", 1, (200, 108, 94)),
    "Zuordnung": (ev.Settings(7, 8, "zuordnung", 6), 5, 124, ((3, 4), (4, 11), (5, 2)), "84,0", "80,1", "60,0", 97, (364, 75, 38)),
    "Arboreszenz (fest)": (ev.Settings(6, 8, "arboreszenz", 6), 5, 232, ((4, 3), (5, 21)), "7,9", "98,4", "80,0", 5, (364, 62, 24)),
}


def test_the_four_examples_on_the_plan():
    for name, (s, opt, common, maximal, fail, mean, worst, mm_count, calls) in EXAMPLES.items():
        a = ev.analyse(s)
        assert (a.opt, a.n_common, a.maximal) == (opt, common, maximal), name
        g = ev.greedy_view(s, 1000)
        fails = sum(1 for x in g["sizes"] if x < opt)
        assert (ev.prozent(fails / 1000), ev.prozent(statistics.mean(g["sizes"]) / opt), ev.prozent(g["worst"] / opt)) == (fail, mean, worst), name
        cv = ev.cert_view(s)
        assert (cv["minmax"]["value"], cv["minmax"]["count"]) == (opt, mm_count), name
        assert tuple(ev.oracle_view(s)[v]["calls"] for v in A.VARIANTS) == calls, name
        assert a.is_matroid is False, name
        line = [l for l in README.splitlines() if l.startswith("| " + name + " |")]
        maximal_text = ", ".join(f"{size}: {count}" for size, count in maximal)
        assert line and f"| {opt} | {common} | {maximal_text} | {fail} % | {mean} % | {worst} % |" in line[0], name


def test_all_small_pairs():
    rows = ev.small_rows()
    assert [r["pairs"] for r in rows] == [4, 25, 256, 4624, 164836] and sum(r["pairs"] for r in rows) == 169745
    assert [r["fail"] for r in rows] == [0, 0, 6, 360, 24210] and sum(r["fail"] for r in rows) == 24576
    assert [r["half"] for r in rows] == [0, 0, 6, 300, 10870] and sum(r["half"] for r in rows) == 11176 and all(r["below_half"] == 0 for r in rows)
    assert [r["worst"] for r in rows] == [1.0, 1.0, 0.5, 0.5, 0.5] and [r["minmax"] for r in rows] == [r["pairs"] for r in rows]
    assert [r["checked"] for r in rows] == [4, 25, 256, 4624, 6000] and sum(r["checked"] for r in rows) == 10909
    assert all(r["alg_ok"] == r["checked"] == r["cert_ok"] for r in rows)


def test_the_series_of_oracle_calls():
    expected = {
        "regenbogen": ((253, 97, 64), (385, 150, 99), (571, 202, 131)),
        "zuordnung": ((202, 52, 30), (314, 76, 41), (443, 105, 59)),
    }
    for system, rows in expected.items():
        got = ev.oracle_series(system)
        assert [(round(r["naiv"]), round(r["faul"]), round(r["faul+greedy"])) for r in got] == list(rows), system
        for n, row in zip((6, 7, 8), rows):
            assert f"n = {n}: {row[0]} / {row[1]} / {row[2]}" in README, (system, n)


def test_the_path_with_three_edges_by_hand(weg):
    assert weg.opt == 2 and A.popcount(A.greedy_common(weg, [1, 0, 2])) == 1
    assert A.steps(weg, "schlecht")[0]["path"] == [2, 1, 0]                                  # c → b → a: drei Knoten
    assert tuple(A.intersect(weg, v)["calls"] for v in A.VARIANTS) == (20, 8, 6)


def test_readme_names_every_checked_number():
    for needle in ("**164 836**", "**169 745**", "**6**, **360**, **24 210**", "(zusammen 24 576)", "6, 300 und 10 870 Paaren (zusammen **11 176**)", "**unter ½ liegt keines**", "bei **allen 169 745**",
                   "**10 909**", "(5, 3, 5, 5)", "bei 4, 1, 97, 5 Mengen A", "**364 / 150 / 119**", "200 / 108 / 94", "**364 / 75 / 38**", "**364 / 62 / 24**", "Orakelaufrufe 20 / 8 / 6",
                   "bei 6 von 256 Paaren", "6 (= n − 1 bei 7 Standorten)", "9 von 25 Paaren", "6 000 Zufallspaaren"):
        assert needle in README, needle


def test_readme_tables_have_no_decimal_points():
    table = README.split("## Befunde (gemessen, keine Behauptungen)")[1].split("## Ehrliche Grenzen")[0]
    assert not re.search(r"\d\.\d", table)
