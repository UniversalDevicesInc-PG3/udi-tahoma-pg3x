#!/usr/bin/env python3
"""One-time dev helper: log getJsonProfile() from a running EISY plugin.

Run on the EISY after the plugin has started with static profile/ still present
(or after a JSON push). Waits for PG3 to finish processing, then logs JSON.

Usage (on EISY, from plugin directory):
  python3 scripts/capture_json_profile.py

(C) 2026 Stephen Jenkins
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import udi_interface  # noqa: E402


def main() -> int:
    delay = 10
    print(f"Waiting {delay}s for PG3/IoX profile processing...", flush=True)
    time.sleep(delay)

    poly = udi_interface.Interface([])
    profile = poly.getJsonProfile({"waitResponse": True})
    print(json.dumps(profile, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
