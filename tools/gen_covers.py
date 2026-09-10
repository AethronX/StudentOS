#!/usr/bin/env python3
"""
Student OS Pro — page cover art.

One visual system, twenty-six covers. Every cover shares the same base:
a deep navy ground, soft colour blooms in screen blend, a faint grid,
a vignette and a little grain. What changes per page is the hue family
(which area it belongs to) and a thin-line motif saying what the page is
actually for.

Motifs sit on the RIGHT of the canvas: Notion renders the page icon and
title over the lower-left of a cover, so that corner is left clear.

Output: assets/covers/<slug>.svg  and  assets/covers/<slug>.jpg (1500x600)
"""

import base64
import os
import re
import subprocess
import sys

W, H = 1500, 600
BASE = "#0B1226"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "covers")
CHROME = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"

# ── hue families ──────────────────────────────────────────────────────
# blooms: (colour, cx%, cy%, r%)   accent: the jewel colour for the motif
FAMILIES = {
    "system":   {"blooms": [("#4F46E5", 22, 28, 58), ("#8B5CF6", 72, 30, 52),
                            ("#0EA5E9", 30, 96, 40, 0.5), ("#6366F1", 94, 82, 38, 0.65)],
                 "accent": "#A5B4FC"},
    "start":    {"blooms": [("#10B981", 20, 30, 56), ("#14B8A6", 70, 26, 50),
                            ("#34D399", 28, 96, 38, 0.5), ("#059669", 94, 82, 38, 0.65)],
                 "accent": "#6EE7B7"},
    "review":   {"blooms": [("#F59E0B", 22, 30, 54), ("#F97316", 72, 28, 50),
                            ("#FBBF24", 28, 96, 38, 0.5), ("#EA580C", 94, 82, 36, 0.65)],
                 "accent": "#FCD34D"},
    "admin":    {"blooms": [("#475569", 24, 30, 56), ("#64748B", 72, 30, 50),
                            ("#334155", 30, 96, 38, 0.5), ("#1E293B", 94, 82, 38, 0.65)],
                 "accent": "#94A3B8"},
    "academic": {"blooms": [("#0EA5E9", 24, 30, 58), ("#6366F1", 74, 32, 52),
                            ("#38BDF8", 30, 96, 38, 0.5), ("#4F46E5", 94, 82, 40, 0.65)],
                 "accent": "#7DD3FC"},
    "urgent":   {"blooms": [("#F43F5E", 22, 30, 54), ("#F97316", 70, 30, 50),
                            ("#FB7185", 28, 96, 38, 0.5), ("#E11D48", 94, 82, 36, 0.65)],
                 "accent": "#FDA4AF"},
    "focus":    {"blooms": [("#8B5CF6", 22, 28, 58), ("#6366F1", 72, 32, 52),
                            ("#A78BFA", 30, 96, 38, 0.5), ("#7C3AED", 94, 82, 38, 0.65)],
                 "accent": "#C4B5FD"},
    "jobs":     {"blooms": [("#7C3AED", 24, 30, 56), ("#A855F7", 72, 28, 50),
                            ("#8B5CF6", 30, 96, 38, 0.5), ("#6D28D9", 94, 82, 36, 0.65)],
                 "accent": "#D8B4FE"},
    "finance":  {"blooms": [("#10B981", 24, 30, 56), ("#059669", 72, 30, 50),
                            ("#34D399", 30, 96, 38, 0.5), ("#14B8A6", 94, 82, 38, 0.65)],
                 "accent": "#6EE7B7"},
    "personal": {"blooms": [("#EC4899", 22, 30, 56), ("#F43F5E", 72, 28, 50),
                            ("#F472B6", 30, 96, 38, 0.5), ("#BE185D", 94, 82, 36, 0.65)],
                 "accent": "#F9A8D4"},
    "library":  {"blooms": [("#B45309", 22, 30, 54), ("#F59E0B", 72, 30, 50),
                            ("#D97706", 30, 96, 38, 0.5), ("#92400E", 94, 82, 36, 0.65)],
                 "accent": "#FCD34D"},
}


def dots(pts, r=9, op="0.92"):
    return "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{{A}}" fill-opacity="{op}" stroke="none"/>'
        for x, y in pts
    )


# ── motifs, drawn inside a 360x360 box ────────────────────────────────
# {A} is substituted with the family accent colour.
MOTIFS = {
    # the whole system: nodes that know about each other
    "constellation":
        '<path d="M36 244 L118 120 L248 168 L322 58"/>'
        '<path d="M118 120 L158 286 L248 168"/>'
        '<path d="M158 286 L302 300 L322 58"/>'
        + dots([(36, 244), (118, 120), (248, 168), (322, 58), (158, 286), (302, 300)]),

    # onboarding: a climb with a trajectory over it
    "ascend":
        '<path d="M28 312 H104 V246 H180 V182 H256 V112 H332"/>'
        '<path d="M40 214 Q168 44 330 76" stroke-opacity="0.34" stroke-dasharray="9 11"/>'
        + dots([(330, 76)], r=11),

    # the weekly loop
    "cycle":
        '<path d="M300 128 A128 128 0 1 0 322 208"/>'
        '<path d="M300 128 L258 140 M300 128 L310 86"/>'
        + dots([(180, 200)], r=13),

    # dashboard: a grid of cards
    "cards":
        '<rect x="24" y="58" width="150" height="94" rx="16"/>'
        '<rect x="192" y="58" width="150" height="94" rx="16"/>'
        '<rect x="24" y="172" width="150" height="94" rx="16"/>'
        '<rect x="192" y="172" width="150" height="94" rx="16"/>'
        '<rect x="24" y="286" width="318" height="56" rx="16"/>'
        '<rect x="192" y="58" width="150" height="94" rx="16" fill="{A}" fill-opacity="0.22" stroke="none"/>',

    # the engine room
    "stack":
        '<ellipse cx="182" cy="92" rx="122" ry="36"/>'
        '<path d="M60 92 V168 A122 36 0 0 1 304 168 V92"/>'
        '<path d="M60 168 V244 A122 36 0 0 1 304 244 V168"/>'
        '<path d="M60 244 V318 A122 36 0 0 1 304 318 V244"/>',

    # courses: the backbone
    "cap":
        '<path d="M30 152 L182 92 L334 152 L182 212 Z"/>'
        '<path d="M92 180 V266 Q182 314 272 266 V180"/>'
        '<path d="M334 152 V244"/>'
        + dots([(334, 252), (182, 152)], r=10),

    # an assignment, part-done
    "brief":
        '<path d="M74 40 H244 L296 94 V330 H74 Z"/>'
        '<path d="M244 40 V94 H296"/>'
        '<path d="M112 148 H256 M112 190 H256"/>'
        '<rect x="112" y="244" width="146" height="20" rx="10"/>'
        '<rect x="112" y="244" width="88" height="20" rx="10" fill="{A}" fill-opacity="0.95" stroke="none"/>',

    # the week, in columns
    "timetable":
        '<rect x="28" y="66" width="308" height="266" rx="14"/>'
        '<path d="M28 116 H336" stroke-opacity="0.55"/>'
        '<path d="M105 66 V332 M182 66 V332 M259 66 V332" stroke-opacity="0.4"/>'
        '<rect x="38" y="132" width="57" height="60" rx="9" fill="{A}" fill-opacity="0.8" stroke="none"/>'
        '<rect x="192" y="150" width="57" height="78" rx="9" fill="#fff" fill-opacity="0.5" stroke="none"/>'
        '<rect x="115" y="238" width="57" height="52" rx="9" fill="#fff" fill-opacity="0.34" stroke="none"/>'
        '<rect x="269" y="200" width="57" height="66" rx="9" fill="#fff" fill-opacity="0.42" stroke="none"/>',

    # goals: two or three, not ten
    "target":
        '<circle cx="176" cy="198" r="132"/>'
        '<circle cx="176" cy="198" r="86"/>'
        '<circle cx="176" cy="198" r="42"/>'
        '<path d="M318 62 L206 172" stroke-opacity="0.8"/>'
        '<path d="M318 62 L282 70 M318 62 L310 100"/>'
        + dots([(176, 198)], r=14),

    # an exam, counting down
    "exam":
        '<path d="M52 38 H244 V286 H52 Z"/>'
        '<path d="M92 100 H204 M92 142 H204 M92 184 H166"/>'
        '<circle cx="258" cy="262" r="78" fill="#0B1226" fill-opacity="0.92"/>'
        '<circle cx="258" cy="262" r="78"/>'
        '<path d="M258 262 V208 M258 262 L298 284"/>'
        + dots([(258, 262)], r=8),

    # every file, one place
    "layers":
        '<path d="M182 56 L334 128 L182 200 L30 128 Z"/>'
        '<path d="M30 190 L182 262 L334 190" stroke-opacity="0.72"/>'
        '<path d="M30 252 L182 324 L334 252" stroke-opacity="0.5"/>'
        '<path d="M182 56 L334 128 L182 200 L30 128 Z" fill="{A}" fill-opacity="0.16" stroke="none"/>',

    # notes stacked
    "notes":
        '<path d="M44 96 H222 V342 H44 Z" stroke-opacity="0.45"/>'
        '<path d="M108 40 H286 V286 H108 Z" fill="#0B1226" fill-opacity="0.94"/>'
        '<path d="M108 40 H286 V286 H108 Z"/>'
        '<path d="M142 100 H252 M142 144 H252 M142 188 H214"/>'
        '<rect x="138" y="176" width="80" height="24" rx="7" fill="{A}" fill-opacity="0.7" stroke="none"/>',

    # a project, spread over weeks
    "gantt":
        '<path d="M34 46 V330" stroke-opacity="0.34"/>'
        '<rect x="52" y="76" width="176" height="28" rx="14"/>'
        '<rect x="118" y="138" width="196" height="28" rx="14"/>'
        '<rect x="80" y="200" width="150" height="28" rx="14"/>'
        '<rect x="166" y="262" width="164" height="28" rx="14" fill="{A}" fill-opacity="0.85" stroke="none"/>',

    # what is actually urgent
    "triage":
        '<rect x="58" y="64" width="272" height="34" rx="17" fill="{A}" fill-opacity="0.9" stroke="none"/>'
        '<rect x="58" y="122" width="222" height="34" rx="17"/>'
        '<rect x="58" y="180" width="176" height="34" rx="17" stroke-opacity="0.7"/>'
        '<rect x="58" y="238" width="132" height="34" rx="17" stroke-opacity="0.5"/>'
        '<rect x="58" y="296" width="96" height="34" rx="17" stroke-opacity="0.34"/>'
        '<path d="M30 64 V98" stroke="{A}" stroke-width="7"/>',

    # the board
    "board":
        '<rect x="22" y="52" width="100" height="290" rx="16" stroke-opacity="0.42"/>'
        '<rect x="132" y="52" width="100" height="290" rx="16" stroke-opacity="0.42"/>'
        '<rect x="242" y="52" width="100" height="290" rx="16" stroke-opacity="0.42"/>'
        '<rect x="36" y="76" width="72" height="46" rx="10"/>'
        '<rect x="36" y="136" width="72" height="46" rx="10"/>'
        '<rect x="146" y="76" width="72" height="46" rx="10" fill="{A}" fill-opacity="0.85" stroke="none"/>'
        '<rect x="146" y="136" width="72" height="46" rx="10"/>'
        '<rect x="256" y="76" width="72" height="46" rx="10" stroke-opacity="0.6"/>',

    # levels you climb
    "levels":
        '<rect x="34" y="240" width="56" height="96" rx="12"/>'
        '<rect x="110" y="188" width="56" height="148" rx="12"/>'
        '<rect x="186" y="128" width="56" height="208" rx="12"/>'
        '<rect x="262" y="62" width="56" height="274" rx="12" fill="{A}" fill-opacity="0.85" stroke="none"/>',

    # the forgetting curve, interrupted by reviews — the signature motif
    "spacing":
        '<path d="M30 336 H338" stroke-opacity="0.34"/>'
        '<path d="M34 78 C64 214 96 268 136 282"/>'
        '<path d="M136 282 L136 116" stroke="{A}" stroke-dasharray="7 9" stroke-opacity="0.9"/>'
        '<path d="M136 116 C178 226 210 264 250 274"/>'
        '<path d="M250 274 L250 138" stroke="{A}" stroke-dasharray="7 9" stroke-opacity="0.9"/>'
        '<path d="M250 138 C292 224 314 252 340 260"/>'
        + dots([(136, 116), (250, 138)], r=10),

    # hours, and what they are worth
    "shift":
        '<circle cx="136" cy="152" r="104"/>'
        '<path d="M136 152 V84 M136 152 L186 182"/>'
        '<circle cx="266" cy="278" r="72" fill="#0B1226" fill-opacity="0.94"/>'
        '<circle cx="266" cy="278" r="72"/>'
        '<circle cx="266" cy="278" r="40" stroke-opacity="0.55"/>'
        + dots([(136, 152)], r=8),

    # wishlist to offer
    "funnel":
        '<path d="M34 58 H326 L292 116 H68 Z"/>'
        '<path d="M68 130 H292 L262 188 H98 Z" stroke-opacity="0.8"/>'
        '<path d="M98 202 H262 L234 260 H126 Z" stroke-opacity="0.62"/>'
        '<path d="M126 274 H234 L210 330 H150 Z" fill="{A}" fill-opacity="0.85" stroke="none"/>',

    # spending against a limit
    "budget":
        '<path d="M28 336 H338" stroke-opacity="0.34"/>'
        '<rect x="44" y="206" width="52" height="130" rx="9"/>'
        '<rect x="114" y="156" width="52" height="180" rx="9"/>'
        '<rect x="184" y="236" width="52" height="100" rx="9"/>'
        '<rect x="254" y="104" width="52" height="232" rx="9" fill="{A}" fill-opacity="0.85" stroke="none"/>'
        '<path d="M28 140 H338" stroke="{A}" stroke-dasharray="10 10" stroke-opacity="0.95"/>',

    # keep moving
    "pulse":
        '<path d="M26 200 H104 L136 108 L180 296 L216 166 L246 200 H340"/>'
        + dots([(180, 296), (136, 108)], r=9),

    # decide once
    "plate":
        '<circle cx="180" cy="158" r="108"/>'
        '<circle cx="180" cy="158" r="72" stroke-opacity="0.5"/>'
        '<rect x="30" y="292" width="38" height="46" rx="9" stroke-opacity="0.6"/>'
        '<rect x="76" y="292" width="38" height="46" rx="9" stroke-opacity="0.6"/>'
        '<rect x="122" y="292" width="38" height="46" rx="9" fill="{A}" fill-opacity="0.8" stroke="none"/>'
        '<rect x="168" y="292" width="38" height="46" rx="9" stroke-opacity="0.6"/>'
        '<rect x="214" y="292" width="38" height="46" rx="9" stroke-opacity="0.6"/>'
        '<rect x="260" y="292" width="38" height="46" rx="9" stroke-opacity="0.6"/>'
        '<rect x="306" y="292" width="38" height="46" rx="9" stroke-opacity="0.6"/>',

    # two honest minutes
    "journal":
        '<path d="M180 108 C142 76 84 74 44 90 V304 C84 288 142 290 180 322"/>'
        '<path d="M180 108 C218 76 276 74 316 90 V304 C276 288 218 290 180 322"/>'
        '<path d="M180 108 V322" stroke-opacity="0.6"/>'
        + dots([(96, 44), (180, 30), (264, 44)], r=11),

    # read outside the syllabus
    "spines":
        '<rect x="44" y="96" width="48" height="242" rx="9"/>'
        '<rect x="102" y="62" width="48" height="276" rx="9"/>'
        '<rect x="160" y="118" width="48" height="220" rx="9" fill="{A}" fill-opacity="0.8" stroke="none"/>'
        '<rect x="218" y="86" width="48" height="252" rx="9"/>'
        '<g transform="rotate(14 300 210)"><rect x="276" y="110" width="48" height="228" rx="9" stroke-opacity="0.75"/></g>',

    # consistency, measured
    "streak": "".join(
        f'<rect x="{28 + c * 46}" y="{92 + r_ * 46}" width="34" height="34" rx="9" '
        + ('fill="{A}" fill-opacity="0.85" stroke="none"/>'
           if (c + r_ * 3) % 4 != 3 and not (c == 6 and r_ in (1, 3))
           else 'stroke-opacity="0.42"/>')
        for r_ in range(5) for c in range(7)
    ),

    # the people, not the numbers
    "network":
        '<path d="M110 128 L250 108 M110 128 L188 268 M250 108 L188 268"/>'
        '<circle cx="110" cy="128" r="30" fill="#0B1226" fill-opacity="0.94"/>'
        '<circle cx="110" cy="128" r="30"/>'
        '<path d="M64 214 a46 50 0 0 1 92 0"/>'
        '<circle cx="250" cy="108" r="30" fill="#0B1226" fill-opacity="0.94"/>'
        '<circle cx="250" cy="108" r="30"/>'
        '<path d="M204 194 a46 50 0 0 1 92 0"/>'
        + dots([(188, 268)], r=13),
}


def svg(family_key, motif_key):
    fam = FAMILIES[family_key]
    accent = fam["accent"]
    defs = []
    layers = []
    for i, bloom in enumerate(fam["blooms"]):
        col, cx, cy, r = bloom[:4]
        peak = bloom[4] if len(bloom) > 4 else 1.0
        defs.append(
            f'<radialGradient id="g{i}" cx="{cx}%" cy="{cy}%" r="{r}%">'
            f'<stop offset="0%" stop-color="{col}" stop-opacity="{peak}"/>'
            f'<stop offset="68%" stop-color="{col}" stop-opacity="0"/></radialGradient>'
        )
        layers.append(f'<rect width="{W}" height="{H}" fill="url(#g{i})"/>')

    motif = MOTIFS[motif_key].replace("{A}", accent)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">
<defs>
{chr(10).join(defs)}
<radialGradient id="vig" cx="50%" cy="45%" r="78%">
<stop offset="40%" stop-color="#000" stop-opacity="0"/>
<stop offset="100%" stop-color="#000" stop-opacity="0.38"/>
</radialGradient>
<pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
<path d="M60 0H0V60" fill="none" stroke="#fff" stroke-opacity="0.038" stroke-width="1"/>
</pattern>
<filter id="grain" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.62" numOctaves="2"/>
<feColorMatrix type="saturate" values="0"/>
</filter>
<filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
<feGaussianBlur stdDeviation="14"/>
</filter>
</defs>
<rect width="{W}" height="{H}" fill="{BASE}"/>
<g style="mix-blend-mode:screen">
{chr(10).join(layers)}
</g>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<g transform="translate(946,158) scale(0.79)">
<g fill="none" stroke="{accent}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" opacity="0.32" filter="url(#soft)">{motif}</g>
<g fill="none" stroke="#ffffff" stroke-opacity="0.72" stroke-width="3.9" stroke-linecap="round" stroke-linejoin="round">{motif}</g>
</g>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.07"/>
</svg>'''


# slug, family, motif
PAGES = [
    ("root",        "system",   "constellation"),
    ("start",       "start",    "ascend"),
    ("weekly",      "review",   "cycle"),
    ("dashboard",   "system",   "cards"),
    ("admin",       "admin",    "stack"),
    ("courses",     "academic", "cap"),
    ("assignments", "academic", "brief"),
    ("schedule",    "academic", "timetable"),
    ("goals",       "academic", "target"),
    ("exams",       "urgent",   "exam"),
    ("materials",   "academic", "layers"),
    ("notes",       "academic", "notes"),
    ("projects",    "academic", "gantt"),
    ("agenda",      "urgent",   "triage"),
    ("tasks",       "review",   "board"),
    ("skills",      "focus",    "levels"),
    ("studyhub",    "focus",    "spacing"),
    ("job",         "jobs",     "shift"),
    ("internships", "jobs",     "funnel"),
    ("finance",     "finance",  "budget"),
    ("fitness",     "personal", "pulse"),
    ("meals",       "personal", "plate"),
    ("journal",     "personal", "journal"),
    ("books",       "library",  "spines"),
    ("habits",      "urgent",   "streak"),
    ("contacts",    "system",   "network"),
]


def render_jpeg(svg_text, out_path, quality=0.88):
    """SVG -> JPEG via Chromium's canvas encoder.

    Covers are smooth gradients: PNG stores one at ~1 MB, JPEG at ~60 KB for
    the same picture. Students open these on a phone, so the 16x matters more
    than lossless does. No ImageMagick or PIL in this environment, hence the
    canvas round-trip; the SVG goes in as a data: URI so the canvas stays
    untainted and toDataURL is allowed.
    """
    b64 = base64.b64encode(svg_text.encode()).decode()
    html_path = out_path + ".html"
    with open(html_path, "w") as f:
        f.write(
            f'<!doctype html><body style="margin:0">'
            f'<img id=s src="data:image/svg+xml;base64,{b64}"><div id=o></div><script>\n'
            f'const img=document.getElementById("s");\n'
            f'function go(){{const c=document.createElement("canvas");'
            f'c.width={W};c.height={H};const x=c.getContext("2d");'
            f'x.fillStyle="{BASE}";x.fillRect(0,0,{W},{H});'
            f'x.drawImage(img,0,0,{W},{H});'
            f'try{{document.getElementById("o").textContent='
            f'c.toDataURL("image/jpeg",{quality});}}'
            f'catch(e){{document.getElementById("o").textContent="ERR:"+e.message;}}}}\n'
            f'if(img.complete)go();else img.onload=go;</script></body>')

    r = subprocess.run(
        [CHROME, "--headless", "--no-sandbox", "--disable-gpu",
         "--virtual-time-budget=10000", "--dump-dom", f"file://{html_path}"],
        capture_output=True, timeout=120)
    os.remove(html_path)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r'<div id="o">(.*?)</div>', dom, re.S)
    payload = (m.group(1) if m else "").strip()
    if not payload.startswith("data:image/jpeg"):
        raise RuntimeError(f"encode failed: {payload[:200] or '(empty)'}")

    with open(out_path, "wb") as f:
        f.write(base64.b64decode(payload.split(",", 1)[1]))
    return os.path.getsize(out_path)


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for slug, fam, motif in PAGES:
        s = svg(fam, motif)
        with open(os.path.join(OUT, f"{slug}.svg"), "w") as f:
            f.write(s)
        try:
            size = render_jpeg(s, os.path.join(OUT, f"{slug}.jpg"))
        except RuntimeError as e:
            print(f"FAIL {slug}: {e}", file=sys.stderr)
            return 1
        made.append((slug, size))

    total = sum(sz for _, sz in made)
    for slug, sz in made:
        print(f"  {slug:<12} {sz/1024:6.0f} KB")
    print(f"\n{len(made)} covers, {total/1024:.0f} KB total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
