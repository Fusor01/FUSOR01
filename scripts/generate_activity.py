"""Builds assets/activity.svg from the last 30 days of GitHub contributions."""
import json, os, urllib.request
from datetime import date, timedelta

USER = os.environ.get("GH_USER", "FUSOR01")
TOKEN = os.environ["GITHUB_TOKEN"]
DAYS = 30
BG, PANEL, INK, TEXT, MUTED, LINE, Y, T = "#161B38", "#161B38", "#080B1A", "#EAEFFF", "#8A93C0", "#3A4278", "#FFC857", "#38D9C0"

end = date.today()
start = end - timedelta(days=DAYS - 1)
query = """query($u:String!,$f:DateTime!,$t:DateTime!){user(login:$u){contributionsCollection(from:$f,to:$t){
contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query, "variables": {"u": USER, "f": f"{start}T00:00:00Z", "t": f"{end}T23:59:59Z"}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
)
data = json.load(urllib.request.urlopen(req))
days = {}
for w in data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
    for d in w["contributionDays"]:
        days[d["date"]] = d["contributionCount"]
series = [days.get(str(start + timedelta(i)), 0) for i in range(DAYS)]

W, H, L, R, TOP, BOT = 600, 260, 48, 24, 70, 40
top = max(max(series), 4)
cw, ch = W - L - R, H - TOP - BOT
pts = [(L + cw * i / (DAYS - 1), TOP + ch - ch * v / top) for i, v in enumerate(series)]
line = " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
area = f"M{L} {TOP+ch} L{line} L{L+cw} {TOP+ch}Z"
grid = "".join(
    f'<line x1="{L}" x2="{W-R}" y1="{TOP+ch-ch*k/4:.1f}" y2="{TOP+ch-ch*k/4:.1f}" stroke="{LINE}" stroke-width="1" opacity=".5"/>'
    f'<text x="{L-10}" y="{TOP+ch-ch*k/4+4:.1f}" font-size="11" fill="{MUTED}" text-anchor="end">{round(top*k/4)}</text>'
    for k in range(5)
)
dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{Y}" stroke="{INK}" stroke-width="1.5"/>' for (x, y), v in zip(pts, series) if v)
total = sum(series)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total} contributions in the last {DAYS} days">
<style>text{{font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif}}</style>
<rect width="{W}" height="{H}" rx="22" fill="{BG}"/>
<text x="{L-24}" y="38" font-size="20" font-weight="800" fill="{TEXT}">{total} contributions</text>
<text x="{L-24}" y="58" font-size="13" fill="{MUTED}">Last {DAYS} days</text>
{grid}
<path d="{area}" fill="{T}" opacity=".18"/>
<path d="M{line}" fill="none" stroke="{T}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
{dots}
<text x="{L}" y="{H-14}" font-size="11" fill="{MUTED}">{start.strftime('%b %d')}</text>
<text x="{W-R}" y="{H-14}" font-size="11" fill="{MUTED}" text-anchor="end">{end.strftime('%b %d')}</text>
</svg>'''
os.makedirs("assets", exist_ok=True)
open("assets/activity.svg", "w").write(svg)
