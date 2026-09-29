"""PAVADONIS patiesības slānis: fakti ar derīguma termiņu un invariantu pārbaude.

Integrācijas robeža: `facts.FactStore` var dzīvot tajā pašā bus.sqlite failā (tikai savas
`pav_truth_*` tabulas) vai atsevišķā failā. Invariantu ievaddatus (klienti, ziņas, tikšanās,
uzdevumi) PAVADONIS pusē jāielādē vienkāršās vārdnīcās — shēma aprakstīta `invariants.py`.
"""

from .facts import Fact, FactStore, StaleFact
from .invariants import BUILTIN_INVARIANTS, Invariant, Violation, run_invariants, violations_to_tasks

__all__ = ["BUILTIN_INVARIANTS", "Fact", "FactStore", "Invariant", "StaleFact", "Violation",
           "run_invariants", "violations_to_tasks"]
