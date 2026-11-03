# Matroid-Schnitt – zwei Strukturen auf einmal – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-matroid-schnitt-demo.streamlit.app/)** -->

Siebtes Stück der Reihe **Matroide und Submodularität** (Bereich Kombinatorik) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Die Demo behandelt **zwei Matroide auf einmal**: Gesucht ist die größte Menge, die in M1 **und** in M2 unabhängig ist. Beispiele: ein **Regenbogen-Spannbaum** (Wald und lauter verschiedene Farben), eine **Zuordnung** (bipartites Matching) und eine **Arboreszenz**. Der Schnitt ist **kein Matroid**: Greedy erreicht **mindestens die Hälfte** des Optimums (scharf), der **Austauschgraph** liefert das Optimum, und sein Ende liefert ein **Zertifikat** (Min-Max-Formel von Edmonds). Dazu der Tab **Orakelaufrufe**: naiv gegen faul gegen faul mit Greedy-Start.

**Einordnung in die Reihe:** Nachfolger von [dualmatroid-demo](../dualmatroid-demo) (Stück 6), [greedy-optimalitaet-demo](../greedy-optimalitaet-demo) (Stück 5: Greedy genau bei einem Matroid optimal), [rang-basen-kreise-demo](../rang-basen-kreise-demo) (Stück 4), [matroid-demo](../matroid-demo) (Stück 3), [unabhaengigkeitssystem-demo](../unabhaengigkeitssystem-demo) (Stück 2) und [greedy-austausch-demo](../greedy-austausch-demo) (Stück 1). Anders als in Stück 3 bis 6 sind die Beispiele **Paare** von Matroiden, nicht die elf Systeme eines Matroids. Stück 8 gewichtet den Schnitt.

## Warum dieses Problem

Stück 5 zeigte: Greedy ist genau bei **einem** Matroid für jede Gewichtung optimal. Viele Aufgaben bestehen aber aus **zwei** Bedingungen auf einmal: ein Wald **und** lauter verschiedene Farben, jede Leitung höchstens einmal je Anfang **und** je Ende, ein Baum **und** höchstens ein Eingang je Knoten. Dann ist die Menge der erlaubten Lösungen kein Matroid mehr, und Greedy scheitert bei vielen Reihenfolgen. Offen ist, ob es trotzdem ein exaktes Verfahren mit Beweis gibt. Es gibt es: den Austauschgraphen, und sein Ende zeigt in einem Zertifikat, warum nichts Größeres geht.

## Befunde und Korrekturen gegenüber dem Plan

- **Greedy erreicht mindestens, nicht höchstens die Hälfte:** Die Hook-Formulierung der Gliederung („erreicht höchstens die Hälfte“) hatte die Richtung vertauscht. Gemessen: Jede maximale gemeinsame Menge hat mindestens die Hälfte des Optimums, und das ist scharf (bei 6 von 256 Paaren mit 3 Elementen genau ½).
- **Eigene Farbzahl beim Regenbogen:** Mit den drei Kabelfarben der Stücke 3 bis 6 ist das Optimum die Farbzahl und Greedy scheitert nie. Die Demo hat einen Regler (2 bis 8 Farben), voreingestellt 6 (= n − 1 bei 7 Standorten); das Preset „Drei Farben“ zeigt den langweiligen Fall.
- **Arboreszenz nur als festes Beispiel:** Als Schnitt zweier Matroide braucht sie beide Richtungen jeder Leitung (auf dem Plan 20 bis 32 Elemente, über der Grenze von 16); bei einer festen Orientierung wäre das Partitionsmatroid allein schon der ganze Schnitt.
- **Startmenge wählbar:** leere Menge, Greedy nach Nummer oder die **schlechteste maximale Menge** (voreingestellt). Aus der leeren Menge besteht jeder Weg aus einem einzigen Element und zeigt nichts; die schlechteste maximale Menge zeigt die Verbesserungswege.
- **Zufallsanteile und Messreihen weichen leicht von der Messung vor dem Bau ab:** Die App rechnet 1 000 Zufallsreihenfolgen mit einem aus dem Plan-Seed abgeleiteten Seed (Messung: 2 000), die Messreihe der Orakelaufrufe 20 Pläne je Größe (Messung: 30 für den Regenbogen).
- **Zertifikat mit der Menge R:** Die erste Messung hatte die zwei Mengen im Zertifikat vertauscht (r1(R) + r2(E ∖ R)) und fand es nur bei 9 von 25 Paaren. Richtig: mit R = von den Quellen aus erreichbar gilt r1(E ∖ R) + r2(R) = |I|.
- **Port 9347;** Repo `matroid-schnitt-demo`, Präfix `msc_`; `networkx` nur in den Tests.

## Modell

**Regenbogen-Spannbaum:** M1 = Wald (graphisches Matroid) auf den Leitungen des Plans, M2 = höchstens eine Leitung je Kabelfarbe (Partitionsmatroid, k Farben zufällig aus dem Seed). **Zuordnung:** M1 und M2 sind Partitionsmatroide: höchstens eine Leitung je unterem und je oberem Endpunkt (die Standorte tragen Nummern; das ist bipartites Matching im Doppelgraphen). **Arboreszenz:** festes Beispiel mit 6 Knoten, Wurzel 0 und 12 Bögen: M1 = graphisches Matroid der zugrunde liegenden Kanten, M2 = höchstens ein Eingang je Knoten und keiner in die Wurzel. Plan wie in den Stücken davor: n Standorte, Depot A in der Mitte, min(n(n − 1)/2, 2n − 2) mögliche Leitungen. Formeln und Beweisskizzen: Expander „📐 Mathematische Formulierung“ in der App.

## Methodik

- **Greedy:** Elemente in einer Reihenfolge nehmen, solange die Menge in beiden Matroiden unabhängig bleibt (`greedy_common`); Zufallsreihenfolgen und alle maximalen gemeinsamen Mengen (`random_greedy`, `Pair.maximal`).
- **Austauschgraph:** Pfeile y → x, wenn I − y + x in M1 unabhängig ist, und x → y, wenn I − y + x in M2 unabhängig ist; Quellen X1 (I + x in M1), Senken X2 (I + x in M2); kürzester Weg per Breitensuche, I wird um die symmetrische Differenz mit dem Weg verbessert (`exchange_graph`, `steps`).
- **Zertifikat:** R = von X1 erreichbar, A = E ∖ R, r1(A) + r2(E ∖ A) = |I| (`certificate`); das Minimum über alle A als Gegenprobe (`min_max`).
- **Orakelaufrufe:** jede Frage „ist S unabhängig?“ wird gezählt (`Oracle`); drei Varianten: naiv (ganzer Austauschgraph je Runde), faul (Pfeile erst beim Besuch), faul mit Greedy-Start (`intersect`).
- **Alle kleinen Paare:** alle Paare beschrifteter Matroide mit 1 bis 5 Elementen für den Greedy-Faktor und die Min-Max-Formel; das Verfahren mit Zertifikat an allen Paaren bis 4 Elemente und an 6 000 Zufallspaaren bei 5 (`small_pairs_row`).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py` und werden dort mit den Funktionen der App nachgerechnet. Plan: 7 Standorte, 12 mögliche Leitungen, Seed 8 (die Arboreszenz ist fest und hängt nicht vom Plan ab); Greedy: 1 000 Zufallsreihenfolgen.

| Beispiel | Optimum | gemeinsame Mengen | maximale Mengen (Größe: Zahl) | Greedy scheitert | im Mittel | schlechteste |
|---|---|---|---|---|---|---|
| Regenbogen-Spannbaum mit 6 Farben | 5 | 303 | 4: 41, 5: 18 | 47,1 % | 90,6 % | 80,0 % |
| Regenbogen mit 3 Farben | 3 | 94 | 3: 40 | 0,0 % | 100,0 % | 100,0 % |
| Zuordnung | 5 | 124 | 3: 4, 4: 11, 5: 2 | 84,0 % | 80,1 % | 60,0 % |
| Arboreszenz (fest) | 5 | 232 | 4: 3, 5: 21 | 7,9 % | 98,4 % | 80,0 % |

| Frage | Befund |
|---|---|
| **Der Schnitt ist kein Matroid** (bis 12 Elemente geprüft) | In allen vier Beispielen ist die Familie der gemeinsamen unabhängigen Mengen **kein** Matroid. |
| **Alle Paare beschrifteter Matroide mit 1 bis 5 Elementen** (4, 25, 256, 4 624, **164 836** Paare; zusammen **169 745**) | Greedy kann scheitern bei 0, 0, **6**, **360**, **24 210** Paaren (zusammen 24 576). Das **schlechteste Verhältnis maximale Menge zu Optimum ist genau ½** bei 6, 300 und 10 870 Paaren (zusammen **11 176**); **unter ½ liegt keines**. Die Min-Max-Formel von Edmonds gilt bei **allen 169 745**. |
| **Das Verfahren** (alle Paare bis 4 Elemente, 6 000 Zufallspaare bei 5; zusammen **10 909** Paare) | Das Ergebnis ist bei **allen** das Optimum, und das Zertifikat r1(E ∖ R) + r2(R) = \|I\| stimmt bei **allen**. |
| **Zertifikat auf dem Plan** (Min-Max über alle 4 096 Mengen A) | Das Minimum ist gleich dem Optimum (5, 3, 5, 5) und wird bei 4, 1, 97, 5 Mengen A angenommen. |
| **Orakelaufrufe** (naiv / faul / faul mit Greedy-Start) | Regenbogen mit 6 Farben: **364 / 150 / 119**; mit 3 Farben: 200 / 108 / 94; Zuordnung: **364 / 75 / 38**; Arboreszenz: **364 / 62 / 24**. Alle Varianten finden dasselbe Optimum. |
| **Messreihe** (20 Pläne je Größe, n − 1 Farben beim Regenbogen) | Regenbogen: n = 6: 253 / 97 / 64; n = 7: 385 / 150 / 99; n = 8: 571 / 202 / 131. Zuordnung: n = 6: 202 / 52 / 30; n = 7: 314 / 76 / 41; n = 8: 443 / 105 / 59. |
| **Weg mit drei Kanten von Hand** | Optimum 2, Greedy in der Reihenfolge b, a, c erreicht 1; der kürzeste Weg c → b → a hat 3 Knoten; Orakelaufrufe 20 / 8 / 6. |

## Ehrliche Grenzen

- **Zwei Matroide, ungewichtet.** Drei Matroide sind schon NP-schwer; mit Gewichten braucht der Weg Kosten (Stück 8).
- **Kleine Grundmengen.** Höchstens 16 Elemente; Optimum und Zertifikat kommen aus allen Teilmengen. Die Orakelaufrufe zählen Fragen an Tabellen, keine Rechenzeit; bei großen Matroiden sind die Zahlen der Literatur andere (Stück 8 als Übersicht).
- **Beispiele auf einem Plan.** Die Greedy-Anteile gelten für den Plan 7/8 und 1 000 Zufallsreihenfolgen, die Messreihe für Seeds 0 bis 19; mit drei Farben ist das Regenbogen-Beispiel nutzlos (Optimum gleich Farbzahl).
- **Das Verfahren an Paaren mit 5 Elementen** nur an 6 000 von 164 836 Zufallspaaren; Greedy-Faktor und Min-Max an allen. Der Beweis steht im Expander, die Messung ersetzt ihn nicht.
- **Quellen nur als Auszüge** (Edmonds, Lawler, Cunningham; Websuche): Die Min-Max-Formel in dieser Schreibweise und die Greedy-Garantie ½ sind hier hergeleitet und gemessen, nicht aus einer Quelle übernommen.
- **Die Arboreszenz** ist ein einziges festes Beispiel; die Messreihe über mehrere Pläne gibt es nur für Regenbogen und Zuordnung.

## Verifikation

- **Kern:** Tabellen, Greedy, Austauschgraph, Weg, Zertifikat, Min-Max und die Orakelzahlen 20 / 8 / 6 gegen Handrechnung am Weg mit drei Kanten und am Dreieck mit zwei gleichfarbigen Kanten (`tests/conftest.py`, `tests/test_algorithm.py`); Randfälle: ein Element, Nullmatroid, gleiche Matroide, vertauschte Matroide, leere Startmenge, Reglergrenzen, alle Zweige der Spielwiese (`tests/test_edge_cases.py`).
- **Orakel** (`tests/test_oracle_matroid_schnitt.py`): Regenbogen mit `networkx` (Wald, verschiedene Farben) gegen Aufzählung; Zuordnung gegen `networkx.bipartite.maximum_matching` auf dem Doppelgraphen; Arboreszenz gegen `networkx.maximum_branching`; Austauschgraph aus Mengenoperationen neu berechnet und die Länge des kürzesten Weges gegen `networkx`; Min-Max mit Rängen durch Aufzählung; Greedy ≥ ½ auf allen Paaren bis 4 Elemente mit einfachen Schleifen; Matroidzahlen 2, 5, 16, 68, 406.
- **Eigenschaften** (`tests/test_properties.py`): alle Varianten finden das Optimum und das Zertifikat passt; jede Runde fügt genau ein Element hinzu, Wege haben ungerade Länge und wechseln zwischen innen und außen; jede maximale Menge hat mindestens die Hälfte; faul braucht höchstens so viele Aufrufe wie naiv; Vertauschen der Matroide und Umbenennen ändern Optimum und Größen der maximalen Mengen nicht; schwache Dualität für jedes A; Schnitt mit einem freien Matroid ist das Matroid selbst.
- **Verdikte und Presets:** jeder Zweig und jede Zahl der Verdikte an handgesetzten Werten; jedes Preset zeigt den versprochenen Effekt; kein einzelner Reglerwechsel trifft ein anderes Preset.
- **Zahlen aus dieser README:** `tests/test_claims.py`.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an den Grenzen), Hauptansicht, Experimente, Spielwiese, Permalink, PDF; Layout (Kopf, Schnellstart, Hervorhebung) und Footer.
- **Umfang:** siehe `pytest --collect-only -q tests`.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Oberfläche: Austauschgraph-Lauf, Kernfrage, vier Experimente, Spielwiese, Grenzen, Formeln |
| `msc_constants.py` | Reglergrenzen, die drei Beispiele und ihre Namen, das feste Beispiel Arboreszenz, Farben, Presets |
| `msc_scenario.py` | Plan: Standorte, mögliche Leitungen, Kosten (wie in den Stücken 1 bis 6) |
| `msc_algorithm.py` | Kern: Tabellen, Paar von Matroiden, Greedy, Austauschgraph, Verfahren mit Orakelzählung, Zertifikat, Min-Max, alle kleinen Paare |
| `msc_systems.py` | die drei Beispiele als Paare von Matroiden |
| `msc_evaluation.py` | Kennzahlen, Ansichten der Experimente, Verdikte |
| `msc_visualization.py` | Plan, Digraph für die Arboreszenz, Balken |
| `msc_presets.py` | Permalink, Presets, Zufalls-Seed |
| `msc_layout.py` | fester Kopf |
| `msc_pdf_export.py` | PDF des aktuellen Beispiels |
| `tests/` | Kern, Orakel, Eigenschaften, Verdikte, Presets, Claims, Randfälle, Oberfläche, Layout, Footer, Importe |

## Bewusst nicht umgesetzt

- Gewichteter Schnitt, kürzeste Wege mit Kosten, Stand der Forschung (Stück 8); Vereinigung und Partition (Stück 9); Polytop (Stück 10).
- Matroid-Parität; Schnitt von drei oder mehr Matroiden; Laufzeitschranken von Cunningham und die unterquadratischen Verfahren.
- Eine Arboreszenz auf dem Plan (beide Richtungen jeder Leitung); die elf Systeme der Stücke 3 bis 6 als Paare.
- Erklärseite „verständlich erklärt“ und Website-Einbindung (erst mit der vollständigen Linie).

## Lokal ausführen

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tests: `pip install -r requirements-dev.txt`, dann `python -m pytest tests -q`. Die CI läuft mit Python 3.12 (`.github/workflows/tests.yml`); die in Streamlit Cloud eingestellte Python-Version ist beim Deploy zu nennen.

Gebaut mit Streamlit, Plotly, numpy und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
