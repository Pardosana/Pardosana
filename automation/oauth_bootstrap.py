"""One-time OAuth bootstrap for Google Calendar.

Run this locally to obtain a refresh token, then save the printed value as the
`GOOGLE_REFRESH_TOKEN` env var (or the matching Devin org secret).

    python automation/oauth_bootstrap.py \\
        --client-id $GOOGLE_CLIENT_ID \\
        --client-secret $GOOGLE_CLIENT_SECRET

The script uses the desktop / installed-app flow with `urn:ietf:wg:oauth:2.0:oob`
so it works on a headless machine — paste the URL into a browser, sign in, copy
the resulting code back into the prompt.
"""

from __future__ import annotations

import argparse
import sys
import urllib.parse

import requests


SCOPES = "https://www.googleapis.com/auth/calendar.events.readonly"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret", required=True)
    args = parser.parse_args(argv)

    params = {
        "client_id": args.client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print("Atver šo URL pārlūkā un autorizējies:")
    print(url)
    code = input("Ielīmē authorization code: ").strip()

    response = requests.post(
        TOKEN_URL,
        data={
            "code": code,
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    print("\nGOOGLE_REFRESH_TOKEN=")
    print(payload.get("refresh_token", "<missing — check that prompt=consent + access_type=offline>"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
