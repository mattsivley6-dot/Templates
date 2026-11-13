"""Talk to Fusion's built-in MCP server over raw Streamable HTTP (no MCP client needed). Read-only by default.

  python mcp_probe.py                      initialize + tools/list (names and first line of each description)
  python mcp_probe.py --script "<python>"  also run a READ-ONLY Execute script (must define def run(_context: str))
  python mcp_probe.py --call <tool> <json-args>   call any tool with JSON arguments (careful: can change the model)
URL comes from the MCP_URL env var or http://127.0.0.1:27182/mcp. Verified against build 2705.1.30 on 2026-10-18.
"""
import json
import os
import sys
import urllib.request

URL = os.environ.get("MCP_URL", "http://127.0.0.1:27182/mcp")
SID = None
NID = 0


def post(method, params=None, notify=False):
    global SID, NID
    body = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        body["params"] = params
    if not notify:
        NID += 1
        body["id"] = NID
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    if SID:
        req.add_header("Mcp-Session-Id", SID)
    with urllib.request.urlopen(req, timeout=120) as resp:
        sid = resp.headers.get("Mcp-Session-Id") or resp.headers.get("mcp-session-id")
        if sid:
            SID = sid
        raw = resp.read().decode("utf-8", "replace")
        ctype = resp.headers.get("Content-Type", "")
    if notify or not raw.strip():
        return None
    if "text/event-stream" in ctype:
        data = [l[5:].strip() for l in raw.splitlines() if l.startswith("data:")]
        raw = data[-1] if data else "{}"
    return json.loads(raw)


def main(a):
    init = post("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                               "clientInfo": {"name": "mcp_probe", "version": "1"}})
    res = init.get("result", init)
    print("server:", res.get("serverInfo"), "| protocol:", res.get("protocolVersion"), "| session:", SID)
    post("notifications/initialized", notify=True)
    tl = post("tools/list", {})
    tools = tl.get("result", {}).get("tools", [])
    print("tools:", len(tools))
    for t in tools:
        print("  -", t.get("name"), "|", (t.get("description") or "").strip().splitlines()[0][:110])
    if "--script" in a:
        src = a[a.index("--script") + 1]
        r = post("tools/call", {"name": next((t["name"] for t in tools if t["name"].lower().endswith("execute")), "execute"),
                                "arguments": {"featureType": "script", "object": {"readOnly": True, "script": src}}})
        print("script result:", json.dumps(r.get("result", r), indent=1)[:3000])
    if "--call" in a:
        i = a.index("--call")
        r = post("tools/call", {"name": a[i + 1], "arguments": json.loads(a[i + 2])})
        print("call result:", json.dumps(r.get("result", r), indent=1)[:6000])


if __name__ == "__main__":
    main(sys.argv[1:])
