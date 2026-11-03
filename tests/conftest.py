"""Gemeinsame Fixtures: kleine Paare von Matroiden, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from msc_algorithm import Pair, graphic_table, partition_table  # noqa: E402


@pytest.fixture
def weg():
    """Weg mit drei Kanten als Zuordnung, Elemente a, b, c = 0, 1, 2: M1 mit den Klassen {a, b}, {c}; M2 mit den Klassen {a}, {b, c} (je höchstens ein Element je Klasse).
    Gemeinsam unabhängig: ∅, a, b, c, {a, c}; maximal: {b} (Maske 2) und {a, c} (Maske 5); Optimum 2. Greedy in der Reihenfolge b, a, c nimmt nur b: die Hälfte."""
    return Pair("weg", 3, partition_table(3, [0, 0, 1]), partition_table(3, [0, 1, 1]), ("a", "b", "c"), "kanten")


@pytest.fixture
def dreieck_farben():
    """Dreieck a, b, c (Knoten 0, 1, 2) mit den Farben 0, 0, 1: größter Wald in lauter verschiedenen Farben hat 2 Elemente ({a, c} oder {b, c}); {a, b} ist kein Regenbogen."""
    return Pair("dreieck", 3, graphic_table(3, [(0, 1), (1, 2), (0, 2)]), partition_table(3, [0, 0, 1]), ("a", "b", "c"), "kanten")


@pytest.fixture
def frei():
    """Zwei freie Matroide auf 3 Elementen: jede Menge ist gemeinsam unabhängig, das Optimum ist 3, Greedy scheitert nie."""
    import numpy as np
    ok = np.ones(8, dtype=bool)
    return Pair("frei", 3, ok, ok.copy(), ("a", "b", "c"), "kanten")
