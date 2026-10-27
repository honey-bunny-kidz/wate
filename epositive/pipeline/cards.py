"""E Positive post images: single quote cards and carousel slides, 1080x1350 (4:5), rendered with Chromium.
Usage: python3 cards.py post.json outdir
post.json: {"theme": "teal|sunrise|night|mint|rose",
            "slides": [{"kind":"cover|tip|cta", "art":"<name>", "kicker":"...", "title":"... <b>hl</b> ...", "body":"...", "num":"1"}]}
One slide = a single image post; 3-6 slides = a carousel (album) post.
"""
import json, sys, os
from playwright.sync_api import sync_playwright
from scenes import ART as REEL_ART

THEMES = {
    "teal":    dict(bg="radial-gradient(120% 80% at 50% 15%, #17707A 0%, #0F5257 50%, #0A3B3F 100%)", ink="#FFFFFF", hl="#F4A623", sub="#D6ECE9", chip="#F4A623", chipink="#0A3B3F"),
    "sunrise": dict(bg="linear-gradient(170deg, #FFE3C2 0%, #FFC48C 45%, #F28C6B 100%)", ink="#3A1F14", hl="#B23A48", sub="#5C3326", chip="#3A1F14", chipink="#FFE3C2"),
    "night":   dict(bg="radial-gradient(120% 80% at 50% 10%, #2B3A67 0%, #1B2445 55%, #10162B 100%)", ink="#FFFFFF", hl="#FFC857", sub="#C9D3F2", chip="#FFC857", chipink="#1B2445"),
    "mint":    dict(bg="linear-gradient(170deg, #E8F7EF 0%, #C6EBD6 55%, #9FD9BB 100%)", ink="#123B2B", hl="#0F7B55", sub="#2E5A47", chip="#123B2B", chipink="#E8F7EF"),
    "rose":    dict(bg="linear-gradient(170deg, #FFF1F3 0%, #FFD3DB 55%, #F7A8B8 100%)", ink="#4A1626", hl="#C2185B", sub="#6B2A3C", chip="#4A1626", chipink="#FFF1F3"),
}

S, C = "#F4A623", "#FFF7E8"
ART = dict(REEL_ART)
ART.update({
 "drops": f"""<svg viewBox='0 0 600 520'><path d='M300 40 C260 110 230 150 230 190 a70 70 0 0 0 140 0 C370 150 340 110 300 40z' fill='#5EC4E8'/>
  <path d='M170 300 h260 l-25 190 h-210 z' fill='{C}' opacity='.95'/><rect x='170' y='380' width='260' height='12' fill='#5EC4E8' opacity='.5'/>
  <path d='M182 395 h236 l-14 95 h-208 z' fill='#5EC4E8' opacity='.85'/><circle cx='300' cy='250' r='9' fill='#5EC4E8'/></svg>""",
 "sunrise": f"""<svg viewBox='0 0 600 520'><circle cx='300' cy='330' r='150' fill='{S}'/>
  <g stroke='{S}' stroke-width='14' stroke-linecap='round'><line x1='300' y1='120' x2='300' y2='80'/><line x1='150' y1='190' x2='122' y2='162'/><line x1='450' y1='190' x2='478' y2='162'/><line x1='90' y1='330' x2='50' y2='330'/><line x1='510' y1='330' x2='550' y2='330'/></g>
  <rect x='0' y='330' width='600' height='190' fill='#0F5257' opacity='.55'/><path d='M0 400 Q150 360 300 400 T600 400 V520 H0z' fill='#0A3B3F' opacity='.7'/></svg>""",
 "heart": f"""<svg viewBox='0 0 600 520'><circle cx='300' cy='260' r='230' fill='{S}' opacity='.15'/>
  <path d='M300 430 C120 320 110 190 190 150 C240 125 285 155 300 190 C315 155 360 125 410 150 C490 190 480 320 300 430z' fill='#E76F51'/>
  <path d='M230 200 q20 -25 45 -10' stroke='#fff' stroke-width='10' fill='none' stroke-linecap='round' opacity='.7'/></svg>""",
 "phone_off": f"""<svg viewBox='0 0 600 520'><rect x='210' y='60' width='180' height='340' rx='30' fill='#2B2D42'/><rect x='225' y='90' width='150' height='270' rx='10' fill='#4A4E69'/>
  <circle cx='300' cy='225' r='60' fill='none' stroke='#E76F51' stroke-width='14'/><line x1='258' y1='267' x2='342' y2='183' stroke='#E76F51' stroke-width='14' stroke-linecap='round'/>
  <circle cx='460' cy='120' r='45' fill='{S}'/><path d='M80 470 q60 -80 120 0' fill='#3FAE6B'/><path d='M400 470 q60 -90 130 0' fill='#57C77F'/></svg>""",
 "rain_sun": f"""<svg viewBox='0 0 600 520'><circle cx='390' cy='170' r='90' fill='{S}'/>
  <g fill='#E8F1F5'><circle cx='230' cy='220' r='70'/><circle cx='310' cy='200' r='85'/><circle cx='390' cy='240' r='60'/><rect x='170' y='220' width='280' height='70' rx='35'/></g>
  <g stroke='#5EC4E8' stroke-width='9' stroke-linecap='round'><line x1='210' y1='320' x2='195' y2='360'/><line x1='270' y1='320' x2='255' y2='360'/><line x1='330' y1='320' x2='315' y2='360'/><line x1='390' y1='320' x2='375' y2='360'/></g>
  <path d='M120 470 a180 180 0 0 1 360 0' fill='none' stroke='#E76F51' stroke-width='14'/><path d='M140 470 a160 160 0 0 1 320 0' fill='none' stroke='{S}' stroke-width='14'/><path d='M160 470 a140 140 0 0 1 280 0' fill='none' stroke='#3FAE6B' stroke-width='14'/></svg>""",
 "lamp": f"""<svg viewBox='0 0 600 520'><circle cx='300' cy='250' r='200' fill='{S}' opacity='.18'/>
  <path d='M300 120 C270 170 270 210 300 230 C330 210 330 170 300 120z' fill='#FFC857'/><path d='M300 160 C288 185 290 205 300 215 C310 205 312 185 300 160z' fill='#fff'/>
  <path d='M170 260 h260 C420 340 360 380 300 380 C240 380 180 340 170 260z' fill='#C9733F'/><rect x='250' y='380' width='100' height='30' rx='8' fill='#A85A2E'/></svg>""",
 "javelin": f"""<svg viewBox='0 0 600 520'><circle cx='300' cy='260' r='220' fill='{S}' opacity='.15'/>
  <line x1='90' y1='420' x2='520' y2='110' stroke='{C}' stroke-width='12' stroke-linecap='round'/><path d='M520 110 l-40 12 l18 18z' fill='{C}'/>
  <circle cx='300' cy='400' r='55' fill='{S}'/><text x='300' y='420' font-family='Poppins' font-weight='800' font-size='54' fill='#0A3B3F' text-anchor='middle'>1</text></svg>""",
 "jar": f"""<svg viewBox='0 0 600 520'><rect x='190' y='120' width='220' height='40' rx='10' fill='#A85A2E'/>
  <path d='M180 170 h240 v230 a40 40 0 0 1 -40 40 h-160 a40 40 0 0 1 -40 -40z' fill='{C}' opacity='.9'/>
  <g fill='{S}' stroke='#C98A1A' stroke-width='4'><ellipse cx='260' cy='400' rx='45' ry='16'/><ellipse cx='340' cy='400' rx='45' ry='16'/><ellipse cx='300' cy='378' rx='45' ry='16'/><ellipse cx='265' cy='356' rx='45' ry='16'/><ellipse cx='335' cy='340' rx='45' ry='16'/></g>
  <path d='M300 40 l10 30 l30 0 l-24 18 l9 30 l-25 -18 l-25 18 l9 -30 l-24 -18 l30 0z' fill='{S}'/></svg>""",
})

PAGE = """<!doctype html><html><head><meta charset='utf-8'><style>
*{{box-sizing:border-box}}
body{{margin:0;width:1080px;height:1350px;overflow:hidden;font-family:'Noto Sans Sinhala','Poppins',sans-serif;background:{bg};color:{ink};position:relative}}
.brand{{position:absolute;top:56px;left:70px;display:flex;align-items:center;gap:14px;font-family:Poppins;font-weight:700;letter-spacing:5px;font-size:28px}}
.brand i{{font-style:normal;width:58px;height:58px;border-radius:50%;background:#F4A623;color:#0A3B3F;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:28px;letter-spacing:-1px}}
.count{{position:absolute;top:62px;right:70px;font-family:Poppins;font-weight:700;font-size:28px;opacity:.75}}
.art{{position:absolute;left:0;right:0;display:flex;justify-content:center}}
.art svg{{width:{artw}px;height:auto}}
.kick{{display:inline-block;background:{chip};color:{chipink};font-weight:700;font-size:30px;padding:10px 26px;border-radius:40px;margin-bottom:26px}}
.txt{{position:absolute;left:80px;right:80px;text-align:center}}
h1{{margin:0;font-weight:800;font-size:{tfs}px;line-height:1.38}}
h1 b{{color:{hl}}}
.body{{margin-top:30px;font-size:40px;line-height:1.55;color:{sub};font-weight:500}}
.num{{font-family:Poppins;font-weight:800;font-size:170px;line-height:1;color:{hl};margin-bottom:6px}}
.foot{{position:absolute;bottom:52px;left:0;right:0;text-align:center;font-size:29px;font-weight:600;color:{sub}}}
.swipe{{position:absolute;bottom:52px;right:70px;font-family:Poppins;font-weight:700;font-size:30px;color:{hl}}}
</style></head><body>
<div class='brand'><i>E+</i>E POSITIVE</div>{count}
{art}
<div class='txt' style='top:{ttop}px;{center}'>{num}{kick}<h1>{title}</h1>{body}</div>
{foot}
</body></html>"""


def render(post, outdir):
    os.makedirs(outdir, exist_ok=True)
    th = THEMES[post.get("theme", "teal")]
    slides = post["slides"]
    n = len(slides)
    paths = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, 1):
            kind = s.get("kind", "cover")
            has_art = bool(s.get("art"))
            title = s.get("title", "")
            L = len(title.replace("<b>", "").replace("</b>", "").replace("<br>", ""))
            tfs = 76 if L < 40 else 66 if L < 70 else 56
            center = ""
            if kind == "tip":
                art_html = f"<div class='art' style='top:170px'>{ART[s['art']]}</div>" if has_art else ""
                artw, ttop = 520, (650 if has_art else 0)
                if not has_art:
                    center = "bottom:120px;display:flex;flex-direction:column;justify-content:center;align-items:center"
                    tfs += 8
            elif kind == "cta":
                art_html = f"<div class='art' style='top:170px'>{ART[s['art']]}</div>" if has_art else ""
                artw, ttop = 430, (690 if has_art else 0)
                if not has_art:
                    center = "bottom:120px;display:flex;flex-direction:column;justify-content:center;align-items:center"
            else:
                art_html = f"<div class='art' style='top:150px'>{ART[s['art']]}</div>" if has_art else ""
                artw, ttop = 640, (700 if has_art else 360)
            if kind == "cta":
                foot = "<div class='foot'>ඔබේ යාළුවෙක්ට <b>share</b> කරන්න · E Positive follow කරන්න</div>"
            elif n > 1 and i < n:
                foot = "<div class='swipe'>Swipe →</div>"
            else:
                foot = "<div class='foot'>ඔබේ යාළුවෙක්ට share කරන්න · E Positive</div>"
            html = PAGE.format(
                **th, artw=artw, tfs=tfs, center=center, ttop=ttop, art=art_html, title=title,
                kick=f"<div class='kick'>{s['kicker']}</div><br>" if s.get("kicker") else "",
                num=f"<div class='num'>{s['num']}</div>" if s.get("num") else "",
                body=f"<div class='body'>{s['body']}</div>" if s.get("body") else "",
                count=f"<div class='count'>{i}/{n}</div>" if n > 1 else "", foot=foot)
            pg.set_content(html)
            pg.wait_for_timeout(250)
            path = f"{outdir}/slide{i}.jpg"
            pg.screenshot(path=path, type="jpeg", quality=90)
            paths.append(path)
        b.close()
    return paths


if __name__ == "__main__":
    print("\n".join(render(json.load(open(sys.argv[1])), sys.argv[2])))
