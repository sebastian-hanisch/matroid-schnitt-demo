"""AppTest: Hauptansicht, Experimente, Spielwiese, Permalink und PDF (DEMO-PLAYBOOK §3, §5)."""

import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

import msc_constants as C
import msc_evaluation as ev
from msc_pdf_export import build_pdf

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))
PLAY = "regenbogen_7_8_6"


def _app(params=None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (params or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [m.value for m in list(at.success) + list(at.info) + list(at.warning) + list(at.error)]


def _click_preset(at, name):
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]


def test_default_starts_from_the_worst_maximal_set_and_shows_the_first_path():
    at = _app()
    assert any("Runde 1: I = {A–B, A–C, A–D, A–G} (4 Elemente)" in t and "F–G → A–G → C–G" in t for t in _texts(at))
    assert [m.value for m in at.metric][:4] == ["5", "6", "5", "59"]


def test_round_slider_and_start_modes():
    at = _app()
    at.slider(key=f"round_{PLAY}_schlecht").set_value(2).run()
    assert not at.exception and any("**kein Weg**" in t and "= 3 + 2 = **5**" in t for t in _texts(at))
    at.radio(key="start_mode").set_value("leer").run()
    assert not at.exception and any("Runde 1: I = ∅ (0 Elemente)" in t for t in _texts(at))
    at.radio(key="start_mode").set_value("greedy").run()
    assert not at.exception and any("Runde 1: I = {A–B, A–C, A–D, A–G}" in t for t in _texts(at))


def test_main_verdict_matches_each_preset():
    expected = {
        "Standardfall (Voreinstellung)": "Der kürzeste Weg hat 3 Elemente",
        "Drei Farben": "**kein Weg**",
        "Zuordnung": "Der kürzeste Weg hat 3 Elemente",
        "Arboreszenz (fest)": "Der kürzeste Weg hat 3 Elemente: 1→3 → 5→3 → 3→5",
    }
    at = _app()
    for name, needle in expected.items():
        _click_preset(at, name)
        assert any(needle in t for t in _texts(at)), name


def test_experiment_one_greedy_changes_with_the_trials_and_the_preset():
    at = _app()
    assert any("Greedy liefert bei **47,1 %** der 1 000 Zufallsreihenfolgen" in t for t in _texts(at))
    at.slider(key="trials_slider").set_value(100).run()
    assert not at.exception and any("der 100 Zufallsreihenfolgen" in t for t in _texts(at))
    _click_preset(at, "Drei Farben")
    assert any("scheitert hier bei **keiner**" in t for t in _texts(at))


def test_experiment_two_certificate():
    at = _app()
    assert any("über alle 4 096 Mengen A ist **5**" in t and "bei 4 Mengen A angenommen" in t for t in _texts(at))
    _click_preset(at, "Zuordnung")
    assert any("bei 97 Mengen A angenommen" in t for t in _texts(at))


def test_experiment_three_oracle_counts_and_the_series_on_demand():
    at = _app()
    assert any("naiv **364**, faul **150**" in t for t in _texts(at))
    assert not any("20 Pläne je Größe" in t for t in _texts(at))
    at.button(key="series_run").click().run()
    assert not at.exception and any("Regenbogen-Spannbaum mit n − 1 Farben, 20 Pläne je Größe" in t and "bei 8 Standorten im Mittel **571**" in t for t in _texts(at))
    _click_preset(at, "Arboreszenz (fest)")
    assert any("Die Messreihe über mehrere Pläne gibt es nur für" in t for t in _texts(at))


def test_experiment_four_small_pairs_on_demand():
    at = _app()
    assert not any("169 745" in t for t in _texts(at))
    at.button(key="small_run").click().run()
    assert not at.exception and any("Bei allen 169 745 Paaren von Matroiden mit höchstens 5 Elementen" in t and "genau **½** (bei 11 176 Paaren)" in t for t in _texts(at))
    _click_preset(at, "Zuordnung")
    assert any("169 745" in t for t in _texts(at))                  # das Ergebnis bleibt nach anderen Änderungen


def test_every_example_runs_without_exception_and_has_a_verdict():
    at = _app()
    for system in C.SYSTEMS:
        at.sidebar.selectbox(key="system_select").set_value(system).run()
        assert not at.exception, (system, [str(e) for e in at.exception])
        texts = _texts(at)
        assert any(t.startswith("Runde ") for t in texts) and any("Mengen A" in t for t in texts) and any("Orakelaufrufe" in t for t in texts), system


def test_color_slider_changes_the_regenbogen():
    at = _app()
    at.sidebar.slider(key="k_slider").set_value(3).run()
    assert not at.exception and any("scheitert hier bei **keiner**" in t for t in _texts(at))
    at.sidebar.slider(key="k_slider").set_value(2).run()
    assert not at.exception and any("mit **2** Elementen ist größtmöglich" in t or "2 Elementen" in t for t in _texts(at))


def test_playground_branches():
    at = _app()
    assert any("Kürzester Verbesserungsweg" in t for t in _texts(at))
    at.multiselect(key=f"play_i_{PLAY}").set_value([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]).run()
    assert not at.exception and any("nicht unabhängig" in t for t in _texts(at))
    at.multiselect(key=f"play_i_{PLAY}").set_value([]).run()
    assert not at.exception and any(t.startswith("I hat 0 Elemente") for t in _texts(at))


def test_permalink_loads_valid_values_and_ignores_invalid_choices():
    at = _app(dict(n="8", seed="3", system="zuordnung", k="4"))
    assert at.sidebar.slider(key="n_slider").value == 8 and at.sidebar.number_input(key="seed_input").value == 3 and at.sidebar.selectbox(key="system_select").value == "zuordnung"
    assert at.sidebar.slider(key="k_slider").value == 4
    bad = _app(dict(n="99", seed="-4", system="gibtsnicht", k="99"))
    assert bad.sidebar.slider(key="n_slider").value == C.N_MAX and bad.sidebar.number_input(key="seed_input").value == 0 and bad.sidebar.selectbox(key="system_select").value == "regenbogen"
    assert bad.sidebar.slider(key="k_slider").value == C.K_MAX


def test_address_line_mirrors_the_settings():
    at = _app(dict(system="zuordnung"))
    assert str(at.query_params["system"]) in ("zuordnung", "['zuordnung']")


def test_pdf_button_makes_a_download():
    at = _app()
    at.button(key="pdf_make").click().run()
    assert not at.exception and "pdf_made" in at.session_state and at.session_state["pdf_made"][1][:4] == b"%PDF"


def test_pdf_builds_for_every_example():
    for key in C.SYSTEMS:
        s = ev.Settings(n=6, seed=2, system=key, k=4)
        assert build_pdf(ev.analyse(s), s)[:4] == b"%PDF", key


def test_extreme_plan_sizes_do_not_raise():
    for n in (C.N_MIN, C.N_MAX):
        for system in ("regenbogen", "zuordnung"):
            at = _app(dict(n=str(n), system=system))
            assert not at.exception, (n, system)
