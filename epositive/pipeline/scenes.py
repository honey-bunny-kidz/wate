"""Render E Positive reel scenes (1080x1920 PNG) from a JSON script with Playwright/Chromium.
Usage: python3 scenes.py script.json outdir
Script JSON: {"scenes":[{"art":"<svg-name>","caption":"...","kicker":"..."}]}
"""
import json, sys, os
from playwright.sync_api import sync_playwright

TEAL, DEEP, SUN, CREAM = "#0F5257", "#0A3B3F", "#F4A623", "#FFF7E8"

ART = {
 "books": f"""<svg viewBox='0 0 600 520' width='760'>
  <circle cx='300' cy='230' r='210' fill='{SUN}' opacity='.18'/>
  <rect x='120' y='380' width='360' height='60' rx='10' fill='#E76F51'/>
  <rect x='140' y='320' width='330' height='60' rx='10' fill='{SUN}'/>
  <rect x='110' y='260' width='350' height='60' rx='10' fill='#2A9D8F'/>
  <rect x='150' y='200' width='310' height='60' rx='10' fill='{CREAM}'/>
  <rect x='130' y='140' width='340' height='60' rx='10' fill='#E9C46A'/>
  <text x='300' y='183' font-family='Poppins' font-weight='800' font-size='40' fill='{DEEP}' text-anchor='middle'>O/L 2026</text>
  <g fill='{CREAM}' opacity='.9'><circle cx='90' cy='120' r='8'/><circle cx='520' cy='90' r='6'/><circle cx='540' cy='300' r='5'/></g>
 </svg>""",
 "note_cant": f"""<svg viewBox='0 0 600 520' width='760'>
  <rect x='90' y='60' width='420' height='400' rx='18' fill='{CREAM}' transform='rotate(-3 300 260)'/>
  <g stroke='#9CC9C4' stroke-width='3'><line x1='120' y1='160' x2='480' y2='145'/><line x1='122' y1='230' x2='482' y2='215'/><line x1='124' y1='300' x2='484' y2='285'/><line x1='126' y1='370' x2='486' y2='355'/></g>
  <text x='300' y='262' font-family='Noto Sans Sinhala' font-weight='800' font-size='44' fill='#B23A48' text-anchor='middle' transform='rotate(-3 300 260)'>මට මේ විෂය බෑ</text>
 </svg>""",
 "note_yet": f"""<svg viewBox='0 0 600 520' width='760'>
  <circle cx='300' cy='260' r='250' fill='{SUN}' opacity='.16'/>
  <rect x='90' y='60' width='420' height='400' rx='18' fill='{CREAM}' transform='rotate(-3 300 260)'/>
  <g stroke='#9CC9C4' stroke-width='3'><line x1='120' y1='160' x2='480' y2='145'/><line x1='124' y1='300' x2='484' y2='285'/><line x1='126' y1='370' x2='486' y2='355'/></g>
  <g transform='rotate(-3 300 260)' font-family='Noto Sans Sinhala' font-weight='800' text-anchor='middle'>
   <text x='300' y='250' font-size='33' fill='{DEEP}'>මට මේ විෂය <tspan fill='#E07B00' font-size='44'>තාම</tspan> බෑ</text>
  </g>
  <path d='M330 210 l11 -26 l11 26' fill='none' stroke='#E07B00' stroke-width='6' stroke-linecap='round' transform='rotate(-3 300 260)'/>
 </svg>""",
 "plant": f"""<svg viewBox='0 0 600 520' width='760'>
  <circle cx='470' cy='110' r='70' fill='{SUN}'/>
  <g stroke='{SUN}' stroke-width='8' stroke-linecap='round' opacity='.8'><line x1='470' y1='15' x2='470' y2='0'/><line x1='565' y1='110' x2='590' y2='110'/><line x1='537' y1='43' x2='552' y2='28'/></g>
  <path d='M120 470 h360 l-30 -80 h-300 z' fill='#C9733F'/>
  <rect x='140' y='370' width='320' height='28' rx='8' fill='#A85A2E'/>
  <path d='M300 380 C300 300 300 230 300 150' stroke='#2E8B57' stroke-width='12' fill='none' stroke-linecap='round'/>
  <path d='M300 300 C240 290 200 250 190 200 C250 205 290 240 300 300z' fill='#3FAE6B'/>
  <path d='M300 240 C360 230 400 190 410 140 C350 145 310 180 300 240z' fill='#57C77F'/>
  <path d='M300 170 C270 150 260 120 265 90 C295 105 305 135 300 170z' fill='#7EDB98'/>
 </svg>""",
 "steps": f"""<svg viewBox='0 0 600 520' width='760'>
  <circle cx='500' cy='90' r='60' fill='{SUN}'/>
  <g fill='{CREAM}'><rect x='60' y='420' width='110' height='60' rx='6'/><rect x='170' y='360' width='110' height='120' rx='6'/><rect x='280' y='300' width='110' height='180' rx='6'/><rect x='390' y='240' width='110' height='240' rx='6'/></g>
  <g font-family='Poppins' font-weight='800' font-size='34' fill='{TEAL}' text-anchor='middle'><text x='115' y='462'>1</text><text x='225' y='402'>2</text><text x='335' y='342'>3</text><text x='445' y='282'>4</text></g>
  <path d='M430 200 l20 20 l40 -46' fill='none' stroke='{SUN}' stroke-width='12' stroke-linecap='round' stroke-linejoin='round'/>
 </svg>""",
 "endcard": f"""<svg viewBox='0 0 600 600' width='620'>
  <g stroke='{SUN}' stroke-width='14' stroke-linecap='round'><line x1='300' y1='40' x2='300' y2='80'/><line x1='300' y1='520' x2='300' y2='560'/><line x1='40' y1='300' x2='80' y2='300'/><line x1='520' y1='300' x2='560' y2='300'/><line x1='116' y1='116' x2='144' y2='144'/><line x1='456' y1='456' x2='484' y2='484'/><line x1='484' y1='116' x2='456' y2='144'/><line x1='144' y1='456' x2='116' y2='484'/></g>
  <circle cx='300' cy='300' r='190' fill='{SUN}'/>
  <text x='300' y='330' font-family='Poppins' font-weight='800' font-size='170' fill='{DEEP}' text-anchor='middle' letter-spacing='-6'>E<tspan fill='#fff'>+</tspan></text>
  <text x='300' y='400' font-family='Poppins' font-weight='700' font-size='34' fill='{DEEP}' text-anchor='middle' letter-spacing='7'>POSITIVE</text>
 </svg>""",
}

PAGE = """<!doctype html><html><head><meta charset='utf-8'><style>
body{{margin:0;width:1080px;height:1920px;overflow:hidden;font-family:'Noto Sans Sinhala',sans-serif;
background:radial-gradient(120% 70% at 50% 18%, #17707A 0%, {teal} 45%, {deep} 100%);}}
.top{{position:absolute;top:110px;left:0;right:0;text-align:center;font-family:Poppins;font-weight:700;letter-spacing:6px;color:{sun};font-size:34px}}
.art{{position:absolute;top:300px;left:0;right:0;display:flex;justify-content:center}}
.cap{{position:absolute;left:80px;right:80px;top:1180px;text-align:center;color:#fff;font-weight:800;font-size:{fs}px;line-height:1.45;text-shadow:0 4px 18px rgba(0,0,0,.35)}}
.cap b{{color:{sun}}}
.kick{{position:absolute;bottom:170px;left:0;right:0;text-align:center;color:{cream};opacity:.85;font-size:36px;font-weight:600}}
</style></head><body><div class='top'>E POSITIVE</div><div class='art'>{art}</div><div class='cap'>{cap}</div><div class='kick'>{kick}</div></body></html>"""


def main(script, outdir):
    os.makedirs(outdir, exist_ok=True)
    data = json.load(open(script))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for i, sc in enumerate(data["scenes"], 1):
            cap = sc["caption"]
            fs = 78 if len(cap) < 60 else 66
            html = PAGE.format(teal=TEAL, deep=DEEP, sun=SUN, cream=CREAM, art=ART[sc["art"]], cap=cap, kick=sc.get("kicker", ""), fs=fs)
            pg.set_content(html)
            pg.wait_for_timeout(300)
            pg.screenshot(path=f"{outdir}/s{i}.png")
        b.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
