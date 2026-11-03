"""Verdikte (reine Funktionen in msc_evaluation.py) an handgesetzten Werten: jeder Zweig, jede Zahl im Text (DEMO-PLAYBOOK §4)."""

import msc_algorithm as A
import msc_evaluation as ev


def _setup(system="regenbogen", k=6, n=7, seed=8):
    s = ev.Settings(n, seed, system, k)
    return s, ev.analyse(s), ev.pair_of(s)


# --- Hauptansicht ------------------------------------------------------------------------------------------------------------------------


def test_round_verdict_with_a_path_names_sources_sinks_path_and_the_new_size():
    s, a, p = _setup()
    rounds = ev.run_view(s, "schlecht")
    kind, text = ev.verdict_round(a, p, rounds, 0)
    assert kind == "info" and "Runde 1: I = {A–B, A–C, A–D, A–G} (4 Elemente) (Startmenge: 4 Elemente)" in text
    assert "Quellen X1 = {A–F, E–F, F–G}, Senken X2 = {C–G}" in text and "Der kürzeste Weg hat 3 Elemente: F–G → A–G → C–G" in text and "Nach dem Tausch hat I 5 Elemente" in text


def test_round_verdict_without_a_path_gives_the_certificate_and_checks_it():
    s, a, p = _setup()
    rounds = ev.run_view(s, "schlecht")
    kind, text = ev.verdict_round(a, p, rounds, 1)
    assert kind == "success" and "**kein Weg**" in text and "mit **5** Elementen ist größtmöglich" in text and "r1(A) + r2(E ∖ A) = 3 + 2 = **5**" in text and "R = {A–D, A–F, C–D, D–G, E–F, F–G}" in text
    broken = list(rounds)
    broken[1] = {**rounds[1], "reach": 0}
    assert ev.verdict_round(a, p, broken, 1)[0] == "error"


def test_round_verdict_for_the_empty_start_and_the_empty_reach():
    s, a, p = _setup("arboreszenz", 6, 6, 8)
    rounds = ev.run_view(s, "leer")
    assert "I = ∅ (0 Elemente)" in ev.verdict_round(a, p, rounds, 0)[1] and "Startmenge" not in ev.verdict_round(a, p, rounds, 0)[1]
    kind, text = ev.verdict_round(a, p, rounds, len(rounds) - 1)
    assert kind == "success" and "R = ∅" in text and "= 5 + 0 = **5**" in text


def test_round_rows_and_groups():
    s, a, p = _setup()
    rounds = ev.run_view(s, "schlecht")
    rows = ev.round_rows(a, rounds, 0)
    assert len(rows) == 12 and sum(r["in I"] == "ja" for r in rows) == 4 and {r["im Weg"] for r in rows} == {"–", "1", "2", "3"}
    assert [r["Element"] for r in rows if r["Senke (I + e in M2)"] == "ja"] == ["C–G"]
    groups = ev.round_groups(a, rounds, 0)
    assert [g[0] for g in groups] == ["gemeinsame Menge I", "Verbesserungsweg"] and groups[1][1] == [7, 6, 4] or groups[1][1] == list(rounds[0]["path"])
    assert ev.round_groups(a, rounds, 1)[1][0] == "erreichbar von den Quellen (R)"


# --- Experiment 1 ----------------------------------------------------------------------------------------------------------------------


def _view(opt, worst, sizes, maximal, trials=None):
    return {"opt": opt, "worst": worst, "sizes": sizes, "trials": trials or len(sizes), "maximal": maximal}


def test_greedy_verdict_branches():
    _, a, _ = _setup()
    kind, text = ev.verdict_greedy(a, _view(5, 4, [5, 5, 4, 4], {4: 3, 5: 2}))
    assert kind == "warning" and "**50,0 %** der 4 Zufallsreihenfolgen" in text and "im Mittel 90,0 % davon" in text and "4 Elemente (**80,0 %** des Optimums)" in text and "hier 2,5 Elemente" in text
    kind, text = ev.verdict_greedy(a, _view(3, 3, [3, 3], {3: 40}))
    assert kind == "success" and "scheitert hier bei **keiner** der 2 Reihenfolgen" in text and "kein Matroid" in text
    assert ev.verdict_greedy(a, _view(5, 2, [5, 2], {2: 1, 5: 1}))[0] == "error"            # unter der Hälfte
    assert ev.verdict_greedy(a, _view(4, 2, [4, 2], {2: 1, 4: 1}))[0] == "warning"           # genau die Hälfte ist erlaubt


def test_greedy_rows():
    rows = ev.greedy_rows(_view(5, 4, [5, 5, 4, 4], {4: 3, 5: 2}))
    assert rows[0] == {"Größe der Greedy-Menge": 4, "maximale Mengen dieser Größe": "3", "Zufallsreihenfolgen": "2 (50,0 %)", "Anteil am Optimum": "80,0 %"}
    assert rows[1]["Anteil am Optimum"] == "100,0 %"


# --- Experiment 2 ----------------------------------------------------------------------------------------------------------------------


def test_cert_verdict_and_rows():
    s, a, p = _setup()
    cv = ev.cert_view(s)
    kind, text = ev.verdict_cert(a, cv)
    assert kind == "success" and "über alle 4 096 Mengen A ist **5**" in text and "Es wird bei 4 Mengen A angenommen" in text and "r1(A) = 3 und r2(E ∖ A) = 2" in text
    rows = ev.cert_rows(a, cv)
    assert len(rows) == 4 and all(r["Summe"] == 5 and r["r1(A)"] + r["r2(E ∖ A)"] == 5 for r in rows)
    assert ev.verdict_cert(a, {**cv, "r1": 0})[0] == "error"


# --- Experiment 3 ----------------------------------------------------------------------------------------------------------------------


def test_oracle_verdict_and_rows():
    s, a, p = _setup()
    ov = ev.oracle_view(s)
    kind, text = ev.verdict_oracle(a, ov)
    assert kind == "success" and "naiv **364**, faul **150** (Faktor 2,4 weniger), faul mit Greedy-Start **119** (Faktor 3,1 weniger als naiv)" in text and "Der Greedy-Start liefert 4 von 5 Elementen" in text
    rows = ev.oracle_rows(ov)
    assert [r["Orakelaufrufe"] for r in rows] == ["364", "150", "119"] and rows[2]["Start"] == "4 Elemente (Greedy)" and rows[0]["Start"] == "leer"
    broken = {**ov, "faul": {**ov["faul"], "set": 0}}
    assert ev.verdict_oracle(a, broken)[0] == "error"


def test_series_verdict_and_table():
    rows = [{"n": 6, "m": 10, "naiv": 202.0, "faul": 52.0, "faul+greedy": 30.0, "deficit": 0.1, "missed": 2}, {"n": 8, "m": 14, "naiv": 443.0, "faul": 105.0, "faul+greedy": 59.0, "deficit": 0.15, "missed": 3}]
    kind, text = ev.verdict_series("zuordnung", rows)
    assert kind == "success" and "Zuordnung, 20 Pläne je Größe" in text and "bei 8 Standorten im Mittel **443** Orakelaufrufe, das faule **105**, das faule mit Greedy-Start **59**" in text and "zwischen 6,7 und 7,5" in text
    assert "Regenbogen-Spannbaum mit n − 1 Farben" in ev.verdict_series("regenbogen", rows)[1]
    table = ev.series_table(rows)
    assert table[0] == {"Standorte": 6, "Leitungen": 10, "naiv": "202", "faul": "52", "faul mit Greedy-Start": "30", "Greedy-Start verfehlt das Optimum im Mittel um": "0,10"}


# --- Experiment 4 ----------------------------------------------------------------------------------------------------------------------


def test_small_verdict_and_table_and_the_error_branches():
    rows = tuple(A.small_pairs_row(n, 1000, 1) for n in (1, 2, 3))
    kind, text = ev.verdict_small(rows)
    assert kind == "success" and "Bei allen 285 Paaren von Matroiden mit höchstens 3 Elementen" in text and "Greedy kann bei 6 Paaren scheitern" in text and "genau **½** (bei 6 Paaren)" in text
    assert "bei allen 285 geprüften Paaren" in text
    table = ev.small_table(rows)
    assert table[2]["Paare mit genau ½"] == "6" and table[2]["schlechtestes Verhältnis"] == "0,500" and table[0]["Paare"] == "4"
    assert ev.verdict_small(tuple({**r, "below_half": 1} if r["n"] == 3 else r for r in rows))[0] == "error"
    assert ev.verdict_small(tuple({**r, "minmax": r["minmax"] - 1} if r["n"] == 3 else r for r in rows))[0] == "error"
    assert ev.verdict_small(tuple({**r, "alg_ok": r["alg_ok"] - 1} if r["n"] == 3 else r for r in rows))[0] == "error"
    assert ev.verdict_small(tuple({**r, "cert_ok": r["cert_ok"] - 1} if r["n"] == 3 else r for r in rows))[0] == "error"


# --- Spielwiese ------------------------------------------------------------------------------------------------------------------------


def test_play_verdict_path_and_certificate_text():
    s, a, p = _setup()
    kind, text = ev.verdict_play(a, p, ev.play_view(s, ev.pair_of(s).worst_set))
    assert kind == "info" and "I hat 4 Elemente; Quellen X1 = {A–F, E–F, F–G}, Senken X2 = {C–G}, 33 Pfeile." in text and "Kürzester Verbesserungsweg (3 Elemente): F–G → A–G → C–G; danach hat I 5 Elemente." in text
    final = ev.run_view(s, "leer")[-1]["set"]
    kind, text = ev.verdict_play(a, p, ev.play_view(s, final))
    assert kind == "success" and "Kein Weg: I ist größtmöglich (5)" in text and "= 3 + 2 = 5" in text or "= 5" in text


def test_number_helpers():
    assert ev.de(1.5, 1) == "1,5" and ev.prozent(0.625) == "62,5" and ev.zahl(1234567) == "1 234 567" and ev.elemente(1) == "1 Element" and ev.elemente(3) == "3 Elemente"
