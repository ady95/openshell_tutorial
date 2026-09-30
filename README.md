# OpenShell 따라하기 — 예제 코드

위키독스 책 「OpenShell 따라하기 (로컬 AI 에이전트를 위한 안전한 실행 환경 만들기)」의 실습 코드입니다.

- 책: https://wikidocs.net/book/21463
- 기준 버전: OpenShell v0.1.2, Ubuntu 24.04 LTS + Docker Engine

| 파일 | 책 페이지 | 내용 |
|---|---|---|
| `ch01_unprotected.sh` | 01-2 | 정책 없는 환경에서 셸 명령으로 할 수 있는 일 (가짜 홈·가짜 자격 증명 사용) |
| `images/lab/Dockerfile` | 02-4 이후 | 실습용 샌드박스 이미지 (기본 이미지 + curl, python3, git, jq) |
| `images/lab-target/Dockerfile` | 03-3 | 가짜 비밀 파일을 담은 공격 대상 이미지 |
| `ch03/fs_attack.sh` | 03-3 | 샌드박스 안 파일 공격 스크립트 |
| `ch03/policy-*.yaml` | 03-2~03-4 | 기본·잘못 넓힌·최소·작업 디렉터리 누락·실행 사용자 정책 예 |
| `ch03/proc_probe.sh` | 03-4 | 권한 상승·격리 우회 시도 스크립트 |

## 주의

실습 스크립트는 실제 키를 건드리지 않도록 `~/openshell-lab/` 아래에 가짜 홈 디렉터리를 만들어 실행합니다.
외부 전송 실험은 `127.0.0.1`의 수신 서버로만 보냅니다. 실습이 끝나면 `~/openshell-lab/`을 지우세요.

## 실습 이미지 만들기

```bash
cd images/lab
docker build -t openshell-lab:0.1 .
```
