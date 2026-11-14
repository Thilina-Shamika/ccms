"""Build the CCMS site: every page is generated from the shared parts in src/.

Run from the repository root:  python3 tools/build.py
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import (BASE_URL, TEAM_STATS, RESULT_STATS, PROOF_LINE, HOME_FAQS, SERVICES, STANDARDS,
                     RECRUITMENT, SECTORS, GROUPS, RPO_REASONS, CASE_STUDIES, PAIN_MOCKS)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')


def read(*p):
    with open(os.path.join(SRC, *p)) as f:
        return f.read()


def esc(t):
    return html.escape(t, quote=False)


def attr(t):
    return html.escape(t, quote=True)


ARROW = '<svg class="arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>'
ARROW_UP = '<svg class="arrow" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"></path></svg>'
CARET = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"></path></svg>'
CHECK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2238D6" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5 9-10"></path></svg>'
SHIELD = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6zM9 12l2 2 4-4"></path></svg>'
LOGO = 'assets/d7fee95ddd0788962b6253f583f3de89.png'

# ---------------------------------------------------------------- navigation

def page_url(slug):
    return '%%R%%' + slug


NAV = [
    ('RPO', None, [
        ('RPO overview', 'recruitment-process-outsourcing/'),
        ('Healthcare recruitment', 'industries/healthcare-recruitment/'),
        ('Education recruitment', 'industries/education-recruitment/'),
        ('Construction recruitment', 'industries/construction-recruitment/')]),
    ('Services', None,
     [(s['name'], 'services/%s/' % s['slug']) for s in SERVICES]),
    ('Other industries', None,
     [(g['name'], 'industries/%s/' % g['slug']) for g in GROUPS]),
    ('Digital', 'digital/', None),
    ('Why Sri Lanka', 'why-sri-lanka/', None),
    ('Case studies', 'case-studies/', None),
]


def nav_links(cls, current):
    out = []
    for label, href, sub in NAV:
        cur = ' aria-current="page"' if current and href == current else ''
        if sub:
            items = ''.join('<a href="%s"%s>%s</a>' % (page_url(h), ' aria-current="page"' if h == current else '', esc(t)) for t, h in sub)
            out.append('<div class="ndd"><button class="%s" type="button" aria-haspopup="true">%s %s</button><div class="ddm">%s</div></div>'
                       % (cls, esc(label), CARET, items))
        else:
            out.append('<a class="%s" href="%s"%s>%s</a>' % (cls, page_url(href), cur, esc(label)))
    return ''.join(out)


def header(current, plan_href):
    mm = []
    for label, href, sub in NAV:
        subs = ''
        if sub:
            subs = '<div class="mm-s">' + ''.join('<a href="%s" onClick="{{closeMenu}}">%s</a>' % (page_url(h), esc(t)) for t, h in sub) + '</div>'
        head_ = '<div class="mm-h">%s</div>' % esc(label) if sub else '<a href="%s" onClick="{{closeMenu}}">%s</a>' % (page_url(href), esc(label))
        mm.append('<div class="mm-g">%s%s</div>' % (head_, subs))
    return f'''<div class="{{{{stickCls}}}}" aria-label="Quick links"><a href="%%R%%" aria-label="CCMS home" style="display: inline-flex"><img src="%%R%%{LOGO}" alt="CCMS" width="87" height="21" style="height: 21px; width: auto; display: block"></a>{nav_links('sl', current)}<a class="btn btn-white" href="#contact" style="min-height: 42px; padding: 0 18px; font-size: 15px">Book a call</a></div>
<div class="{{{{mbarCls}}}}" aria-label="Quick actions"><a class="btn" href="{plan_href}" style="background: rgba(255,255,255,.1); color: #FFFFFF; border: 1px solid rgba(255,255,255,.2)">Get a team plan</a><a class="btn btn-white" href="#contact">Book a call</a></div>
<header style="position: relative; z-index: 4">
<nav aria-label="Main" class="wrap" style="height: 76px; display: flex; align-items: center; justify-content: space-between; gap: 24px">
<a href="%%R%%" aria-label="CCMS home" style="text-decoration: none; min-height: 44px; display: inline-flex; align-items: center"><img src="%%R%%{LOGO}" alt="CCMS" width="103" height="25" style="display: block; height: 25px; width: auto"><span class="tagl">Where quality matters.</span></a>
<div class="navlinks" style="display: flex; gap: 26px">
{nav_links('navlink', current)}
</div>
<div style="display: flex; align-items: center; gap: 10px">
<a class="btn btn-white navcta" href="#contact" style="min-height: 42px; padding: 0 18px; font-size: 15px">Book a call</a>
<button class="burger" type="button" onClick="{{{{toggleMenu}}}}" aria-expanded="{{{{menuExpanded}}}}" aria-label="Open menu" style="width: 46px; height: 46px; border-radius: 999px; border: 1px solid rgba(255,255,255,.25); background: rgba(255,255,255,.06); color: #FFFFFF; align-items: center; justify-content: center; cursor: pointer"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 8h16M4 16h16"></path></svg></button>
</div>
</nav>
<sc-if value="{{{{menuOpen}}}}" hint-placeholder-val="{{{{false}}}}">
<div class="mobilemenu" style="margin: 0 16px 12px; border-radius: 20px; background: #FFFFFF; padding: 8px 20px; display: flex; flex-direction: column; box-shadow: 0 24px 60px rgba(0,0,0,.35); animation: ccms-in 220ms var(--ease) both">
{''.join(mm)}
<a class="btn btn-accent" href="#contact" onClick="{{{{closeMenu}}}}" style="margin: 14px 0 12px; min-height: 52px">Book a call</a>
</div>
</sc-if>
</header>
'''

# ---------------------------------------------------------------- building blocks

def sec(id_, inner, bg='#FFFFFF', extra=''):
    return f'<section id="{id_}" class="sec" style="background: {bg}{extra}">\n<div class="wrap">\n{inner}\n</div>\n</section>\n'


def head(label, h2, sub=None, center=False, h2_style=''):
    s = (f'<p class="k" data-a="up" data-d="0">{esc(label)}</p>' if label else '') + f'<h2 class="H" data-a="up" data-d="0" style="{h2_style}">{h2}</h2>'
    if sub:
        s += f'<p class="S" data-a="up" data-d="0">{sub}</p>'
    return f'<div style="text-align: center">{s}</div>' if center else s


def stat_cards(stats, top=40, cols=None):
    cards = ''.join(f'<div class="card6" data-a="up" data-d="0" style="padding: 24px"><div style="font-size: clamp(32px, 3.2vw, 46px); font-weight: 800; letter-spacing: -.055em; line-height: 1; color: var(--ink)">{esc(n)}</div><div style="margin-top: 10px; color: var(--ink2)">{esc(l)}</div></div>' for n, l in stats)
    grid = f'; grid-template-columns: {cols}' if cols else ''
    return f'<div class="g-nums" style="margin-top: {top}px{grid}">{cards}</div>'


def link_card(href, img, chip, color, title, text, cta, img_h=220):
    return f'''<a class="card6 sh h6t cs-card" data-a="up" data-d="0" href="{href}">
<div class="cs-img" style="height:{img_h}px"><img src="%%R%%assets/{img}" alt="" loading="lazy" style="object-position:center 35%"><span class="cs-chip"><i style="background:{color}"></i>{esc(chip)}</span></div>
<div style="display:flex;flex-direction:column;flex:1;padding:22px 14px 10px">
<h3 class="cs-t" style="font-size:clamp(22px,2vw,26px);margin-top:0">{esc(title)}</h3>
<p class="cs-x">{esc(text)}</p>
<span class="lk" style="margin-top:auto;padding-top:6px;color:#2238D6">{esc(cta)} {ARROW}</span>
</div>
</a>'''


RECRUIT_IMG = {'healthcare-recruitment': 'ed3e8c66f268d39a0f6e8cb060b92af4.jpg',
               'education-recruitment': 'd45bde67a2d819b341e5acb1c7721081.jpg',
               'construction-recruitment': '2d0ce4a076ef8df54705d9622d174413.jpg'}


def recruitment_cards():
    return '<div class="g-cards3">' + ''.join(
        link_card(page_url('industries/%s/' % r['slug']), RECRUIT_IMG[r['slug']], 'Recruitment', r['chip'],
                  r['name'], r['card'], 'Explore ' + r['name'].lower()) for r in RECRUITMENT) + '</div>'


def sectors_section(bg='var(--s1)'):
    return sec('sectors', head('Who we work with', 'Recruitment agencies we support') +
               '<div style="margin-top: 44px">' + recruitment_cards() + '</div>', bg)


def novello_feature():
    c = CASE_STUDIES[0]
    stats = ''.join(f'<div><div class="cs-n" style="color:{c["color"] if i == 0 else "var(--ink)"}">{esc(n)}</div><div class="cs-l">{esc(l)}</div></div>' for i, (n, l) in enumerate(c['stats']))
    return f'''<a class="card6 sh h6t cs-feat" data-a="up" data-d="0" href="%%R%%case-studies/">
<div class="cs-img" style="min-height:380px"><img src="%%R%%assets/{c['img']}" alt="" loading="lazy"><span class="cs-chip"><i style="background:{c['color']}"></i>{esc(c['chip'])}</span></div>
<div style="display:flex;flex-direction:column;padding:clamp(20px,3vw,36px)">
<div class="cs-meta"><b>Featured story</b><span aria-hidden="true">·</span>{esc(c['name'])}</div>
<h3 class="cs-t" style="font-size:clamp(26px,2.6vw,36px)">{esc(c['title'])}</h3>
<p class="cs-x">25 of 26 nurses rated the service 10/10.</p>
<div class="cs-stats">{stats}</div>
<span class="lk" style="margin-top:auto;padding-top:22px;color:#2238D6">See all case studies {ARROW}</span>
</div>
</a>'''


def results_section(bg='#FFFFFF'):
    top = f'''<div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; flex-wrap: wrap">
<div>{head('Case studies', 'Results our clients see')}</div>
<a class="lk" data-a="up" data-d="0" href="%%R%%case-studies/">See all case studies {ARROW}</a>
</div>'''
    line = f'''<div class="proofl" data-a="up" data-d="0"><div><b>Most of our clients came by referral.</b> <span style="color: var(--ink2)">Many have added work without being asked.</span></div><a class="btn btn-accent" href="#contact">Book a call {ARROW_UP}</a></div>'''
    return sec('results', top + '<div style="margin-top: 40px">' + novello_feature() + '</div>' + stat_cards(RESULT_STATS, 16) + line, bg)


def proof_section(line, bg='#FFFFFF'):
    body = (head('Proof', esc(line), h2_style='max-width: 900px; font-size: clamp(30px, 3.4vw, 46px)') + stat_cards(RESULT_STATS) +
            f'<div class="proofl" data-a="up" data-d="0"><div><b>Most of our clients came by referral.</b> <span style="color: var(--ink2)">Many have added work without being asked.</span></div><a class="lk" href="%%R%%case-studies/" style="color:#2238D6">See all case studies {ARROW}</a></div>')
    return sec('proof', body, bg)


def faq_section(faqs, bg='var(--s1)', title='Common questions'):
    items = []
    for i, (q, a) in enumerate(faqs):
        items.append(f'''<div style="border-top: 1px solid var(--line2)">
<h3 style="margin: 0"><button class="faqbtn" type="button" onClick="{{{{fq{i}t}}}}" aria-expanded="{{{{fq{i}e}}}}"><span>{esc(q)}</span><span class="faqicon" aria-hidden="true" style="background: {{{{fq{i}b}}}}; transform: {{{{fq{i}r}}}}"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="{{{{fq{i}c}}}}" stroke-width="2.6" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"></path></svg></span></button></h3>
<p style="display: {{{{fq{i}d}}}}; margin: 0; padding: 0 52px 24px 0; color: var(--ink2); animation: ccms-in 260ms var(--ease) both">{esc(a)}</p>
</div>''')
    return f'''<section id="faq" class="sec" style="background: {bg}">
<div class="wrap" style="max-width: 860px">
<div style="text-align: center"><p class="k" data-a="up" data-d="0">FAQs</p><h2 class="H" data-a="up" data-d="0">{esc(title)}</h2><p class="sub" data-a="up" data-d="0" style="margin-left: auto; margin-right: auto">Something else? <a href="#contact">Ask us on a call.</a></p></div>
<div data-a="up" data-d="0" style="margin-top: 44px; text-align: left">
{chr(10).join(items)}
<div style="border-top: 1px solid var(--line2)"></div>
</div>
</div>
</section>
'''


AV = ['#DCFCE7', '#E0E7FF', '#FCE7F3']
PV_TICK = '<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5 9-10"></path></svg>'


def pain_mock(spec):
    """Homepage pain-card mock-ups (classes pv, pv1 to pv4 in styles.css) filled with this pain's details."""
    kind = spec[0]
    sw = lambda a, b, ca='pv1-a', cb='pv1-b': f'<span class="pv-sw"><span class="{ca}">{esc(a)}</span><span class="{cb}">{esc(b)}</span></span>'
    if kind == 'list':
        _, head_, a, b, rows = spec
        out = f'<div class="pv-h">{esc(head_)}<span class="pv-tag pv1-c">{sw(a, b)}</span></div>'
        for i, (av, name, sub, tag) in enumerate(rows):
            last = isinstance(tag, tuple)
            t = f'<span class="pv-tag pv1-c">{sw(*tag)}</span>' if last else f'<span class="pv-tag">{esc(tag)}</span>'
            out += f'<div class="pv-row{" pv1-r" if last else ""}"><span class="pv-av" style="background:{AV[i % 3]}">{esc(av)}</span><span class="pv-n"><b>{esc(name)}</b><i>{esc(sub)}</i></span>{t}</div>'
    elif kind == 'inbox':
        _, head_, rows = spec
        out = (f'<div class="pv-h">{esc(head_)}<span class="pv3-b"><span>1</span><span>2</span><span>3</span><span>4</span></span></div><div>' +
               ''.join(f'<div class="pv3-m"><span class="pv3-dot"></span><span class="pv-n"><b>{esc(t)}</b><i>{esc(d)}</i></span><span class="pv3-t">{esc(tm)}</span></div>' for t, d, tm in rows) + '</div>')
    elif kind == 'audit':
        _, head_, due, items, pct = spec
        k = [f'<span class="pv4-k y">{PV_TICK}</span>', f'<span class="pv4-k y">{PV_TICK}</span>', '<span class="pv4-k s"></span>', '<span class="pv4-k e"></span>']
        out = (f'<div class="pv-h">{esc(head_)}<span class="pv-tag pv-red">{esc(due)}</span></div>' +
               ''.join(f'<div class="pv4-i{" m" if i == 3 else ""}">{k[i]}{esc(t)}</div>' for i, t in enumerate(items)) +
               f'<div class="pv4-bars"><div><div class="pv4-bl"><span>Ready</span><span>{esc(pct)}</span></div><div class="pv4-tr"><div class="pv4-fr"></div></div></div><div><div class="pv4-bl"><span>Time left</span></div><div class="pv4-tr"><div class="pv4-ft"></div></div></div></div>')
    else:
        _, head_, a, b, legend = spec
        cells = 'ffffoffffxffffoffofff'
        out = (f'<div class="pv-h">{esc(head_)}<span class="pv-tag">{sw(a, b, "pv2-n1", "pv2-n2")}</span></div><div class="pv2-g">' +
               ''.join(f'<span class="pv2-d">{d}</span>' for d in 'MTWTFSS') + ''.join(f'<span class="pv2-c {c}"></span>' for c in cells) +
               f'</div><div class="pv2-l"><s></s>{esc(legend)}</div>')
    return f'<div class="pv" aria-hidden="true">{out}</div>'


def pain_section(pains, bg='#FFFFFF', recruitment=False):
    cards = ''.join(f'<div class="card6" data-a="up" data-d="0" style="padding: 14px 14px 20px; background: #FFFBF5; border-color: rgba(180,83,9,.14)">{pain_mock(PAIN_MOCKS[p])}<div style="font-size: 18px; font-weight: 700; letter-spacing: -.01em; line-height: 1.35">{esc(p)}</div></div>' for p in pains)
    top = (head('Sound familiar?', 'Recruitment is getting harder. <span style="color: #8A909C">Your back office shouldn\'t be.</span>', h2_style='max-width: 980px')
           if recruitment else head(None, 'Sound familiar?'))
    return sec('story', top +
               f'<div class="g-pain g-pain3" style="margin-top: 52px">{cards}</div>', bg)


def role_card(name, desc=None, href=None):
    inner = f'<span class="ric">{CHECK}</span><span><h3>{esc(name)}</h3>' + (f'<p>{esc(desc)}</p>' if desc else '') + '</span>'
    if href:
        return f'<a class="card6 sh h6t rolec" data-a="up" data-d="0" href="{href}">{inner}</a>'
    return f'<div class="card6 rolec" data-a="up" data-d="0">{inner}</div>'


def rules_box(text):
    """The homepage's dark closing band, used for 'The rules you work to'."""
    return f'''<div class="cta-band" data-a="up" data-d="0" style="margin-top: 16px; background-color: #0A0F2C; background-image: radial-gradient(60% 120% at 85% 50%, rgba(47,75,255,.35), rgba(47,75,255,0) 70%), radial-gradient(rgba(255,255,255,.07) 1px, transparent 1.2px); background-size: auto, 18px 18px">
<div style="position: relative; flex: 1 1 380px">
<div style="font-size: 13px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #AEB8FF">The rules you work to</div>
<div style="margin-top: 10px; font-size: clamp(20px, 2vw, 26px); font-weight: 700; letter-spacing: -.02em; line-height: 1.3">{esc(text)}</div>
</div>
<a class="btn btn-white" href="#contact" style="position: relative">Book a call {ARROW_UP}</a>
</div>'''


def strip_plan(hero_html):
    """Hero without the team plan card: keep an empty surface so the clouds still have somewhere to settle."""
    a = hero_html.index('<div data-ccms="hero-surface"')
    b = hero_html.rindex('</div>\n</div>')
    return hero_html[:a] + '<div data-ccms="hero-surface" aria-hidden="true" style="height: 1px"></div>\n' + hero_html[b + len('</div>\n'):]


def accent(h1):
    """Two-tone headline like the homepage: the part after 'for' takes the lighter colour."""
    if '<span' in h1 or ' for ' not in h1:
        return h1
    first, rest = h1.split(' for ', 1)
    return f'{first} for <span style="color: #AEB8FF">{rest}</span>'


def hero(crumbs, eyebrow, h1, intro, buttons, surface=None):
    """The homepage hero with this page's words: same layout, trust line and team plan card."""
    s = read('home-hero.html')
    s = s.replace('>Back office teams for UK recruitment agencies<', '>' + esc(eyebrow) + '<', 1)
    s = re.sub(r'(<h1 class="hero-in" style=")[^"]*(">).*?(</h1>)',
               lambda m: m.group(1) + ('margin: 0; font-size: clamp(38px, 4.8vw, 66px); line-height: 1.02; letter-spacing: -.05em; font-weight: 800; animation-delay: 60ms' if len(re.sub('<[^>]+>', '', h1)) > 48 else 'margin: 0; font-size: clamp(42px, 5.6vw, 78px); line-height: 1; letter-spacing: -.05em; font-weight: 800; animation-delay: 60ms') + m.group(2) + accent(h1) + m.group(3),
               s, count=1, flags=re.S)
    s = s.replace('Compliance, bookings, payroll, finance and resourcing for healthcare, education and construction recruitment agencies. Your team works only for you, in your systems, on UK hours.', esc(intro), 1)
    s = re.sub(r'(<div style="margin-top: 26px; display: flex; gap: 10px; flex-wrap: wrap">\n).*?(\n</div>\n<div class="ghero-proof")',
               lambda m: m.group(1) + '\n'.join(buttons) + m.group(2), s, count=1, flags=re.S)
    return s.replace('%%TEAMPLAN%%', TEAMPLAN)


def btn_call():
    return f'<a class="btn btn-white" href="#contact">Book a call {ARROW_UP}</a>'


def btn_line(text, href):
    return f'<a class="btn btn-line" href="{href}">{esc(text)}</a>'


def hook(left, card, plan=False):
    pid = ' id="plan"' if plan else ''
    return f'<div data-ccms="hero-surface"{pid} class="hero-in hero-hook" style="animation-delay: 220ms">\n<div class="hh-left">\n{left}\n</div>\n{card}\n</div>'


def hook_left(eye, h2, p=None, stats=TEAM_STATS):
    s = f'<div class="hh-eye">{eye}</div>\n<h2 style="margin: 14px 0 0; font-size: clamp(28px, 3vw, 40px); line-height: 1.08; letter-spacing: -.04em; font-weight: 800">{h2}</h2>'
    if p:
        s += f'\n<p style="margin: 14px 0 0; font-size: 17px; line-height: 1.6; color: #C9D0EE; max-width: 42ch">{esc(p)}</p>'
    if stats:
        s += '\n<dl class="hh-proof">' + ''.join(f'<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>' for a, b in stats) + '</dl>'
    return s


TEAMPLAN = None


def plan_hook(eye='Free team plan <span aria-hidden="true">/</span> 30 seconds'):
    return hook(hook_left(eye, 'See what your team could look like.',
                          "Pick your agency type and the roles you need. We'll email you a team plan with the roles, the set-up and a timeline."),
                TEAMPLAN, plan=True)


def list_card(title, rows):
    items = ''.join(f'<a href="{h}"><span>{esc(t)}' + (f'<small>{esc(s)}</small>' if s else '') + f'</span>{ARROW}</a>' if h else
                    f'<div><span>{esc(t)}' + (f'<small>{esc(s)}</small>' if s else '') + '</span></div>' for t, s, h in rows)
    return f'<div class="hh-card"><div style="font-size: 13px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--ink3)">{esc(title)}</div><div class="hh-list" style="margin-top: 6px">{items}</div></div>'


def svc_mocks():
    s = read('sections', 'rpo.html')
    arts = re.findall(r'<article class="card6 sh".*?</article>', s, flags=re.S)
    out = {}
    for a in arts:
        t = re.search(r'<h3[^>]*>([^<]*)</h3>', a).group(1)
        out[t] = re.search(r'<div data-a="up" data-d="100">(<div class="mini".*?)</div>\n</div>\n</article>', a, flags=re.S).group(1)
    return out


def home_section(name, new_id=None):
    s = read('sections', name + '.html')
    if new_id:
        s = re.sub(r'<section id="[^"]*"', f'<section id="{new_id}"', s, count=1)
    return s


def svc_section(id_, h2, sub, roles=None, side='', after='', bg='#FFFFFF', badge='RPO', links=True):
    """The homepage RPO layout: sticky heading on the left, service rows with mock-ups on the right.
    roles: list of (label, service name) to show, renamed and in that order."""
    rows = svc_rows()
    if roles is not None:
        arts = {re.search(r'<h3[^>]*>([^<]*)</h3>', a).group(1): a for a in re.findall(r'<article class="card6 sh".*?</article>', rows, flags=re.S)}
        picked = []
        for i, (label, svc) in enumerate(roles):
            a = arts[svc]
            a = re.sub(r'(<h3[^>]*>)[^<]*(</h3>)', lambda m: m.group(1) + esc(label) + m.group(2), a, count=1)
            a = re.sub(r'(color: #2238D6">)0\d(</span>)', lambda m: m.group(1) + '0%d' % (i + 1) + m.group(2), a, count=1)
            a = re.sub(r'style="top: \d+px"', 'style="top: %dpx"' % (96 + 18 * i), a, count=1)
            picked.append(a)
        rows = '<div class="stk">' + ''.join(picked) + '</div>'
    if not links:
        rows = re.sub(r'<a class="lk"[^>]*>Learn more.*?</a>', '', rows, flags=re.S)
    subp = f'<p class="S" data-a="up" data-d="0">{sub}</p>\n' if sub else ''
    return (f'<section id="{id_}" class="sec" style="background: {bg}">\n<div class="wrap chap">\n<div class="chap-head">\n'
            f'<span class="badge6" data-a="up" data-d="0" style="background: #0A0F2C; color: #FFFFFF">{esc(badge)}</span>\n'
            f'<h2 class="H" data-a="up" data-d="0" style="font-size: clamp(28px, 2.8vw, 38px); margin-top: 22px">{h2}</h2>\n'
            f'{subp}{side}</div>\n{rows}\n</div>\n'
            + (f'<div class="wrap">{after}</div>\n' if after else '') + '</section>\n')


TICK = '<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5 9-10"></path></svg>'


def feature_grid(items, visual=None):
    """Editorial numbered list: outlined numbers that fill on hover, optional text and proof tag. items: (title, text or None, tag or None)."""
    short = all(not d and not tag for _, d, tag in items)
    rows = []
    for i, (t, d, tag) in enumerate(items):
        body = f'<h3>{esc(t)}</h3>' + (f'<p>{esc(d)}</p>' if d else '') + (f'<span class="ftag"><i>{TICK}</i>{esc(tag)}</span>' if tag else '')
        rows.append(f'<article class="fitem" data-a="up" data-d="0"><span class="fnum" aria-hidden="true">{i + 1:02d}</span><div>{body}</div></article>')
    return f'<div class="flist{" short" if short else ""}">' + ''.join(rows) + '</div>'


def numbered_cards(items, cols=None):
    return feature_grid([(t, d, None) for t, d in items])


def svc_rows():
    s = read('sections', 'rpo.html')
    return s[s.index('<!--@svcrows-->') + len('<!--@svcrows-->'):s.index('<!--/@svcrows-->')]


# ---------------------------------------------------------------- schema

ORG = {'@type': 'Organization', '@id': BASE_URL + '#org', 'name': 'CCMS Ltd', 'url': BASE_URL,
       'logo': BASE_URL + LOGO, 'slogan': 'Where quality matters.',
       'description': 'Dedicated offshore back office teams in Sri Lanka for UK recruitment agencies and other UK businesses.'}


def schema(path, crumbs, faqs=None, service=None):
    graph = [ORG]
    if crumbs:
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': t, 'item': BASE_URL + p} for i, (t, p) in enumerate(crumbs)]})
    if service:
        graph.append({'@type': 'Service', 'name': service[0], 'description': service[1], 'serviceType': service[0],
                      'provider': {'@id': BASE_URL + '#org'}, 'areaServed': {'@type': 'Country', 'name': 'United Kingdom'},
                      'url': BASE_URL + path})
    if faqs:
        graph.append({'@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]})
    return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=1).replace('</', '<\\/')


def describe(text, limit=158):
    text = re.sub(r'<[^>]+>', '', text)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(' ', 1)[0].rstrip(',;:')
    return cut + '.' if not cut.endswith('.') else cut


# ---------------------------------------------------------------- page assembly

PAGES = []


def add_page(path, title, desc, hero_html, body, crumbs=None, faqs=None, service=None, industry=0, plan=True):
    PAGES.append(dict(path=path, title=title, desc=desc, hero=hero_html, body=body, crumbs=crumbs,
                      faqs=faqs or [], service=service, industry=industry, plan=plan))
    if not plan:
        PAGES[-1]['hero'] = strip_plan(hero_html)


def render(p):
    depth = p['path'].count('/')
    R = './' if depth == 0 else '../' * depth
    plan_href = '#plan' if p['plan'] else '%%R%%#plan'
    current = p['path']
    crumbs_ld = None
    if p['crumbs']:
        crumbs_ld = [('Home', '')] + [(t, h) for t, h in p['crumbs']]
    cfg = json.dumps({'industry': p['industry'], 'faqCount': len(p['faqs']), 'clouds': p['path'] != ''})
    page = f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p['title'])}</title>
<meta name="description" content="{attr(p['desc'])}">
<link rel="canonical" href="{BASE_URL + p['path']}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="CCMS">
<meta property="og:title" content="{attr(p['title'])}">
<meta property="og:description" content="{attr(p['desc'])}">
<meta property="og:url" content="{BASE_URL + p['path']}">
<link rel="icon" type="image/png" href="%%R%%assets/favicon.png">
<script type="application/ld+json">
{schema(p['path'], crumbs_ld, p['faqs'], p['service'])}
</script>
<script>window.CCMS_PAGE = {cfg};</script>
<script src="%%R%%vendor/react.js"></script>
<script src="%%R%%vendor/react-dom.js"></script>
<script src="%%R%%support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{STYLES}</helmet>
<div class="c">
<!-- ============ HERO ============ -->
<section id="top" data-ccms="hero" style="position: relative; overflow: hidden; background: #0A0F2C; color: #FFFFFF">
<canvas data-ccms="hero-canvas" aria-hidden="true" style="position: absolute; inset: 0; width: 100%; height: 100%; display: block; pointer-events: none; z-index: 0"></canvas>
{header(current, plan_href)}{p['hero']}</section>
{p['body']}<!-- ============ CTA + FOOTER ============ -->
{CTA}</div>
</x-dc>
{SCRIPT_OPEN}{LOGIC}</script>
</body>
</html>
'''
    page = page.replace('./assets/', '%%R%%assets/').replace('%%R%%', R)
    out = os.path.join(ROOT, p['path'], 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        f.write(page)
    return out


# ---------------------------------------------------------------- pages

def build_home():
    hero_html = read('home-hero.html').replace('%%TEAMPLAN%%', TEAMPLAN)
    s = lambda n: read('sections', n + '.html')
    other = sec('industries', head('Other industries we support', 'The same standards, beyond recruitment') +
                '<div class="g-cards3" style="margin-top: 44px">' + ''.join(
                    link_card(page_url('industries/%s/' % g['slug']), g['img'], 'Other industries', g['chip'], g['name'], g['intro'], 'Explore ' + g['name']) for g in GROUPS) + '</div>' +
                f'<div class="dpanel" data-a="up" data-d="0"><div><b style="font-size: 18px">Digital services</b> <span style="color: var(--ink2)">Software development, website development and SEO, from our in-house team.</span></div><a class="lk" href="%%R%%digital/" style="color:#2238D6">Explore digital {ARROW}</a></div>',
                'var(--s1)')
    body = (s('clients') + '<!-- ============ PROBLEM ============ -->\n' + s('problem') +
            '<!-- ============ WHAT WE DO ============ -->\n' + s('answer') +
            '<!-- ============ OUTCOME ============ -->\n' + s('outcome') +
            '<!-- ============ WHY CCMS ============ -->\n' + s('why') +
            '<!-- ============ RPO ============ -->\n' + s('rpo').replace('<!--@svcrows-->', '').replace('<!--/@svcrows-->', '') +
            '<!-- ============ WHO WE WORK WITH ============ -->\n' + sectors_section() +
            '<!-- ============ RESULTS ============ -->\n' + results_section() +
            '<!-- ============ HOW IT WORKS ============ -->\n' + s('how') +
            '<!-- ============ WHY SRI LANKA ============ -->\n' + s('people') +
            '<!-- ============ OTHER INDUSTRIES ============ -->\n' + other +
            '<!-- ============ SECURITY ============ -->\n' + s('safety') +
            '<!-- ============ FAQ ============ -->\n' + faq_section(HOME_FAQS))
    add_page('', 'Offshore Back Office Teams for UK Recruitment Agencies | CCMS',
             'Dedicated back office teams in Sri Lanka for UK recruitment agencies: compliance, bookings, payroll, finance and resourcing, on UK hours.',
             hero_html, body, faqs=HOME_FAQS)


def build_rpo():
    path = 'recruitment-process-outsourcing/'
    intro = 'Your consultants should spend their day placing candidates and winning clients. CCMS gives you a dedicated back office team that handles compliance, bookings, payroll, finance and resourcing. The team works only for you, in your CRM, on UK hours.'
    why = sec('why', head('Why CCMS', 'Why agencies <span style="color: #8A909C">choose CCMS</span>') + feature_grid(RPO_REASONS, 'report'), 'var(--s1)')
    services = (f'<section id="services" class="sec" style="background: #FFFFFF">\n<div class="wrap chap">\n<div class="chap-head">\n'
                f'<span class="badge6" data-a="up" data-d="0" style="background: #0A0F2C; color: #FFFFFF">RPO</span>\n'
                f'<h2 class="H" data-a="up" data-d="0" style="font-size: clamp(32px, 3.4vw, 46px); margin-top: 22px">Six services. <span style="color: #8A909C">One dedicated team.</span></h2>\n'
                f'<p class="S" data-a="up" data-d="0">Recruitment back office is relationship work, heavy on compliance, with no room for error. It is where we started, and it is what we do best.</p>\n'
                f'</div>\n{svc_rows()}\n</div>\n</section>\n')
    faqs = HOME_FAQS
    body = why + services + sectors_section() + results_section() + faq_section(faqs)
    h = hero([('Home', '%%R%%'), ('RPO', None)], 'Recruitment process outsourcing', 'RPO for UK recruitment agencies', intro,
             [btn_call(), btn_line('See the services', '#services')], plan_hook())
    add_page(path, 'RPO for UK Recruitment Agencies | CCMS', describe(intro), h, body,
             crumbs=[('RPO', path)], faqs=faqs, service=('Recruitment process outsourcing', intro))


def build_recruitment(r):
    path = 'industries/%s/' % r['slug']
    names = {s['slug']: s['name'] for s in SERVICES}
    handle = svc_section('roles', 'What your team <span style="color: #8A909C">can handle</span>', None,
                         [(x[0], names[x[1]]) for x in r['roles']], badge=r['name'], after=rules_box(r['rules']))
    pains = pain_section(r['pains'], 'var(--s1)', recruitment=True)
    proof = results_section() if r['proof'] == 'novello' else proof_section(PROOF_LINE)
    body = pains + handle + proof + faq_section(r['faqs'])
    h = hero([('Home', '%%R%%'), ('RPO', '%%R%%recruitment-process-outsourcing/'), (r['name'], None)],
             r['name'] + ' agencies', esc(r['h1']), r['intro'],
             [btn_call(), btn_line('See what your team can handle', '#roles')], plan_hook())
    add_page(path, r['title'], describe(r['intro']), h, body,
             crumbs=[('RPO', 'recruitment-process-outsourcing/'), (r['name'], path)], faqs=r['faqs'],
             service=('Back office teams for ' + r['name'].lower() + ' agencies', r['intro']), industry=r['industry'])


def build_service(sv, mocks):
    path = 'services/%s/' % sv['slug']
    faqs = [HOME_FAQS[i] for i in sv['faqs']]
    does = '<div class="mini" data-a="up" data-d="0" style="margin-top: 26px; background: #FFFFFF">' + ''.join(
        f'<div class="mrow"><span style="width: 20px; height: 20px; flex-shrink: 0; border-radius: 50%; background: #1B7A4A; display: flex; align-items: center; justify-content: center"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5 9-10"></path></svg></span><span style="flex: 1">{esc(d)}</span></div>' for d in sv['does']) + '</div>'
    body = (svc_section('does', 'What your team <span style="color: #8A909C">does</span>', esc(sv['short']), [(sv['name'], sv['name'])], side=does, badge=sv['name'], bg='var(--s1)', links=False) +
            sec('standards', head('Quality', 'How we keep standards') + numbered_cards([(t, None) for t in STANDARDS], 'g-nums')) +
            sec('sectors', head('Who we work with', 'For healthcare, education and construction agencies') + '<div style="margin-top: 44px">' + recruitment_cards() + '</div>', 'var(--s1)') +
            faq_section(faqs))
    card = '<div class="hh-card">' + mocks[sv['name']] + '</div>'
    h = hero([('Home', '%%R%%'), ('Services', '%%R%%recruitment-process-outsourcing/#services'), (sv['name'], None)],
             'Services', esc(sv['h1']), sv['intro'], [btn_call(), btn_line('What your team does', '#does')],
             hook(hook_left(esc(sv['name']), esc(sv['short'])), card))
    add_page(path, sv['h1'] + ' | CCMS', describe(sv['intro']), h, body,
             crumbs=[(sv['name'], path)], faqs=faqs,
             service=(sv['h1'], sv['intro']), plan=False)


def build_sector(sc):
    path = 'industries/%s/' % sc['slug']
    g = next(x for x in GROUPS if x['slug'] == sc['group'])
    handle = sec('roles', head('Your team', 'What your team can handle') + numbered_cards([(x, None) for x in sc['roles']]) + rules_box(sc['rules']))
    proof = proof_section(PROOF_LINE + ' Now bringing the same standards to ' + sc['short'] + '.')
    body = pain_section(sc['pains'], 'var(--s1)') + handle + proof + faq_section(sc['faqs'])
    h = hero([('Home', '%%R%%'), (g['name'], page_url('industries/%s/' % g['slug'])), (sc['name'], None)],
             sc['name'], esc(sc['h1']), sc['intro'], [btn_call(), btn_line('See what your team can handle', '#roles')],
             plan_hook())
    add_page(path, sc['h1'] + ' | CCMS', describe(sc['intro']), h, body,
             crumbs=[(g['name'], 'industries/%s/' % g['slug']), (sc['name'], path)], faqs=sc['faqs'],
             service=(sc['h1'], sc['intro']), industry=sc['industry'])


def build_group(g):
    path = 'industries/%s/' % g['slug']
    secs = [s for s in SECTORS if s['group'] == g['slug']]
    imgs = ['ed3e8c66f268d39a0f6e8cb060b92af4.jpg', 'd45bde67a2d819b341e5acb1c7721081.jpg', '2d0ce4a076ef8df54705d9622d174413.jpg', '1cb1da7470562d009acabbf10e59b8b0.jpg']
    cards = ''.join(link_card(page_url('industries/%s/' % s['slug']), imgs[i % 4], g['name'], g['chip'], s['name'], s['intro'], 'Explore ' + s['name'].lower()) for i, s in enumerate(secs))
    grid = 'g-cards2' if len(secs) % 2 == 0 else 'g-cards3'
    body = (sec('sectors', head('Sectors', 'Sectors we support') + f'<div class="{grid}" style="margin-top: 44px">{cards}</div>', 'var(--s1)') +
            proof_section(PROOF_LINE + ' Now bringing the same standards to ' + g['name'].lower() + '.'))
    rows = [(s['name'], None, page_url('industries/%s/' % s['slug'])) for s in secs]
    h = hero([('Home', '%%R%%'), (g['name'], None)], 'Other industries', esc(g['name']), g['intro'],
             [btn_call(), btn_line('See the sectors', '#sectors')],
             hook(hook_left('The same standards', esc(PROOF_LINE)), list_card('Sectors', rows)))
    add_page(path, g['name'] + ' Back Office Teams | CCMS', describe(g['intro']), h, body,
             crumbs=[(g['name'], path)], plan=False)


def build_why_sri_lanka():
    path = 'why-sri-lanka/'
    intro = "We didn't pick Sri Lanka from a spreadsheet. Our founder moved here in 2016 to build a team for a UK healthcare recruitment agency. What he found was people who wanted careers, not just jobs. That is still why we are here."
    clock = ('<div class="hh-card"><div style="font-size: 13px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--ink3)">Time difference</div>'
             '<div class="clk" style="margin-top: 12px"><div><span>UK summer</span><b>+4.5 hrs</b></div><div><span>UK winter</span><b>+5.5 hrs</b></div></div>'
             '<div class="hh-list" style="margin-top: 8px"><div><span>Early starts, evenings and weekends</span></div><div><span>Up to 24/7, where you need it</span></div></div></div>')
    s1 = sec('time', '<div class="g-kandy"><div>' + head('UK time', 'A team that works on UK time',
             'Sri Lanka is 4.5 hours ahead of the UK in summer and 5.5 hours in winter. Your team starts when your day starts. Need early starts, evenings, weekends or round-the-clock cover? We can work up to 24/7, where you need it.') +
             '</div>' + clock.replace('class="hh-card"', 'class="card6 sh" data-a="up" data-d="0" style="padding: 24px"') + '</div>')
    s2 = sec('hiring', head('Hiring', 'We interview 20 people for every one we hire',
                            'We hire for attitude first, then skills. Every candidate is tested on spoken and written English. Then we train them on your systems, processes and tone before they go live.') +
             numbered_cards([('Attitude first', 'We hire for attitude first, then skills.'), ('English tested', 'Every candidate is tested on spoken and written English.'), ('Trained your way', 'We train them on your systems, processes and tone before they go live.')]), 'var(--s1)')
    people = read('sections', 'people.html')
    photos = people[people.index('<div class="g-kph">'):people.rindex('</div>\n</section>')]
    s3 = sec('careers', '<div class="g-kandy"><div>' + head('Careers', 'Careers, not stopovers',
             "Our office sits outside the busy outsourcing hubs, so our people aren't poached by the next call centre down the road. They build long careers with us. It is why 8 of our first 10 hires are still with us.") +
             '</div>' + photos + '</div>' + stat_cards([('200+', 'people'), ('8 of 10', 'first hires still with us'), ('1 in 20', 'candidates hired')], cols='repeat(auto-fit, minmax(200px, 1fr))'))
    s4 = sec('data', head('Security', "Your data is safe. Your work doesn't stop.") + feature_grid([(x, None, None) for x in ['Controlled office access', 'No personal devices', 'Backup power and internet', 'UK GDPR agreements (IDTA)', 'Quality checked independently', 'ISO 9001, Cyber Essentials (in progress)']]), 'var(--s1)')
    s5 = sec('founder', '<div class="founder"><div class="ph5 has-img" style="min-height: 360px; border-radius: 22px" role="img" aria-label="The CCMS team in Sri Lanka"><img class="phi" src="%%R%%assets/d45bde67a2d819b341e5acb1c7721081.jpg" alt="" loading="lazy"></div><div>' +
             head('Our story', 'Founder-led since day one',
                  'Danu, our founder, has worked in UK healthcare recruitment since 2011, rising from recruiter to operations director. In 2016 he moved to Sri Lanka to set up an offshore team for a UK agency. He saw what most offshore providers got wrong: they sold volume, when agencies needed quality. So he built CCMS to do it properly, and we have grown by referral ever since.') +
             '</div></div>')
    band = sec('meet', f'''<div class="cta-band" data-a="up" data-d="0" style="background-color: #0A0F2C; background-image: radial-gradient(60% 120% at 85% 50%, rgba(47,75,255,.35), rgba(47,75,255,0) 70%), radial-gradient(rgba(255,255,255,.07) 1px, transparent 1.2px); background-size: auto, 18px 18px">
<div style="position: relative; flex: 1 1 380px">
<div style="font-size: clamp(24px, 2.6vw, 34px); font-weight: 800; letter-spacing: -.03em; line-height: 1.1">Meet the team behind your team.</div>
<div style="margin-top: 8px; color: #C9D0EE">A 30-minute call, no obligation.</div>
<div style="margin-top: 22px; display: flex; gap: 10px; flex-wrap: wrap"><a class="btn btn-white" href="#contact">Book a call {ARROW_UP}</a><a class="btn btn-line" href="%%R%%#plan">Build your team</a></div>
</div>
</div>''')
    h = hero([('Home', '%%R%%'), ('Why Sri Lanka', None)], 'Why Sri Lanka', 'Why Sri Lanka?', intro,
             [btn_call(), btn_line('Our story', '#founder')], s1)
    add_page(path, 'Why Sri Lanka | Offshore Back Office Teams | CCMS', describe(intro), h,
             s1 + s2 + s3 + s4 + s5 + band, crumbs=[('Why Sri Lanka', path)], plan=False)


def build_case_studies():
    path = 'case-studies/'
    cards = []
    for c in CASE_STUDIES[1:]:
        stats = ''.join(f'<div><div class="cs-n" style="color:{c["color"] if i == 0 else "var(--ink)"}">{esc(n)}</div><div class="cs-l">{esc(l)}</div></div>' for i, (n, l) in enumerate(c['stats']))
        cards.append(f'''<article class="card6 sh cs-card" data-a="up" data-d="0">
<div class="cs-img" style="height:220px"><img src="%%R%%assets/{c['img']}" alt="" loading="lazy" style="object-position:center 35%"><span class="cs-chip"><i style="background:{c['color']}"></i>{esc(c['chip'])}</span></div>
<div style="display:flex;flex-direction:column;flex:1;padding:22px 14px 10px">
<div class="cs-meta"><b>Case study</b><span aria-hidden="true">·</span>{esc(c['name'])}</div>
<h2 class="cs-t" style="font-size:clamp(22px,2vw,28px)">{esc(c['title'])}</h2>
''' + (f'<p class="cs-x">{esc(c["text"])}</p>\n' if c['text'] else '') + (f'<div class="cs-stats" style="grid-template-columns: repeat({len(c["stats"])}, 1fr)">{stats}</div>\n' if stats else '') + '</div>\n</article>')
    feat = novello_feature().replace('<a class="card6 sh h6t cs-feat" data-a="up" data-d="0" href="%%R%%case-studies/">', '<article class="card6 sh cs-feat" data-a="up" data-d="0">').replace('</a>', '</article>')
    feat = re.sub(r'<span class="lk"[^>]*>See all case studies.*?</span>\n', '', feat, flags=re.S)
    feat = feat.replace('<h3 class="cs-t"', '<h2 class="cs-t"').replace('</h3>', '</h2>')
    feat = feat.replace('<p class="cs-x">25 of 26 nurses rated the service 10/10.</p>', '<p class="cs-x">A 12-week trial with 2 compliance officers. 25 of 26 nurses rated the service 10/10.</p>')
    body = sec('stories', feat + '<div class="cs-row">' + ''.join(cards) + '</div>' +
               '<div class="proofl" data-a="up" data-d="0"><div><b>Most of our clients came by referral.</b> <span style="color: var(--ink2)">Many have added work without being asked.</span></div><a class="btn btn-accent" href="#contact">Book a call ' + ARROW_UP + '</a></div>', 'var(--s1)')
    rows = [(c['name'], c['title'], None) for c in CASE_STUDIES]
    intro = 'Real results for UK recruitment agencies, from audit-ready compliance files to bookings teams that grew from 2 to 50+ people in a year.'
    h = hero([('Home', '%%R%%'), ('Case studies', None)], 'Case studies', 'Results our clients see', intro,
             [btn_call(), btn_line('Read the stories', '#stories')],
             hook(hook_left('Proof', esc(PROOF_LINE), None, [RESULT_STATS[0], RESULT_STATS[1], ('25 of 26', 'Novello nurses rated us 10/10')]),
                  list_card('Case studies', rows)))
    add_page(path, 'Case Studies | CCMS', describe(intro), h, body, crumbs=[('Case studies', path)], plan=False)


def build_digital():
    path = 'digital/'
    s = read('digital-section.html')
    s = s.replace('<section id="digital" class="sec" style="background: var(--s1)">', '<section id="services" class="sec" style="background: var(--s1)">')
    for ph, anchor in [('[SOFTWARE-URL]', 'software'), ('[WEBSITE-URL]', 'website'), ('[SEO-URL]', 'seo')]:
        s = s.replace(f'href="{ph}"', 'href="#contact"')
    s = s.replace('>Learn more <svg', '>Talk to us <svg')
    s = re.sub(r'<h2 class="H"[^>]*>The tech behind your business, built by our in-house team\.</h2>', '<h2 class="H" data-a="up" data-d="0">Software, websites and SEO</h2>', s)
    s = s.replace('<span class="badge6" data-a="up" data-d="0"', '<span class="badge6" data-a="up" data-d="0"')
    arts = re.findall(r'<article class="card6 sh h6t"', s)
    for aid in ['software', 'website', 'seo']:
        s = s.replace('<article class="card6 sh h6t"', f'<article id="{aid}" class="card6 sh h6t"', 1)
    intro = 'The same team that builds our own systems can build yours. Same standards, same ownership of the outcome. On its own, or alongside your back office team.'
    rows = [('Software development', 'Custom systems, portals and integrations', '#software'),
            ('Website development', 'Fast, mobile-first websites', '#website'),
            ('SEO', 'Get found by the clients searching for you', '#seo')]
    h = hero([('Home', '%%R%%'), ('Digital', None)], 'Digital services', 'The tech behind your business, built by our in-house team.', intro,
             [btn_call(), btn_line('See digital services', '#services')],
             hook(hook_left('Digital', 'Built by our in-house team', None), list_card('Digital services', rows)))
    add_page(path, 'Digital Services: Software, Websites and SEO | CCMS', describe(intro), h, s,
             crumbs=[('Digital', path)], service=('Software development, website development and SEO', intro), plan=False)


def text_section(id_, blocks, bg='#FFFFFF'):
    body = ''.join(f'<h2 style="margin: 36px 0 0; font-size: 24px; font-weight: 800; letter-spacing: -.02em">{esc(h)}</h2>' +
                   ''.join(f'<p style="margin: 12px 0 0; font-size: 17px; line-height: 1.7; color: var(--ink2)">{esc(p)}</p>' for p in ps)
                   for h, ps in blocks)
    return f'<section id="{id_}" class="sec" style="background: {bg}">\n<div class="wrap" style="max-width: 820px">\n{body}\n</div>\n</section>\n'


FOUNDER = 'Danu, our founder, has worked in UK healthcare recruitment since 2011, rising from recruiter to operations director. In 2016 he moved to Sri Lanka to set up an offshore team for a UK agency. He saw what most offshore providers got wrong: they sold volume, when agencies needed quality. So he built CCMS to do it properly, and we have grown by referral ever since.'


def build_our_story():
    path = 'our-story/'
    intro = "We've never chased volume. We built CCMS on one idea: do fewer things, and do them properly."
    timeline = list_card('Our story', [('2011', 'Danu starts in UK healthcare recruitment', None),
                                       ('2016', 'Moves to Sri Lanka to build an offshore team for a UK agency', None),
                                       ('Today', '200+ people, 20+ UK clients, grown by referral', None)])
    founder = sec('founder', '<div class="founder"><div class="ph5 has-img" style="min-height: 360px; border-radius: 22px" role="img" aria-label="The CCMS team in Sri Lanka"><img class="phi" src="%%R%%assets/d45bde67a2d819b341e5acb1c7721081.jpg" alt="" loading="lazy"></div><div>' +
                  head('Founder', 'Founder-led since day one', FOUNDER) + '</div></div>')
    reasons = sec('timeline', head('Our story', 'From recruiter to CCMS') + feature_grid([
        ('2011', 'Danu starts in UK healthcare recruitment, rising from recruiter to operations director.', None),
        ('2016', 'He moves to Sri Lanka to set up an offshore team for a UK agency.', None),
        ('Today', '200+ people and 20+ UK clients, grown by referral.', None)]), 'var(--s1)')
    h = hero([('Home', '%%R%%'), ('Our story', None)], 'Our story', 'Built by a recruiter, for recruiters', intro,
             [btn_call(), btn_line('Meet the founder', '#founder')],
             hook(hook_left('Since 2011', 'In UK healthcare recruitment since 2011', None), timeline))
    add_page(path, 'Our Story | CCMS', describe(intro + ' ' + FOUNDER), h, founder + reasons,
             crumbs=[('Our story', path)], plan=False)


def build_careers():
    path = 'careers/'
    intro = "Our office sits outside the busy outsourcing hubs, so our people aren't poached by the next call centre down the road. They build long careers with us."
    points = numbered_cards([
        ('Careers, not stopovers', 'It is why 8 of our first 10 hires are still with us.'),
        ('Training from day one', 'We invest in careers and training, and train every new starter on the systems, processes and tone of the team they join.'),
        ('Attitude first', 'We hire for attitude first, then skills. Every candidate is tested on spoken and written English.')])
    body = sec('life', head('Life at CCMS', 'A place to build a career', None) + points +
               stat_cards([('200+', 'people'), ('8 of 10', 'first hires still with us'), ('1 in 20', 'candidates hired')], 16, 'repeat(auto-fit, minmax(200px, 1fr))'), 'var(--s1)')
    people = read('sections', 'people.html')
    photos = people[people.index('<div class="g-kph">'):people.rindex('</div>\n</section>')]
    body += sec('team', head('Our team', 'Our team in Sri Lanka') + f'<div style="margin-top: 44px">{photos}</div>')
    h = hero([('Home', '%%R%%'), ('Careers', None)], 'Careers', 'Careers at CCMS', intro,
             [f'<a class="btn btn-white" href="%%R%%contact/">Get in touch {ARROW_UP}</a>', btn_line('Life at CCMS', '#life')],
             hook(hook_left('Join us', 'Careers, not stopovers', 'We interview around 20 people for every one we hire, and our managers are measured on keeping teams stable.', [('200+', 'people'), ('8 of 10', 'first hires still with us')]),
                  list_card('Teams we hire for', [(s['name'], s['short'], None) for s in SERVICES[:5]])))
    add_page(path, 'Careers | CCMS', describe(intro), h, body, crumbs=[('Careers', path)], plan=False)


def build_contact():
    path = 'contact/'
    intro = 'A 30-minute call, no obligation. You leave with a suggested team, a timeline and clear next steps.'
    rows = [('A real person replies within one UK working day.', None, None),
            ('Founder-led, from the very first call.', None, None),
            ('UK GDPR protected', None, None)]
    h = hero([('Home', '%%R%%'), ('Contact', None)], 'Contact', 'Tell us what you need. We\'ll show you your team.', intro,
             [btn_call(), btn_line('Get a team plan', '%%R%%#plan')],
             hook(hook_left('Book a call', 'Book your 30-minute call', 'Tell us a little about your business below. It takes a minute.', None),
                  list_card('What to expect', rows)))
    add_page(path, 'Contact CCMS | Book a Call', describe(intro), h, '', crumbs=[('Contact', path)], plan=False)


def build_privacy():
    path = 'privacy/'
    intro = 'How CCMS Ltd uses the details you give us on this website.'
    blocks = [
        ('Who we are', ['CCMS Ltd builds and manages dedicated back office teams for UK businesses, with an operations centre in Sri Lanka.']),
        ('What we collect', ['When you book a call or ask for a team plan, we ask for your name, work email, company and, if you choose, your phone number, plus details about the team you need.']),
        ('How we use it', ['We use these details only to arrange and prepare for your call and to send the team plan you asked for. We do not sell your details or share them for marketing.']),
        ('Your rights', ['Under UK GDPR you can ask to see, correct or delete the details we hold about you at any time. Contact us and we will reply within one UK working day.']),
        ('Client data', ['Every client signs a UK GDPR data agreement (IDTA) before their team starts work. Client teams work on secure company equipment in a controlled office and see only what each task needs.']),
    ]
    h = hero([('Home', '%%R%%'), ('Privacy', None)], 'Privacy', 'Privacy policy', intro, [btn_line('Cookie policy', '%%R%%cookies/')],
             hook(hook_left('UK GDPR', 'Your details are only used to arrange your call', None),
                  list_card('On this page', [(b[0], None, None) for b in blocks])))
    add_page(path, 'Privacy Policy | CCMS', describe(intro), h, text_section('policy', blocks), crumbs=[('Privacy', path)], plan=False)


def build_cookies():
    path = 'cookies/'
    intro = 'This website does not use cookies for tracking or advertising.'
    blocks = [
        ('Cookies on this website', ['This website does not set cookies for tracking, analytics or advertising.']),
        ('Fonts', ['Our fonts are loaded from Google Fonts, which receives your IP address so it can send the font files. Google Fonts does not set cookies on this website.']),
        ('Changes', ['If we add analytics or other cookies in future, we will update this page and ask for your consent first.']),
    ]
    h = hero([('Home', '%%R%%'), ('Cookies', None)], 'Cookies', 'Cookie policy', intro, [btn_line('Privacy policy', '%%R%%privacy/')],
             hook(hook_left('Cookies', 'No tracking cookies', None), list_card('On this page', [(b[0], None, None) for b in blocks])))
    add_page(path, 'Cookie Policy | CCMS', describe(intro), h, text_section('policy', blocks), crumbs=[('Cookies', path)], plan=False)


def write_extras():
    urls = [p['path'] for p in PAGES]
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in urls:
            f.write(f'  <url><loc>{BASE_URL + u}</loc></url>\n')
        f.write('</urlset>\n')
    with open(os.path.join(ROOT, 'robots.txt'), 'w') as f:
        f.write(f'User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n')


def main():
    global STYLES, CTA, SCRIPT_OPEN, LOGIC, TEAMPLAN
    STYLES = read('styles.css')
    CTA = read('cta-footer.html')
    SCRIPT_OPEN = read('script-open.html')
    LOGIC = read('logic.js')
    TEAMPLAN = read('teamplan-card.html').rstrip()
    mocks = svc_mocks()
    build_home()
    build_rpo()
    for r in RECRUITMENT:
        build_recruitment(r)
    for sv in SERVICES:
        build_service(sv, mocks)
    for g in GROUPS:
        build_group(g)
    for sc in SECTORS:
        build_sector(sc)
    build_why_sri_lanka()
    build_case_studies()
    build_digital()
    build_our_story()
    build_careers()
    build_contact()
    build_privacy()
    build_cookies()
    for p in PAGES:
        render(p)
    write_extras()
    print('Built %d pages' % len(PAGES))


if __name__ == '__main__':
    main()
