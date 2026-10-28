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
 "rain_cloud": f"""<svg viewBox='0 0 600 520' width='760'>
  <g fill='#5B7C85'><circle cx='210' cy='200' r='85'/><circle cx='310' cy='160' r='110'/><circle cx='410' cy='210' r='80'/><rect x='130' y='200' width='360' height='90' rx='45'/></g>
  <g stroke='#5EC4E8' stroke-width='10' stroke-linecap='round'><line x1='180' y1='330' x2='160' y2='385'/><line x1='250' y1='330' x2='230' y2='385'/><line x1='320' y1='330' x2='300' y2='385'/><line x1='390' y1='330' x2='370' y2='385'/><line x1='215' y1='410' x2='195' y2='465'/><line x1='285' y1='410' x2='265' y2='465'/><line x1='355' y1='410' x2='335' y2='465'/><line x1='425' y1='410' x2='405' y2='465'/></g>
  <text x='300' y='215' font-family='Poppins' font-weight='800' font-size='90' fill='{CREAM}' text-anchor='middle'>?</text>
 </svg>""",
 "paddy": f"""<svg viewBox='0 0 600 520' width='760'>
  <g fill='#E8F1F5' opacity='.95'><circle cx='200' cy='110' r='55'/><circle cx='270' cy='90' r='70'/><circle cx='340' cy='115' r='50'/><rect x='150' y='110' width='240' height='50' rx='25'/></g>
  <g stroke='#5EC4E8' stroke-width='7' stroke-linecap='round'><line x1='190' y1='185' x2='180' y2='215'/><line x1='250' y1='185' x2='240' y2='215'/><line x1='310' y1='185' x2='300' y2='215'/><line x1='370' y1='185' x2='360' y2='215'/></g>
  <rect x='40' y='400' width='520' height='90' rx='14' fill='#3E8E9A' opacity='.6'/>
  <g stroke='#7EDB98' stroke-width='7' stroke-linecap='round' fill='none'>
   <path d='M90 420 q-10 -70 -30 -110'/><path d='M90 420 q10 -80 30 -120'/><path d='M170 420 q-10 -70 -30 -110'/><path d='M170 420 q10 -80 30 -120'/>
   <path d='M250 420 q-10 -70 -30 -110'/><path d='M250 420 q10 -80 30 -120'/><path d='M330 420 q-10 -70 -30 -110'/><path d='M330 420 q10 -80 30 -120'/>
   <path d='M410 420 q-10 -70 -30 -110'/><path d='M410 420 q10 -80 30 -120'/><path d='M490 420 q-10 -70 -30 -110'/><path d='M490 420 q10 -80 30 -120'/></g>
  <g fill='{SUN}'><circle cx='120' cy='300' r='9'/><circle cx='280' cy='300' r='9'/><circle cx='440' cy='300' r='9'/><circle cx='200' cy='305' r='8'/><circle cx='360' cy='305' r='8'/><circle cx='520' cy='305' r='8'/></g>
 </svg>""",
 "glasses": f"""<svg viewBox='0 0 600 520' width='760'>
  <circle cx='300' cy='260' r='230' fill='{SUN}' opacity='.14'/>
  <circle cx='190' cy='270' r='105' fill='#5B7C85'/><circle cx='410' cy='270' r='105' fill='{SUN}'/>
  <g stroke='#5EC4E8' stroke-width='8' stroke-linecap='round'><line x1='160' y1='230' x2='150' y2='255'/><line x1='200' y1='250' x2='190' y2='275'/><line x1='175' y1='295' x2='165' y2='320'/><line x1='225' y1='300' x2='215' y2='325'/></g>
  <circle cx='410' cy='270' r='40' fill='#FFF3C4'/>
  <g stroke='{CREAM}' stroke-width='16' fill='none'><circle cx='190' cy='270' r='105'/><circle cx='410' cy='270' r='105'/><path d='M295 260 q15 -22 30 0'/><line x1='85' y1='250' x2='40' y2='225'/><line x1='515' y1='250' x2='560' y2='225'/></g>
 </svg>""",
 "bulb": f"""<svg viewBox='0 0 600 520' width='760'>
  <circle cx='300' cy='220' r='210' fill='{SUN}' opacity='.16'/>
  <g stroke='{SUN}' stroke-width='12' stroke-linecap='round'><line x1='300' y1='20' x2='300' y2='60'/><line x1='140' y1='90' x2='168' y2='118'/><line x1='460' y1='90' x2='432' y2='118'/><line x1='90' y1='240' x2='130' y2='240'/><line x1='510' y1='240' x2='470' y2='240'/></g>
  <path d='M300 100 C210 100 170 170 180 230 C190 290 240 310 245 360 h110 C360 310 410 290 420 230 C430 170 390 100 300 100z' fill='#FFC857'/>
  <rect x='245' y='370' width='110' height='26' rx='8' fill='{CREAM}'/><rect x='255' y='402' width='90' height='26' rx='8' fill='{CREAM}'/><rect x='275' y='434' width='50' height='20' rx='8' fill='{CREAM}'/>
  <text x='300' y='280' font-family='Poppins' font-weight='800' font-size='120' fill='{DEEP}' text-anchor='middle'>?</text>
 </svg>""",
 "rain_sun": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='390' cy='170' r='90' fill='{SUN}'/>
  <g fill='#E8F1F5'><circle cx='230' cy='220' r='70'/><circle cx='310' cy='200' r='85'/><circle cx='390' cy='240' r='60'/><rect x='170' y='220' width='280' height='70' rx='35'/></g>
  <g stroke='#5EC4E8' stroke-width='9' stroke-linecap='round'><line x1='210' y1='320' x2='195' y2='360'/><line x1='270' y1='320' x2='255' y2='360'/><line x1='330' y1='320' x2='315' y2='360'/><line x1='390' y1='320' x2='375' y2='360'/></g>
  <path d='M120 470 a180 180 0 0 1 360 0' fill='none' stroke='#E76F51' stroke-width='14'/><path d='M140 470 a160 160 0 0 1 320 0' fill='none' stroke='{SUN}' stroke-width='14'/><path d='M160 470 a140 140 0 0 1 280 0' fill='none' stroke='#3FAE6B' stroke-width='14'/></svg>""",
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
            if i == 1 and len(cap) < 40:
                fs = 104  # scene-1 hook: big enough to read in under 2 s
            html = PAGE.format(teal=TEAL, deep=DEEP, sun=SUN, cream=CREAM, art=ART[sc["art"]], cap=cap, kick=sc.get("kicker", ""), fs=fs)
            pg.set_content(html)
            pg.wait_for_timeout(300)
            pg.screenshot(path=f"{outdir}/s{i}.png")
        b.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
