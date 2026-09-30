#!/usr/bin/env bash
# 03-4 실습: 샌드박스 안에서 권한 상승·격리 우회 시도
run() { printf '\n$ %s\n' "$*"; timeout 10 bash -c "$*" 2>&1 | head -4; printf '(exit=%s)\n' "${PIPESTATUS[0]}"; }
echo "== 신원과 권한 ==";         run 'id'; run 'grep -E "^(CapEff|CapBnd|NoNewPrivs|Seccomp)" /proc/self/status'
echo "== root 되기 ==";           run 'python3 -c "import os; os.setuid(0)"'; run 'ls -l /usr/bin/su'; run 'su -c id root < /dev/null'
echo "== 네임스페이스·마운트 ==";  run 'unshare -r id'; run 'mkdir -p /tmp/m && mount -t tmpfs none /tmp/m'
echo "== 다른 프로세스 엿보기 ==";  run 'ps -o pid,user,cmd -e | head -4'; run 'cat /proc/1/environ | tr "\0" "\n" | head -3'
echo "== 자원 한도 ==";           run 'cat /sys/fs/cgroup/pids.max'; run 'ulimit -c'
