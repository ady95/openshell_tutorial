"""8장 실습용 서버관리 에이전트: 로컬 LLM(Ollama)의 도구 호출로 opsd API를 부른다.

샌드박스 안에서 실행한다. 정책에 막히면 policy.local에 좁은 규칙을 제안하고
사람의 결정을 기다린다. 표준 라이브러리만 사용한다.
사용: python3 server_agent.py "요청 문장"
"""
import json, os, re, sys, time, urllib.error, urllib.request

LLM = os.environ.get("OPENAI_BASE_URL", "http://host.openshell.internal:11434/v1")
MODEL = os.environ.get("AGENT_MODEL", "qwen3.5:4b")
OPS = os.environ.get("OPS_BASE_URL", "http://host.openshell.internal:18080")
TOKEN = os.environ.get("OPS_TOKEN", "")          # Provider가 넣어 주는 자리표시자
MAX_STEPS = int(os.environ.get("AGENT_MAX_STEPS", "8"))

SYSTEM = """당신은 리눅스 서버를 관리하는 보조 에이전트입니다.
서버는 ops API로만 다룹니다. 사용할 수 있는 경로:
- GET /v1/status/disk, /v1/status/memory, /v1/status/uptime, /v1/containers
- GET /v1/services/<이름>/status, /v1/services/<이름>/logs?lines=N
- POST /v1/services/<이름>/restart
서비스 이름은 web 하나입니다.
규칙:
1. 먼저 조회로 상황을 파악하고, 꼭 필요할 때만 변경 작업을 합니다.
2. 요청이 policy_denied로 막히면 그 작업에 필요한 메서드와 경로 하나만 request_permission으로 요청하고 결과를 기다립니다. 넓은 권한을 요청하지 않습니다.
3. 권한 요청이 거부되면 우회하지 말고 사용자에게 이유를 보고합니다.
4. 작업이 끝나면 한국어로 짧게 결과를 보고합니다."""

TOOLS = [
    {"type": "function", "function": {"name": "ops_get", "description": "ops API에 GET 요청",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "ops_post", "description": "ops API에 POST 요청 (변경 작업)",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "request_permission", "description": "막힌 요청 하나에 대한 권한을 사람에게 요청하고 결정을 기다림",
     "parameters": {"type": "object", "properties": {"method": {"type": "string"}, "path": {"type": "string"},
                    "reason": {"type": "string"}}, "required": ["method", "path", "reason"]}}},
]


def http(method, url, body=None, headers=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except urllib.error.URLError as e:
        return 0, f"connection failed: {e.reason}"


def ops(method, path):
    code, text = http(method, OPS + path, headers={"X-Ops-Token": TOKEN})
    if code == 403 and "policy_denied" in text:
        text = json.dumps({"error": "policy_denied", "detail": json.loads(text).get("detail")}, ensure_ascii=False)
    return f"HTTP {code}: {text[:1500]}"


def request_permission(method, path, reason):
    path = path.split("?")[0]
    name = "ops_" + method.lower() + "_" + re.sub(r"[^a-z0-9]+", "_", path.lower()).strip("_")
    proposal = {"intent_summary": reason, "operations": [{"addRule": {"ruleName": name, "rule": {
        "name": name,
        "endpoints": [{"host": "host.openshell.internal", "port": 18080, "protocol": "rest",
                       "enforcement": "enforce", "rules": [{"allow": {"method": method.upper(), "path": path}}]}],
        "binaries": [{"path": "/usr/bin/python3.12"}]}}}]}
    code, text = http("POST", "http://policy.local/v1/proposals", proposal)
    if not (200 <= code < 300) or not json.loads(text).get("accepted_chunk_ids"):
        return f"proposal not accepted: {text[:500]}"
    cid = json.loads(text)["accepted_chunk_ids"][0]
    print(f"    [권한 요청 제출] chunk={cid} {method.upper()} {path} — 사람의 승인을 기다립니다...", flush=True)
    for _ in range(20):
        code, text = http("GET", f"http://policy.local/v1/proposals/{cid}/wait?timeout=60", timeout=90)
        d = json.loads(text) if 200 <= code < 300 else {}
        if d.get("status") in ("approved", "rejected"):
            break
    if d.get("status") == "approved":
        for _ in range(10):
            if d.get("policy_reloaded"):
                break
            time.sleep(3)
            d = json.loads(http("GET", f"http://policy.local/v1/proposals/{cid}")[1])
        return "approved: 권한이 승인되어 적용되었습니다. 원래 요청을 다시 시도하세요."
    return f"{d.get('status', 'timeout')}: {d.get('rejection_reason', '')}"


def chat(messages):
    code, text = http("POST", LLM + "/chat/completions", {
        "model": MODEL, "messages": messages, "tools": TOOLS,
        "temperature": 0, "reasoning_effort": "none"}, timeout=900)
    if code != 200:
        raise SystemExit(f"LLM error {code}: {text[:300]}")
    return json.loads(text)["choices"][0]["message"]


def main():
    task = sys.argv[1] if len(sys.argv) > 1 else "서버 상태를 점검해 주세요."
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": task}]
    print(f"[사용자] {task}", flush=True)
    for step in range(1, MAX_STEPS + 1):
        t = time.time()
        msg = chat(messages)
        messages.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")})
        calls = msg.get("tool_calls") or []
        if not calls:
            print(f"[{step}] 에이전트 보고 ({time.time() - t:.0f}s): {msg.get('content', '').strip()}", flush=True)
            return
        for c in calls:
            fn, args = c["function"]["name"], json.loads(c["function"]["arguments"] or "{}")
            print(f"[{step}] 도구 호출 ({time.time() - t:.0f}s): {fn} {json.dumps(args, ensure_ascii=False)}", flush=True)
            if fn == "ops_get":
                out = ops("GET", args["path"])
            elif fn == "ops_post":
                out = ops("POST", args["path"])
            elif fn == "request_permission":
                out = request_permission(args["method"], args["path"], args["reason"])
            else:
                out = f"unknown tool {fn}"
            print("    → " + out[:300].replace("\n", " | "), flush=True)
            messages.append({"role": "tool", "tool_call_id": c.get("id", fn), "content": out})
    print("[중단] 단계 상한에 도달했습니다.", flush=True)


if __name__ == "__main__":
    main()
