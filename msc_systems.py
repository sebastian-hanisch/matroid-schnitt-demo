"""Die drei Beispiele der Demo als Paare von Matroiden: Regenbogen-Spannbaum und Zuordnung auf dem Leitungsnetz, Arboreszenz als festes Beispiel."""

import random
from functools import lru_cache

import msc_constants as C
from msc_algorithm import Pair, graphic_table, partition_table
from msc_scenario import Instance, make_instance


def edge_colors(inst: Instance, seed: int, k: int) -> list[int]:
    """Farbe (0 bis k − 1) je Leitung, deterministisch aus dem Seed."""
    rng = random.Random(seed * 31 + 7)
    return [rng.randrange(k) for _ in range(inst.m)]


def color_name(c: int) -> str:
    return f"F{c + 1}"


def build_pair(key: str, n: int, seed: int, k: int) -> Pair:
    """Das Beispiel `key` (aus C.SYSTEMS) auf dem Plan (n, seed); k Farben beim Regenbogen. Die Arboreszenz hängt nicht vom Plan ab."""
    if key not in C.SYSTEMS:
        raise ValueError(f"unbekanntes Beispiel: {key}")
    if key == "arboreszenz":
        arcs = C.ARBORESCENCE_ARCS
        m = len(arcs)
        heads = ["wurzel" if h == 0 else h for _, h in arcs]
        return Pair(key, m, graphic_table(6, arcs), partition_table(m, heads, {"wurzel": 0}), tuple(f"{a}→{b}" for a, b in arcs), "boegen")
    inst = make_instance(n, seed)
    edges = [(u, w) for u, w, _ in inst.edges]
    labels = tuple(inst.label(e) for e in range(inst.m))
    if key == "regenbogen":
        colors = edge_colors(inst, seed, k)
        return Pair(key, inst.m, graphic_table(inst.n, edges), partition_table(inst.m, colors), labels, "kanten", inst, tuple(colors))
    return Pair(key, inst.m, partition_table(inst.m, [u for u, _ in edges]), partition_table(inst.m, [w for _, w in edges]), labels, "kanten", inst)


@lru_cache(maxsize=24)
def _cached_pair(key: str, n: int, seed: int, k: int) -> Pair:
    return build_pair(key, n, seed, k)


def get_pair(key: str, n: int, seed: int, k: int) -> Pair:
    """Gleiches Paar für gleiche Eingaben: der Aufbau der Tabellen kostet bei 16 Leitungen etwa eine Sekunde. n, seed und k zählen nur, wo sie das Beispiel bestimmen
    (die Arboreszenz ist fest, die Zuordnung hängt nicht von k ab); die übrigen Werte werden vor dem Zwischenspeichern auf 0 gesetzt."""
    if key == "arboreszenz":
        n, seed, k = 0, 0, 0
    elif key == "zuordnung":
        k = 0
    return _cached_pair(key, n, seed, k)
