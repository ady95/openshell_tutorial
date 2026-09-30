#!/usr/bin/env bash
# 관문: 후보 정책이 경계 안에 있을 때만(within_boundary) 하위 에이전트 샌드박스를 만든다.
# 사용: bash gate.sh <candidate.yaml> <boundary.yaml> <sandbox-name> [image]
set -u
cand=$1; boundary=$2; name=$3; image=${4:-openshell-lab:0.1}
json=$(openshell-prover check "$cand" --boundary "$boundary" --output json)
result=$(printf '%s' "$json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"])')
echo "prover: $result"
if [ "$result" != "within_boundary" ]; then
  printf '%s' "$json" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("reason:", d.get("reason") or d.get("counterexample"))'
  echo "REJECT: 하위 에이전트를 만들지 않습니다."
  exit 1
fi
openshell sandbox create --name "$name" --from "$image" --no-auto-providers --detach --policy "$cand" </dev/null | tail -1
echo "APPLY: $name 생성"
