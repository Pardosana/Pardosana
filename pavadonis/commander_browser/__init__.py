"""PAVADONIS Commander atsevišķais Chrome profils: statuss un pieteikšanās pārbaude.

Nekad neatgriež sīkdatņu vērtības — tikai to, vai sesija ir.
"""

from .core import SITES, cdp_endpoint, login_state, status

__all__ = ["SITES", "cdp_endpoint", "login_state", "status"]
