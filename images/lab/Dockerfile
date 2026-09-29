# OpenShell 따라하기 실습용 샌드박스 이미지
# 기본 이미지(nvcr.io/nvidia/base/ubuntu:24.04)에는 curl 같은 도구가 없어
# 네트워크·파일 실험에 필요한 최소 도구만 더한다.
FROM nvcr.io/nvidia/base/ubuntu:24.04

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl python3 git jq iproute2 procps \
 && rm -rf /var/lib/apt/lists/*
