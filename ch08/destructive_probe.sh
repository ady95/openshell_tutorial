#!/usr/bin/env bash
# 08-3 실습: 서버관리 샌드박스 안에서 파괴적 명령을 시도한다 (샌드박스 밖에는 영향 없음)
run() { printf '\n$ %s\n' "$*"; timeout 10 bash -c "$*" 2>&1 | head -3; printf '(exit=%s)\n' "${PIPESTATUS[0]}"; }
echo "== 파일시스템 파괴";   run 'rm -rf /usr/bin/python3.12'; run 'chmod -R 777 /etc'; run 'mkfs.ext4 /dev/sda'
echo "== 사용자 관리";       run 'userdel ubuntu'; run 'useradd attacker'
echo "== 네트워크 변경";     run 'iptables -F'; run 'ip link set lo down'
echo "== 서비스 직접 제어";  run 'systemctl stop nginx'; run 'docker stop lab-nginx'; run 'kill -9 1'
echo "== 작업 폴더 삭제";    run 'mkdir -p /sandbox/work && touch /sandbox/work/a && rm -rf /sandbox/work && echo removed'
