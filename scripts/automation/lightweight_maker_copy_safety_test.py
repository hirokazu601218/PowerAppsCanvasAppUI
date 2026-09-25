"""Exercise the isolated revision gates and deliberate post-import restoration.

The active app, its data references, and every runtime rule are read back.
The observed solution import made this isolated app live immediately, even without a separate
Publish action. This is an isolated test script with exactly three test modes.
The original revision workflow stays disabled.
"""
import copy
import hashlib
import json
import shutil
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
MANIFEST = json.loads((ROOT / "automation/lightweight-maker-copy-change.json").read_text())
MODE = sys.argv[1] if len(sys.argv) == 2 else ""
bridge.require(MODE in ("wrong-target", "wrong-before", "rollback"), "explicit safety-test mode required")
ORIGINAL_FORMULA = MANIFEST["changes"][0]["after"]
if MODE == "wrong-target":
    MANIFEST["target"]["app_id"] = CFG["target"]["app_id"]
else:
    MANIFEST["changes"][0]["before"] = ORIGINAL_FORMULA
if MODE == "wrong-before":
    MANIFEST["changes"][0]["before"] = "=BAD_PRE_IMPORT_TEST"
if MODE == "rollback":
    MANIFEST["changes"][0]["after"] = ORIGINAL_FORMULA.replace("【GitHub配布試験】", "【切り戻し試験】")
    bridge.require(MANIFEST["changes"][0]["after"] != ORIGINAL_FORMULA, "test marker missing")
OUT = ROOT / "artifacts/lightweight-maker-copy-safety" / MODE
OUT.mkdir(parents=True, exist_ok=False)
result = {"operation": "maker_copy_safety_test", "mode": MODE, "app_id": MANIFEST["target"]["app_id"],
          "status": "started", "touched": False, "restoration": "not_needed"}
backup = None
baseline = None

def command(args, name, timeout=600):
    with (OUT / (name + ".log")).open("w") as log:
        subprocess.run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                       timeout=timeout, check=True)

def inspect(folder):
    root = ET.parse(folder / "Other/Solution.xml").getroot()
    components = [(e.get("type"), e.get("schemaName")) for e in root.iter("RootComponent")]
    bridge.require(components == [("300", MANIFEST["component"])],
                   "isolated solution scope expanded")
    apps = list((folder / "CanvasApps").glob("*_DocumentUri.msapp"))
    metas = list((folder / "CanvasApps").glob("*.meta.xml"))
    bridge.require(len(apps) == len(metas) == 1, "expected one Canvas document")
    refs = verify_database_references(metas[0], EXPECTED["required_database_sources"])
    archive = bridge.read_archive(apps[0])
    bridge.require("Src/scrHome.pa.yaml" in archive and
                   "Src/scrStaffMasterSearch.pa.yaml" in archive,
                   "unexpected Canvas source structure")
    return {"app": apps[0], "refs": refs, "archive": archive,
            "sources": source_hashes(archive), "runtime": runtime_hashes(archive)}

def export(name):
    path = OUT / (name + ".zip")
    command(["pac", "solution", "export", "--name", MANIFEST["solution"],
             "--path", str(path), "--overwrite"], name + "-export")
    folder = OUT / name
    command(["pac", "solution", "unpack", "--zipfile", str(path),
             "--folder", str(folder), "--packagetype", "Unmanaged"], name + "-unpack", 180)
    return path, inspect(folder)

def import_package(path, name):
    command(["pac", "solution", "import", "--path", str(path),
             "--environment", CFG["target"]["dataverse_url"],
             "--force-overwrite"], name + "-import", 600)

def same(left, right):
    return all(left[k] == right[k] for k in ("refs", "sources", "runtime"))

try:
    bridge.require(MANIFEST["schema"] == 1 and MANIFEST["approved"] is True,
                   "missing approved revision manifest")
    bridge.require(MANIFEST["target"]["environment_id"] == CFG["target"]["environment_id"]
                   and MANIFEST["target"]["dataverse_url"] == CFG["target"]["dataverse_url"]
                   and MANIFEST["target"]["app_id"] != CFG["target"]["app_id"],
                   "target is not the isolated environment and copy")
    bridge.require(MANIFEST["target"]["app_id"] == "c5dece33-b799-43be-a55b-3344c83979d9"
                   and MANIFEST["solution"] == "DEPLOYPROBE_AUTOPUBLISH_SOLUTION_20260925",
                   "unapproved isolated target")
    changes = MANIFEST["changes"]
    bridge.require(len(changes) == 1 and changes[0]["source"] == "Src/scrHome.pa.yaml"
                   and changes[0]["control"] == "lblHomePrototype"
                   and changes[0]["property"] == "Text",
                   "unapproved change scope")
    command(["pac", "auth", "create", "--name", "maker-copy-revision",
             "--githubFederated", "--tenant", CFG["tenant_id"],
             "--applicationId", CFG["client_id"],
             "--environment", CFG["target"]["dataverse_url"]], "auth", 120)
    backup, baseline = export("baseline")
    baseline_sha = hashlib.sha256(baseline["app"].read_bytes()).hexdigest()
    if MODE in ("wrong-before", "rollback"):
        current_doc = yaml.safe_load(baseline["archive"]["Src/scrHome.pa.yaml"])
        current_nodes = bridge.nodes(current_doc, "lblHomePrototype")
        bridge.require(len(current_nodes) == 1 and
                       current_nodes[0]["Properties"]["Text"] == ORIGINAL_FORMULA,
                       "current live copy is not the approved v3 test baseline")
        MANIFEST["baseline_msapp_sha256"] = baseline_sha
    bridge.require(baseline_sha == MANIFEST["baseline_msapp_sha256"],
                   "server baseline changed since read-only qualification")
    doc = yaml.safe_load(baseline["archive"][changes[0]["source"]])
    nodes = bridge.nodes(doc, changes[0]["control"])
    bridge.require(len(nodes) == 1 and
                   nodes[0]["Properties"][changes[0]["property"]] == changes[0]["before"],
                   "baseline label is different from GitHub manifest")
    work = OUT / "bridge-input"
    (work / "config/apps").mkdir(parents=True)
    local_cfg = copy.deepcopy(CFG)
    local_cfg["target"] = MANIFEST["target"]
    local_cfg.update(baseline_msapp="baseline.msapp", baseline_sha256=baseline_sha)
    (work / "config/apps/staff-master.json").write_text(json.dumps(local_cfg))
    shutil.copyfile(baseline["app"], work / "baseline.msapp")
    for name, data in baseline["archive"].items():
        if name.startswith("Src/") and name.endswith(".pa.yaml"):
            dest = work / "powerapps/canvas-v3" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    target = work / "powerapps/canvas-v3" / changes[0]["source"]
    nodes[0]["Properties"][changes[0]["property"]] = changes[0]["after"]
    target.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False))
    candidate_app = OUT / "candidate.msapp"
    result["build"] = bridge.build(work, candidate_app, MANIFEST)
    candidate_archive = bridge.read_archive(candidate_app)
    candidate_sources = source_hashes(candidate_archive)
    candidate_runtime = runtime_hashes(candidate_archive)
    bridge.require({k for k in candidate_sources if candidate_sources[k] != baseline["sources"][k]}
                   == {changes[0]["source"]}, "unexpected source change")
    bridge.require({k for k in candidate_runtime if candidate_runtime[k] != baseline["runtime"][k]}
                   == {changes[0]["control"]}, "unexpected runtime change")
    staged = OUT / "staged"
    shutil.copytree(OUT / "baseline", staged)
    shutil.copyfile(candidate_app, staged / "CanvasApps" / baseline["app"].name)
    candidate = OUT / "candidate.zip"
    command(["pac", "solution", "pack", "--folder", str(staged), "--zipfile", str(candidate),
             "--packagetype", "Unmanaged"], "candidate-pack")
    checked = OUT / "checked"
    command(["pac", "solution", "unpack", "--zipfile", str(candidate),
             "--folder", str(checked), "--packagetype", "Unmanaged"], "candidate-unpack", 180)
    preflight = inspect(checked)
    bridge.require(preflight["refs"] == baseline["refs"] and
                   preflight["sources"] == candidate_sources and
                   preflight["runtime"] == candidate_runtime,
                   "candidate package drift")
    result["backup_sha256"] = hashlib.sha256(backup.read_bytes()).hexdigest()
    result["candidate_sha256"] = hashlib.sha256(candidate.read_bytes()).hexdigest()
    result["touched"] = True
    import_package(candidate, "candidate")
    _, deployed = export("deployed")
    bridge.require(deployed["refs"] == baseline["refs"] and
                   deployed["sources"] == candidate_sources and
                   deployed["runtime"] == candidate_runtime,
                   "server readback mismatch")
    bridge.verify_download(deployed["app"], work, MANIFEST)
    if MODE == "rollback":
        result["injection"] = "post_import_verification_failure"
        bridge.require(False, "injected post-import mismatch for restoration test")
    result.update(status="pass", revision_readback="exact",
                  database_sources=sorted(deployed["refs"]["default.cds"]["dataSources"]),
                  after_formula=changes[0]["after"])
except Exception as error:
    result.update(status="fail", error_type=type(error).__name__, error=str(error))
    if result["touched"] and backup is not None:
        try:
            import_package(backup, "failure-restoration")
            _, restored = export("restored")
            result["restoration"] = "verified" if same(restored, baseline) else "mismatch"
        except Exception as restore_error:
            result["restoration"] = type(restore_error).__name__ + ": " + str(restore_error)
    if MODE == "wrong-target" and not result["touched"] and "target is not the isolated" in str(error):
        result.update(status="pass", expected_stop="target_id")
    elif MODE == "wrong-before" and not result["touched"] and "baseline label is different" in str(error):
        result.update(status="pass", expected_stop="before_value")
    elif MODE == "rollback" and result.get("injection") == "post_import_verification_failure" and result["restoration"] == "verified":
        result.update(status="pass", expected_failure="post_import_mismatch", restored_formula=ORIGINAL_FORMULA)
    else:
        raise
finally:
    (OUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False), flush=True)
