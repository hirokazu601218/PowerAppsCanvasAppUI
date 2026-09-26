#!/usr/bin/env python3
"""Read selected public metadata for the fixed current Canvas app via OIDC."""

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.testing.validate_selection import APP_ID, ENV_ID

TENANT_RESOURCE = "https://service.powerapps.com/"
URL = (f"https://api.powerapps.com/providers/Microsoft.PowerApps/apps/{APP_ID}"
       f"?api-version=2018-10-01&%24filter=environment%20eq%20%27{ENV_ID}%27")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    token = subprocess.check_output(
        ["az", "account", "get-access-token", "--resource", TENANT_RESOURCE,
         "--query", "accessToken", "--output", "tsv"], text=True).strip()
    request = urllib.request.Request(URL, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(request, timeout=90) as response:
        props = json.load(response)["properties"]
    selected = {name: props.get(name) for name in
                ("status", "lastPublishTime", "lastDraftVersion", "appOpenUri")}
    args.output.write_text(json.dumps(selected, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
