#!/usr/bin/env bash
# 서버관리 에이전트 작업 하나를 실행하고, 끝나면 승인된 권한을 회수하고 경계를 검사한다.
# 사용: bash run_task.sh "<요청>"   (호스트에서 실행)
set -u
S=${SANDBOX:-srv}; BOUNDARY=${BOUNDARY:-boundary-server.yaml}; AUDIT=${OPS_AUDIT:-opsd-audit.log}
before=$(wc -l < "$AUDIT" 2>/dev/null || echo 0)
echo "=== 작업 시작 $(date +%T)"
openshell sandbox exec -n "$S" --no-login-shell --timeout 0 -- python3 -u /sandbox/server_agent.py "$1" < /dev/null
echo "=== 작업 종료 $(date +%T)"
echo "=== 이번 작업에서 서버에 실제로 도달한 요청 (운영 API 감사 기록)"
tail -n +$((before + 1)) "$AUDIT"
echo "=== 승인된 규칙 회수"
for r in $(openshell policy get "$S" --base 2>/dev/null | grep -oE '^  ops_(post|delete)_[a-z0-9_]+' | sort -u); do
  openshell policy update "$S" --remove-rule "$r" --wait 2>&1 | tail -1
done
echo "=== 경계 검사"
openshell sandbox get "$S" --policy-only > /tmp/eff-$S.yaml
openshell-prover check /tmp/eff-$S.yaml --boundary "$BOUNDARY"
