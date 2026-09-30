"""샌드박스 안에서 로컬 모델을 부르는 최소 예제 (표준 라이브러리만 사용)."""
import json, os, sys, time, urllib.request

base = os.environ.get("OPENAI_BASE_URL", "http://host.openshell.internal:11434/v1")
model = sys.argv[1] if len(sys.argv) > 1 else "qwen3.5:4b"
prompt = sys.argv[2] if len(sys.argv) > 2 else "한 문장으로 자기소개를 해 주세요."
body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                   "stream": False, "reasoning_effort": "none"}).encode()
req = urllib.request.Request(base + "/chat/completions", data=body,
                             headers={"Content-Type": "application/json"})
t = time.time()
with urllib.request.urlopen(req, timeout=600) as r:
    data = json.load(r)
print(data["choices"][0]["message"]["content"].strip())
u = data.get("usage", {})
print(f"[{model}] {time.time() - t:.1f}s, completion_tokens={u.get('completion_tokens')}", file=sys.stderr)
