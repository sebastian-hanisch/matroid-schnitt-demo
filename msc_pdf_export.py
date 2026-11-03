"""PDF-Export des aktuellen Beispiels (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

import msc_constants as C
from msc_evaluation import Analysis, Settings, cert_view, elemente, pair_of, run_view, verdict_cert, verdict_round, zahl

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "×": "x", "≈": "~", "∖": "\\", "∩": "n", "∅": "{}", "½": "1/2", "₁": "1", "₂": "2", "²": "2"}


def _s(text) -> str:
    out = str(text).replace("**", "")
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis, settings: Settings) -> bytes:
    pair = pair_of(settings)
    rounds = run_view(settings, "schlecht")
    cv = cert_view(settings)
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Matroid-Schnitt"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    plan = "festes Beispiel" if settings.system == "arboreszenz" else f"{settings.n} Standorte, Plan-Seed {settings.seed}" + (f", {settings.k} Farben" if settings.system == "regenbogen" else "")
    pdf.multi_cell(0, 5, _s(f"{C.SYSTEM_NAMES[settings.system]}; {plan}; {elemente(a.m)}; größte gemeinsame Menge {a.opt}; {zahl(a.n_common)} gemeinsame unabhängige Mengen."), new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(0, 5, _s("M1: " + C.MATROID_NAMES[settings.system][0] + ". M2: " + C.MATROID_NAMES[settings.system][1] + "."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, _s("Lauf ab der schlechtesten maximalen Menge"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for i in range(len(rounds)):
        pdf.multi_cell(0, 5, _s(verdict_round(a, pair, rounds, i)[1]), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    pdf.multi_cell(0, 5, _s(verdict_cert(a, cv)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: matroid-schnitt-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
