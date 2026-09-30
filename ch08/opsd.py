"""opsd: 서버의 운영 기능을 정해진 HTTP 경로로만 노출하는 작은 운영 API (8장 실습용).

에이전트는 샌드박스 안에서 이 API만 부를 수 있고, 어떤 경로를 부를 수 있는지는
OpenShell 네트워크 정책이 정한다. opsd 자체는 호스트의 루프백에만 연다.

  GET    /v1/status/disk | /v1/status/memory | /v1/status/uptime
  GET    /v1/containers
  GET    /v1/services/<name>/status
  GET    /v1/services/<name>/logs?lines=N
  POST   /v1/services/<name>/restart      (중간 위험)
  POST   /v1/services/<name>/stop         (높은 위험)
  DELETE /v1/services/<name>              (높은 위험)

사용: OPS_TOKEN=... python3 opsd.py   (기본 127.0.0.1:18080)
"""
import datetime, json, os, re, subprocess, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SERVICES = {"web": "lab-nginx"}          # 서비스 이름 -> 컨테이너 이름 (허용 목록)
TOKEN = os.environ.get("OPS_TOKEN", "")
AUDIT = os.environ.get("OPS_AUDIT", "opsd-audit.log")


def sh(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return (p.stdout + p.stderr).strip()


class H(BaseHTTPRequestHandler):
    def _reply(self, code, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        with open(AUDIT, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} {self.command} {self.path} -> {code}\n")

    def _auth(self):
        if TOKEN and self.headers.get("X-Ops-Token") != TOKEN:
            self._reply(401, {"error": "unauthorized"})
            return False
        return True

    def _service(self, name):
        if name not in SERVICES:
            self._reply(404, {"error": f"unknown service '{name}'", "services": list(SERVICES)})
            return None
        return SERVICES[name]

    def do_GET(self):
        if not self._auth():
            return
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/v1/status/disk":
            return self._reply(200, {"output": sh("df", "-h", "/")})
        if u.path == "/v1/status/memory":
            return self._reply(200, {"output": sh("free", "-m")})
        if u.path == "/v1/status/uptime":
            return self._reply(200, {"output": sh("uptime")})
        if u.path == "/v1/containers":
            return self._reply(200, {"output": sh("docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}")})
        m = re.fullmatch(r"/v1/services/([a-z0-9-]+)/(status|logs)", u.path)
        if m:
            c = self._service(m.group(1))
            if c is None:
                return
            if m.group(2) == "status":
                return self._reply(200, {"service": m.group(1), "output": sh("docker", "inspect", "-f", "{{.State.Status}} since {{.State.StartedAt}} restarts={{.RestartCount}}", c)})
            lines = str(min(int(q.get("lines", ["20"])[0]), 200))
            return self._reply(200, {"service": m.group(1), "output": sh("docker", "logs", "--tail", lines, c)})
        self._reply(404, {"error": "not found"})

    def do_POST(self):
        if not self._auth():
            return
        m = re.fullmatch(r"/v1/services/([a-z0-9-]+)/(restart|stop)", urllib.parse.urlparse(self.path).path)
        if not m:
            return self._reply(404, {"error": "not found"})
        c = self._service(m.group(1))
        if c is None:
            return
        return self._reply(200, {"service": m.group(1), "action": m.group(2), "output": sh("docker", m.group(2), c)})

    def do_DELETE(self):
        if not self._auth():
            return
        m = re.fullmatch(r"/v1/services/([a-z0-9-]+)", urllib.parse.urlparse(self.path).path)
        if not m:
            return self._reply(404, {"error": "not found"})
        c = self._service(m.group(1))
        if c is None:
            return
        return self._reply(200, {"service": m.group(1), "action": "delete", "output": sh("docker", "rm", "-f", c)})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    host, port = os.environ.get("OPS_HOST", "127.0.0.1"), int(os.environ.get("OPS_PORT", "18080"))
    print(f"opsd on {host}:{port}, services={SERVICES}, auth={'on' if TOKEN else 'off'}", flush=True)
    ThreadingHTTPServer((host, port), H).serve_forever()
