"""Matroid-Schnitt - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 7 der Reihe „Matroide und Submodularität“ (Bereich Kombinatorik). Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import msc_constants as C
from msc_algorithm import START_NAMES, elements
from msc_evaluation import (
    Settings,
    analyse,
    cert_rows,
    cert_view,
    elemente,
    greedy_rows,
    greedy_view,
    oracle_rows,
    oracle_series,
    oracle_view,
    pair_of,
    play_view,
    round_groups,
    round_rows,
    run_view,
    series_table,
    small_rows,
    small_table,
    verdict_cert,
    verdict_greedy,
    verdict_oracle,
    verdict_play,
    verdict_round,
    verdict_series,
    verdict_small,
    zahl,
)
from msc_layout import dunkles_design, kopf_css
from msc_pdf_export import build_pdf
from msc_presets import bounds, init_session_state_defaults, load_permalink_settings, randomize_seed, sidebar_presets, sync_query_params
from msc_visualization import build_bar_chart, build_figure, build_grouped_bars

st.set_page_config(page_title="Matroid-Schnitt – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner="Tabellen der zwei Matroide aufbauen …")
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _run(settings, start):
    return run_view(settings, start)


@st.cache_data(show_spinner=False)
def _greedy(settings, trials):
    return greedy_view(settings, trials)


@st.cache_data(show_spinner=False)
def _cert(settings):
    return cert_view(settings)


@st.cache_data(show_spinner="Die drei Varianten zählen …")
def _oracle(settings):
    return oracle_view(settings)


@st.cache_data(show_spinner="Pläne mit 6 bis 8 Standorten durchrechnen (einige Sekunden) …")
def _series(system):
    return oracle_series(system)


@st.cache_data(show_spinner="Alle Paare von Matroiden bis 5 Elemente prüfen (einige Sekunden) …")
def _small():
    return small_rows()


@st.cache_data(show_spinner=False)
def _play(settings, mask):
    return play_view(settings, mask)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in msc_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧲 Matroid-Schnitt")
st.markdown(
    """
Bisher war es **ein** Matroid. Hier sind es **zwei auf einmal**: Gesucht ist die größte Menge, die in M1 **und** in M2 unabhängig ist (eine **gemeinsame unabhängige Menge**). Beispiele: ein **Regenbogen-Spannbaum** (Wald und lauter verschiedene Farben), eine **Zuordnung** (bipartites Matching) und eine **Arboreszenz**. Der Schnitt zweier Matroide ist im Allgemeinen **kein Matroid** mehr: Greedy erreicht nur noch **mindestens die Hälfte** des Optimums. Exakt wird es über den **Austauschgraphen**: Ein kürzester Weg von den Quellen zu den Senken vergrößert die Menge um ein Element, und wenn kein Weg mehr da ist, liefert die erreichbare Menge ein **Zertifikat** (Min-Max-Formel von Edmonds).

Dies ist das **siebte Stück** der Reihe „Matroide und Submodularität“. Weiter unten: vier Experimente (🔬, darunter der Tab **Orakelaufrufe**), eine **Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So hängt es zusammen", expanded=True):
    st.markdown(
        """
1. **Gemeinsam unabhängig:** in M1 und in M2 unabhängig. **Greedy:** Elemente der Reihe nach nehmen, solange die Menge in beiden unabhängig bleibt. Das Ergebnis ist eine **maximale** gemeinsame Menge, aber nicht unbedingt die größte.
2. **Greedy erreicht mindestens die Hälfte:** Jedes Element der größten Menge wird in M1 oder in M2 von der Greedy-Menge blockiert, je höchstens so viele wie die Greedy-Menge Elemente hat. Das ist scharf (Experiment 4).
3. **Austauschgraph zu I:** Pfeil y → x (y in I, x außerhalb), wenn I − y + x in M1 unabhängig ist; Pfeil x → y, wenn I − y + x in M2 unabhängig ist. **Quellen** X1: I + x in M1. **Senken** X2: I + x in M2.
4. **Verbessern:** Ein kürzester Weg von X1 nach X2 wird zu I hinzugenommen und herausgenommen (symmetrische Differenz); I wird um 1 größer und bleibt gemeinsam unabhängig.
5. **Zertifikat:** Gibt es keinen Weg, sei R die von X1 aus erreichbare Menge und A = E ∖ R. Dann ist r1(A) + r2(E ∖ A) = |I|, und kleiner kann dieser Ausdruck nie sein: Die größte gemeinsame Menge ist das Minimum über alle A.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Beispiel**")
    system = st.selectbox("Zwei Matroide", C.SYSTEMS, key="system_select", format_func=C.SYSTEM_NAMES.get,
                          help="Regenbogen-Spannbaum und Zuordnung liegen auf dem Leitungsnetz, die Arboreszenz ist ein festes Beispiel mit 12 Bögen.")
    st.markdown("**Plan**")
    n = st.slider("Standorte (mit Depot A)", *bounds("n_slider"), key="n_slider", help="Wie viele Standorte der Plan hat. Bis 9 (16 mögliche Leitungen). Die Arboreszenz hängt nicht vom Plan ab.")
    seed = st.number_input("Zufalls-Seed des Plans", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neuen Plan generieren", width="stretch", on_click=randomize_seed)
    k = st.slider("Kabelfarben (Regenbogen)", *bounds("k_slider"), key="k_slider", help="Wie viele Farben die Leitungen haben. Mit n − 1 Farben kann es einen Spannbaum in lauter verschiedenen Farben geben; mit 3 Farben ist das Optimum die Farbzahl.")

sync_query_params({"n_slider": int(n), "seed_input": int(seed), "system_select": system, "k_slider": int(k)})

settings = Settings(int(n), int(seed), system, int(k))
a = _analysis(settings)
pair = pair_of(settings)
play_id = f"{system}_{settings.n}_{settings.seed}_{settings.k}"
m1_name, m2_name = C.MATROID_NAMES[system]

# --- Austauschgraph-Lauf ---------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Austauschgraph-Lauf")
st.caption(f"{C.SYSTEM_NAMES[system]}: M1 = {m1_name}; M2 = {m2_name}. {a.m} Elemente, {zahl(a.n_common)} gemeinsame unabhängige Mengen; der Schnitt ist {'kein ' if not a.is_matroid else 'ein '}Matroid"
           + ("." if a.is_matroid is not None else " (bei mehr als 12 Elementen nicht geprüft)."))
mc1, mc2, mc3, mc4 = st.columns(4)
mc1.metric("Größte gemeinsame Menge", a.opt)
mc2.metric("Rang von M1", a.rank1)
mc3.metric("Rang von M2", a.rank2)
mc4.metric("Maximale gemeinsame Mengen", zahl(sum(c for _, c in a.maximal)), delta=f"{len(a.maximal)} verschiedene Größen" if len(a.maximal) > 1 else "alle gleich groß", delta_color="off")
start = st.radio("Start", tuple(START_NAMES), index=2, horizontal=True, key="start_mode", format_func=START_NAMES.get,
                 help="Womit das Verfahren beginnt. Die schlechteste maximale Menge ist der ungünstigste Greedy-Ausgang und zeigt die Verbesserungswege am besten.")
rounds = _run(settings, start)
r_idx = 0
if len(rounds) > 1:
    r_idx = st.slider("Runde", 1, len(rounds), 1, key=f"round_{play_id}_{start}", help="Welche Runde des Verfahrens angezeigt wird.") - 1
rd = rounds[r_idx]
col_a, col_b = st.columns(2)
with col_a:
    path_text = {v: str(i + 1) for i, v in enumerate(rd["path"] or [])}
    st.plotly_chart(build_figure(pair, round_groups(a, rounds, r_idx), edge_text=path_text), width="stretch", key="map_round")
    st.caption("Blaugrün: die gemeinsame Menge I. Orange: der Verbesserungsweg (Zahlen: Reihenfolge)" + ("." if rd["path"] is not None else "; violett: die von den Quellen aus erreichbare Menge R."))
with col_b:
    st.markdown("**Die Elemente in dieser Runde**")
    st.dataframe(round_rows(a, rounds, r_idx), hide_index=True, width="stretch")

if st.button("📄 PDF des aktuellen Beispiels erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a, settings))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="matroid-schnitt.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie löst man zwei Strukturen auf einmal?")
kind_v, text_v = verdict_round(a, pair, rounds, r_idx)
getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Greedy gegen Optimum")
st.caption("Elemente in zufälliger Reihenfolge nehmen, solange die Menge in beiden Matroiden unabhängig bleibt: Wie oft verfehlt das den größten Wert, und wie schlecht kann es werden?")
trials = st.slider("Zahl der Zufallsreihenfolgen", C.TRIALS_MIN, C.TRIALS_MAX, C.TRIALS_DEFAULT, C.TRIALS_STEP, key="trials_slider")
gv = _greedy(settings, int(trials))
st.dataframe(greedy_rows(gv), hide_index=True, width="stretch")
sizes_sorted = sorted(gv["maximal"])
shares = [100.0 * sum(1 for s in gv["sizes"] if s == size) / gv["trials"] for size in sizes_sorted]
g1, g2 = st.columns(2)
with g1:
    st.plotly_chart(
        build_bar_chart([str(s) for s in sizes_sorted], shares, [C.COLOR_OPT if s == gv["opt"] else C.COLOR_WORST for s in sizes_sorted], "Größe der Greedy-Menge", "Zufallsreihenfolgen (%)", "Größe %{x}: %{y:.1f} %"),
        width="stretch", key="greedy_chart",
    )
with g2:
    st.plotly_chart(build_figure(pair, [("schlechteste maximale Menge", elements(gv["worst_set"], a.m), C.COLOR_WORST)], height=300), width="stretch", key="map_worst")
    st.caption("Die schlechteste maximale gemeinsame Menge (orange).")
kind_v, text_v = verdict_greedy(a, gv)
getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 2: Das Zertifikat")
st.caption("Wenn kein Weg mehr da ist, zeigt die von den Quellen aus erreichbare Menge R eine Menge A = E ∖ R, bei der r1(A) + r2(E ∖ A) so groß ist wie die gemeinsame Menge. Daneben alle Mengen A, bei denen das Minimum angenommen wird.")
cv = _cert(settings)
cc1, cc2 = st.columns(2)
with cc1:
    st.plotly_chart(build_figure(pair, [("A (zählt für M1)", elements(cv["a"], a.m), C.COLOR_SOURCE), ("E ∖ A = R (zählt für M2)", elements(cv["reach"], a.m), C.COLOR_REACH)], height=330), width="stretch", key="map_cert")
with cc2:
    st.markdown("**Mengen A mit dem kleinsten Wert von r1(A) + r2(E ∖ A)** (die ersten acht nach Größe)")
    st.dataframe(cert_rows(a, cv), hide_index=True, width="stretch")
kind_v, text_v = verdict_cert(a, cv)
getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 3: Orakelaufrufe als Kostenmaß")
st.caption("Jede Frage „ist diese Menge unabhängig?“ ist ein Orakelaufruf. Naiv: den ganzen Austauschgraphen je Runde bauen. Faul: Pfeile erst beim Besuch prüfen. Dazu der Start mit Greedy.")
ov = _oracle(settings)
st.dataframe(oracle_rows(ov), hide_index=True, width="stretch")
kind_v, text_v = verdict_oracle(a, ov)
getattr(st, kind_v)(text_v)
if system == "arboreszenz":
    st.info("Die Messreihe über mehrere Pläne gibt es nur für den Regenbogen-Spannbaum und die Zuordnung; die Arboreszenz ist ein einziges festes Beispiel.")
else:
    if st.button("📊 Messreihe über 20 Pläne je Größe (6 bis 8 Standorte)", key="series_run"):
        st.session_state["series_done"] = True
    if st.session_state.get("series_done"):
        rows = _series(system)
        st.dataframe(series_table(rows), hide_index=True, width="stretch")
        st.plotly_chart(
            build_grouped_bars([f"{r['n']} Standorte" for r in rows], [("naiv", [r["naiv"] for r in rows], C.COLOR_WORST), ("faul", [r["faul"] for r in rows], C.COLOR_SOURCE),
                                                                     ("faul mit Greedy-Start", [r["faul+greedy"] for r in rows], C.COLOR_OPT)], "Plangröße", "Orakelaufrufe (Mittel)"),
            width="stretch", key="series_chart",
        )
        kind_v, text_v = verdict_series(system, rows)
        getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 4: Alle kleinen Paare")
st.caption("Alle Paare von Matroiden auf 1 bis 5 Elementen (beschriftet): Greedy-Faktor, Min-Max-Formel und das Verfahren mit seinem Zertifikat.")
if st.button("📊 Alle Paare bis 5 Elemente prüfen", key="small_run"):
    st.session_state["small_done"] = True
if st.session_state.get("small_done"):
    rows = _small()
    st.dataframe(small_table(rows), hide_index=True, width="stretch")
    kind_v, text_v = verdict_small(rows)
    getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🛠️ Spielwiese: Eine eigene gemeinsame Menge verbessern")
st.caption("Wählen Sie eine Menge I. Ist sie in M1 und M2 unabhängig, zeigt die App Quellen, Senken, die Zahl der Pfeile und einen kürzesten Verbesserungsweg (oder das Zertifikat).")
default_i = elements(pair.worst_set, a.m)
sel = st.multiselect("Menge I", list(range(a.m)), default=default_i, key=f"play_i_{play_id}", format_func=lambda x: a.labels[x])
pv = _play(settings, sum(1 << x for x in sel))
kind_v, text_v = verdict_play(a, pair, pv)
getattr(st, kind_v)(text_v)
if sel:
    groups = [("gewählte Menge I", sel, C.COLOR_SET)]
    if pv["path"]:
        groups.append(("Verbesserungsweg", list(pv["path"]), C.COLOR_PATH))
    elif pv["reach"]:
        groups.append(("erreichbare Menge R", elements(pv["reach"], a.m), C.COLOR_REACH))
    st.plotly_chart(build_figure(pair, groups, height=330), width="stretch", key="map_play")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist (wer setzt an) |
|---|---|
| **Zwei Matroide, nicht drei** | Der Schnitt von drei oder mehr Matroiden ist schon als Frage nach einer größten gemeinsamen Menge NP-schwer; das Verfahren hier gilt für genau zwei. **(nicht in dieser Reihe)** |
| **Ungewichtet** | Hier zählt jedes Element gleich. Mit Gewichten braucht der Weg Kosten (+w für Elemente in I, −w außerhalb) und bei Gleichstand die kleinste Knotenzahl. **(Stück 8)** |
| **Kleine Grundmengen (höchstens 16 Elemente)** | Optimum und Zertifikat werden aus allen Teilmengen berechnet; die Orakelaufrufe zählen Fragen an Tabellen, nicht Rechenzeit. Bei großen Matroiden gibt es nur ein Orakel; dort zählt die Zahl der Aufrufe, und es gibt Verfahren mit deutlich weniger. **(Stück 8: Stand der Forschung)** |
| **Das Beispiel ist klein und zufällig** | Greedy-Anteile und Aufrufe gelten für den gezeigten Plan und die Seeds der Messreihe (0 bis 19), nicht allgemein. Mit den drei Kabelfarben der früheren Stücke wäre das Regenbogen-Beispiel wenig aussagekräftig (das Optimum ist die Farbzahl). **(Stück 7)** |
| **Arboreszenz nur fest** | Als Schnitt zweier Matroide braucht sie beide Richtungen jeder Leitung (20 bis 32 Bögen auf dem Plan, über der Grenze von 16); bei einer festen azyklischen Orientierung genügt das Partitionsmatroid allein. **(Stück 7)** |
| **Vereinigung statt Schnitt** | Wie viele disjunkte Strukturen in ein Matroid passen (zum Beispiel kantendisjunkte Spannbäume), ist die Vereinigung von Matroiden; sie wird auf den Schnitt zurückgeführt. **(Stück 9)** |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** zwei Matroide $M_1 = (E, \mathcal{I}_1)$ und $M_2 = (E, \mathcal{I}_2)$ mit Rangfunktionen $r_1, r_2$. Gesucht ist $\max\{\lvert I \rvert : I \in \mathcal{I}_1 \cap \mathcal{I}_2\}$.

| Symbol | Bedeutung |
|---|---|
| $D(I)$ | Austauschgraph zu $I \in \mathcal{I}_1 \cap \mathcal{I}_2$ auf $E$ |
| $(y, x)$ | Pfeil für $y \in I$, $x \notin I$ mit $I - y + x \in \mathcal{I}_1$ |
| $(x, y)$ | Pfeil für $y \in I$, $x \notin I$ mit $I - y + x \in \mathcal{I}_2$ |
| $X_1, X_2$ | Quellen $\{x \notin I : I + x \in \mathcal{I}_1\}$, Senken $\{x \notin I : I + x \in \mathcal{I}_2\}$ |
| $R$ | die von $X_1$ aus erreichbaren Elemente |

**Greedy.** Jede maximale gemeinsame unabhängige Menge $J$ hat $\lvert J \rvert \ge \tfrac12 \max$: Jedes $x$ der größten Menge $O$ außerhalb von $J$ liegt in $\operatorname{span}_1(J)$ oder in $\operatorname{span}_2(J)$, und $O \cap \operatorname{span}_i(J)$ ist unabhängig in $M_i$, hat also höchstens $r_i(J) = \lvert J \rvert$ Elemente; also $\lvert O \rvert \le 2 \lvert J \rvert$.

**Verbessern.** Ein kürzester Weg $P$ von $X_1$ nach $X_2$ in $D(I)$ liefert $I \triangle V(P) \in \mathcal{I}_1 \cap \mathcal{I}_2$ mit einem Element mehr (die Kürzeste-Weg-Eigenschaft schließt Abkürzungen aus). Gibt es keinen Weg, ist $I$ größtmöglich.

**Zertifikat (Edmonds).** Gibt es keinen Weg, gilt mit $A = E \setminus R$: $r_1(A) + r_2(E \setminus A) = \lvert I \rvert$, denn $I \cap A$ spannt $A$ in $M_1$ und $I \cap R$ spannt $R$ in $M_2$. Weil jede gemeinsame Menge $J$ höchstens $r_1(A) + r_2(E \setminus A)$ Elemente hat, ist
$$\max_{J \in \mathcal{I}_1 \cap \mathcal{I}_2} \lvert J \rvert = \min_{A \subseteq E} \big( r_1(A) + r_2(E \setminus A) \big).$$

**Orakelaufrufe.** Naiv: je Runde $2\,\lvert E \setminus I \rvert + 2\,\lvert I \rvert\,\lvert E \setminus I \rvert$ Fragen. Faul: Pfeile erst beim Besuch eines Elements. Mit Greedy-Start entfallen die ersten $\lvert J \rvert$ Runden.

**Literatur.** Der Satz über die größte gemeinsame unabhängige Menge stammt von Edmonds, der Austauschgraph und seine Wege von Lawler und anderen (Quelle: Websuche, Auszüge; Standardwerk: Schrijver, *Combinatorial Optimization*, Kap. 41, nicht eingesehen). Die Greedy-Garantie ½ ist hier hergeleitet und an allen kleinen Paaren nachgerechnet.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Matroide: vom Spannbaum zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-matroide.html)."
)
