"""Read-only inspection of the SCR-003 draft flow; never logs credentials."""
import json, subprocess, urllib.request
from urllib.parse import urlencode
URL="https://orge762dd9e.crm7.dynamics.com"
token=subprocess.check_output(["az","account","get-access-token","--resource",URL,"--query","accessToken","-o","tsv"],text=True).strip()
def get(path):
    with urllib.request.urlopen(urllib.request.Request(URL+"/api/data/v9.2/"+path,headers={"Authorization":"Bearer "+token,"Accept":"application/json"}),timeout=60) as r:
        return json.load(r)
assert get("WhoAmI")["OrganizationId"].lower()=="9efe0732-a9b0-f111-8ade-002248f061b1"
query=urlencode({"$select":"workflowid,name,statecode,clientdata,ismanaged","$filter":"category eq 5 and name eq 'SCR003_勤務時間報告_Excel取込_開発中'"})
rows=get("workflows?"+query)["value"]
assert len(rows)==1, "Exact draft flow not uniquely found"
flow=rows[0]
assert flow["statecode"]==0 and not flow["ismanaged"], "Draft-only inspection"
data=json.loads(flow["clientdata"])
definition=data["properties"]["definition"]
def scrub(obj):
    if isinstance(obj,dict):
        return {k:("[REDACTED]" if any(s in k.lower() for s in ("password","secret","token","credential")) else scrub(v)) for k,v in obj.items()}
    if isinstance(obj,list): return [scrub(x) for x in obj]
    return obj
print("FLOW_ID",flow["workflowid"])
print("DEFINITION",json.dumps(scrub(definition),ensure_ascii=False))
print("CONNECTION_APIS",json.dumps({k:v.get("api",{}) for k,v in data["properties"].get("connectionReferences",{}).items()}))
