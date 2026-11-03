"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und jedes Preset zeigt den Effekt, den sein Hilfetext verspricht."""

import msc_constants as C
import msc_evaluation as ev
import msc_presets as P


def _settings(name):
    return ev.Settings(**C.PRESETS[name])


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_bounds_and_choices():
    for preset in C.PRESETS.values():
        assert C.N_MIN <= preset["n"] <= C.N_MAX and 0 <= preset["seed"] <= C.SEED_MAX and preset["system"] in C.SYSTEMS and C.K_MIN <= preset["k"] <= C.K_MAX


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()
    assert [P.SETTING_SPECS[key].default for key in ("system_select", "k_slider")] == [ev.Settings().system, ev.Settings().k]


def test_setting_specs_cover_every_preset_key_and_have_valid_defaults():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    for spec in P.SETTING_SPECS.values():
        assert spec.choices is None or (spec.default in spec.choices and spec.lo in spec.choices and spec.hi in spec.choices)


def test_no_single_regler_change_of_the_default_lands_on_another_preset():
    """Das Layout setzt jeden Regler auf seinen Höchstwert (oder Tiefstwert): das darf kein Preset treffen, sonst bliebe ein Preset markiert."""
    default = dict(C.PRESETS["Standardfall (Voreinstellung)"])
    for state_key, spec in P.SETTING_SPECS.items():
        key = next(k for k, v in P.PRESET_KEYS.items() if v == state_key)
        for value in (spec.hi, spec.lo):
            if value == default[key]:
                continue                                  # das Layout setzt dann den anderen Wert
            variant = {**default, key: value}
            assert all(variant != preset for preset in C.PRESETS.values()), (state_key, value)


def test_standardfall_help_numbers_hold():
    a = ev.analyse(_settings("Standardfall (Voreinstellung)"))
    assert a.opt == 5 and dict(a.maximal) == {4: 41, 5: 18}
    assert ev.greedy_view(_settings("Standardfall (Voreinstellung)"), 1000)["worst"] == 4


def test_three_colors_help_says_greedy_never_fails():
    s = _settings("Drei Farben")
    a = ev.analyse(s)
    assert a.opt == 3 and dict(a.maximal) == {3: 40} and ev.verdict_greedy(a, ev.greedy_view(s, 300))[0] == "success"


def test_zuordnung_help_says_greedy_fails_on_most_orders():
    s = _settings("Zuordnung")
    v = ev.greedy_view(s, 1000)
    assert sum(1 for x in v["sizes"] if x < v["opt"]) > 500


def test_arboreszenz_help_numbers_hold():
    a = ev.analyse(_settings("Arboreszenz (fest)"))
    assert (a.m, a.opt, dict(a.maximal)) == (12, 5, {4: 3, 5: 21}) and a.kind == "boegen"
