# 3장 공격 실험용 이미지: 실습 이미지 + 가짜 비밀 파일
# 파일 소유자를 샌드박스 사용자(uid 1000)로 두어, 파일 권한이 아니라
# OpenShell 정책(Landlock)이 접근을 막는지 확인할 수 있게 한다.
FROM openshell-lab:0.1

RUN mkdir -p /home/ubuntu/.ssh /home/ubuntu/.aws /srv/other-project \
 && printf -- '-----BEGIN OPENSSH PRIVATE KEY-----\nFAKE-KEY-FOR-OPENSHELL-BOOK-DO-NOT-USE\n-----END OPENSSH PRIVATE KEY-----\n' > /home/ubuntu/.ssh/id_ed25519 \
 && printf '[default]\naws_access_key_id = AKIAFAKEFAKEFAKE0000\naws_secret_access_key = fake/secret/for/book\n' > /home/ubuntu/.aws/credentials \
 && echo "DB_PASSWORD=fake-other-project-password" > /srv/other-project/.env \
 && chown -R 1000:1000 /home/ubuntu /srv/other-project \
 && chmod 700 /home/ubuntu/.ssh && chmod 600 /home/ubuntu/.ssh/id_ed25519 /home/ubuntu/.aws/credentials
