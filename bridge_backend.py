# bridge_backend.py
# -----------------
import json
from typing import Any, List

import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

MCP_SSE_URL = "http://localhost:8010/sse"
TOOL_NAME   = "generate_match_questions"

app = FastAPI(title="Matchmaker Bridge & UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/questions", response_class=JSONResponse)
async def request_match_questions() -> List[dict[str, Any]]:
    # (Optional) fetch user data from Flask
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/questions")
            resp.raise_for_status()
            user_data = resp.json()
    except Exception as e:
        print(f"[bridge] Flask fetch failed: {e}")
        user_data = {}  # let the MCP tool default

    payload = {"tool": TOOL_NAME, "arguments": user_data}
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
    }

    # 1) POST → MCP
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(MCP_SSE_URL, headers=headers, json=payload)
            resp.raise_for_status()
            text = resp.text
    except httpx.HTTPError as exc:
        print("[bridge] error talking to MCP:", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not reach MCP: {exc}"
        ) from exc

    # 2) Parse out the first "data: [...]" line
    questions = None
    for line in text.splitlines():
        if not line.startswith("data:"):
            continue
        body = line[len("data:"):].strip()
        if body == "[DONE]":
            continue
        try:
            parsed = json.loads(body)

            # if MCP streamed an {"error": "..."} message -> 502 with detail
            if isinstance(parsed, dict) and "error" in parsed:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"MCP error: {parsed['error']}"
                )

            questions = parsed    # normal happy path (a list)

            # questions = json.loads(body)
            break
        except json.JSONDecodeError:
            print("[bridge] invalid JSON in SSE payload:", body)
            continue

    if not isinstance(questions, list):
        print("[bridge] no questions list found in MCP response:")
        print(text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MCP did not return a questions list"
        )

    return questions


# ─────────────────────────────────────────────────────────────────────────────
# A tiny HTML UI so you can test in-browser
# ─────────────────────────────────────────────────────────────────────────────
HTML_PAGE = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>Matchmaker Bridge</title>
<style>body{font-family:sans-serif;padding:2rem}button{padding:.7rem 1.4rem}</style>
</head><body>
  <h1>Matchmaker Questions</h1>
  <button id="load">Load questions</button>
  <pre id="out">[click “Load questions”]</pre>
  <script>
    document.getElementById("load").onclick = async () => {
      const out = document.getElementById("out");
      out.textContent = "Loading…";
      try {
        const resp = await fetch("/questions", { method: "POST" });
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        const data = await resp.json();
        out.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        out.textContent = "Error: " + err;
      }
    };
  </script>
</body></html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(HTML_PAGE)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bridge_backend:app", host="0.0.0.0", port=8080, reload=True)