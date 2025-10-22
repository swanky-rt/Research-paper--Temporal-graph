# mcp_server.py  –  MCP with POST /sse that really works
import json
from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import StreamingResponse
from fastmcp import FastMCP

# ─── 1. FastMCP app and tool ───────────────────────────────────────────────
mcp = FastMCP("Matchmaker AI Tools")

@mcp.tool()
async def generate_match_questions(
    *, preferences: List[str] | None = None, bio: str | None = None
) -> List[Dict[str, Any]]:
    # (same implementation as before) ………………………………………
    if preferences is None and bio is None:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://localhost:8000/questions")
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            print("Flask fetch failed:", e)
            data = {"preferences": [], "bio": ""}
    else:
        data = {"preferences": preferences or [], "bio": bio or ""}

    prefs, bio_txt = data.get("preferences", []), data.get("bio", "")
    q = []
    q.append({"q_id": "q1",
              "text": f"What do you enjoy most about {prefs[0]}?"
                       if prefs else
                       "What is a hobby or interest that excites you the most?"})
    q.append({"q_id": "q2",
              "text": f"How does your interest in {prefs[1]} influence your ideal match?"
                       if len(prefs) > 1 else
                       "How would you describe your ideal weekend with a partner?"})
    q.append({"q_id": "q3",
              "text": f'Your bio mentions "{bio_txt[:30]}..." – tell me more?'
                       if bio_txt else
                       "Which personal quality are you most proud of?"})
    q.append({"q_id": "q4", "text": "What are you looking for in an ideal partner?"})
    q.append({"q_id": "q5", "text": "If you could plan a perfect date, what would you do?"})
    return q

# ─── 2. Manual tool registry  ──────────────────────────────────────────────
TOOL_REGISTRY = {
    "generate_match_questions": generate_match_questions,
}

# ─── 3. Outer FastAPI app with POST /sse  ──────────────────────────────────
app = FastAPI(title="MCP Server with POST /sse")

@app.post("/sse")
async def sse_post(request: Request):
    """
    Accept JSON {tool, arguments} via POST and stream back SSE.
    """
    body = await request.json()
    tool_name = body.get("tool")
    args      = body.get("arguments", {}) or {}

    tool_fn = TOOL_REGISTRY.get(tool_name)
    if tool_fn is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown tool '{tool_name}'",
        )
    # ─── call the async tool ──────────────────────────────────────────
    try:
        result = await tool_fn(**args)
    except Exception as exc:
        error_msg = str(exc)          # ← capture while still in scope

        async def err_stream():
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(err_stream(), media_type="text/event-stream")


    # Happy path – two-chunk SSE
    async def event_stream():
        yield f"data: {json.dumps(result)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

# Mount MCP so GET /sse (and FastMCP’s other endpoints) still work
app.mount("/", mcp)

# ─── 4. Run  ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=8010, reload=True)