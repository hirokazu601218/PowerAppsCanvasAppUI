"""Read-only export and scope check for the maker-owned publish probe copy."""
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge
from lightweight_transaction import verify_database_references, source_hashes, runtime_hashes

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/apps/staff-master.json").read_text())
EXPECTED = json.loads((ROOT / "automation/lightweight-expected.json").read_text())
APP_ID = "c5dece33-b799-43be-a55b-3344c83979d9"
SOLUTION = "DEPLOYPROBE_AUTOPUBLISH_SOLUTION_20260925"
COMPONENT = "cra05_deployprobeautopublish20260924_d98b1"
OUT = ROOT / "artifacts/lightweight-maker-copy-probe"
OUT.mkdir(parents=True, exist_ok=False)
result = {"operation": "maker_copy_read_only_export", "app_id": APP_ID,
          "solution": SOLUTION, "status": "started", "touched": False}

def command(args, name, timeout=300):
    with (OUT / (name + ".log")).open("w") as log:
        subprocess.run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                       timeout=timeout, check=True)

try:
    bridge.require(APP_ID != CFG["target"]["app_id"], "stable app is not a probe target")
    env = CFG["target"]["dataverse_url"]
    command(["pac", "auth", "create", "--name", "maker-copy-probe",
             "--githubFederated", "--tenant", CFG["tenant_id"],
             "--applicationId", CFG["client_id"], "--environment", env], "auth", 120)
    package = OUT / "current.zip"
    command(["pac", "solution", "export", "--name", SOLUTION,
             "--path", str(package), "--overwrite"], "export", 300)
    folder = OUT / "current"
    command(["pac", "solution", "unpack", "--zipfile", str(package),
             "--folder", str(folder), "--packagetype", "Unmanaged"], "unpack", 180)
    root = ET.parse(folder / "Other/Solution.xml").getroot()
    components = [(e.get("type"), e.get("schemaName")) for e in root.iter("RootComponent")]
    bridge.require(components == [("300", COMPONENT)], "solution component scope mismatch")
    metas = list((folder / "CanvasApps").glob("*.meta.xml"))
    apps = list((folder / "CanvasApps").glob("*_DocumentUri.msapp"))
    bridge.require(len(metas) == len(apps) == 1, "expected exactly one Canvas document")
    refs = verify_database_references(metas[0], EXPECTED["required_database_sources"])
    archive = bridge.read_archive(apps[0])
    bridge.require("Src/scrHome.pa.yaml" in archive and
                   "Src/scrStaffMasterSearch.pa.yaml" in archive,
                   "unexpected Canvas source structure")
    home = yaml.safe_load(archive["Src/scrHome.pa.yaml"])
    nodes = bridge.nodes(home, "lblHomePrototype")
    bridge.require(len(nodes) == 1, "home probe label is not unique")
    formula = nodes[0]["Properties"]["Text"]
    bridge.require("【公開試験】UI検討用 v1.27" in formula,
                   "published v2 baseline marker missing")
    result.update(status="pass", components=components,
                  database_sources=sorted(refs["default.cds"]["dataSources"]),
                  source_count=len(source_hashes(archive)),
                  runtime_control_count=len(runtime_hashes(archive)),
                  app_sha256=hashlib.sha256(apps[0].read_bytes()).hexdigest(),
                  home_label_formula=formula)
except Exception as error:
    result.update(status="fail", error_type=type(error).__name__, error=str(error))
    raise
finally:
    (OUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False), flush=True)
