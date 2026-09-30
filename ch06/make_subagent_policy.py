"""부모 에이전트 역할: 하위 작업 명세(JSON)로 하위 에이전트 정책(YAML)을 만든다.
사용: python3 make_subagent_policy.py task.json > candidate.yaml
task.json 예: {"name": "issue-reader", "rules": [{"host": "api.github.com", "binary": "/usr/bin/curl", "access": "read-only"}]}
"""
import json, sys

task = json.load(open(sys.argv[1], encoding="utf-8"))
lines = [
    "# generated for subagent: " + task["name"],
    "version: 1",
    "filesystem_policy:",
    "  include_workdir: false",
    "  read_only: [/usr, /lib, /etc, /var/log, /proc, /dev/urandom]",
    "  read_write: [/sandbox, /tmp, /dev/null]",
    "landlock:",
    "  compatibility: hard_requirement",
]
if task.get("rules"):
    lines.append("network_policies:")
for i, r in enumerate(task.get("rules", [])):
    lines += [
        f"  rule_{i}:",
        "    endpoints:",
        f"      - host: {r['host']}",
        f"        port: {r.get('port', 443)}",
        "        protocol: rest",
        "        enforcement: enforce",
        f"        access: {r.get('access', 'read-only')}",
        "    binaries:",
        f"      - path: {r['binary']}",
    ]
print("\n".join(lines))
