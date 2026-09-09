#!/usr/bin/env python3
"""
Instagram assets for Student OS Pro.

Renders a bilingual feed carousel (1080x1080) and stories (1080x1920)
with headless Chromium, using the same palette as the product covers.

    python3 generate.py [output_dir]

Edit SLIDES below to change the copy — no design work required.
"""
import html
import os
import subprocess
import sys

CHROME = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "instagram")

FEED = (1080, 1080)
STORY = (1080, 1920)

# Accent pairs reused from the cover system, one per slide theme.
THEME = {
    "indigo": ("#4F46E5", "#0EA5E9", "#0B1020"),
    "violet": ("#7C3AED", "#C026D3", "#140A24"),
    "teal":   ("#14B8A6", "#0EA5E9", "#071A1C"),
    "green":  ("#059669", "#10B981", "#04180F"),
    "rose":   ("#F43F5E", "#F97316", "#1C0A12"),
}

SHELL = """<!doctype html><html lang="{lang}" dir="{dir}"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
body{{
  font-family:{font};
  background:{bg};
  color:#EEF1F8;
  position:relative;
  display:flex;flex-direction:column;
  padding:{pad}px;
}}
.blobs{{position:absolute;inset:0;pointer-events:none}}
.blobs i{{position:absolute;border-radius:50%;filter:blur(90px);opacity:.85;display:block}}
.b1{{width:62%;aspect-ratio:1;background:{c1};top:-14%;{start}:-12%}}
.b2{{width:55%;aspect-ratio:1;background:{c2};bottom:-16%;{end}:-10%}}
.grid{{position:absolute;inset:0;opacity:.05;
  background-image:linear-gradient(to right,#fff 1px,transparent 1px),
                   linear-gradient(to bottom,#fff 1px,transparent 1px);
  background-size:90px 90px}}
.veil{{position:absolute;inset:0;background:
  radial-gradient(120% 90% at 50% 40%,transparent 30%,rgba(0,0,0,.55) 100%)}}
.content{{position:relative;display:flex;flex-direction:column;height:100%}}
.top{{display:flex;align-items:center;gap:14px;font-weight:800;font-size:34px;letter-spacing:-.5px}}
.top .mark{{font-size:38px}}
.accent{{background:linear-gradient(120deg,{c2},{c1});-webkit-background-clip:text;color:transparent}}
.mid{{flex:1;display:flex;flex-direction:column;justify-content:center;gap:26px}}
.kicker{{display:inline-flex;align-items:center;gap:12px;align-self:flex-start;
  background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.16);
  border-radius:999px;padding:12px 24px;font-size:26px;font-weight:600;color:#C8D0E6}}
h1{{font-size:{h1}px;line-height:1.12;font-weight:800;letter-spacing:-1.5px}}
h1 em{{font-style:normal;background:linear-gradient(120deg,{c2},{c1});
  -webkit-background-clip:text;color:transparent}}
p.sub{{font-size:32px;line-height:1.5;color:#AEB7CE;max-width:22ch}}
.bot{{display:flex;align-items:center;justify-content:space-between;
  font-size:26px;color:#8b93ab;font-weight:500}}
.pageno{{background:rgba(255,255,255,.09);border-radius:999px;padding:8px 20px}}
ul.list{{list-style:none;display:flex;flex-direction:column;gap:20px}}
ul.list li{{display:flex;align-items:flex-start;gap:16px;font-size:32px;line-height:1.4;color:#D7DDEC}}
ul.list li b{{flex:none;font-size:30px}}
.bad b{{color:#FB7185}} .good b{{color:#34D399}}
.tiles{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.tile{{border:1px solid rgba(255,255,255,.14);border-radius:26px;padding:28px 30px;
  background:rgba(255,255,255,.06)}}
.tile .ic{{font-size:42px;margin-bottom:12px}}
.tile h3{{font-size:31px;font-weight:700;margin-bottom:8px}}
.tile p{{font-size:24px;color:#A7B0C8;line-height:1.4}}
.demo{{display:flex;flex-wrap:wrap;align-items:center;gap:14px;
  border:1px solid rgba(255,255,255,.14);border-radius:24px;padding:28px;
  background:rgba(255,255,255,.06)}}
.chip{{background:rgba(255,255,255,.12);border-radius:14px;padding:12px 20px;
  font-size:30px;font-weight:700}}
.chip.out{{background:linear-gradient(120deg,{c1},{c2});color:#fff}}
.op{{font-size:28px;color:#8b93ab;font-weight:700}}
.cta{{display:inline-block;align-self:flex-start;
  background:linear-gradient(120deg,{c1},{c2});color:#fff;
  font-size:36px;font-weight:800;border-radius:999px;padding:26px 52px}}
</style></head><body>
<div class="blobs"><i class="b1"></i><i class="b2"></i></div>
<div class="grid"></div><div class="veil"></div>
<div class="content">
  <div class="top"><span class="mark">🎓</span><span>Student<span class="accent">OS</span></span></div>
  <div class="mid">{body}</div>
  <div class="bot"><span>{footer}</span>{page}</div>
</div>
</body></html>"""


def esc(s):
    return html.escape(s, quote=False)


def body_hook(d):
    return (f'<span class="kicker">{esc(d["kicker"])}</span>'
            f'<h1>{d["title"]}</h1>'
            f'<p class="sub">{esc(d["sub"])}</p>')


def body_list(d):
    items = "".join(
        f'<li><b>{"✕" if d.get("kind") == "bad" else "✓"}</b><span>{esc(x)}</span></li>'
        for x in d["items"])
    return (f'<h1>{d["title"]}</h1>'
            f'<ul class="list {d.get("kind","good")}">{items}</ul>')


def body_feature(d):
    demo = ""
    if d.get("demo"):
        # dir="auto" isolates each chip so Latin grades like "A−" keep their
        # order inside an RTL slide instead of flipping to "−A".
        parts = "".join(
            f'<span class="op">{esc(p[1:])}</span>' if p.startswith("~")
            else f'<span class="chip out" dir="auto">{esc(p[1:])}</span>' if p.startswith("!")
            else f'<span class="chip" dir="auto">{esc(p)}</span>'
            for p in d["demo"])
        demo = f'<div class="demo">{parts}</div>'
    return (f'<span class="kicker">{esc(d["kicker"])}</span>'
            f'<h1>{d["title"]}</h1>'
            f'<p class="sub">{esc(d["sub"])}</p>{demo}')


def body_tiles(d):
    tiles = "".join(
        f'<div class="tile"><div class="ic">{t[0]}</div>'
        f'<h3>{esc(t[1])}</h3><p>{esc(t[2])}</p></div>' for t in d["tiles"])
    return f'<h1>{d["title"]}</h1><div class="tiles">{tiles}</div>'


def body_cta(d):
    return (f'<h1>{d["title"]}</h1>'
            f'<p class="sub">{esc(d["sub"])}</p>'
            f'<span class="cta">{esc(d["cta"])}</span>')


BUILDERS = {"hook": body_hook, "list": body_list, "feature": body_feature,
            "tiles": body_tiles, "cta": body_cta}

# ── copy ───────────────────────────────────────────────────────────────
SLIDES = {
    "en": [
        dict(type="hook", theme="indigo", h1=88, kicker="Built for university students",
             title="Your entire student life,<br><em>finally</em> in one system.",
             sub="20 connected databases that run themselves."),
        dict(type="list", theme="rose", h1=70, kind="bad",
             title="Most student templates<br>break by week three.",
             items=["Lists that don't talk to each other",
                    "You calculate your own GPA",
                    "Deadlines live in three places",
                    "Unusable on a phone",
                    "Arrives empty, so you never start"]),
        dict(type="feature", theme="indigo", h1=76, kicker="No calculator",
             title="Your GPA<br><em>calculates itself</em>.",
             sub="Set a letter grade. Credits, points and semester GPA update automatically.",
             demo=["A−", "~×", "3 cr", "~+", "B+", "~×", "4 cr", "~=", "!GPA 3.47"]),
        dict(type="feature", theme="teal", h1=76, kicker="One source of truth",
             title="Everything links<br>to a <em>course</em>.",
             sub="Assignments, exams, notes, materials and projects all connect back. Open one course, see the whole picture."),
        dict(type="feature", theme="violet", h1=76, kicker="Phone-first",
             title="Actually works<br>on your <em>phone</em>.",
             sub="Three visible columns, title frozen. Not a 15-column table called mobile-friendly."),
        dict(type="tiles", theme="green", h1=64, title="What's inside",
             tiles=[("🎓", "Student Area", "Courses, exams, notes, agenda, tasks"),
                    ("💼", "Jobs Area", "Shifts, income, internship pipeline"),
                    ("💳", "Finance", "Income, expenses, real balance"),
                    ("🧬", "Personal", "Habits, journal, meals, books")]),
        dict(type="cta", theme="indigo", h1=80,
             title="Stop organising.<br><em>Start studying.</em>",
             sub="Set it up once. Use it all semester.",
             cta="Link in bio →"),
    ],
    "ar": [
        dict(type="hook", theme="indigo", h1=86, kicker="مصمَّم لطلاب الجامعات",
             title="حياتك الدراسية كاملة،<br>في نظام <em>واحد</em> أخيراً.",
             sub="٢٠ قاعدة بيانات مترابطة تدير نفسها."),
        dict(type="list", theme="rose", h1=66, kind="bad",
             title="معظم قوالب الطلاب<br>تنهار في الأسبوع الثالث.",
             items=["قوائم لا يتحدث بعضها إلى بعض",
                    "تحسب معدلك التراكمي بنفسك",
                    "المواعيد موزّعة في ثلاثة أماكن",
                    "غير صالح للاستخدام على الهاتف",
                    "يصلك فارغاً، فلا تبدأ أبداً"]),
        dict(type="feature", theme="indigo", h1=72, kicker="بلا آلة حاسبة",
             title="معدلك التراكمي<br><em>يحسب نفسه</em>.",
             sub="ضع تقدير الحرف، فتتحدّث الساعات والنقاط ومعدل الفصل تلقائياً.",
             demo=["A−", "~×", "٣ س", "~+", "B+", "~×", "٤ س", "~=", "!المعدل ٣٫٤٧"]),
        dict(type="feature", theme="teal", h1=72, kicker="مصدر واحد للحقيقة",
             title="كل شيء مرتبط<br>بـ<em>المادة</em>.",
             sub="الواجبات والاختبارات والملاحظات والمواد والمشاريع كلها مترابطة. افتح مادة واحدة، وشاهد الصورة كاملة."),
        dict(type="feature", theme="violet", h1=72, kicker="الهاتف أولاً",
             title="يعمل فعلاً<br>على <em>هاتفك</em>.",
             sub="ثلاثة أعمدة ظاهرة مع تثبيت العنوان. وليس جدولاً بخمسة عشر عموداً يُسمّى متوافقاً مع الهاتف."),
        dict(type="tiles", theme="green", h1=62, title="ماذا يوجد بالداخل",
             tiles=[("🎓", "المساحة الدراسية", "مواد، اختبارات، ملاحظات، أجندة، مهام"),
                    ("💼", "مساحة العمل", "ورديات، دخل، مسار التدريب"),
                    ("💳", "المالية", "دخل، مصروفات، رصيد حقيقي"),
                    ("🧬", "الشخصية", "عادات، يوميات، وجبات، كتب")]),
        dict(type="cta", theme="indigo", h1=76,
             title="توقّف عن الترتيب.<br><em>وابدأ الدراسة.</em>",
             sub="أعدّه مرة واحدة. واستخدمه الفصل كله.",
             cta="الرابط في البايو ←"),
    ],
}

FOOTER = {"en": "studentos", "ar": "studentos"}


def render(slide, lang, size, path, page_label=None):
    w, h = size
    c1, c2, bg = THEME[slide.get("theme", "indigo")]
    is_ar = lang == "ar"
    scale = h / 1080
    body = BUILDERS[slide["type"]](slide)
    page = f'<span class="pageno">{page_label}</span>' if page_label else ""
    doc = SHELL.format(
        lang=lang, dir="rtl" if is_ar else "ltr", w=w, h=h,
        pad=int(72 * (w / 1080)),
        font='"Liberation Sans","DejaVu Sans",sans-serif' if is_ar
             else '"Liberation Sans","DejaVu Sans",sans-serif',
        bg=bg, c1=c1, c2=c2,
        start="right" if is_ar else "left",
        end="left" if is_ar else "right",
        h1=int(slide.get("h1", 76) * scale),
        body=body, footer=FOOTER[lang], page=page,
    )
    src = path + ".html"
    with open(src, "w") as f:
        f.write(doc)
    subprocess.run([
        CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", f"--window-size={w},{h}",
        "--virtual-time-budget=3000", f"--screenshot={path}", f"file://{src}",
    ], check=True, capture_output=True, timeout=120)
    os.remove(src)
    return path


if __name__ == "__main__":
    made = 0
    for lang, slides in SLIDES.items():
        d = os.path.join(OUT, lang)
        os.makedirs(d, exist_ok=True)
        n = len(slides)
        for i, s in enumerate(slides, 1):
            p = os.path.join(d, f"{i:02d}-{s['type']}.png")
            render(s, lang, FEED, p, page_label=f"{i}/{n}")
            made += 1
        # One story from the hook slide.
        p = os.path.join(d, "story-hook.png")
        render(slides[0], lang, STORY, p)
        made += 1
    print(f"{made} images -> {OUT}")
