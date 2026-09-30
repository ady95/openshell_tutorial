# 7장 실습용: 실습 이미지 + OpenCode CLI
FROM openshell-lab:0.1
ARG OPENCODE_VERSION=1.18.33
RUN curl -fsSL -o /tmp/oc.tgz \
      "https://github.com/anomalyco/opencode/releases/download/v${OPENCODE_VERSION}/opencode-linux-x64.tar.gz" \
 && tar -xzf /tmp/oc.tgz -C /usr/local/bin opencode \
 && chmod 755 /usr/local/bin/opencode && rm /tmp/oc.tgz \
 && opencode --version
