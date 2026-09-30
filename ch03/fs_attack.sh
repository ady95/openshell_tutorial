#!/usr/bin/env bash
# 03-3 실습: 샌드박스 안에서 1장의 파일 공격을 다시 시도한다.
# 호스트에서 실행: openshell sandbox exec -n <이름> --no-login-shell -- bash -s < ch03/fs_attack.sh
run() { printf '\n$ %s\n' "$*"; bash -c "$*" 2>&1 | head -6; printf '(exit=%s)\n' "${PIPESTATUS[0]}"; }
echo "== 0. 작업 디렉터리 확인 =="; run 'cd /sandbox && pwd && echo "고객 목록 원본" > important-file.txt && ls'
cd /sandbox 2>&1 || true
echo "== 1. /etc 읽기·쓰기 ==";          run 'head -2 /etc/passwd'; run 'echo x >> /etc/hosts'
echo "== 2. SSH 키 읽기 ==";              run 'cat /home/ubuntu/.ssh/id_ed25519'
echo "== 3. 클라우드 자격 증명 읽기 ==";   run 'cat /home/ubuntu/.aws/credentials'
echo "== 4. 사용자 홈 디렉터리 목록 ==";   run 'ls -la /home/ubuntu'
echo "== 5. 다른 프로젝트 접근 ==";        run 'cat /srv/other-project/.env'
echo "== 6. 시스템 바이너리 변조 ==";      run 'cp /bin/true /usr/local/bin/sneaky'
echo "== 7. 작업 폴더 안 파일 삭제 ==";    run 'rm -v /sandbox/important-file.txt'
echo "== 8. 셸 시작 파일 수정 ==";         run 'echo "# planted" >> /sandbox/.bashrc && tail -1 /sandbox/.bashrc'
echo "== 9. /dev/null 사용 ==";           run 'echo test > /dev/null && echo ok'
