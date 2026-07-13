import json, sys
core, sol_in, sol_out = sys.argv[1], sys.argv[2], sys.argv[3]
m = {}
for line in open(core):
    r = json.loads(line)
    if r.get("type") == "col":
        m[r["col"]] = r["source_col"]
with open(sol_out, "w") as f:
    for line in open(sol_in):
        r = json.loads(line)
        c = r["col"]
        if c in m:
            f.write(json.dumps({"source_col": m[c], "num": r["num"], "den": r["den"]}) + "\n")
print("converted", len(m), "cols")