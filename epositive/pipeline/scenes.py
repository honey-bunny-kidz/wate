"""Render E Positive reel scenes (1080x1920 PNG, 9:16) from a JSON script with Playwright/Chromium.
Usage: python3 scenes.py script.json outdir
Script JSON: {"voice":"line 1 ... line 2 ...", "scenes":[{"art":"<svg-name>","caption":"...","kicker":"..."}]}
Mobile safe zones: nothing below y=1536 (bottom 20%: Reels/Shorts buttons and caption) and nothing in the
right 15% beside the text block (like/share buttons). Closed captions are added later by build.py at y~1290-1500.
"""
import json, sys, os
from playwright.sync_api import sync_playwright

TEAL, DEEP, SUN, CREAM = "#0F5257", "#0A3B3F", "#F4A623", "#FFF7E8"

ART = {
 "lamp_one": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='240' fill='{SUN}' opacity='.12'/><circle cx='200' cy='290.0' r='95.0' fill='{SUN}' opacity='.22'/><path d='M200 210.0 C172.0 255.0 174.0 290.0 200 308.0 C226.0 290.0 228.0 255.0 200 210.0z' fill='#FFC857'/><path d='M200 245.0 C189.0 268.0 191.0 288.0 200 297.0 C209.0 288.0 211.0 268.0 200 245.0z' fill='#fff'/><path d='M90.0 315.0 h220.0 C300.0 385.0 250.0 410.0 200 410.0 C150.0 410.0 100.0 385.0 90.0 315.0z' fill='#C9733F'/><rect x='160.0' y='408.0' width='80.0' height='24.0' rx='7.0' fill='#A85A2E'/><line x1='420' y1='310.0' x2='420' y2='292.0' stroke='#3a2a20' stroke-width='5.0' stroke-linecap='round'/><path d='M310.0 315.0 h220.0 C520.0 385.0 470.0 410.0 420 410.0 C370.0 410.0 320.0 385.0 310.0 315.0z' fill='#C9733F'/><rect x='380.0' y='408.0' width='80.0' height='24.0' rx='7.0' fill='#A85A2E'/><text x='310' y='160' font-family='Poppins' font-weight='800' font-size='90' fill='{CREAM}' text-anchor='middle'>?</text></svg>""",
 "lamps_two": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='250' fill='{SUN}' opacity='.20'/><circle cx='200' cy='290.0' r='95.0' fill='{SUN}' opacity='.22'/><path d='M200 210.0 C172.0 255.0 174.0 290.0 200 308.0 C226.0 290.0 228.0 255.0 200 210.0z' fill='#FFC857'/><path d='M200 245.0 C189.0 268.0 191.0 288.0 200 297.0 C209.0 288.0 211.0 268.0 200 245.0z' fill='#fff'/><path d='M90.0 315.0 h220.0 C300.0 385.0 250.0 410.0 200 410.0 C150.0 410.0 100.0 385.0 90.0 315.0z' fill='#C9733F'/><rect x='160.0' y='408.0' width='80.0' height='24.0' rx='7.0' fill='#A85A2E'/><circle cx='410' cy='290.0' r='95.0' fill='{SUN}' opacity='.22'/><path d='M410 210.0 C382.0 255.0 384.0 290.0 410 308.0 C436.0 290.0 438.0 255.0 410 210.0z' fill='#FFC857'/><path d='M410 245.0 C399.0 268.0 401.0 288.0 410 297.0 C419.0 288.0 421.0 268.0 410 245.0z' fill='#fff'/><path d='M300.0 315.0 h220.0 C510.0 385.0 460.0 410.0 410 410.0 C360.0 410.0 310.0 385.0 300.0 315.0z' fill='#C9733F'/><rect x='370.0' y='408.0' width='80.0' height='24.0' rx='7.0' fill='#A85A2E'/><g fill='{CREAM}' opacity='.9'><circle cx='80' cy='110' r='7'/><circle cx='530' cy='90' r='6'/><circle cx='300' cy='60' r='5'/></g></svg>""",
 "lamps_row": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='250' fill='{SUN}' opacity='.14'/><circle cx='90' cy='228.0' r='52.25000000000001' fill='{SUN}' opacity='.22'/><path d='M90 184.0 C74.6 208.75 75.7 228.0 90 237.9 C104.3 228.0 105.4 208.75 90 184.0z' fill='#FFC857'/><path d='M90 203.25 C83.95 215.9 85.05 226.9 90 231.85 C94.95 226.9 96.05 215.9 90 203.25z' fill='#fff'/><path d='M29.499999999999993 241.75 h121.00000000000001 C145.0 280.25 117.5 294.0 90 294.0 C62.5 294.0 34.99999999999999 280.25 29.499999999999993 241.75z' fill='#C9733F'/><rect x='68.0' y='292.9' width='44.0' height='13.200000000000001' rx='3.8500000000000005' fill='#A85A2E'/><circle cx='195' cy='248.0' r='52.25000000000001' fill='{SUN}' opacity='.22'/><path d='M195 204.0 C179.6 228.75 180.7 248.0 195 257.9 C209.3 248.0 210.4 228.75 195 204.0z' fill='#FFC857'/><path d='M195 223.25 C188.95 235.9 190.05 246.9 195 251.85 C199.95 246.9 201.05 235.9 195 223.25z' fill='#fff'/><path d='M134.5 261.75 h121.00000000000001 C250.0 300.25 222.5 314.0 195 314.0 C167.5 314.0 140.0 300.25 134.5 261.75z' fill='#C9733F'/><rect x='173.0' y='312.9' width='44.0' height='13.200000000000001' rx='3.8500000000000005' fill='#A85A2E'/><circle cx='300' cy='228.0' r='52.25000000000001' fill='{SUN}' opacity='.22'/><path d='M300 184.0 C284.6 208.75 285.7 228.0 300 237.9 C314.3 228.0 315.4 208.75 300 184.0z' fill='#FFC857'/><path d='M300 203.25 C293.95 215.9 295.05 226.9 300 231.85 C304.95 226.9 306.05 215.9 300 203.25z' fill='#fff'/><path d='M239.5 241.75 h121.00000000000001 C355.0 280.25 327.5 294.0 300 294.0 C272.5 294.0 245.0 280.25 239.5 241.75z' fill='#C9733F'/><rect x='278.0' y='292.9' width='44.0' height='13.200000000000001' rx='3.8500000000000005' fill='#A85A2E'/><circle cx='405' cy='248.0' r='52.25000000000001' fill='{SUN}' opacity='.22'/><path d='M405 204.0 C389.6 228.75 390.7 248.0 405 257.9 C419.3 248.0 420.4 228.75 405 204.0z' fill='#FFC857'/><path d='M405 223.25 C398.95 235.9 400.05 246.9 405 251.85 C409.95 246.9 411.05 235.9 405 223.25z' fill='#fff'/><path d='M344.5 261.75 h121.00000000000001 C460.0 300.25 432.5 314.0 405 314.0 C377.5 314.0 350.0 300.25 344.5 261.75z' fill='#C9733F'/><rect x='383.0' y='312.9' width='44.0' height='13.200000000000001' rx='3.8500000000000005' fill='#A85A2E'/><circle cx='510' cy='228.0' r='52.25000000000001' fill='{SUN}' opacity='.22'/><path d='M510 184.0 C494.6 208.75 495.7 228.0 510 237.9 C524.3 228.0 525.4 208.75 510 184.0z' fill='#FFC857'/><path d='M510 203.25 C503.95 215.9 505.05 226.9 510 231.85 C514.95 226.9 516.05 215.9 510 203.25z' fill='#fff'/><path d='M449.5 241.75 h121.00000000000001 C565.0 280.25 537.5 294.0 510 294.0 C482.5 294.0 455.0 280.25 449.5 241.75z' fill='#C9733F'/><rect x='488.0' y='292.9' width='44.0' height='13.200000000000001' rx='3.8500000000000005' fill='#A85A2E'/><circle cx='140' cy='398.0' r='52.25000000000001' fill='{SUN}' opacity='.22'/><path d='M140 354.0 C124.6 378.75 125.7 398.0 140 407.9 C154.3 398.0 155.4 378.75 140 354.0z' fill='#FFC857'/><path d='M140 373.25 C133.95 385.9 135.05 396.9 140 401.85 C144.95 396.9 146.05 385.9 140 373.25z' fill='#fff'/><path d='M79.5 411.75 h121.00000000000001 C195.0 450.25 167.5 464.0 140 464.0 C112.5 464.0 85.0 450.25 79.5 411.75z' fill='#C9733F'/><rect x='118.0' y='462.9' width='44.0' height='13.200000000000001' rx='3.8500000000000005' fill='#A85A2E'/><circle cx='250' cy='398.0' r='52.25000000000001' fill='{SUN}' opacity='.22'/><path d='M250 354.0 C234.6 378.75 235.7 398.0 250 407.9 C264.3 398.0 265.4 378.75 250 354.0z' fill='#FFC857'/><path d='M250 373.25 C243.95 385.9 245.05 396.9 250 401.85 C254.95 396.9 256.05 385.9 250 373.25z' fill='#fff'/><path d='M189.5 411.75 h121.00000000000001 C305.0 450.25 277.5 464.0 250 464.0 C222.5 464.0 195.0 450.25 189.5 411.75z' fill='#C9733F'/><rect x='228.0' y='462.9' width='44.0' height='13.200000000000001' rx='3.8500000000000005' fill='#A85A2E'/><circle cx='355' cy='398.0' r='52.25000000000001' fill='{SUN}' opacity='.22'/><path d='M355 354.0 C339.6 378.75 340.7 398.0 355 407.9 C369.3 398.0 370.4 378.75 355 354.0z' fill='#FFC857'/><path d='M355 373.25 C348.95 385.9 350.05 396.9 355 401.85 C359.95 396.9 361.05 385.9 355 373.25z' fill='#fff'/><path d='M294.5 411.75 h121.00000000000001 C410.0 450.25 382.5 464.0 355 464.0 C327.5 464.0 300.0 450.25 294.5 411.75z' fill='#C9733F'/><rect x='333.0' y='462.9' width='44.0' height='13.200000000000001' rx='3.8500000000000005' fill='#A85A2E'/><circle cx='460' cy='398.0' r='52.25000000000001' fill='{SUN}' opacity='.22'/><path d='M460 354.0 C444.6 378.75 445.7 398.0 460 407.9 C474.3 398.0 475.4 378.75 460 354.0z' fill='#FFC857'/><path d='M460 373.25 C453.95 385.9 455.05 396.9 460 401.85 C464.95 396.9 466.05 385.9 460 373.25z' fill='#fff'/><path d='M399.5 411.75 h121.00000000000001 C515.0 450.25 487.5 464.0 460 464.0 C432.5 464.0 405.0 450.25 399.5 411.75z' fill='#C9733F'/><rect x='438.0' y='462.9' width='44.0' height='13.200000000000001' rx='3.8500000000000005' fill='#A85A2E'/></svg>""",
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
 "trees": f"""<svg viewBox='0 0 600 520' width='760'>
  <circle cx='300' cy='250' r='230' fill='{SUN}' opacity='.12'/>
  <rect x='40' y='470' width='520' height='14' rx='7' fill='#2E8B57'/>
  <rect x='130' y='250' width='26' height='222' rx='10' fill='#8DB85A'/>
  <path d='M143 255 C90 230 60 190 55 140 C105 165 135 205 143 255z' fill='#3FAE6B'/>
  <path d='M143 255 C200 225 225 180 225 130 C180 160 150 205 143 255z' fill='#57C77F'/>
  <path d='M143 250 C130 200 140 150 160 110 C170 160 160 210 143 250z' fill='#7EDB98'/>
  <g fill='#F4D35E'><ellipse cx='170' cy='300' rx='9' ry='26' transform='rotate(-25 170 300)'/><ellipse cx='186' cy='306' rx='9' ry='26' transform='rotate(-15 186 306)'/><ellipse cx='155' cy='306' rx='9' ry='26' transform='rotate(-35 155 306)'/></g>
  <rect x='410' y='300' width='34' height='172' rx='12' fill='#8B5A2B'/>
  <path d='M427 330 L380 280 M427 320 L470 270' stroke='#8B5A2B' stroke-width='14' stroke-linecap='round'/>
  <circle cx='427' cy='200' r='118' fill='#2E8B57'/><circle cx='360' cy='240' r='70' fill='#3FAE6B'/><circle cx='495' cy='235' r='72' fill='#3FAE6B'/><circle cx='430' cy='130' r='70' fill='#57C77F'/>
  <g fill='{SUN}'><ellipse cx='380' cy='250' rx='16' ry='22'/><ellipse cx='470' cy='265' rx='16' ry='22'/><ellipse cx='430' cy='180' rx='16' ry='22'/><ellipse cx='505' cy='200' rx='16' ry='22'/></g>
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
 "frog": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='270' r='220' fill='{SUN}' opacity='.15'/>
  <ellipse cx='300' cy='330' rx='190' ry='130' fill='#3FAE6B'/><ellipse cx='300' cy='370' rx='120' ry='70' fill='#9BE0B0'/>
  <circle cx='215' cy='200' r='62' fill='#3FAE6B'/><circle cx='385' cy='200' r='62' fill='#3FAE6B'/>
  <circle cx='215' cy='195' r='38' fill='#fff'/><circle cx='385' cy='195' r='38' fill='#fff'/><circle cx='222' cy='200' r='18' fill='#1B2445'/><circle cx='378' cy='200' r='18' fill='#1B2445'/>
  <path d='M230 300 q70 50 140 0' stroke='#1B5E3A' stroke-width='12' fill='none' stroke-linecap='round'/>
  <circle cx='190' cy='300' r='14' fill='#F7A8B8'/><circle cx='410' cy='300' r='14' fill='#F7A8B8'/>
  <ellipse cx='150' cy='450' rx='70' ry='24' fill='#2E8A55'/><ellipse cx='450' cy='450' rx='70' ry='24' fill='#2E8A55'/></svg>""",
 "trophy": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='250' r='220' fill='{SUN}' opacity='.15'/>
  <path d='M200 90 h200 v90 a100 100 0 0 1 -200 0z' fill='{SUN}'/><path d='M200 110 h-55 a50 50 0 0 0 55 80' fill='none' stroke='{SUN}' stroke-width='16'/><path d='M400 110 h55 a50 50 0 0 1 -55 80' fill='none' stroke='{SUN}' stroke-width='16'/>
  <rect x='280' y='275' width='40' height='70' fill='#C98A1A'/><rect x='220' y='345' width='160' height='34' rx='8' fill='#C98A1A'/>
  <g fill='{CREAM}'><rect x='120' y='440' width='60' height='40' rx='6'/><rect x='200' y='415' width='60' height='65' rx='6'/><rect x='280' y='390' width='60' height='90' rx='6' opacity='0'/><rect x='360' y='415' width='60' height='65' rx='6'/><rect x='440' y='440' width='60' height='40' rx='6'/></g>
  <path d='M300 125 l10 25 l27 2 l-21 17 l7 26 l-23 -14 l-23 14 l7 -26 l-21 -17 l27 -2z' fill='#fff'/></svg>""",
 "coconut": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.15'/><ellipse cx='300' cy='270' rx='150' ry='180' fill='#7A4A26'/><ellipse cx='300' cy='270' rx='150' ry='180' fill='none' stroke='#5C3418' stroke-width='5' stroke-dasharray='22 16' opacity='.7'/><g fill='#3B2210'><circle cx='272' cy='150' r='12'/><circle cx='328' cy='150' r='12'/><circle cx='300' cy='185' r='12'/></g><text x='470' y='130' font-family='Poppins' font-weight='800' font-size='90' fill='{CREAM}' text-anchor='middle'>?</text><ellipse cx='300' cy='455' rx='170' ry='16' fill='#000' opacity='.18'/></svg>""",
 "coconut_hits": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.15'/><ellipse cx='270' cy='280' rx='140' ry='170' fill='#7A4A26'/><ellipse cx='270' cy='280' rx='140' ry='170' fill='none' stroke='#5C3418' stroke-width='5' stroke-dasharray='22 16' opacity='.7'/><g fill='#3B2210'><circle cx='242' cy='170' r='12'/><circle cx='298' cy='170' r='12'/><circle cx='270' cy='205' r='12'/></g><g transform='rotate(-30 470 150)'><rect x='455' y='120' width='26' height='170' rx='8' fill='#A0703C'/><rect x='420' y='80' width='96' height='56' rx='12' fill='#6C757D'/></g><g stroke='{CREAM}' stroke-width='9' stroke-linecap='round'><line x1='60' y1='120' x2='60' y2='190'/><line x1='85' y1='120' x2='85' y2='190'/><line x1='110' y1='120' x2='110' y2='190'/><line x1='135' y1='120' x2='135' y2='190'/><line x1='45' y1='175' x2='150' y2='135'/></g><text x='100' y='250' font-family='Poppins' font-weight='800' font-size='56' fill='{SUN}' text-anchor='middle'>x20</text><ellipse cx='300' cy='455' rx='170' ry='16' fill='#000' opacity='.18'/></svg>""",
 "coconut_crack": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='235' fill='{SUN}' opacity='.25'/><g transform='rotate(-14 200 300)'><path d='M90 300 a110 110 0 0 0 220 0z' fill='#7A4A26'/><path d='M104 300 a96 96 0 0 0 192 0z' fill='#FFF7E8'/><path d='M126 300 a74 74 0 0 0 148 0z' fill='#E8F4F1'/></g><g transform='rotate(14 400 300)'><path d='M290 300 a110 110 0 0 0 220 0z' fill='#7A4A26'/><path d='M304 300 a96 96 0 0 0 192 0z' fill='#FFF7E8'/><path d='M326 300 a74 74 0 0 0 148 0z' fill='#E8F4F1'/></g><g stroke='{SUN}' stroke-width='10' stroke-linecap='round'><line x1='300' y1='200' x2='300' y2='120'/><line x1='240' y1='215' x2='200' y2='150'/><line x1='360' y1='215' x2='400' y2='150'/></g><g fill='#9AD1F5'><circle cx='250' cy='420' r='10'/><circle cx='350' cy='430' r='8'/><circle cx='300' cy='445' r='7'/></g><text x='300' y='95' font-family='Poppins' font-weight='800' font-size='64' fill='{CREAM}' text-anchor='middle'>101</text></svg>""",
 "hourglass": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.15'/>
  <rect x='180' y='50' width='240' height='30' rx='12' fill='{CREAM}'/><rect x='180' y='440' width='240' height='30' rx='12' fill='{CREAM}'/>
  <path d='M205 80 h190 C395 170 330 220 310 260 C330 300 395 350 395 440 h-190 C205 350 270 300 290 260 C270 220 205 170 205 80z' fill='none' stroke='{CREAM}' stroke-width='12'/>
  <path d='M240 120 h120 C350 170 315 205 300 235 C285 205 250 170 240 120z' fill='{SUN}'/>
  <path d='M230 425 C240 375 275 350 300 340 C325 350 360 375 370 425z' fill='{SUN}'/><line x1='300' y1='240' x2='300' y2='340' stroke='{SUN}' stroke-width='6' stroke-dasharray='10 8'/>
  <circle cx='480' cy='130' r='58' fill='{SUN}'/><text x='480' y='150' font-family='Poppins' font-weight='800' font-size='56' fill='{DEEP}' text-anchor='middle'>20</text></svg>""",
 "phone_off": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='250' r='220' fill='{SUN}' opacity='.15'/><rect x='210' y='60' width='180' height='340' rx='30' fill='#2B2D42'/><rect x='225' y='90' width='150' height='270' rx='10' fill='#4A4E69'/>
  <circle cx='300' cy='225' r='60' fill='none' stroke='#E76F51' stroke-width='14'/><line x1='258' y1='267' x2='342' y2='183' stroke='#E76F51' stroke-width='14' stroke-linecap='round'/>
  <circle cx='460' cy='120' r='45' fill='{SUN}'/><path d='M80 470 q60 -80 120 0' fill='#3FAE6B'/><path d='M400 470 q60 -90 130 0' fill='#57C77F'/></svg>""",
 "heart": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='230' fill='{SUN}' opacity='.15'/>
  <path d='M300 430 C120 320 110 190 190 150 C240 125 285 155 300 190 C315 155 360 125 410 150 C490 190 480 320 300 430z' fill='#E76F51'/>
  <path d='M230 200 q20 -25 45 -10' stroke='#fff' stroke-width='10' fill='none' stroke-linecap='round' opacity='.7'/></svg>""",
 "tea": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.15'/>
  <g fill='none' stroke='{CREAM}' stroke-width='10' stroke-linecap='round' opacity='.8'><path d='M240 170 q-20 -35 0 -70 q20 -35 0 -70'/><path d='M300 170 q-20 -35 0 -70 q20 -35 0 -70'/><path d='M360 170 q-20 -35 0 -70 q20 -35 0 -70'/></g>
  <path d='M170 200 h260 v120 a100 100 0 0 1 -100 100 h-60 a100 100 0 0 1 -100 -100z' fill='{CREAM}'/>
  <path d='M430 230 h30 a50 50 0 0 1 0 100 h-40' fill='none' stroke='{CREAM}' stroke-width='22'/>
  <path d='M300 360 C250 330 248 290 272 280 C287 274 297 284 300 292 C303 284 313 274 328 280 C352 290 350 330 300 360z' fill='#E76F51'/>
  <ellipse cx='300' cy='450' rx='200' ry='22' fill='{CREAM}' opacity='.6'/></svg>""",
 "five": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.15'/>
  <circle cx='300' cy='260' r='150' fill='{SUN}'/><text x='300' y='330' font-family='Poppins' font-weight='800' font-size='210' fill='{DEEP}' text-anchor='middle'>5</text>
  <g fill='#E76F51'><path d='M110 120 C80 100 80 78 94 72 C102 69 108 74 110 79 C112 74 118 69 126 72 C140 78 140 100 110 120z'/><path d='M490 110 C460 90 460 68 474 62 C482 59 488 64 490 69 C492 64 498 59 506 62 C520 68 520 90 490 110z'/>
  <path d='M95 420 C65 400 65 378 79 372 C87 369 93 374 95 379 C97 374 103 369 111 372 C125 378 125 400 95 420z'/><path d='M505 430 C475 410 475 388 489 382 C497 379 503 384 505 389 C507 384 513 379 521 382 C535 388 535 410 505 430z'/>
  <path d='M300 500 C270 480 270 458 284 452 C292 449 298 454 300 459 C302 454 308 449 316 452 C330 458 330 480 300 500z'/></g></svg>""",
 "rocks_jar": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.15'/>
  <rect x='195' y='55' width='210' height='34' rx='10' fill='#A85A2E'/>
  <path d='M180 95 h240 v300 a50 50 0 0 1 -50 50 h-140 a50 50 0 0 1 -50 -50z' fill='{CREAM}' opacity='.18' stroke='{CREAM}' stroke-width='10'/>
  <path d='M188 360 q112 -30 224 0 v35 a42 42 0 0 1 -42 42 h-140 a42 42 0 0 1 -42 -42z' fill='#E9C46A'/>
  <g stroke='#4A4E69' stroke-width='4'><ellipse cx='245' cy='330' rx='48' ry='38' fill='#8D99AE'/><ellipse cx='350' cy='325' rx='52' ry='40' fill='#A3AAB8'/>
  <ellipse cx='295' cy='255' rx='55' ry='42' fill='#8D99AE'/><ellipse cx='240' cy='180' rx='40' ry='32' fill='#A3AAB8'/><ellipse cx='355' cy='190' rx='45' ry='35' fill='#8D99AE'/></g>
  <g fill='#E9C46A'><circle cx='300' cy='175' r='6'/><circle cx='205' cy='255' r='5'/><circle cx='395' cy='260' r='6'/><circle cx='300' cy='320' r='5'/><circle cx='215' cy='395' r='4'/></g>
</svg>""",
 "ice": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.15'/>
  <rect x='150' y='150' width='230' height='230' rx='34' fill='#BDE6F5' stroke='{CREAM}' stroke-width='10'/>
  <path d='M175 185 h60 M175 205 h30' stroke='#fff' stroke-width='12' stroke-linecap='round' opacity='.9'/>
  <rect x='170' y='370' width='190' height='14' rx='7' fill='#8FD3EA' opacity='.6'/>
  <rect x='440' y='90' width='44' height='300' rx='22' fill='{CREAM}'/><circle cx='462' cy='410' r='42' fill='#5EC4E8'/>
  <rect x='452' y='250' width='20' height='150' rx='10' fill='#5EC4E8'/>
  <g stroke='{DEEP}' stroke-width='5'><line x1='440' y1='130' x2='458' y2='130'/><line x1='440' y1='180' x2='458' y2='180'/><line x1='440' y1='230' x2='458' y2='230'/><line x1='440' y1='280' x2='458' y2='280'/><line x1='440' y1='330' x2='458' y2='330'/></g>
  <text x='265' y='470' font-family='Poppins' font-weight='800' font-size='48' fill='{SUN}' text-anchor='middle'>-5° -4° -3°</text></svg>""",
 "ice_melt": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.15'/>
  <ellipse cx='270' cy='405' rx='190' ry='40' fill='#5EC4E8' opacity='.75'/>
  <path d='M175 395 C165 300 190 240 230 230 h90 C360 235 380 300 368 395z' fill='#BDE6F5' stroke='{CREAM}' stroke-width='8'/>
  <path d='M200 270 h40' stroke='#fff' stroke-width='12' stroke-linecap='round' opacity='.9'/>
  <path d='M300 120 C285 150 275 165 275 180 a25 25 0 0 0 50 0 C325 165 315 150 300 120z' fill='#5EC4E8'/>
  <path d='M430 405 C424 375 438 350 455 340 M455 340 c-25 -5 -40 -25 -40 -45 c25 0 40 20 40 45 M455 340 c25 -5 40 -25 40 -45 c-25 0 -40 20 -40 45' stroke='#3FAE6B' stroke-width='9' fill='#57C77F' stroke-linecap='round'/>
  <circle cx='470' cy='130' r='62' fill='{SUN}'/><text x='470' y='152' font-family='Poppins' font-weight='800' font-size='62' fill='{DEEP}' text-anchor='middle'>0°</text></svg>""",
 "alarm": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.15'/>
  <path d='M150 150 a60 60 0 0 1 85 -60' stroke='{SUN}' stroke-width='22' fill='none' stroke-linecap='round'/><path d='M450 150 a60 60 0 0 0 -85 -60' stroke='{SUN}' stroke-width='22' fill='none' stroke-linecap='round'/>
  <line x1='200' y1='420' x2='170' y2='465' stroke='{CREAM}' stroke-width='16' stroke-linecap='round'/><line x1='400' y1='420' x2='430' y2='465' stroke='{CREAM}' stroke-width='16' stroke-linecap='round'/>
  <circle cx='300' cy='275' r='170' fill='{CREAM}'/><circle cx='300' cy='275' r='145' fill='#fff' stroke='#E76F51' stroke-width='10'/>
  <text x='300' y='330' font-family='Poppins' font-weight='800' font-size='150' fill='#E76F51' text-anchor='middle'>5</text>
  <g font-family='Poppins' font-weight='800' font-size='40' fill='{DEEP}' text-anchor='middle' opacity='.55'><text x='300' y='170'>4</text><text x='400' y='290'>3</text><text x='300' y='405'>2</text><text x='200' y='290'>1</text></g></svg>""",
 "battery_low": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.15'/>
  <rect x='110' y='150' width='340' height='200' rx='34' fill='none' stroke='{CREAM}' stroke-width='20'/><rect x='450' y='210' width='40' height='80' rx='12' fill='{CREAM}'/>
  <rect x='138' y='178' width='46' height='144' rx='14' fill='#E76F51'/>
  <text x='300' y='292' font-family='Poppins' font-weight='800' font-size='96' fill='#E76F51' text-anchor='middle'>10%</text>
  <g font-family='Poppins' font-weight='800' font-size='70' fill='{SUN}'><text x='470' y='130'>!</text></g>
  <path d='M150 440 q60 -50 120 0 t120 0 t120 0' stroke='{CREAM}' stroke-width='8' fill='none' opacity='.5'/></svg>""",
 "battery_full": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='220' fill='{SUN}' opacity='.18'/>
  <rect x='110' y='150' width='340' height='200' rx='34' fill='none' stroke='{CREAM}' stroke-width='20'/><rect x='450' y='210' width='40' height='80' rx='12' fill='{CREAM}'/>
  <rect x='138' y='178' width='284' height='144' rx='16' fill='#3FAE6B'/>
  <path d='M300 185 l-55 75 h45 l-20 60 l70 -85 h-45 l25 -50z' fill='{CREAM}'/>
  <path d='M480 90 a45 45 0 1 0 30 80 a55 55 0 0 1 -30 -80z' fill='{SUN}'/>
  <g fill='{CREAM}'><circle cx='110' cy='100' r='7'/><circle cx='170' cy='60' r='5'/><circle cx='540' cy='420' r='6'/></g></svg>""",
 "circles": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='245' fill='{SUN}' opacity='.10'/><circle cx='300' cy='260' r='235' fill='none' stroke='{CREAM}' stroke-width='6' stroke-dasharray='18 14' opacity='.7'/><circle cx='300' cy='260' r='95' fill='{SUN}'/><text x='300' y='118' font-family='Noto Sans Sinhala' font-weight='700' font-size='26' fill='{CREAM}' opacity='.75' text-anchor='middle'>ආර්ථිකය</text><text x='175' y='178' font-family='Noto Sans Sinhala' font-weight='700' font-size='26' fill='{CREAM}' opacity='.75' text-anchor='middle'>කාලගුණය</text><text x='432' y='178' font-family='Noto Sans Sinhala' font-weight='700' font-size='26' fill='{CREAM}' opacity='.75' text-anchor='middle'>අනුන්</text><text x='170' y='345' font-family='Noto Sans Sinhala' font-weight='700' font-size='26' fill='{CREAM}' opacity='.75' text-anchor='middle'>ප්‍රවෘත්ති</text><text x='430' y='345' font-family='Noto Sans Sinhala' font-weight='700' font-size='26' fill='{CREAM}' opacity='.75' text-anchor='middle'>අතීතය</text><text x='300' y='255' font-family='Noto Sans Sinhala' font-weight='800' font-size='44' fill='{DEEP}' text-anchor='middle'>මම</text><text x='300' y='305' font-family='Noto Sans Sinhala' font-weight='800' font-size='34' fill='{DEEP}' text-anchor='middle'>කරන දේ</text></svg>""",
 "circles_big": f"""<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='260' r='245' fill='{SUN}' opacity='.10'/><circle cx='300' cy='260' r='235' fill='none' stroke='{CREAM}' stroke-width='6' stroke-dasharray='18 14' opacity='.7'/><circle cx='300' cy='260' r='155' fill='{SUN}'/><text x='300' y='80' font-family='Noto Sans Sinhala' font-weight='700' font-size='26' fill='{CREAM}' opacity='.75' text-anchor='middle'>ආර්ථිකය</text><text x='300' y='462' font-family='Noto Sans Sinhala' font-weight='700' font-size='26' fill='{CREAM}' opacity='.75' text-anchor='middle'>අනුන්</text><text x='300' y='200' font-family='Noto Sans Sinhala' font-weight='800' font-size='38' fill='{DEEP}' text-anchor='middle'>පාඩම</text><text x='220' y='265' font-family='Noto Sans Sinhala' font-weight='800' font-size='36' fill='{DEEP}' text-anchor='middle'>නින්ද</text><text x='380' y='265' font-family='Noto Sans Sinhala' font-weight='800' font-size='36' fill='{DEEP}' text-anchor='middle'>වචන</text><text x='300' y='330' font-family='Noto Sans Sinhala' font-weight='800' font-size='34' fill='{DEEP}' text-anchor='middle'>අලුත් දෙයක්</text></svg>""",
}


def _coin_stack(x, base, n, r=46):
    """n coins stacked upward from base, centred at x (ellipse coins, amber/gold)."""
    out = []
    for k in range(n):
        y = base - k * 18
        out.append(f"<rect x='{x-r}' y='{y-14}' width='{2*r}' height='18' fill='#C98A12'/><ellipse cx='{x}' cy='{y+4}' rx='{r}' ry='14' fill='#C98A12'/><ellipse cx='{x}' cy='{y-14}' rx='{r}' ry='14' fill='#FFC857' stroke='#E09B16' stroke-width='3'/>")
    return "".join(out)


def _coins(stacks, glow=.14, label=""):
    xs = [300] if len(stacks) == 1 else [120 + i * (360 / (len(stacks) - 1)) for i in range(len(stacks))]
    body = "".join(_coin_stack(x, 450, n) for x, n in zip(xs, stacks))
    lab = f"<text x='300' y='90' font-family='Poppins' font-weight='800' font-size='64' fill='{CREAM}' text-anchor='middle'>{label}</text>" if label else ""
    return f"<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='290' r='230' fill='{SUN}' opacity='{glow}'/>{body}{lab}</svg>"


# Compound effect / magic rupee (12 Nov): one coin -> small stacks -> huge stacks
ART["coin_one"] = (f"<svg viewBox='0 0 600 520' width='760'><circle cx='300' cy='270' r='220' fill='{SUN}' opacity='.15'/>"
                   f"<circle cx='300' cy='270' r='150' fill='#E09B16'/><circle cx='300' cy='270' r='128' fill='#FFC857'/>"
                   f"<text x='300' y='318' font-family='Poppins' font-weight='800' font-size='150' fill='#9A6408' text-anchor='middle'>1</text>"
                   f"<text x='470' y='120' font-family='Poppins' font-weight='800' font-size='90' fill='{CREAM}' text-anchor='middle'>×2</text></svg>")
ART["coins_10"] = _coins([1, 2, 3], .12, "")
ART["coins_20"] = _coins([3, 5, 7, 9], .18, "")
ART["coins_30"] = _coins([9, 13, 17, 21, 17], .30, "")

PAGE = """<!doctype html><html><head><meta charset='utf-8'><style>
body{{margin:0;width:1080px;height:1920px;overflow:hidden;font-family:'Noto Sans Sinhala',sans-serif;
background:radial-gradient(120% 70% at 50% 18%, #17707A 0%, {teal} 45%, {deep} 100%);}}
.top{{position:absolute;top:96px;left:0;right:0;text-align:center;font-family:Poppins;font-weight:700;letter-spacing:6px;color:{sun};font-size:34px}}
.kick{{position:absolute;top:150px;left:110px;right:170px;text-align:center;color:{cream};opacity:.85;font-size:32px;font-weight:600}}
.art{{position:absolute;top:240px;left:0;right:56px;display:flex;justify-content:center}}
.art svg{{width:640px;height:auto;max-height:600px}}
.cap{{position:absolute;left:110px;right:170px;top:880px;text-align:center;color:#fff;font-weight:800;font-size:{fs}px;line-height:1.4;text-shadow:0 4px 18px rgba(0,0,0,.35)}}
.cap b{{color:{sun}}}
</style></head><body><div class='top'>E POSITIVE</div><div class='kick'>{kick}</div><div class='art'>{art}</div><div class='cap'>{cap}</div></body></html>"""


def main(script, outdir):
    os.makedirs(outdir, exist_ok=True)
    data = json.load(open(script))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for i, sc in enumerate(data["scenes"], 1):
            cap = sc["caption"]
            fs = 72 if len(cap) < 60 else 62
            if i == 1 and len(cap) < 40:
                fs = 96  # scene-1 hook: big enough to read in under 2 s
            html = PAGE.format(teal=TEAL, deep=DEEP, sun=SUN, cream=CREAM, art=ART[sc["art"]], cap=cap, kick=sc.get("kicker", ""), fs=fs)
            pg.set_content(html)
            pg.wait_for_timeout(300)
            # keep the headline clear of the closed-caption band (y >= 1280): shrink until it fits
            pg.evaluate("""() => { const c = document.querySelector('.cap'); let f = parseFloat(getComputedStyle(c).fontSize);
              while (c.getBoundingClientRect().bottom > 1250 && f > 40) { f -= 3; c.style.fontSize = f + 'px'; } }""")
            pg.screenshot(path=f"{outdir}/s{i}.png")
        b.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
