"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

N_MIN, N_MAX, DEFAULT_N = 6, 9, 7           # Standorte inklusive Depot (Knoten A); bis 9 (16 mögliche Leitungen)
SEED_MAX, DEFAULT_SEED = 999999, 8
HUB_FACTOR = 0.4                            # nur vom Plan-Erzeuger gebraucht (keine Nabe in dieser Demo)
COST_SCALE = 100                            # Kosten einer Leitung = Entfernung auf dem Plan mal 100 (nur vom Plan-Erzeuger gebraucht)
K_MIN, K_MAX, DEFAULT_K = 2, 8, 6           # Zahl der Kabelfarben beim Regenbogen-Spannbaum (voreingestellt n − 1 = 6 bei 7 Standorten)
ENUM_MAX_N = 5                              # alle Paare von Matroiden bis zu so vielen Elementen aufzählen
SMALL_SAMPLE = 6000                         # bei 5 Elementen das Verfahren nur an so vielen Zufallspaaren prüfen (alle 164 836 Paare für Greedy und Min-Max)
TRIALS_MIN, TRIALS_MAX, TRIALS_DEFAULT, TRIALS_STEP = 100, 5000, 1000, 100   # Experiment 1: Zahl der Zufallsreihenfolgen
SERIES_N = (6, 7, 8)                        # Experiment 3: Plangrößen der Messreihe der Orakelaufrufe
SERIES_SEEDS = 20                           # und so viele Pläne je Größe (Seeds 0 bis 19)
PLAY_SEED = 20261109

SYSTEMS = ("regenbogen", "zuordnung", "arboreszenz")
SYSTEM_NAMES = {
    "regenbogen": "Regenbogen-Spannbaum (Wald und lauter verschiedene Farben)",
    "zuordnung": "Zuordnung (höchstens eine Leitung je unterem und je oberem Endpunkt)",
    "arboreszenz": "Arboreszenz (festes Beispiel mit 12 Bögen)",
}
MATROID_NAMES = {
    "regenbogen": ("Wald (graphisches Matroid)", "höchstens eine Leitung je Farbe (Partitionsmatroid)"),
    "zuordnung": ("höchstens eine Leitung je unterem Endpunkt (Partitionsmatroid)", "höchstens eine Leitung je oberem Endpunkt (Partitionsmatroid)"),
    "arboreszenz": ("Wald im zugrunde liegenden Graphen (graphisches Matroid)", "höchstens ein Eingang je Knoten, keiner in die Wurzel (Partitionsmatroid)"),
}

# Festes Beispiel Arboreszenz: 6 Knoten, Wurzel 0, 12 Bögen (Anfang, Ende); Bögen in die Wurzel sind nie zulässig.
ARBORESCENCE_ARCS = ((0, 1), (0, 2), (1, 2), (2, 1), (1, 3), (2, 4), (3, 4), (4, 3), (3, 5), (4, 5), (1, 0), (5, 3))
ARBORESCENCE_POINTS = ((0.08, 0.5), (0.32, 0.82), (0.32, 0.18), (0.62, 0.82), (0.62, 0.18), (0.92, 0.5))

COLOR_SET = "#2F6B65"                       # gemeinsame unabhängige Menge I
COLOR_PATH = "#d95f02"                      # Verbesserungsweg
COLOR_SOURCE = "#4c78a8"                    # Quellen X1
COLOR_SINK = "#1b9e77"                      # Senken X2
COLOR_REACH = "#9467bd"                     # erreichbare Menge R
COLOR_OPT = "#2F6B65"
COLOR_WORST = "#d95f02"
COLOR_OTHER = "rgba(150,150,150,0.55)"
COLOR_NODE = "#4c78a8"
COLOR_DEPOT = "#f0a30a"
PALETTE = ("rgba(200,60,60,0.55)", "rgba(60,150,80,0.55)", "rgba(70,110,200,0.55)", "rgba(200,150,40,0.55)", "rgba(150,80,180,0.55)", "rgba(40,170,170,0.55)",
           "rgba(170,100,60,0.55)", "rgba(120,120,120,0.55)")

PRESETS = {
    "Standardfall (Voreinstellung)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "regenbogen", "k": DEFAULT_K},
    "Drei Farben": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "regenbogen", "k": 3},
    "Zuordnung": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "zuordnung", "k": DEFAULT_K},
    "Arboreszenz (fest)": {"n": N_MIN, "seed": DEFAULT_SEED, "system": "arboreszenz", "k": DEFAULT_K},
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "Wald und sechs Farben auf 7 Standorten: Greedy scheitert bei vielen Reihenfolgen, der Austauschgraph findet den Regenbogen-Wald.",
    "Drei Farben": "Nur drei Farben: Das Optimum ist die Farbzahl, und Greedy scheitert auf dem Standardplan nie; der Schnitt ist hier kein gutes Beispiel für Greedy-Fehler.",
    "Zuordnung": "Bipartites Matching im Doppelgraphen: Greedy scheitert bei den meisten Reihenfolgen.",
    "Arboreszenz (fest)": "Festes Beispiel mit 6 Knoten und 12 Bögen, unabhängig vom Plan: ein graphisches Matroid und ein Partitionsmatroid.",
}
