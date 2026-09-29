"""Commander Chrome profila statuss (stdlib) un pieteikšanās pārbaude (Playwright, ja ir).

Integrācijas robeža ar `browser_ui_v1`: tam jāpievienojas `cdp_endpoint(port)`
(piem., Playwright `chromium.connect_over_cdp(...)`), nevis jāpalaiž savs pārlūks.
Kā tieši `browser_ui_v1` to dara, ir PAVADONIS pusē — šeit neminam.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Callable

DEFAULT_PORT = 9223
HOST = "127.0.0.1"

# Vietne -> (URL sīkdatņu nolasīšanai, sīkdatnes NOSAUKUMS, kas nozīmē "pieteicies").
SITES: dict[str, tuple[str, str]] = {
    "instagram": ("https://www.instagram.com", "sessionid"),
    "facebook": ("https://www.facebook.com", "c_user"),
}


def cdp_endpoint(port: int = DEFAULT_PORT) -> str:
    if not isinstance(port, int) or isinstance(port, bool) or not 1024 <= port <= 65535:
        raise ValueError("nederīgs ports")
    return f"http://{HOST}:{port}"


def status(port: int = DEFAULT_PORT,
           urlopen: Callable[..., Any] = urllib.request.urlopen) -> dict:
    """Vai Commander Chrome darbojas. Tikai lasīšana, tikai 127.0.0.1."""
    url = cdp_endpoint(port) + "/json/version"
    try:
        with urlopen(url, timeout=2) as resp:
            info = json.loads(resp.read() or b"{}")
    except (urllib.error.URLError, OSError, ValueError):
        return {"running": False, "endpoint": cdp_endpoint(port), "browser": None}
    return {"running": bool(info.get("Browser")), "endpoint": cdp_endpoint(port),
            "browser": info.get("Browser")}


def login_state(site: str, port: int = DEFAULT_PORT, playwright_factory=None) -> dict:
    """Vai profilā ir aktīva sesija vietnei. Atgriež tikai true/false, nekad vērtības."""
    if site not in SITES:
        raise ValueError(f"nezināma vietne: {site!r}; atļautas: {', '.join(SITES)}")
    url, cookie_name = SITES[site]
    if not status(port)["running"]:
        return {"site": site, "running": False, "logged_in": None}
    if playwright_factory is None:
        try:
            from playwright.sync_api import sync_playwright as playwright_factory
        except ImportError:
            return {"site": site, "running": True, "logged_in": None,
                    "error": "playwright nav instalēts"}
    with playwright_factory() as pw:
        browser = pw.chromium.connect_over_cdp(cdp_endpoint(port))
        try:
            contexts = browser.contexts
            names = {c.get("name") for ctx in contexts for c in ctx.cookies(url)}
        finally:
            # Atvienojamies no CDP; Commander Chrome paliek atvērts.
            browser.close()
    return {"site": site, "running": True, "logged_in": cookie_name in names}
