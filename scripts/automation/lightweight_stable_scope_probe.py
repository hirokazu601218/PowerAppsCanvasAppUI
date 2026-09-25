"""Read-only inventory of the stable solution for isolated-scope transferability."""
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge
from lightweight_transaction import verify_database_references

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/apps/staff-master.json").read_text())
EXPECTED = json.loads((ROOT / "automation/lightweight-expected.json").read_text())
OUT = ROOT / "artifacts/lightweight-stable-scope"
OUT.mkdir(parents=True, exist_ok=False)
result = {"operation": "stable_solution_scope_read_only", "status": "started",
          "target": CFG["target"]["app_id"], "touched": False}

def command(args, name, timeout=300):
    with (OUT / (name + ".log")).open("w") as log:
        subprocess.run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=timeout)

try:
    bridge.require(CFG["target"]["app_id"] == "362ac991-eead-4f07-8373-afdb3ebfdba1",
                   "unexpected stable target")
    bridge.require(EXPECTED.get("deployment_enabled") is not True,
                   "stable deployment must remain disabled")
    command(["pac", "auth", "create", "--name", "stable-scope",
             "--githubFederated", "--tenant", CFG["tenant_id"],
             "--applicationId", CFG["client_id"],
             "--environment", CFG["target"]["dataverse_url"]], "auth", 120)
    package = OUT / "current.zip"
    command(["pac", "solution", "export", "--name", CFG["solution_name"],
             "--path", str(package), "--overwrite"], "export")
    folder = OUT / "current"
    command(["pac", "solution", "unpack", "--zipfile", str(package),
             "--folder", str(folder), "--packagetype", "Unmanaged"], "unpack", 180)
    root = ET.parse(folder / "Other/Solution.xml").getroot()
    components = [(e.get("type"), e.get("schemaName")) for e in root.iter("RootComponent")]
    apps = list((folder / "CanvasApps").glob("*_DocumentUri.msapp"))
    metas = list((folder / "CanvasApps").glob("*.meta.xml"))
    result["root_component_count"] = len(components)
    result["root_component_type_counts"] = {
        kind: sum(x[0] == kind for x in components) for kind in sorted({x[0] for x in components})}
    result["canvas_document_count"] = len(apps)
    result["canvas_metadata_count"] = len(metas)
    result["same_one_component_scope"] = len(components) == len(apps) == len(metas) == 1 and components[0][0] == "300"
    if len(metas) == 1:
        try:
            refs = verify_database_references(metas[0], EXPECTED["required_database_sources"])
            result["three_database_references_in_solution"] = sorted(refs["default.cds"]["dataSources"])
        except Exception as exc:
            result["three_database_references_in_solution"] = []
            result["reference_verification_error"] = str(exc)
    result["status"] = "pass"
except Exception as error:
    result.update(status="fail", error_type=type(error).__name__, error=str(error))
    raise
finally:
    (OUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False), flush=True)
