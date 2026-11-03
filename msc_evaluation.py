"""Kennzahlen, Experimente und Verdikte. Alle sichtbaren Zahlen kommen aus diesen Funktionen."""

import statistics
from dataclasses import dataclass
from functools import lru_cache

import msc_constants as C
from msc_algorithm import (
    VARIANTS,
    bfs_path,
    certificate,
    elements,
    exchange_graph,
    greedy_common,
    intersect,
    intersection_is_matroid,
    maximal_sizes,
    min_max,
    popcount,
    random_greedy,
    small_pairs_row,
    steps,
)
from msc_systems import get_pair


def de(x: float, digits: int = 1) -> str:
    """Zahl mit Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


def prozent(x: float, digits: int = 1) -> str:
    return de(100.0 * x, digits)


def zahl(n: int) -> str:
    """Ganze Zahl mit Leerzeichen als Tausendertrenner."""
    return f"{n:,}".replace(",", " ")


def elemente(k: int) -> str:
    return "1 Element" if k == 1 else f"{k} Elemente"


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    system: str = "regenbogen"
    k: int = C.DEFAULT_K


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    m: int
    labels: tuple
    kind: str                   # "kanten" oder "boegen"
    opt: int                    # größte gemeinsame unabhängige Menge
    n_common: int               # Zahl aller gemeinsamen unabhängigen Mengen
    maximal: tuple              # ((Größe, Zahl), ...) der maximalen gemeinsamen Mengen
    is_matroid: bool | None     # ist der Schnitt selbst ein Matroid? (None: nicht gerechnet)
    rank1: int
    rank2: int


def pair_of(settings: Settings):
    return get_pair(settings.system, settings.n, settings.seed, settings.k)


def analyse(settings: Settings) -> Analysis:
    p = pair_of(settings)
    return Analysis(settings, p.m, p.labels, p.kind, p.opt, p.n_common, tuple(maximal_sizes(p).items()), intersection_is_matroid(p), int(p.ur1[p.full]), int(p.ur2[p.full]))


def names(a: Analysis, mask: int) -> str:
    return ", ".join(a.labels[e] for e in elements(mask, a.m))


def setstr(a: Analysis, mask: int) -> str:
    """Menge als {a, b, c}; die leere Menge als ∅."""
    return "{" + names(a, mask) + "}" if mask else "∅"


def seq(a: Analysis, path) -> str:
    return " → ".join(a.labels[v] for v in path)


# --- Hauptansicht: Austauschgraph-Lauf ------------------------------------------------------------------------------------------------------


@lru_cache(maxsize=32)
def run_view(settings: Settings, start: str = "leer") -> tuple:
    return tuple(steps(pair_of(settings), start))


def round_groups(a: Analysis, rounds, index: int) -> list:
    """Gruppen für das Bild der Runde: die Menge I, der Weg (bzw. am Ende die erreichbare Menge R)."""
    rd = rounds[index]
    groups = [("gemeinsame Menge I", elements(rd["set"], a.m), C.COLOR_SET)]
    if rd["path"] is not None:
        groups.append(("Verbesserungsweg", list(rd["path"]), C.COLOR_PATH))
    else:
        groups.append(("erreichbar von den Quellen (R)", elements(rd["reach"], a.m), C.COLOR_REACH))
    return groups


def round_rows(a: Analysis, rounds, index: int) -> list[dict]:
    rd = rounds[index]
    out = []
    pos = {v: i + 1 for i, v in enumerate(rd["path"] or [])}
    for e in range(a.m):
        out.append({
            "Element": a.labels[e], "in I": "ja" if rd["set"] >> e & 1 else "nein", "Quelle (I + e in M1)": "ja" if e in rd["x1"] else "–", "Senke (I + e in M2)": "ja" if e in rd["x2"] else "–",
            "im Weg": str(pos[e]) if e in pos else "–",
        })
    return out


def verdict_round(a: Analysis, p, rounds, index: int) -> tuple[str, str]:
    rd = rounds[index]
    size = popcount(rd["set"])
    start = f" (Startmenge: {elemente(size)})" if index == 0 and size else ""
    if rd["path"] is not None:
        path = rd["path"]
        return "info", (
            f"Runde {index + 1}: I = {setstr(a, rd['set'])} ({elemente(size)}){start}. Quellen X1 = {{{', '.join(a.labels[x] for x in rd['x1'])}}}, Senken X2 = {{{', '.join(a.labels[x] for x in rd['x2'])}}}. "
            f"Der kürzeste Weg hat {elemente(len(path))}: {seq(a, path)}. Nach dem Tausch hat I {elemente(size + 1)}."
        )
    x, y, total = certificate(p, rd["reach"])
    reach = setstr(a, rd["reach"])
    ok = total == size
    if not ok:
        return "error", "Das Zertifikat passt nicht zur Größe von I. Das darf nicht sein: Rechenfehler."
    return "success", (
        f"Runde {index + 1}: Von den Quellen führt **kein Weg** zu den Senken. I = {setstr(a, rd['set'])} mit **{size}** Elementen ist größtmöglich. Erreichbar sind R = {reach}; "
        f"mit A = E ∖ R gilt r1(A) + r2(E ∖ A) = {x} + {y} = **{total}**: kein gemeinsames Element mehr als {total} passt (Zertifikat)."
    )


# --- Experiment 1: Greedy gegen Optimum ---------------------------------------------------------------------------------------------------------


def greedy_view(settings: Settings, trials: int) -> dict:
    p = pair_of(settings)
    res = random_greedy(p, trials, settings.seed * 1000 + 17)
    sizes = p.maximal
    from msc_algorithm import pc_table
    pcs = pc_table()[sizes]
    worst_set = int(sizes[int(pcs.argmin())])
    return {"sizes": res["sizes"], "trials": trials, "opt": p.opt, "opt_set": p.opt_set, "worst_set": worst_set, "worst": popcount(worst_set), "maximal": maximal_sizes(p)}


def greedy_rows(view: dict) -> list[dict]:
    t = view["trials"]
    out = []
    for size in sorted(view["maximal"]):
        hits = sum(1 for s in view["sizes"] if s == size)
        out.append({"Größe der Greedy-Menge": size, "maximale Mengen dieser Größe": zahl(view["maximal"][size]), "Zufallsreihenfolgen": f"{zahl(hits)} ({prozent(hits / t)} %)",
                    "Anteil am Optimum": f"{prozent(size / view['opt'])} %"})
    return out


def verdict_greedy(a: Analysis, view: dict) -> tuple[str, str]:
    opt, worst, t = view["opt"], view["worst"], view["trials"]
    if 2 * worst < opt:
        return "error", "Eine maximale gemeinsame Menge hat weniger als die Hälfte des Optimums. Das darf nicht sein: Rechenfehler."
    fails = sum(1 for s in view["sizes"] if s < opt)
    mean = statistics.mean(view["sizes"]) / opt
    if worst == opt:
        return "success", (
            f"Alle maximalen gemeinsamen Mengen haben {elemente(opt)}, gleich dem Optimum: Greedy scheitert hier bei **keiner** der {zahl(t)} Reihenfolgen. "
            f"(Das gilt für dieses Beispiel, nicht für jeden Schnitt: Der Schnitt ist {'ein Matroid' if a.is_matroid else 'kein Matroid'}.)"
        )
    half = de(opt / 2, 1)
    return "warning", (
        f"Greedy liefert bei **{prozent(fails / t)} %** der {zahl(t)} Zufallsreihenfolgen nicht das Optimum ({opt}), im Mittel {prozent(mean)} % davon. Die schlechteste maximale Menge hat {worst} Elemente "
        f"(**{prozent(worst / opt)} %** des Optimums); garantiert ist mindestens die Hälfte, hier {half} Elemente (Experiment 4: die Hälfte kommt vor)."
    )


# --- Experiment 2: Zertifikat -----------------------------------------------------------------------------------------------------------------


def cert_view(settings: Settings) -> dict:
    p = pair_of(settings)
    rd = run_view(settings, "leer")[-1]
    reach = rd["reach"]
    a_set = p.full ^ reach
    mm = min_max(p)
    return {"set": rd["set"], "reach": reach, "a": a_set, "r1": int(p.ur1[a_set]), "r2": int(p.ur2[reach]), "minmax": mm, "opt": p.opt}


def cert_rows(a: Analysis, view: dict) -> list[dict]:
    p = pair_of(a.settings)
    out = []
    for mask in view["minmax"]["first"]:
        out.append({"A": "{" + names(a, mask) + "}", "Elemente von A": popcount(mask), "r1(A)": int(p.ur1[mask]), "r2(E ∖ A)": int(p.ur2[p.full ^ mask]), "Summe": int(p.ur1[mask] + p.ur2[p.full ^ mask])})
    return out


def verdict_cert(a: Analysis, view: dict) -> tuple[str, str]:
    mm = view["minmax"]
    total = view["r1"] + view["r2"]
    if not (mm["value"] == view["opt"] == popcount(view["set"]) == total):
        return "error", "Optimum, Min-Max-Wert und Zertifikat stimmen nicht überein. Das darf nicht sein: Rechenfehler."
    return "success", (
        f"Das Minimum von r1(A) + r2(E ∖ A) über alle {zahl(2 ** a.m)} Mengen A ist **{mm['value']}**, gleich der größten gemeinsamen Menge. Es wird bei {zahl(mm['count'])} Mengen A angenommen; "
        f"das Verfahren findet eine davon: A = {setstr(a, view['a'])} mit r1(A) = {view['r1']} und r2(E ∖ A) = {view['r2']}."
    )


# --- Experiment 3: Orakelaufrufe ------------------------------------------------------------------------------------------------------------------


def oracle_view(settings: Settings) -> dict:
    p = pair_of(settings)
    return {v: intersect(p, v) for v in VARIANTS}


def oracle_rows(view: dict) -> list[dict]:
    names_ = {"naiv": "naiv (ganzer Austauschgraph je Runde)", "faul": "faul (Pfeile erst beim Besuch)", "faul+greedy": "faul mit Greedy-Start"}
    return [{"Verfahren": names_[v], "Orakelaufrufe": zahl(r["calls"]), "Runden": r["rounds"], "Start": "leer" if v != "faul+greedy" else f"{r['start']} Elemente (Greedy)",
             "Wege (Knotenzahl)": ", ".join(str(x) for x in r["lengths"]) or "–"} for v, r in view.items()]


def verdict_oracle(a: Analysis, view: dict) -> tuple[str, str]:
    sizes = {popcount(r["set"]) for r in view.values()}
    if len(sizes) != 1 or sizes != {a.opt}:
        return "error", "Die drei Varianten liefern nicht dasselbe Optimum. Das darf nicht sein: Rechenfehler."
    n, f, g = (view[v]["calls"] for v in VARIANTS)
    return "success", (
        f"Alle drei Varianten finden das Optimum {a.opt}. Orakelaufrufe: naiv **{zahl(n)}**, faul **{zahl(f)}** (Faktor {de(n / f)} weniger), faul mit Greedy-Start **{zahl(g)}** "
        f"(Faktor {de(n / g)} weniger als naiv). Der Greedy-Start liefert {view['faul+greedy']['start']} von {a.opt} Elementen, der Rest kommt über {view['faul+greedy']['rounds']} Verbesserungsweg(e)."
    )


@lru_cache(maxsize=4)
def oracle_series(system: str) -> tuple:
    """Mittel der Orakelaufrufe je Plangröße (6 bis 8 Standorte, Seeds 0 bis 19); Regenbogen mit n − 1 Farben."""
    rows = []
    for n in C.SERIES_N:
        calls = {v: [] for v in VARIANTS}
        deficits = []
        for seed in range(C.SERIES_SEEDS):
            p = get_pair(system, n, seed, n - 1)
            res = {v: intersect(p, v) for v in VARIANTS}
            assert len({popcount(r["set"]) for r in res.values()}) == 1
            for v, r in res.items():
                calls[v].append(r["calls"])
            deficits.append(p.opt - res["faul+greedy"]["start"])
        rows.append({"n": n, "m": 2 * n - 2, **{v: statistics.mean(calls[v]) for v in VARIANTS}, "deficit": statistics.mean(deficits), "missed": sum(d > 0 for d in deficits)})
    return tuple(rows)


def series_table(rows) -> list[dict]:
    return [{"Standorte": r["n"], "Leitungen": r["m"], "naiv": zahl(round(r["naiv"])), "faul": zahl(round(r["faul"])), "faul mit Greedy-Start": zahl(round(r["faul+greedy"])),
             "Greedy-Start verfehlt das Optimum im Mittel um": de(r["deficit"], 2)} for r in rows]


def verdict_series(system: str, rows) -> tuple[str, str]:
    name = "Regenbogen-Spannbaum mit n − 1 Farben" if system == "regenbogen" else "Zuordnung"
    last = rows[-1]
    lo = min(r["naiv"] / r["faul+greedy"] for r in rows)
    hi = max(r["naiv"] / r["faul+greedy"] for r in rows)
    return "success", (
        f"{name}, {C.SERIES_SEEDS} Pläne je Größe: Das naive Verfahren braucht bei {last['n']} Standorten im Mittel **{zahl(round(last['naiv']))}** Orakelaufrufe, das faule **{zahl(round(last['faul']))}**, "
        f"das faule mit Greedy-Start **{zahl(round(last['faul+greedy']))}**; der Faktor naiv gegen faul mit Greedy-Start liegt zwischen {de(lo)} und {de(hi)}."
    )


# --- Experiment 4: alle kleinen Paare ---------------------------------------------------------------------------------------------------------


@lru_cache(maxsize=1)
def small_rows() -> tuple:
    return tuple(small_pairs_row(n, C.SMALL_SAMPLE, C.PLAY_SEED) for n in range(1, C.ENUM_MAX_N + 1))


def small_table(rows) -> list[dict]:
    return [{
        "Elemente n": r["n"], "Matroide": zahl(r["matroids"]), "Paare": zahl(r["pairs"]), "Greedy kann scheitern": zahl(r["fail"]), "schlechtestes Verhältnis": de(r["worst"], 3),
        "Paare mit genau ½": zahl(r["half"]), "Min-Max gilt": zahl(r["minmax"]), "Verfahren geprüft": zahl(r["checked"]), "Verfahren = Optimum": zahl(r["alg_ok"]), "Zertifikat stimmt": zahl(r["cert_ok"]),
    } for r in rows]


def verdict_small(rows) -> tuple[str, str]:
    pairs = sum(r["pairs"] for r in rows)
    bad = sum(r["below_half"] for r in rows) + sum(r["pairs"] - r["minmax"] for r in rows) + sum(r["checked"] - r["alg_ok"] for r in rows) + sum(r["checked"] - r["cert_ok"] for r in rows)
    if bad:
        return "error", f"Bei {bad} Prüfungen gilt eine Aussage nicht. Das darf nicht sein: Rechenfehler."
    last = rows[-1]
    fail, half = sum(r["fail"] for r in rows), sum(r["half"] for r in rows)
    checked = sum(r["checked"] for r in rows)
    return "success", (
        f"Bei allen {zahl(pairs)} Paaren von Matroiden mit höchstens {last['n']} Elementen: Greedy kann bei {zahl(fail)} Paaren scheitern; das schlechteste Verhältnis ist genau **½** (bei {zahl(half)} Paaren), "
        f"**kein** Paar liegt darunter. Die Min-Max-Formel von Edmonds gilt bei **allen**. Das Verfahren findet bei allen {zahl(checked)} geprüften Paaren das Optimum, und das Zertifikat stimmt bei allen."
    )


# --- Spielwiese -----------------------------------------------------------------------------------------------------------------------------


def play_view(settings: Settings, mask: int) -> dict:
    p = pair_of(settings)
    out = {"mask": mask, "ok1": bool(p.ok1[mask]), "ok2": bool(p.ok2[mask]), "graph": None, "path": None, "reach": None}
    if out["ok1"] and out["ok2"]:
        g = exchange_graph(p, mask)
        adj: dict[int, list[int]] = {v: [] for v in range(p.m)}
        for x, y, _ in g["arcs"]:
            adj[x].append(y)
        sinks = set(g["x2"])
        path, seen = bfs_path(g["x1"], lambda v: v in sinks, lambda v: adj[v])
        out.update(graph=g, path=path, reach=None if path else sum(1 << v for v in seen), optimal=popcount(mask) == p.opt)
    return out


def verdict_play(a: Analysis, p, view: dict) -> tuple[str, str]:
    if not view["ok1"] or not view["ok2"]:
        which = "beiden Matroiden" if not view["ok1"] and not view["ok2"] else ("M1" if not view["ok1"] else "M2")
        return "info", f"Die Menge ist in {which} nicht unabhängig, also keine gemeinsame unabhängige Menge. Wählen Sie eine Menge, die in beiden passt."
    g = view["graph"]
    size = popcount(view["mask"])
    head = f"I hat {elemente(size)}; Quellen X1 = {{{', '.join(a.labels[x] for x in g['x1'])}}}, Senken X2 = {{{', '.join(a.labels[x] for x in g['x2'])}}}, {zahl(len(g['arcs']))} Pfeile. "
    if view["path"]:
        return "info", head + f"Kürzester Verbesserungsweg ({elemente(len(view['path']))}): {seq(a, view['path'])}; danach hat I {elemente(size + 1)}."
    x, y, total = certificate(p, view["reach"])
    return "success", head + f"Kein Weg: I ist größtmöglich ({size}), Zertifikat r1(E ∖ R) + r2(R) = {x} + {y} = {total}."
