#!/usr/bin/env python3
"""
build_site.py — render the canonical Markdown source-of-truth (seagrass_site.md)
into the styled, self-contained HTML site (seagrass_site.html).

Design goals
------------
* The Markdown file is the single source of truth. Edit it (append / correct);
  never regenerate content from scratch. This script only *renders*.
* Rich components (hero, cards, stat grids, pipeline, people, ranking, sites,
  figures) are expressed as fenced blocks:  ::: <type>  ... YAML ...  :::
  Everything else is standard Markdown (headings, prose, tables, lists,
  blockquotes, bold/italic/links).
* Figures are embedded as base64 data-URIs so the output HTML is a single,
  fully portable file (safe to publish or drop in Drive/GitHub).

Usage
-----
    python build_site.py [input.md] [output.html] [--figdir DIR]

Figure resolution: a ::: figure block gives `file:` (path, tried relative to
--figdir then CWD) and/or `artifact:` (a version_id; resolved via
figures/<version_id>.png if present). Provide the PNGs in --figdir.
"""
import sys, os, re, base64, html
import yaml

# ----------------------------------------------------------------------------
# Theme CSS — copied verbatim from the published site so output matches exactly.
# ----------------------------------------------------------------------------
CSS = r""":root{
  --abyss:#071a1e;--deep:#0b262b;--panel:#0f343a;--raised:#123f45;--border:#1c474d;
  --grass:#5bc2a0;--light:#8fe3d0;--kelp:#3a9c86;
  --sand:#e4cb92;--sand-dim:#c8a866;--ember:#e8916a;
  --foam:#eef6f3;--text:#dbe8e4;--muted:#8fa8a4;--faint:#5f7a77;
  --green:#5bd39a;--yellow:#e6c463;--red:#ef8f7a;--teal:#5bc2a0;--accent:#8fe3d0;
  --serif:'Fraunces',Georgia,'Times New Roman',serif;
  --sans:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,'SF Mono',Menlo,monospace;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:var(--sans);background:var(--abyss);color:var(--text);line-height:1.7;font-size:16px;
  background-image:linear-gradient(180deg,#0a2126 0%,var(--abyss) 34%);background-attachment:fixed}
a{color:var(--light);text-decoration:none;transition:color .15s}
a:hover{color:var(--sand)}

/* ---------- hero: the water column ---------- */
.hero{position:relative;padding:7rem 2rem 4.5rem;text-align:center;overflow:hidden;
  background:linear-gradient(180deg,#12454b 0%,#0d343a 40%,#0a262c 72%,var(--abyss) 100%);
  border-bottom:1px solid var(--border)}
.hero::before{content:'';position:absolute;inset:0;pointer-events:none;
  background:
    radial-gradient(120% 60% at 50% -8%,rgba(143,227,208,0.22),transparent 60%),
    radial-gradient(80% 40% at 18% 8%,rgba(143,227,208,0.10),transparent 60%);
  mix-blend-mode:screen}
/* drifting light shafts */
.hero::after{content:'';position:absolute;inset:-20% -10% 0;pointer-events:none;opacity:.5;
  background:repeating-linear-gradient(104deg,transparent 0 60px,rgba(180,240,225,0.05) 60px 61px,transparent 61px 150px);
  transform:translateX(0);animation:drift 26s linear infinite}
@keyframes drift{to{transform:translateX(150px)}}
@media(prefers-reduced-motion:reduce){.hero::after{animation:none}}
.hero>.container{position:relative;z-index:2;max-width:1000px}
.hero-badge{display:inline-block;font-family:var(--mono);font-size:.68rem;padding:.35rem .9rem;border-radius:2px;
  background:rgba(228,203,146,0.08);color:var(--sand);border:1px solid rgba(228,203,146,0.28);
  text-transform:uppercase;letter-spacing:.22em;font-weight:500;margin-bottom:1.6rem}
.hero h1{font-family:var(--serif);font-optical-sizing:auto;font-size:clamp(2rem,6vw,4.2rem);font-weight:500;
  letter-spacing:-.015em;line-height:1.04;margin:0 auto .9rem;max-width:15ch;color:var(--foam);overflow-wrap:break-word}
.hero h1 em{font-style:italic;color:var(--light);font-weight:400}
.hero .tagline{font-size:clamp(1rem,2.2vw,1.22rem);color:var(--muted);max-width:640px;margin:0 auto 2.4rem;line-height:1.55}
.hero-stats{display:flex;flex-wrap:wrap;justify-content:center;gap:0;margin-top:2.4rem;
  border-top:1px solid var(--border);padding-top:1.8rem}
.hero-stat{text-align:center;flex:1;min-width:130px;padding:0 1.2rem;position:relative}
.hero-stat+.hero-stat::before{content:'';position:absolute;left:0;top:.2rem;bottom:.2rem;width:1px;background:var(--border)}
.hero-stat .val{font-family:var(--mono);font-size:clamp(1.4rem,3vw,1.9rem);font-weight:600;color:var(--sand);letter-spacing:-.01em}
.hero-stat .lbl{font-size:.68rem;color:var(--faint);text-transform:uppercase;letter-spacing:.08em;margin-top:.5rem;line-height:1.4}
/* section jump list — for pages long enough that scrolling is the cost */
.toc{border-bottom:1px solid var(--border);background:rgba(15,52,58,.5);
  position:sticky;top:0;z-index:20;backdrop-filter:blur(8px)}
.toc .container{display:flex;flex-wrap:wrap;align-items:center;gap:.2rem .35rem;padding-top:.7rem;padding-bottom:.7rem}
.toc-label{font-family:var(--mono);font-size:.62rem;text-transform:uppercase;letter-spacing:.12em;
  color:var(--faint);margin-right:.6rem}
.toc a{font-size:.8rem;color:var(--muted);padding:.25rem .6rem;border-radius:3px;
  border:1px solid transparent;transition:color .15s,border-color .15s,background .15s}
.toc a:hover{color:var(--foam);border-color:var(--border);background:rgba(143,227,208,.06)}
section{scroll-margin-top:4.5rem}
@media(max-width:700px){.toc{position:static}.toc-label{width:100%;margin-bottom:.2rem}}

/* draft banner — stays up until an end-to-end run is completed */
.draftbar{background:linear-gradient(90deg,rgba(232,145,106,.16),rgba(232,145,106,.05));
  border-bottom:1px solid rgba(232,145,106,.4);padding:.6rem 0;font-size:.82rem;color:var(--sand)}
.draftbar strong{color:var(--ember);font-family:var(--mono);font-size:.72rem;letter-spacing:.1em;
  text-transform:uppercase;margin-right:.5rem}

/* validation markers — the protocol page's main claim, so they read as status
   chips rather than as prose. Colour carries meaning, the label repeats it. */
.marker{display:inline-block;font-family:var(--mono);font-size:.62rem;font-weight:600;
  letter-spacing:.08em;padding:.16em .5em;border-radius:3px;border:1px solid;
  vertical-align:.08em;white-space:nowrap}
.marker-mfr{color:var(--green);border-color:rgba(91,211,154,.5);background:rgba(91,211,154,.1)}
.marker-adapted{color:var(--yellow);border-color:rgba(230,196,99,.5);background:rgba(230,196,99,.1)}
.marker-untested{color:var(--red);border-color:rgba(239,143,122,.6);background:rgba(239,143,122,.12)}
strong .marker{font-weight:600}

/* ---------- structure ---------- */
.container{max-width:1080px;margin:0 auto;padding:0 2rem}
section{padding:4rem 0;border-bottom:1px solid rgba(28,71,77,0.55)}
section:last-of-type{border-bottom:none}
section>.container{position:relative;padding-left:2.8rem}
/* the dive-profile spine + station node */
section>.container::before{content:'';position:absolute;left:.85rem;top:.1rem;bottom:0;width:1px;
  background:linear-gradient(var(--border) 0%,rgba(28,71,77,0.15) 100%)}
h2{font-family:var(--serif);font-optical-sizing:auto;font-size:clamp(1.7rem,3.4vw,2.3rem);font-weight:500;
  letter-spacing:-.01em;line-height:1.1;margin-bottom:.35rem;color:var(--foam);position:relative}
h2::before{content:'';position:absolute;left:-1.95rem;top:.55em;width:11px;height:11px;border-radius:50%;
  background:var(--abyss);border:2px solid var(--sand);box-shadow:0 0 0 4px var(--abyss)}
h2 .hl{color:var(--light);font-style:italic}
.section-sub{color:var(--muted);font-size:1rem;margin-bottom:2rem;max-width:720px;line-height:1.6}
h3{font-family:var(--serif);font-size:1.3rem;font-weight:500;margin:2rem 0 .75rem;color:var(--light)}
h4{font-family:var(--sans)}
p{margin:.7rem 0}
section .container p,.container>section p{font-size:.98rem;color:var(--text)}
ul,ol{margin:.6rem 0 .6rem 1.3rem}
li{font-size:.95rem;margin-bottom:.35rem}
strong{color:var(--foam);font-weight:600}
em{color:var(--light)}
code{font-family:var(--mono);font-size:.85em;background:rgba(143,227,208,0.08);padding:.1em .4em;border-radius:3px;color:var(--light)}

/* ---------- cards ---------- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:1rem;margin:1.5rem 0}
.card{background:linear-gradient(160deg,var(--panel),var(--deep));border:1px solid var(--border);border-radius:12px;
  padding:1.4rem;transition:transform .18s,border-color .18s,box-shadow .18s}
.card:hover{transform:translateY(-3px);border-color:var(--kelp);box-shadow:0 10px 30px -12px rgba(0,0,0,0.6)}
.card h4{font-size:1.05rem;margin:0 0 .5rem;color:var(--foam);font-weight:600}
.card p,.card li{font-size:.9rem;color:var(--muted);line-height:1.6}
.card ul{padding-left:1.2rem;margin-top:.5rem}
.card ul li{margin-bottom:.3rem}
.card .species-name{font-style:italic;color:var(--light)}
.card-accent{border-left:3px solid var(--grass)}

/* why-boxes with SVG glyphs */
.why-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:1rem;margin:1.8rem 0}
.why-box{background:linear-gradient(160deg,var(--panel),var(--deep));border:1px solid var(--border);border-radius:12px;
  padding:1.5rem 1.35rem;transition:transform .18s,border-color .18s;text-align:left}
.why-box:hover{transform:translateY(-3px);border-color:var(--kelp)}
.why-box .iconwrap{width:42px;height:42px;border-radius:10px;display:flex;align-items:center;justify-content:center;
  background:rgba(228,203,146,0.09);border:1px solid rgba(228,203,146,0.22);margin-bottom:1rem}
.why-box .iconwrap svg{width:22px;height:22px;stroke:var(--sand);fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.why-box .icon{font-size:1.6rem;margin-bottom:.6rem}
.why-box .title{font-weight:600;font-size:1rem;margin-bottom:.45rem;color:var(--foam)}
.why-box .desc{font-size:.86rem;color:var(--muted);line-height:1.6}

/* ---------- stats: instrument readings ---------- */
.stat-grid{display:flex;flex-wrap:wrap;gap:1rem;margin:1.8rem 0}
.stat-box{background:var(--deep);border:1px solid var(--border);border-radius:10px;padding:1.1rem 1.25rem;
  flex:1;min-width:150px;text-align:left;position:relative;overflow:hidden}
.stat-box::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--sand)}
.stat-box .n{font-family:var(--mono);font-size:1.7rem;font-weight:600;line-height:1.1;color:var(--sand);letter-spacing:-.01em}
.stat-box .l{font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-top:.5rem;line-height:1.45}

/* ---------- tables ---------- */
table{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.88rem}
th,td{text-align:left;padding:.6rem .8rem;border-bottom:1px solid var(--border)}
th{font-family:var(--mono);color:var(--sand-dim);font-weight:500;font-size:.66rem;text-transform:uppercase;
  letter-spacing:.08em;background:var(--deep)}
td{color:var(--text)}
.table-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:12px;margin:1.5rem 0}
.table-wrap table{margin:0}
.table-wrap th:first-child,.table-wrap td:first-child{position:sticky;left:0;background:var(--deep);z-index:1}
tr:hover td{background:rgba(143,227,208,0.04)}

/* ---------- pipeline ---------- */
.pipeline{display:flex;flex-wrap:wrap;align-items:stretch;gap:0;margin:2rem 0;overflow-x:auto}
.pipeline-step{background:linear-gradient(160deg,var(--panel),var(--deep));border:1px solid var(--border);border-radius:12px;
  padding:1.15rem 1.3rem;text-align:left;flex:1;min-width:150px}
.pipeline-step .step-num{font-family:var(--mono);font-size:.62rem;color:var(--sand);text-transform:uppercase;
  letter-spacing:.14em;font-weight:600;margin-bottom:.4rem}
.pipeline-step .step-title{font-size:1rem;font-weight:600;color:var(--foam)}
.pipeline-step .step-detail{font-size:.8rem;color:var(--muted);margin-top:.35rem;line-height:1.5}
.pipeline-arrow{color:var(--sand-dim);font-size:1.3rem;padding:0 .35rem;flex-shrink:0;align-self:center}

/* ---------- tags ---------- */
.tag{display:inline-block;font-family:var(--mono);font-size:.68rem;padding:.22rem .6rem;border-radius:4px;
  font-weight:500;margin:.15rem .12rem;letter-spacing:.02em}
.tag-teal{background:rgba(91,194,160,0.12);color:var(--grass);border:1px solid rgba(91,194,160,0.3)}
.tag-blue{background:rgba(143,227,208,0.1);color:var(--light);border:1px solid rgba(143,227,208,0.25)}
.tag-green{background:rgba(91,211,154,0.12);color:var(--green);border:1px solid rgba(91,211,154,0.28)}
.tag-yellow{background:rgba(230,196,99,0.12);color:var(--yellow);border:1px solid rgba(230,196,99,0.28)}
.tag-muted{background:var(--deep);color:var(--muted);border:1px solid var(--border)}

/* ---------- people / sites ---------- */
.people-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:1rem;margin:1.5rem 0}
.person{background:var(--deep);border:1px solid var(--border);border-radius:12px;padding:1.2rem}
.person .name{font-weight:600;font-size:1rem;color:var(--foam)}
.person .role{color:var(--sand);font-size:.82rem;margin-top:.15rem;font-family:var(--mono)}
.person .affil{color:var(--muted);font-size:.82rem;margin-top:.3rem}
.site-card{background:linear-gradient(160deg,var(--panel),var(--deep));border:1px solid var(--border);border-radius:12px;padding:1.4rem;margin-bottom:1rem}
.site-card h4{margin:0 0 .5rem;display:flex;align-items:center;gap:.55rem;font-size:1.05rem;color:var(--foam)}
.site-dot{width:10px;height:10px;border-radius:50%;display:inline-block;flex-shrink:0}
.site-dot.primary{background:var(--grass)}
.site-dot.secondary{background:var(--light)}
.site-dot.tertiary{background:var(--sand)}
.site-species{margin-top:.6rem;display:flex;flex-wrap:wrap;gap:.4rem}

.two-col{display:grid;grid-template-columns:1fr 1fr;gap:2rem;align-items:start}
.rank-row{display:flex;align-items:center;gap:1rem;padding:.85rem 1.1rem;background:var(--deep);
  border:1px solid var(--border);border-radius:10px;margin-bottom:.5rem}
.rank-row .rn{font-family:var(--mono);font-weight:600;min-width:2rem;font-size:1.15rem}

/* ---------- blockquote ---------- */
blockquote{border-left:3px solid var(--sand);padding:1rem 1.3rem;margin:1.8rem 0;
  background:var(--deep);border-radius:0 10px 10px 0;font-size:.98rem;color:var(--text);font-style:italic;
  font-family:var(--serif);line-height:1.55}
blockquote cite{display:block;margin-top:.6rem;font-size:.8rem;color:var(--sand);font-style:normal;font-family:var(--sans)}

/* ---------- figures ---------- */
figure{margin:2rem 0;background:var(--deep);border:1px solid var(--border);border-radius:12px;padding:1.1rem}
figure img{width:100%;border-radius:8px;display:block;background:#fff}
figcaption{font-size:.84rem;color:var(--muted);margin-top:.7rem;line-height:1.55}
figcaption .fnum{color:var(--sand);font-weight:600;font-family:var(--mono)}

.update-banner{background:rgba(143,227,208,0.06);border:1px solid rgba(143,227,208,0.2);border-radius:10px;
  padding:.8rem 1.1rem;font-size:.86rem;color:var(--muted);margin:1.2rem 0}
.cta-wrap{margin:1.8rem 0;text-align:center}
.cta-wrap a{display:inline-block;background:var(--grass);color:#052620;font-family:var(--sans);font-weight:600;
  font-size:.98rem;padding:.85rem 1.8rem;border-radius:8px;text-decoration:none;transition:transform .15s,box-shadow .15s;
  box-shadow:0 6px 20px -8px rgba(91,194,160,0.5)}
.cta-wrap a:hover{transform:translateY(-2px);color:#052620;box-shadow:0 10px 26px -8px rgba(91,194,160,0.65)}

.keyfinding{background:linear-gradient(150deg,rgba(91,194,160,0.14),rgba(143,227,208,0.05));
  border:1px solid rgba(91,194,160,0.32);border-left:4px solid var(--grass);border-radius:12px;padding:1.4rem 1.6rem;margin:1.8rem 0}
.keyfinding .kf-headline{font-family:var(--serif);font-size:1.3rem;font-weight:500;color:var(--light);line-height:1.3;margin-bottom:.6rem}
.keyfinding .kf-body{font-size:.95rem;color:var(--text);line-height:1.65}

footer{padding:3rem 2rem;text-align:center;color:var(--muted);font-size:.85rem;border-top:1px solid var(--border);background:var(--deep)}
footer strong{font-family:var(--serif);font-weight:500;font-size:1.1rem}
footer a{color:var(--light)}
.ref-list{font-size:.82rem;color:var(--muted);line-height:1.8;columns:2;column-gap:2.5rem}
.ref-list li{break-inside:avoid}

/* ---------- nav ---------- */
.sitenav{position:sticky;top:0;z-index:50;background:rgba(7,26,30,0.82);backdrop-filter:blur(12px) saturate(1.2);
  border-bottom:1px solid var(--border)}
.sitenav .inner{max-width:1080px;margin:0 auto;padding:.8rem 2rem;display:flex;align-items:center;gap:1.6rem;flex-wrap:wrap}
.sitenav .brand{font-family:var(--serif);font-weight:500;color:var(--foam);font-size:1.1rem;margin-right:auto;letter-spacing:-.01em}
.sitenav .brand .dot{color:var(--sand)}
.sitenav a{color:var(--muted);font-size:.78rem;font-weight:500;text-transform:uppercase;letter-spacing:.08em;
  font-family:var(--mono);padding:.2rem 0;border-bottom:1.5px solid transparent;transition:color .15s}
.sitenav a:hover{color:var(--foam)}
.sitenav a.active{color:var(--sand);border-bottom-color:var(--sand)}

/* ---------- downloads ---------- */
.dlgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1.2rem;margin:1.8rem 0}
.dlcard{background:linear-gradient(160deg,var(--panel),var(--deep));border:1px solid var(--border);border-radius:12px;
  padding:1.4rem;display:flex;flex-direction:column;gap:.5rem;transition:transform .18s,border-color .18s}
.dlcard:hover{transform:translateY(-3px);border-color:var(--kelp)}
.dlcard .dt{font-weight:600;color:var(--foam);font-size:1.05rem}
.dlcard .dd{color:var(--muted);font-size:.86rem;flex:1;line-height:1.55}
.dlcard .dlbtn{margin-top:.6rem;display:inline-block;background:var(--sand);color:#241c08;font-weight:600;
  font-size:.85rem;font-family:var(--sans);padding:.55rem 1rem;border-radius:8px;text-align:center;transition:opacity .15s}
.dlcard .dlbtn:hover{opacity:.88;color:#241c08}

@media(max-width:768px){
  .hero{padding:4.5rem 1.5rem 3rem}
  .container{padding:0 1.5rem}
  section>.container{padding-left:1.5rem}
  section>.container::before{display:none}
  h2::before{display:none}
  .two-col{grid-template-columns:1fr}
  .pipeline{flex-direction:column;align-items:stretch}
  .pipeline-arrow{transform:rotate(90deg);text-align:center;align-self:center}
  .hero h1{max-width:none}
  .hero-stats{display:grid;grid-template-columns:1fr 1fr;gap:1.4rem 1rem;padding-top:1.4rem}
  .hero-stat{min-width:0;padding:0}
  .hero-stat+.hero-stat::before{display:none}
  .ref-list{columns:1}
}
"""

# ----------------------------------------------------------------------------
# Inline markdown -> HTML  (links, bold, italic, code, subscript, br)
# ----------------------------------------------------------------------------

# Protocol validation markers. The brief makes these the protocol page's main
# claim, so they render as badges rather than plain text — the status has to
# survive skim-reading.
MARKER_RE = re.compile(r"\[(MFR|ADAPTED|UNTESTED)\]")


def inline(t):
    if t is None:
        return ""
    t = str(t)
    # protect existing simple HTML entities but escape angle brackets/amp first
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # validation markers -> badges. Substituted before the link rule so the
    # bracket form is consumed here; [MFR] is never followed by "(" so the two
    # rules cannot collide, but order makes that independent of the link regex.
    t = MARKER_RE.sub(
        lambda m: f'<span class="marker marker-{m.group(1).lower()}">{m.group(1)}</span>',
        t)
    # links [text](url)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    # bold **x**
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    # italic *x* (avoid ** already handled)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    # inline code `x`
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    # subscript ~x~
    t = re.sub(r"~([^~]+)~", r"<sub>\1</sub>", t)
    # explicit line break: two spaces + newline, or \\
    t = t.replace("\\n", "<br>")
    return t

def h2_hl(title):
    """Render 'Word <hl>Highlight</hl>' — last word teal by convention if wrapped in {}."""
    m = re.search(r"\{([^}]+)\}", title)
    if m:
        base = title[:m.start()].strip()
        hl = m.group(1)
        return f'{inline(base)} <span class="hl">{inline(hl)}</span>'
    return inline(title)

# ----------------------------------------------------------------------------
# Component renderers (payload = parsed YAML)
# ----------------------------------------------------------------------------
def tag_html(tags):
    if not tags:
        return ""
    out = []
    for tg in tags:
        if isinstance(tg, str):
            out.append(f'<span class="tag tag-muted">{inline(tg)}</span>')
        else:
            cls = tg.get("cls", "muted")
            out.append(f'<span class="tag tag-{cls}">{inline(tg.get("text",""))}</span>')
    return " ".join(out)

# ----------------------------------------------------------------------------
# Field-guide line glyphs — swap the source Markdown's emoji for consistent,
# single-stroke SVG icons (currentColor via CSS). Falls back to the raw
# character for anything unmapped, so the Markdown stays the source of truth.
# ----------------------------------------------------------------------------
_SVG = {
    # wave / ocean
    "\U0001F30A": '<path d="M2 15c2.5 0 2.5-2 5-2s2.5 2 5 2 2.5-2 5-2 2.5 2 5 2"/><path d="M2 19c2.5 0 2.5-2 5-2s2.5 2 5 2 2.5-2 5-2 2.5 2 5 2"/><path d="M4 11c1.5-3 4.5-4 8-3"/>',
    # shark / large fish -> biodiversity
    "\U0001F988": '<path d="M3 13c4-6 12-7 18-4-2 1-3 3-3 5 0 1 .5 2 1.5 2.5C15 18 8 18 3 13Z"/><path d="M14 8c1-2 3-3 5-3-1 2-1 3 0 4"/><circle cx="8" cy="12.5" r=".6" fill="currentColor" stroke="none"/>',
    # thermometer -> climate canary
    "\U0001F321": '<path d="M12 4a2 2 0 0 0-2 2v7.5a3.5 3.5 0 1 0 4 0V6a2 2 0 0 0-2-2Z"/><path d="M12 9v5"/>',
    "\U0001F321️": '<path d="M12 4a2 2 0 0 0-2 2v7.5a3.5 3.5 0 1 0 4 0V6a2 2 0 0 0-2-2Z"/><path d="M12 9v5"/>',
    # warning -> crisis
    "⚠": '<path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v4"/><circle cx="12" cy="17" r=".6" fill="currentColor" stroke="none"/>',
    "⚠️": '<path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v4"/><circle cx="12" cy="17" r=".6" fill="currentColor" stroke="none"/>',
    # sprout -> blue carbon / growth
    "\U0001F331": '<path d="M12 20v-7"/><path d="M12 13C12 9 9 7 4 7c0 4 3 6 8 6Z"/><path d="M12 15c0-3 2.5-5 7-5 0 3-2.5 5-7 5Z"/>',
    # fish -> aquaculture
    "\U0001F41F": '<path d="M3 12c3-4 8-5 13-3 2 .8 3.5 2 4 3-.5 1-2 2.2-4 3-5 2-10 1-13-3Z"/><path d="M20 9c1-1 1.5-1 2.5-1.2C22 9 22 10 22 11.8 21 11 20.5 11 20 10"/><circle cx="8" cy="11" r=".6" fill="currentColor" stroke="none"/>',
    # construction -> beneficial dredge reuse (crane hook)
    "\U0001F3D7": '<path d="M4 21V4l12 3"/><path d="M4 7h9"/><path d="M13 7v4"/><path d="M11 11h4"/><path d="M13 11v3a1.5 1.5 0 0 0 3 0"/><path d="M4 21h9"/>',
    "\U0001F3D7️": '<path d="M4 21V4l12 3"/><path d="M4 7h9"/><path d="M13 7v4"/><path d="M11 11h4"/><path d="M13 11v3a1.5 1.5 0 0 0 3 0"/><path d="M4 21h9"/>',
    # coral -> reefs
    "\U0001FAB8": '<path d="M12 21v-6"/><path d="M12 15c-1.5-1-2-2.5-2-4.5S9 7 7.5 7 6 9 7 11"/><path d="M12 15c1.5-1 2-2.5 2-4.5S15 7 16.5 7 18 9 17 11"/><path d="M12 13c0-2 .5-4 .5-6"/><path d="M6 21h12"/>',
    # institution / columns -> government
    "\U0001F3DB": '<path d="M3 9 12 4l9 5"/><path d="M4 9v8"/><path d="M9 9v8"/><path d="M15 9v8"/><path d="M20 9v8"/><path d="M3 20h18"/>',
    "\U0001F3DB️": '<path d="M3 9 12 4l9 5"/><path d="M4 9v8"/><path d="M9 9v8"/><path d="M15 9v8"/><path d="M20 9v8"/><path d="M3 20h18"/>',
    # check -> fits the rules
    "✅": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5 11 15.5 16 9"/>',
    "✔": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5 11 15.5 16 9"/>',
    "✔️": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5 11 15.5 16 9"/>',
}

def icon_html(raw):
    """Return an SVG glyph wrapper for a known emoji, else the raw character."""
    if raw is None:
        return ""
    key = str(raw).strip()
    body = _SVG.get(key) or _SVG.get(key.rstrip("️"))
    if body:
        return ('<div class="iconwrap"><svg viewBox="0 0 24 24" '
                'role="img" aria-hidden="true">' + body + '</svg></div>')
    return f'<div class="icon">{raw}</div>'


def render_cards(p):
    variant = p.get("variant", "grid")
    cls = "why-grid" if variant == "why" else ("grid grid-list" if variant == "list" else ("grid grid-stack" if variant == "stack" else "grid"))
    style = f' style="{p["style"]}"' if p.get("style") else ""
    out = [f'<div class="{cls}"{style}>']
    for c in p.get("items", []):
        if variant == "why":
            out.append('<div class="why-box">')
            if c.get("icon"): out.append(icon_html(c["icon"]))
            out.append(f'<div class="title">{inline(c.get("title",""))}</div>')
            out.append(f'<div class="desc">{inline(c.get("desc",""))}</div>')
            out.append('</div>')
            continue
        cardcls = "card card-accent" if c.get("accent") else "card"
        cstyle = f' style="{c["style"]}"' if c.get("style") else ""
        out.append(f'<div class="{cardcls}"{cstyle}>')
        if c.get("title"): out.append(f'<h4>{inline(c["title"])}</h4>')
        if c.get("tags"): out.append(f'<div style="margin:.5rem 0">{tag_html(c["tags"])}</div>')
        if c.get("p"): out.append(f'<p>{inline(c["p"])}</p>')
        if c.get("ul"):
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in c["ul"]) + "</ul>")
        if c.get("tags_after"): out.append(f'<div style="margin-top:.5rem">{tag_html(c["tags_after"])}</div>')
        out.append('</div>')
    out.append('</div>')
    return "\n".join(out)

def render_downloads(p):
    out = ['<div class="dlgrid">']
    for c in p.get("items", []):
        out.append('<div class="dlcard">')
        out.append(f'<div class="dt">{inline(c.get("title",""))}</div>')
        if c.get("desc"): out.append(f'<div class="dd">{inline(c["desc"])}</div>')
        href = c.get("href", "#")
        label = c.get("btn", "Download")
        out.append(f'<a class="dlbtn" href="{href}" download>{inline(label)}</a>')
        out.append('</div>')
    out.append('</div>')
    return "\n".join(out)

def render_stats(p):
    out = ['<div class="stat-grid">']
    for s in p.get("items", []):
        out.append(f'<div class="stat-box"><div class="n">{inline(s.get("n",""))}</div>'
                   f'<div class="l">{inline(s.get("l",""))}</div></div>')
    out.append('</div>')
    return "\n".join(out)

def render_pipeline(p):
    steps = p.get("items", [])
    out = ['<div class="pipeline">']
    for i, s in enumerate(steps):
        out.append('<div class="pipeline-step">'
                   f'<div class="step-num">{inline(s.get("num",""))}</div>'
                   f'<div class="step-title">{inline(s.get("title",""))}</div>'
                   f'<div class="step-detail">{inline(s.get("detail",""))}</div></div>')
        if i < len(steps) - 1:
            out.append('<div class="pipeline-arrow">&#8594;</div>')
    out.append('</div>')
    return "\n".join(out)

def render_people(p):
    out = ['<div class="people-grid">']
    for person in p.get("items", []):
        affil = person.get("affil", "")
        if person.get("url"):
            affil = f'<a href="{person["url"]}">{inline(affil)}</a>'
        else:
            affil = inline(affil)
        out.append('<div class="person">'
                   f'<div class="name">{inline(person.get("name",""))}</div>'
                   f'<div class="role">{inline(person.get("role",""))}</div>'
                   f'<div class="affil">{affil}</div></div>')
    out.append('</div>')
    return "\n".join(out)

def render_ranking(p):
    out = []
    for r in p.get("items", []):
        color = r.get("color", "muted")
        cmap = {"green":"var(--green)","yellow":"var(--yellow)","red":"var(--red)"}
        cc = cmap.get(color, "var(--muted)")
        out.append(f'<div class="rank-row" style="border-left:3px solid {cc}">'
                   f'<span class="rn" style="color:{cc}">{inline(r.get("rank",""))}</span>'
                   f'<div>{inline(r.get("text",""))}</div></div>')
    return "\n".join(out)

def render_sites(p):
    out = ['<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(320px,1fr))">']
    for s in p.get("items", []):
        out.append('<div class="site-card">'
                   f'<h4><span class="site-dot {s.get("dot","primary")}"></span> {inline(s.get("name",""))}</h4>'
                   f'<p style="font-size:.85rem;color:var(--muted)">{inline(s.get("body",""))}</p>')
        if s.get("species"):
            out.append(f'<div class="site-species">{tag_html(s["species"])}</div>')
        out.append('</div>')
    out.append('</div>')
    return "\n".join(out)

def render_figure(p, figdir):
    src = p.get("file")
    data_uri = None
    candidates = []
    if p.get("artifact"):
        candidates.append(os.path.join(figdir, p["artifact"] + ".png"))
    if src:
        candidates += [os.path.join(figdir, src), src]
    for path in candidates:
        if path and os.path.exists(path):
            with open(path, "rb") as fh:
                b = base64.b64encode(fh.read()).decode()
            ext = "png" if path.lower().endswith("png") else "jpeg"
            data_uri = f"data:image/{ext};base64,{b}"
            break
    num = p.get("num", "")
    cap = inline(p.get("caption", ""))
    numhtml = f'<span class="fnum">{inline(num)}.</span> ' if num else ""
    if data_uri:
        img = f'<img src="{data_uri}" alt="{html.escape(str(p.get("num","figure")))}">'
    else:
        img = ('<div style="padding:2rem;text-align:center;color:var(--muted);'
               f'border:1px dashed var(--border);border-radius:6px">[figure not found: '
               f'{html.escape(str(src or p.get("artifact","")))} — place PNG in figdir]</div>')
    return f'<figure>{img}<figcaption>{numhtml}{cap}</figcaption></figure>'

def render_keyfinding(p):
    return ('<div class="keyfinding">'
            f'<div class="kf-headline">{inline(p.get("headline",""))}</div>'
            f'<div class="kf-body">{inline(p.get("body",""))}</div></div>')

COMPONENTS = {
    "keyfinding": lambda p, fd: render_keyfinding(p),
    "cards": lambda p, fd: render_cards(p),
    "downloads": lambda p, fd: render_downloads(p),
    "stats": lambda p, fd: render_stats(p),
    "pipeline": lambda p, fd: render_pipeline(p),
    "people": lambda p, fd: render_people(p),
    "ranking": lambda p, fd: render_ranking(p),
    "sites": lambda p, fd: render_sites(p),
    "figure": lambda p, fd: render_figure(p, fd),
}

# ----------------------------------------------------------------------------
# Block-level markdown: tables, blockquotes, lists, headings, paragraphs
# ----------------------------------------------------------------------------
def render_table(lines):
    rows = [ln for ln in lines if ln.strip().startswith("|")]
    if len(rows) < 2:
        return ""
    def cells(r):
        return [c.strip() for c in r.strip().strip("|").split("|")]
    header = cells(rows[0])
    body = [cells(r) for r in rows[2:]]  # skip separator row
    out = ['<div class="table-wrap"><table><thead><tr>']
    out += [f"<th>{inline(h)}</th>" for h in header]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)

def render_markdown_block(md):
    """Render a run of standard markdown (no fenced components)."""
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1; continue
        # table
        if s.startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i]); i += 1
            out.append(render_table(tbl)); continue
        # blockquote (possibly multi-line, optional — cite last line)
        if s.startswith(">"):
            q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip()); i += 1
            text = " ".join(x for x in q if not x.startswith("—") and not x.startswith("--"))
            cite = next((x for x in q if x.startswith("—") or x.startswith("--")), None)
            block = f"<blockquote>{inline(text)}"
            if cite:
                block += f"<cite>{inline(cite.lstrip('—').lstrip('-').strip())}</cite>"
            block += "</blockquote>"
            out.append(block); continue
        # headings
        if s.startswith("### "):
            out.append(f"<h3>{inline(s[4:])}</h3>"); i += 1; continue
        if s.startswith("#### "):
            out.append(f"<h4>{inline(s[5:])}</h4>"); i += 1; continue
        # update banner  !> text
        if s.startswith("!>"):
            out.append(f'<div class="update-banner">{inline(s[2:].strip())}</div>'); i += 1; continue
        # CTA button  @> [label](href)
        if s.startswith("@>"):
            out.append(f'<div class="cta-wrap">{inline(s[2:].strip())}</div>'); i += 1; continue
        # unordered list
        if s.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(f"<li>{inline(lines[i].strip()[2:])}</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>"); continue
        # ordered list
        if re.match(r"^\d+\.\s", s):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
                item_txt = re.sub(r"^\d+\.\s", "", lines[i].strip())
                items.append(f"<li>{inline(item_txt)}</li>"); i += 1
            out.append("<ol>" + "".join(items) + "</ol>"); continue
        # paragraph (gather until blank / block start)
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(\||>|#|-\s|\d+\.\s|!>)", lines[i].strip()):
            para.append(lines[i].strip()); i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)

# ----------------------------------------------------------------------------
# Top-level parse: frontmatter + sections + fenced components
# ----------------------------------------------------------------------------
def parse(md):
    fm = {}
    if md.startswith("---"):
        _, fmtext, md = md.split("---", 2)
        fm = yaml.safe_load(fmtext) or {}
    return fm, md

def slugify(title):
    """Stable anchor id from a heading. Strips the {highlight} markup."""
    s = re.sub(r"\{([^}]*)\}", r"\1", str(title))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "section"


def render_toc(sections):
    """Jump list for long pages. Rendered only when front matter sets toc."""
    if len(sections) < 2:
        return ""
    links = "".join(f'<a href="#{slug}">{html.escape(title)}</a>'
                    for title, slug in sections)
    return ('<nav class="toc" aria-label="Sections"><div class="container">'
            f'<span class="toc-label">Jump to</span>{links}</div></nav>')


def render_body(md, figdir, sections_out=None):
    """Walk lines; ## starts a section; ::: type opens a component block."""
    lines = md.split("\n")
    sections = []            # list of (title, [chunks])
    cur_title, cur_sub, chunks = None, None, []
    buf = []
    i = 0

    def flush_buf():
        if buf:
            chunks.append(("md", "\n".join(buf)))
            buf.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("## "):
            # close previous section
            flush_buf()
            if cur_title is not None:
                sections.append((cur_title, cur_sub, chunks))
            cur_title = s[3:].strip()
            cur_sub = None
            chunks = []
            i += 1
            # optional sub line marked with "sub: ..." on the next non-blank
            continue
        if s.startswith("sub:") and not buf and cur_title is not None:
            cur_sub = s[4:].strip()
            i += 1; continue
        if s.startswith(":::"):
            flush_buf()
            ctype = s[3:].strip()
            payload = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                payload.append(lines[i]); i += 1
            i += 1  # skip closing :::
            data = yaml.safe_load("\n".join(payload)) or {}
            chunks.append(("comp", ctype, data))
            continue
        buf.append(ln); i += 1

    flush_buf()
    if cur_title is not None:
        sections.append((cur_title, cur_sub, chunks))

    # emit
    html_out = []
    for title, sub, chks in sections:
        slug = slugify(re.sub(r"\{|\}", "", title))
        if sections_out is not None:
            sections_out.append((re.sub(r"\{|\}", "", title), slug))
        html_out.append(f'<section id="{slug}"><div class="container">')
        html_out.append(f"<h2>{h2_hl(title)}</h2>")
        if sub:
            html_out.append(f'<p class="section-sub">{inline(sub)}</p>')
        for ch in chks:
            if ch[0] == "md":
                html_out.append(render_markdown_block(ch[1]))
            else:
                _, ctype, data = ch
                if ctype in COMPONENTS:
                    html_out.append(COMPONENTS[ctype](data, figdir))
                else:
                    html_out.append(f"<!-- unknown component: {ctype} -->")
        html_out.append("</div></section>")
    return "\n".join(html_out)

# ----------------------------------------------------------------------------
# Academic print stylesheet — light, serif body, journal-like. Used for PDF.
# ----------------------------------------------------------------------------
PRINT_CSS = r"""
@page { size: A4; margin: 20mm 18mm; @bottom-center { content: counter(page) " / " counter(pages); font-size: 8pt; color: #666; } }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: Georgia,'Times New Roman',serif; color:#111; line-height:1.5; font-size:10.5pt; background:#fff; }
a { color:#1a4f8b; text-decoration:none; }
/* Markers must stay legible in greyscale print, so each carries a border
   weight and a background tint rather than relying on hue alone. */
.marker { font-family:Helvetica,Arial,sans-serif; font-size:7pt; font-weight:700; letter-spacing:.06em;
  padding:.1em .4em; border:0.5pt solid #666; border-radius:2pt; white-space:nowrap; }
.marker-mfr { color:#1a5c3a; border-color:#1a5c3a; background:#eef7f1; }
.marker-adapted { color:#7a5c10; border-color:#7a5c10; background:#fdf6e3; }
.marker-untested { color:#8c2f1a; border-color:#8c2f1a; background:#fdeeea; border-width:1pt; }
.draftbar { border:1pt solid #8c2f1a; background:#fdeeea; color:#8c2f1a; padding:6pt 8pt;
  margin-bottom:12pt; font-family:Helvetica,Arial,sans-serif; font-size:9pt; }
.draftbar strong { text-transform:uppercase; letter-spacing:.08em; margin-right:.4em; }
.hero { text-align:left; padding:0 0 12pt; border-bottom:2px solid #111; margin-bottom:14pt; }
.hero-badge { display:block; font-size:8pt; letter-spacing:.08em; text-transform:uppercase; color:#555; margin-bottom:8pt; font-family:Helvetica,Arial,sans-serif; }
.hero h1 { font-size:19pt; font-weight:700; line-height:1.2; margin-bottom:6pt; color:#111; }
.hero .tagline { font-size:10.5pt; font-style:italic; color:#333; max-width:none; margin-bottom:10pt; }
.hero-stats { display:flex; flex-wrap:nowrap; gap:10pt; margin-top:8pt; border-top:1px solid #ccc; padding-top:8pt; }
.hero-stat { flex:1 1 0; min-width:0; text-align:center; padding:0 2pt; }
.hero-stat .val { font-size:13pt; font-weight:700; color:#1a4f8b; }
.hero-stat .lbl { font-size:7pt; text-transform:uppercase; letter-spacing:.03em; color:#666; font-family:Helvetica,Arial,sans-serif; line-height:1.25; overflow-wrap:anywhere; }
.container { max-width:none; padding:0; }
section { padding:6pt 0; border-bottom:none; break-inside:auto; }
h2, h3 { break-after:avoid; }
figcaption { break-before:avoid; }
h2 { font-size:14pt; font-weight:700; margin:12pt 0 4pt; color:#111; border-bottom:1px solid #999; padding-bottom:2pt; break-after:avoid; font-family:Helvetica,Arial,sans-serif; }
h2 .hl { color:#1a4f8b; }
.section-sub { color:#444; font-size:9.5pt; font-style:italic; margin-bottom:8pt; max-width:none; }
h3 { font-size:11.5pt; font-weight:700; margin:10pt 0 4pt; color:#1a4f8b; break-after:avoid; font-family:Helvetica,Arial,sans-serif; }
h4 { font-size:10.5pt; font-weight:700; margin:6pt 0 3pt; color:#111; }
p { margin:4pt 0; font-size:10pt; }
section p, .container p { font-size:10pt; }
ul,ol { margin:4pt 0 4pt 16pt; }
li { font-size:9.5pt; margin-bottom:1.5pt; }
/* inline-block flow (not flex): cards sit side-by-side but the container can break between rows across a page boundary, so a heading + grid never jumps whole and strands a blank page */
/* inline-block flow (not flex): cards sit side-by-side but the container can break between rows across a page boundary */
.grid,.why-grid,.people-grid { display:block; margin:6pt 0; font-size:0; }
.card,.why-box,.person,.site-card { display:inline-block; vertical-align:top; box-sizing:border-box; background:#f7f7f5; border:1px solid #ddd; border-radius:4pt; padding:8pt 10pt; margin:0 0 6pt; width:49%; font-size:9pt; }
.card:nth-child(odd),.why-box:nth-child(odd),.person:nth-child(odd),.site-card:nth-child(odd) { margin-right:1.5%; }
/* short cards stay whole; tall text cards (species profiles etc.) may split across a page so they fill it instead of jumping and stranding a heading */
.why-box,.person,.stat-box,.rank-row,.keyfinding { break-inside:avoid; }
.card { break-inside:auto; }
/* long reference/list card blocks (Downloads, Methods): fragmentable columns so a tall card fills the page instead of orphaning it */
/* download/methods lists: full-width stacked cards (flow top-to-bottom, break across pages — no column imbalance), each card's long list wrapped into 2 internal columns to stay compact */
.grid-list { display:block; }
.grid-list .card { display:block; width:100%; margin:0 0 6pt; break-inside:auto; }
.grid-list .card ul { column-count:2; column-gap:14pt; margin-top:2pt; }
.grid-list .card li { break-inside:avoid; }
/* stacked full-width cards in reading order; the block flows down the page (fills it) while each card stays whole */
.grid-stack { display:block; font-size:0; }
.grid-stack .card { display:block; width:100%; margin:0 0 6pt; break-inside:auto; font-size:9pt; }
.stat-box,.keyfinding,figure,blockquote,.rank-row { break-inside:avoid; }
.card h4,.why-box .title { font-size:10pt; }
.card p,.card li,.why-box .desc,.person .affil { color:#333; font-size:9pt; }
.card-accent { border-left:3px solid #1a4f8b; }
.why-box { text-align:left; } .why-box .icon, .why-box .iconwrap { display:none; }
.stat-grid { display:flex; flex-wrap:nowrap; gap:8pt; margin:8pt 0; }
.stat-box { background:#f0f3f8; border:1px solid #d5dce8; border-radius:4pt; padding:5pt 4pt; text-align:center; flex:1 1 0; min-width:0; break-inside:avoid; }
.stat-box .l { word-break:normal; overflow-wrap:anywhere; }
.stat-box .n { font-size:13pt; font-weight:700; color:#1a4f8b; }
.stat-box .l { font-size:7pt; text-transform:uppercase; color:#666; font-family:Helvetica,Arial,sans-serif; }
table { width:100%; border-collapse:collapse; margin:6pt 0; font-size:8.5pt; break-inside:auto; }
th,td { text-align:left; padding:3pt 5pt; border-bottom:1px solid #ccc; }
th { color:#333; font-weight:700; font-size:7.5pt; text-transform:uppercase; background:#eee; font-family:Helvetica,Arial,sans-serif; }
td { color:#111; }
.table-wrap { overflow:visible; border:1px solid #ccc; border-radius:4pt; margin:6pt 0; break-inside:auto; }
.table-wrap table { margin:0; }
thead { display:table-header-group; }
tr { break-inside:avoid; }
tr:hover td { background:transparent; }
.pipeline { display:flex; flex-wrap:wrap; gap:4pt; margin:8pt 0; }
.pipeline-step { background:#f7f7f5; border:1px solid #ddd; border-radius:4pt; padding:5pt 8pt; text-align:center; flex:1; min-width:70pt; }
.pipeline-step .step-num { font-size:6.5pt; color:#1a4f8b; text-transform:uppercase; font-weight:700; }
.pipeline-step .step-title { font-size:9pt; font-weight:700; }
.pipeline-step .step-detail { font-size:7pt; color:#666; }
.pipeline-arrow { color:#999; font-size:11pt; align-self:center; }
.tag { display:inline-block; font-size:7pt; padding:1pt 5pt; border-radius:8pt; margin:1pt; border:1px solid #ccc; background:#eee; color:#333; }
.person .name { font-weight:700; font-size:9.5pt; } .person .role { color:#1a4f8b; font-size:8pt; }
.site-dot { display:none; }
.rank-row { display:flex; align-items:center; gap:8pt; padding:4pt 8pt; background:#f7f7f5; border:1px solid #ddd; border-radius:4pt; margin-bottom:3pt; break-inside:avoid; }
.rank-row .rn { font-weight:700; min-width:16pt; font-size:11pt; }
blockquote { border-left:3px solid #1a4f8b; padding:5pt 10pt; margin:8pt 0; background:#f5f5f2; font-size:9.5pt; color:#444; font-style:italic; break-inside:avoid; }
blockquote cite { display:block; margin-top:3pt; font-size:8pt; color:#1a4f8b; font-style:normal; }
figure { margin:5pt 0; border:1px solid #ddd; border-radius:4pt; padding:5pt; break-inside:avoid; background:#fff; }
figure img { max-width:100%; max-height:3.6in; width:auto; height:auto; display:block; margin:0 auto; }
figcaption { font-size:8.5pt; color:#444; margin-top:4pt; line-height:1.4; }
figcaption .fnum { color:#1a4f8b; font-weight:700; }
.update-banner { background:#eef2f9; border:1px solid #cdd8ea; border-radius:4pt; padding:4pt 8pt; font-size:8.5pt; color:#444; margin:6pt 0; }
.cta-wrap { margin:8pt 0; text-align:center; }
.cta-wrap a { display:inline-block; background:#128678; color:#fff; font-weight:700; font-size:10pt; padding:5pt 12pt; border-radius:4pt; text-decoration:none; }
.keyfinding { background:#eef6f4; border:1px solid #9ccfc6; border-left:4pt solid #128678; border-radius:4pt; padding:8pt 12pt; margin:8pt 0; break-inside:avoid; }
.keyfinding .kf-headline { font-size:12pt; font-weight:700; color:#0f6b5f; line-height:1.3; margin-bottom:4pt; font-family:Helvetica,Arial,sans-serif; }
.keyfinding .kf-body { font-size:9.5pt; color:#222; line-height:1.5; }
footer { padding:10pt 0 0; text-align:left; color:#666; font-size:8pt; border-top:1px solid #999; margin-top:12pt; }
footer a { color:#1a4f8b; }
.ref-list { font-size:8.5pt; color:#333; line-height:1.5; }
.ref-list li { margin-bottom:2pt; }
"""

def render_hero(fm, mode="web"):
    if mode == "print":
        stats = fm.get("hero_stats", [])
        sh = "".join(f'<div class="hero-stat"><div class="val">{inline(s["val"])}</div>'
                     f'<div class="lbl">{inline(s["lbl"])}</div></div>' for s in stats)
        return (f'<header class="hero">'
                f'<span class="hero-badge">{inline(fm.get("badge",""))}</span>'
                f'<h1>{inline(fm.get("title_display", fm.get("title","")))}</h1>'
                f'<p class="tagline">{inline(fm.get("tagline") or fm.get("sub",""))}</p>'
                f'<div class="hero-stats">{sh}</div></header>')
    return _render_hero_web(fm)

def render_draft_banner(fm):
    """Draft banner, driven by front-matter `status`.

    The brief requires this to stay up until an end-to-end run has been
    completed. It is keyed on `status` so removing the banner means editing the
    register of fact, not deleting a decoration.
    """
    status = fm.get("status")
    if not status:
        return ""
    # The label already says Draft; strip a leading "draft —" from the status
    # text so the banner does not say it twice.
    detail = re.sub(r"^\s*draft\s*[—–-]*\s*", "", str(status), flags=re.I)
    return ('<div class="draftbar" role="status"><div class="container">'
            f'<strong>Draft</strong> — {inline(detail)}</div></div>')


def _render_hero_web(fm):
    stats = fm.get("hero_stats", [])
    sh = "".join(f'<div class="hero-stat"><div class="val">{inline(s["val"])}</div>'
                 f'<div class="lbl">{inline(s["lbl"])}</div></div>' for s in stats)
    badge = fm.get("badge", "")
    # `sub` is the seed protocol page's key for the same slot as `tagline`.
    tagline = fm.get("tagline") or fm.get("sub", "")
    return (f'<header class="hero"><div class="container">'
            f'<span class="hero-badge">{inline(badge)}</span>'
            f'<h1>{inline(fm.get("title_display", fm.get("title","")))}</h1>'
            f'<p class="tagline">{inline(tagline)}</p>'
            f'<div class="hero-stats">{sh}</div></div></header>')

def render_footer(fm):
    f = dict(fm.get("footer", {}) or {})
    # Pages that carry a bare `updated` date and no footer block still get it.
    if fm.get("updated") and not f.get("copyright"):
        f["copyright"] = f"Updated {fm['updated']}."
    return ('<footer><div class="container">'
            f'<p style="margin-bottom:.5rem"><strong style="color:var(--text)">{inline(f.get("org",""))}</strong></p>'
            f'<p>{inline(f.get("line",""))}</p>'
            f'<p style="margin-top:.75rem;font-size:.7rem">{inline(f.get("note",""))}</p>'
            + (f'<p style="margin-top:.5rem;font-size:.7rem">{inline(f.get("copyright",""))}</p>' if f.get("copyright") else "")
            + '</div></footer>')

NAV_PAGES = [("index.html", "Overview"), ("inventory.html", "Inventory"),
             ("buy-list.html", "Buy list"), ("software.html", "Software"),
             ("open-questions.html", "Open questions"),
             ("protocol.html", "Protocol")]

def render_nav(active):
    links = "".join(
        f'<a href="{href}" class="{"active" if href==active else ""}">{label}</a>'
        for href, label in NAV_PAGES)
    return ('<nav class="sitenav"><div class="inner">'
            '<span class="brand">Good Ancestor open lab<span class="dot">.</span></span>'
            f'{links}</div></nav>')

def build(md_path, out_path, figdir, mode="web", nav_active=None):
    with open(md_path, encoding="utf-8") as fh:
        md = fh.read()
    fm, body_md = parse(md)
    sections = []
    body = render_body(body_md, figdir, sections)
    toc = render_toc(sections) if (mode == "web" and fm.get("toc")) else ""
    css = PRINT_CSS if mode == "print" else CSS
    nav = render_nav(nav_active) if (mode == "web" and nav_active) else ""
    fonts = "" if mode == "print" else (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Fraunces:ital,opsz,wght@0,9..144,400..600;1,9..144,400..500&'
        'family=IBM+Plex+Mono:wght@400;500;600&'
        'family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">')
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(fm.get('title',''))}</title>
<meta name="description" content="{html.escape(fm.get('description',''))}">
{fonts}
<style>{css}</style>
</head><body>
{nav}
{render_draft_banner(fm)}
{render_hero(fm, mode)}
{toc}
{body}
{render_footer(fm)}
</body></html>"""
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return len(doc)

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    figdir = "figures"
    if "--figdir" in sys.argv:
        figdir = sys.argv[sys.argv.index("--figdir") + 1]
    mode = "print" if "--print" in sys.argv else "web"
    nav_active = None
    if "--nav" in sys.argv:
        nav_active = sys.argv[sys.argv.index("--nav") + 1]
    md_path = args[0] if args else "seagrass_site.md"
    out_path = args[1] if len(args) > 1 else "seagrass_site.html"
    n = build(md_path, out_path, figdir, mode, nav_active=nav_active)
    print(f"wrote {out_path} ({n} bytes) from {md_path} [figdir={figdir}, mode={mode}, nav={nav_active}]")
