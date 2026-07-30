#!/usr/bin/env python3
"""Live editor for the hand-written site pages.

    python3 scripts/edit_server.py        # then open http://127.0.0.1:8765

Edit the markdown in the browser, hit Cmd-S, and the page rebuilds and reloads
in the preview beside it. The file on disk is the source of truth throughout —
this writes to site/*.md exactly as a text editor would, so nothing about the
build or the repo changes.

Why edit the markdown rather than the rendered page: converting edited HTML back
to markdown loses the front matter, the ::: component blocks, and the table
syntax. Editing the source and re-rendering keeps every feature of the page
available, and what you save is what git sees.

Local only. It binds to 127.0.0.1, writes to files under site/, and runs the
build — do not expose it. There is no authentication because there is no
network surface.
"""
import http.server
import json
import pathlib
import re
import subprocess
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PUB = ROOT / "publish"
# 8765 is Claude Science on this machine, so start above it and step past
# anything else already listening.
PORT = 8791

# Hand-written pages only. The rest generate from data/ and editing them here
# would be overwritten by the next build.
PAGES = {
    "overview.md": "index.html",
    "sequencing-protocol.md": "protocol.html",
}

BANNED = re.compile(
    r"honest|it's not |not a [A-Z]|not an arbitrary|the point is"
    r"|worth (noting|being explicit)|in other words|crucially|importantly,"
    r"|notably,|the beauty|state-of-the-art|by design|division of labor"
    r"|neither half|is the point|makes it (ideal|clear)|the case rests",
    re.I)


QUESTION_HEADING = re.compile(r"^(sub:.*\?|#{2,4} .*\?)\s*$")

# build_site.py rewrites ~x~ to <sub>x</sub>. A *pair* on one line swallows the
# text between them; a lone tilde in a path renders fine and is not flagged.
PAIRED_TILDE = re.compile(r"~[^~]+~")


def lint(text):
    """The doc-voice tells, surfaced while writing instead of at build time.

    Everything here is advisory and none of it blocks a save. A grep cannot
    tell a rhetorical question from a real either/or, so it reports and the
    writer decides. The one exception is a paired tilde, which is not a matter
    of taste — it silently eats the text between the tildes — so it is marked
    as breakage to match the build gate in doc_voice_check.sh.
    """
    out = []
    for n, line in enumerate(text.split("\n"), 1):
        if PAIRED_TILDE.search(line):
            out.append({"line": n, "kind": "breakage",
                        "text": "paired tildes — the text between them "
                                "renders as <sub> and disappears"})
        for m in BANNED.finditer(line):
            out.append({"line": n, "kind": "advisory",
                        "text": line.strip()[:120]})
        if QUESTION_HEADING.match(line):
            out.append({"line": n, "kind": "advisory",
                        "text": line.strip()[:120]})
    return out


def build():
    r = subprocess.run(["./publish.sh", "build"], cwd=ROOT,
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr)[-4000:]


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>openlab — live edit</title>
<style>
 *{box-sizing:border-box;margin:0;padding:0}
 body{font:14px ui-monospace,Menlo,monospace;background:#071a1e;color:#dbe8e4;height:100vh;
   display:flex;flex-direction:column;overflow:hidden}
 header{display:flex;align-items:center;gap:1rem;padding:.6rem 1rem;background:#0f343a;
   border-bottom:1px solid #1c474d;flex:none}
 header b{color:#eef6f3;font-weight:600}
 select,button{font:inherit;background:#123f45;color:#dbe8e4;border:1px solid #1c474d;
   border-radius:4px;padding:.35rem .7rem;cursor:pointer}
 button:hover,select:hover{border-color:#3a9c86}
 #status{margin-left:auto;font-size:.8rem;color:#8fa8a4}
 #status.ok{color:#5bd39a} #status.err{color:#ef8f7a} #status.busy{color:#e6c463}
 main{flex:1;display:flex;min-height:0}
 .pane{flex:1;display:flex;flex-direction:column;min-width:0}
 .pane+.pane{border-left:1px solid #1c474d}
 textarea{flex:1;width:100%;background:#0b262b;color:#dbe8e4;border:0;padding:1rem;
   font:13px/1.6 ui-monospace,Menlo,monospace;resize:none;outline:none;tab-size:2}
 iframe{flex:1;width:100%;border:0;background:#fff}
 #lint{flex:none;max-height:26vh;overflow:auto;background:#0b262b;border-top:1px solid #1c474d;
   padding:.5rem 1rem;font-size:.78rem;line-height:1.5}
 #lint:empty{display:none}
 #lint .h{color:#e6c463} #lint .l{color:#5f7a77;margin-right:.5rem}
 #lint .b{color:#ff9a8b}
 #log{white-space:pre-wrap;color:#ef8f7a;font-size:.75rem;padding:.5rem 1rem;
   background:#0b262b;border-top:1px solid #1c474d;max-height:22vh;overflow:auto}
 #log:empty{display:none}
</style></head><body>
<header>
  <b>openlab</b>
  <select id="file"></select>
  <button id="save">Save &amp; rebuild &nbsp;<span style="opacity:.6">&#8984;S</span></button>
  <span id="status">ready</span>
</header>
<main>
  <div class="pane"><textarea id="src" spellcheck="false"></textarea><div id="lint"></div></div>
  <div class="pane"><iframe id="prev"></iframe></div>
</main>
<div id="log"></div>
<script>
const $=s=>document.querySelector(s);
let current=null;

function setStatus(t,c){ const s=$('#status'); s.textContent=t; s.className=c||''; }

// Built with DOM nodes and textContent throughout: every string here is file
// content, so it must never be parsed as markup.
function showLint(items){
  const box=$('#lint');
  box.replaceChildren();
  if(!items.length) return;
  const broke=items.filter(i=>i.kind==='breakage').length;
  const h=document.createElement('div');
  h.className='h';
  // Breakage stops the build; the rest is a suggestion. Say which is which,
  // or every save looks equally like a failure.
  h.textContent = broke
    ? 'doc-voice: '+broke+' breaking the page, '+(items.length-broke)+' to consider'
    : 'doc-voice: '+items.length+' to consider — none of these block a save';
  box.appendChild(h);
  for(const i of items){
    const row=document.createElement('div');
    if(i.kind==='breakage') row.className='b';
    const num=document.createElement('span');
    num.className='l'; num.textContent=i.line;
    row.appendChild(num);
    row.appendChild(document.createTextNode(i.text));
    box.appendChild(row);
  }
}

async function load(name){
  const r = await fetch('/api/file?name='+encodeURIComponent(name));
  const d = await r.json();
  current = name;
  $('#src').value = d.text;
  showLint(d.lint);
  $('#prev').src = '/publish/'+d.html+'?t='+Date.now();
}

async function save(){
  setStatus('building\\u2026','busy');
  const r = await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({name: current, text: $('#src').value})});
  const d = await r.json();
  showLint(d.lint);
  $('#log').textContent = d.ok ? '' : d.output;
  if(d.ok){ setStatus('saved '+new Date().toLocaleTimeString(),'ok');
            $('#prev').src = '/publish/'+d.html+'?t='+Date.now(); }
  else setStatus('build failed','err');
}

fetch('/api/pages').then(r=>r.json()).then(names=>{
  const sel=$('#file');
  for(const n of names){
    const o=document.createElement('option');
    o.value=n; o.textContent=n;
    sel.appendChild(o);
  }
  load(sel.value);
});

$('#save').onclick = save;
$('#file').onchange = e => load(e.target.value);
addEventListener('keydown', e => {
  if((e.metaKey||e.ctrlKey) && e.key==='s'){ e.preventDefault(); save(); }
});
</script></body></html>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        body = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            return self._send(200, PAGE, "text/html")

        if u.path == "/api/pages":
            return self._send(200, json.dumps(list(PAGES)))

        if u.path == "/api/file":
            name = urllib.parse.parse_qs(u.query).get("name", [""])[0]
            if name not in PAGES:
                return self._send(404, json.dumps({"error": "unknown page"}))
            text = (SITE / name).read_text(encoding="utf-8")
            return self._send(200, json.dumps(
                {"text": text, "html": PAGES[name], "lint": lint(text)}))

        if u.path.startswith("/publish/"):
            # Serve only inside publish/, resolved, so a crafted path cannot
            # walk out of it even though this is a local-only tool.
            target = (PUB / u.path[len("/publish/"):].split("?")[0]).resolve()
            if not str(target).startswith(str(PUB.resolve())) or not target.is_file():
                return self._send(404, "not found", "text/plain")
            ctype = ("text/html" if target.suffix == ".html"
                     else "application/octet-stream")
            return self._send(200, target.read_bytes(), ctype)

        return self._send(404, "not found", "text/plain")

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/api/save":
            return self._send(404, json.dumps({"error": "not found"}))
        n = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(n) or b"{}")
        name = data.get("name")
        if name not in PAGES:
            return self._send(400, json.dumps({"error": "unknown page"}))
        (SITE / name).write_text(data.get("text", ""), encoding="utf-8")
        ok, output = build()
        self._send(200, json.dumps({"ok": ok, "output": output,
                                    "html": PAGES[name],
                                    "lint": lint(data.get("text", ""))}))

    def log_message(self, *a):
        pass


def serve():
    for port in range(PORT, PORT + 10):
        try:
            srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
        except OSError:
            continue          # in use by something else; try the next one
        print(f"editing {', '.join(PAGES)}")
        print(f"open http://127.0.0.1:{port}   (Ctrl-C to stop)")
        srv.serve_forever()
        return
    raise SystemExit(f"no free port in {PORT}-{PORT + 9}")


if __name__ == "__main__":
    serve()
