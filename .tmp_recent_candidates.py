import yaml

path = r"problems_external\_sources\teorth_erdosproblems_live\data\problems.yaml"
with open(path, encoding="utf-8") as handle:
    problems = yaml.safe_load(handle)

items = [
    item
    for item in problems
    if item.get("status", {}).get("state") in {"open", "decidable", "falsifiable"}
    and item.get("status", {}).get("last_update", "") >= "2026-01-01"
]
items.sort(key=lambda item: item["status"]["last_update"], reverse=True)

for item in items:
    status = item["status"]
    tags = ",".join(item.get("tags", []))
    formal = item.get("formalized", {}).get("state", "")
    comments = item.get("comments", "")
    print(
        f"{item['number']} {status['state']} {status['last_update']} "
        f"tags={tags} formal={formal} comments={comments}"
    )
