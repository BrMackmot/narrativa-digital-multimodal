#!/usr/bin/env python3
"""Genera docs/index.html a partir de content.json y de las fotos de assets/fotos/.

    python build.py            # construye y avisa de lo pendiente
    python build.py --strict   # falla si quedan [marcadores] sin completar

Solo biblioteca estándar. Una foto se publica únicamente si en assets/fotos/fotos.json
tiene "consent": true y un texto "alt".
"""
import argparse, html, json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
FOTOS = ROOT / "assets" / "fotos"
EXT = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_BRACKETS = {"[Película documental]"}   # corchetes legítimos de APA
DARK = {"hook", "data", "turn", "closing"}      # máx. ~40 % de escenas oscuras

URL_RE = re.compile(r"(https?://[^\s<]+)")
TODO_RE = re.compile(r"(\[[^\]]+\])")
ITALIC_RE = re.compile(r"\*([^*]+)\*")


def e(s):
    return html.escape(str(s), quote=True)


def rich(text):
    t = e(text)
    t = TODO_RE.sub(lambda m: m.group(0) if m.group(0) in ALLOWED_BRACKETS
                    else f'<mark class="todo">{m.group(0)}</mark>', t)
    t = ITALIC_RE.sub(r"<em>\1</em>", t)
    return URL_RE.sub(r'<a href="\1" rel="noopener" target="_blank">\1</a>', t)


def btn(link, ghost=False):
    cls = "btn ghost" if ghost else "btn"
    ext = ' target="_blank" rel="noopener"' if link["href"].startswith("http") else ""
    return f'<a class="{cls}" href="{e(link["href"])}"{ext}>{e(link["label"])}</a>'


# ---------------------------------------------------------------- fotos
def load_photos():
    """Devuelve (aprobadas, pendientes). aprobadas: {carpeta: [dict]}; pendientes: [(ruta, motivo)]."""
    meta_path = FOTOS / "fotos.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    ok, pend = {}, []
    if not FOTOS.exists():
        return ok, pend
    for folder in sorted(p for p in FOTOS.iterdir() if p.is_dir()):
        for f in sorted(folder.iterdir()):
            if f.suffix.lower() not in EXT:
                continue
            key = f"{folder.name}/{f.name}"
            m = meta.get(key)
            if not m:
                pend.append((key, "sin entrada en fotos.json")); continue
            if m.get("consent") is not True:
                pend.append((key, 'falta "consent": true')); continue
            if not str(m.get("alt", "")).strip() or str(m.get("alt", "")).strip().startswith("["):
                pend.append((key, 'falta "alt"')); continue
            ok.setdefault(folder.name, []).append({
                "src": f"assets/fotos/{key}", "alt": m["alt"], "caption": m.get("caption", ""),
                "credit": m.get("credit", ""), "territory": folder.name})
    return ok, pend


def figure(path, alt, credit=None, cls="media"):
    if (ROOT / path).exists():
        body = f'<img src="{e(path)}" alt="{e(alt)}" loading="lazy" decoding="async">'
    else:
        body = f'<div class="ph" role="img" aria-label="{e(alt)}"><span>Falta imagen<br><small>{e(path)}</small></span></div>'
    cap = f'<figcaption class="credit">{rich(credit)}</figcaption>' if credit else ""
    return f'<figure class="{cls}">{body}{cap}</figure>'


# ---------------------------------------------------------------- marquee
def marquee(items, style="dark", reverse=False, big=False, speed=None):
    group = "".join(f"<span>{e(i)}</span>" for i in items)
    n = max(1, 14 // max(1, len(items)))          # repite hasta llenar el ancho
    group = group * n
    secs = speed or max(25, len(items) * n * 3.2)
    cls = f"marquee {style}{' rev' if reverse else ''}{' big' if big else ''}"
    return (f'<div class="{cls}" style="--speed:{secs:.0f}s" role="presentation">'
            f'<div class="track"><div class="grp">{group}</div><div class="grp" aria-hidden="true">{group}</div></div></div>')


# ---------------------------------------------------------------- escenas
def kick(n, label):
    return f'<p class="kicker"><b>{n:02d}</b> {e(label)}</p>'


def r_hook(s, n, ctx):
    photos = ctx["photos"].get(s.get("photo_folder", ""), [])
    bg = ""
    if photos:
        p = photos[0]
        bg = (f'<div class="bg"><img src="{e(p["src"])}" alt="{e(p["alt"])}" fetchpriority="high"></div>')
        credit = f'<p class="credit">{rich(p["credit"])}</p>' if p["credit"] else ""
    else:
        bg, credit = '<div class="bg art" aria-hidden="true"></div>', ""
    title = e(s["title"]).replace("CONECTARSE", "<span class='grad'>CONECTARSE</span>")
    return (f'{bg}<div class="inner"><p class="kicker"><b>Narrativa digital multimodal</b></p>'
            f'<h1 class="reveal">{title}</h1><p class="lead reveal" style="--d:.15s">{e(s["subtitle"])}</p>'
            f'<p class="cite reveal" style="--d:.3s">{e(s["tagline"])}</p>'
            f'<a class="scroll-hint" href="#territorio">Explorar <span aria-hidden="true">↓</span></a>{credit}</div>'
            + (marquee(s["marquee"], "glass", big=False) if s.get("marquee") else ""))


def r_territory(s, n, ctx):
    layers = "".join(f'<li class="reveal" style="--d:{i*.1:.1f}s"><strong>{e(l["name"])}</strong>{e(l["desc"])}</li>'
                     for i, l in enumerate(s["layers"]))
    return (f'<div class="inner">{kick(n,"Territorio")}<h2 class="reveal">{e(s["title"])}</h2>'
            f'<p class="lead reveal">{e(s["text"])}</p><ul class="layers">{layers}</ul>'
            f'<p class="cite">{e(s["cite"])}</p>{figure(s["image"], s["alt"], s.get("credit"))}</div>')


def r_data(s, n, ctx):
    stats = "".join(f'<div class="stat reveal" style="--d:{i*.15:.2f}s"><div class="n" data-count="{e(x["value"])}">{e(x["value"])}</div>'
                    f'<p>{e(x["caption"])}</p></div>' for i, x in enumerate(s["stats"]))
    return (f'<div class="inner">{kick(n,"El dato")}<h2 class="reveal">{e(s["title"])}</h2>'
            f'<div class="stats">{stats}</div><p class="cite">{e(s["source"])}</p>{btn(s["link"])}'
            f'<p class="transition reveal">{e(s["transition"])}</p></div>')


def r_turn(s, n, ctx):
    lines = "".join(f'<p class="reveal" style="--d:{.2+i*.9:.1f}s">{e(x)}</p>' for i, x in enumerate(s["lines"]))
    d = .2 + len(s["lines"]) * .9
    return (f'<div class="inner turn">{kick(n,"El giro")}<h2>{e(s["title"])}</h2>'
            f'<div class="lines">{lines}</div><p class="q reveal" style="--d:{d:.1f}s">{e(s["question"])}</p></div>')


def xp_runs(xp):
    """Pruebas del experimento que ya tienen su imagen."""
    return [r for r in (xp or {}).get("runs", []) if (ROOT / r["image"]).exists()]


def xp_ready(xp):
    return bool(xp_runs(xp))


def r_algorithm(s, n, ctx):
    xp = s.get("experiment", {})
    body = ""
    if xp_ready(xp):
        runs = "".join(
            f'<article class="run"><p class="cap">{e(r["label"])}</p>{figure(r["image"], r["alt"])}'
            f'<p class="prompt"><b>Prompt:</b> “{e(r["prompt"])}”</p><p class="obs">{rich(r["observation"])}</p></article>'
            for r in xp_runs(xp))
        concl = ""
        if xp.get("conclusion"):
            concl = (f'<div class="xp-concl"><p class="xp-title">{e(xp["conclusion_title"])}</p>'
                     + "".join(f"<p>{rich(t)}</p>" for t in xp["conclusion"]) + "</div>")
        body = (f'<div class="xp"><p class="xp-title">{e(xp["title"])}</p><div class="runs">{runs}</div>{concl}'
                f'<p class="xp-note">Herramienta: {rich(xp["tool"])} · Fecha: {rich(xp["date"])}. {e(xp["note"])}</p></div>')
    return (f'<div class="inner">{kick(n,"El algoritmo")}<h2 class="reveal">{e(s["title"])}</h2>'
            f'<p class="lead">{e(s["text"])}</p>{body}<p class="bigq reveal">{e(s["question"])}</p>'
            f'<p class="cite">{e(s["cite"])}</p>{btn(s["link"])}</div>')


def r_film(s, n, ctx):
    kw = "".join(f"<li>{e(k)}</li>" for k in s["keywords"])
    return (f'<div class="inner">{kick(n,"Coded Bias")}<h2 class="reveal">{e(s["title"])}</h2>'
            f'<p class="lead">{e(s["text"])}</p><ul class="keywords">{kw}</ul>'
            f'{figure(s["thumbnail"], s["alt"], s.get("credit")) if s.get("thumbnail") else ""}{btn(s["link"])}<p class="cite">{e(s["ref"])}</p></div>')


def r_voices(s, n, ctx):
    cards = []
    for i, c in enumerate(s["cards"]):
        cards.append(
            f'<details class="card reveal" style="--d:{i*.07:.2f}s"><summary><span class="num">VOZ {c["n"]}</span>'
            f'<h3>{e(c["name"])} <small>({e(c["year"])})</small></h3><span class="meta">{e(c["format"])}</span>'
            f'<span class="tag">{e(c["axis"])}</span><span class="plus" aria-hidden="true">+</span></summary>'
            f'<dl><dt>Qué es</dt><dd>{rich(c["what"])}</dd><dt>Por qué es pertinente</dt><dd>{rich(c["relevance"])}</dd>'
            f'<dt>Por qué es confiable</dt><dd>{rich(c["reliability"])}</dd>'
            f'<dt>Voz que aporta y límite</dt><dd>{rich(c["voice_limit"])}</dd>'
            f'<dt>Se relaciona con</dt><dd>{rich(c["related"])}</dd></dl>'
            f'<a class="btn" href="{e(c["href"])}" target="_blank" rel="noopener">{e(c["button"])} →</a></details>')
    return (f'<div class="inner">{kick(n,"Curaduría")}<h2 class="reveal">{e(s["title"])}</h2>'
            f'<p class="lead">{e(s["text"])}</p><div class="cards">{"".join(cards)}</div>'
            f'<p class="gap reveal">{e(s["gap"])}</p></div>')


def r_field(s, n, ctx):
    cases = []
    for i, c in enumerate(s["cases"]):
        ph = ctx["photos"].get(c.get("photo_folder", ""), [])
        pic = (f'<img src="{e(ph[0]["src"])}" alt="{e(ph[0]["alt"])}" loading="lazy">' if ph else "")
        cases.append(f'<div class="case reveal" style="--d:{i*.15:.2f}s">{pic}<div class="body"><h3>{e(c["place"])}</h3>'
                     f'<p>{rich(c["text"])}</p></div></div>')
    return (f'<div class="inner">{kick(n,"Experiencia situada")}<h2 class="reveal">{e(s["title"])}</h2>'
            f'<p class="lead">{e(s["text"])}</p><div class="cases">{"".join(cases)}</div>'
            f'<p class="caveat">{e(s["caveat"])}</p><p class="bigq reveal">{e(s["closing"])}</p></div>')


def r_gallery(s, n, ctx):
    allp = [p for k in s["territories"] if k in ctx["photos"] for p in ctx["photos"][k] if k != "portada"]
    labels = s["territories"]
    if not allp:
        ghosts = "".join('<div class="tile ghost"><span>Tu foto aquí</span></div>' for _ in range(6))
        return (f'<div class="inner">{kick(n,"Territorio en imágenes")}<h2 class="reveal">{e(s["title"])}</h2>'
                f'<p class="lead">{e(s["text"])}</p><div class="masonry">{ghosts}</div>'
                f'<p class="caveat">{e(s["empty"])}</p></div>')
    imgs = "".join(f'<img src="{e(p["src"])}" alt="" loading="lazy">' for p in allp)
    reps = max(1, 8 // len(allp))
    strip = (f'<div class="marquee photos" style="--speed:{max(30,len(allp)*reps*6)}s" aria-hidden="true">'
             f'<div class="track"><div class="grp">{imgs*reps}</div><div class="grp">{imgs*reps}</div></div></div>')
    tiles = "".join(
        f'<figure class="tile reveal"><button type="button" class="open" data-src="{e(p["src"])}" '
        f'data-cap="{e(p["caption"])}" data-credit="{e(p["credit"])}" aria-label="Ampliar: {e(p["alt"])}">'
        f'<img src="{e(p["src"])}" alt="{e(p["alt"])}" loading="lazy" decoding="async"></button>'
        f'<figcaption><span class="chip">{e(labels.get(p["territory"], p["territory"]))}</span> {e(p["caption"])}</figcaption></figure>'
        for p in allp)
    return (f'<div class="inner">{kick(n,"Territorio en imágenes")}<h2 class="reveal">{e(s["title"])}</h2>'
            f'<p class="lead">{e(s["text"])}</p></div>{strip}<div class="inner"><div class="masonry">{tiles}</div></div>')


def r_analysis(s, n, ctx):
    paras = "".join(f"<p>{rich(p)}</p>" for p in s["paragraphs"])
    return (f'<div class="inner">{kick(n,"Lectura crítica")}<h2>{e(s["title"])}</h2>{paras}'
            f'<p class="wc">Extensión: {word_count(s)} palabras (requisito: {s["min_words"]}–{s["max_words"]}).</p></div>')


def r_response(s, n, ctx):
    steps = "".join(f"<span>{e(x)}</span>" for x in s["steps"])
    return (f'<div class="inner">{kick(n,"Respuesta")}<h2 class="reveal">{e(s["title"])}</h2>'
            f'<p class="lead">{e(s["text"])}</p><div class="steps" aria-label="Recorrido">{steps}</div>'
            f'<a class="shot-link" href="{e(s["link"]["href"])}" target="_blank" rel="noopener" aria-label="Abrir OnLife Afro (se abre en una pestaña nueva)">{figure(s["image"], s["alt"], s.get("credit"))}</a>{btn(s["link"])}<p class="limit">{e(s["limit"])}</p></div>')


def r_closing(s, n, ctx):
    lines = "".join(f'<p class="reveal" style="--d:{i*.18:.2f}s">{e(x)}</p>' for i, x in enumerate(s["lines"]))
    buttons = "".join(btn(b, ghost=True) for b in s["buttons"])
    return (f'<div class="inner">{kick(n,"Cierre")}<h2>{e(s["title"])}</h2>'
            f'<div class="lines">{lines}</div><p class="last reveal" style="--d:1s">{e(s["last"])}</p>{buttons}</div>')


def r_sources(s, n, ctx):
    refs = "".join(f"<li>{rich(r)}</li>" for r in s["references"])
    ai_html = f'<p class="ai">{rich(s["ai_note"])}</p>' if s.get("ai_note", "").strip() else ""
    return (f'<div class="inner">{kick(n,"Fuentes")}<h2>{e(s["title"])}</h2><p>{e(s["text"])}</p>'
            f'<h3>Referencias</h3><ol class="refs">{refs}</ol>'
            f'<p class="cite">{rich(s["credits"])}</p>{ai_html}</div>')


RENDER = {"hook": r_hook, "territory": r_territory, "data": r_data, "turn": r_turn, "algorithm": r_algorithm,
          "film": r_film, "voices": r_voices, "field": r_field, "gallery": r_gallery, "analysis": r_analysis,
          "response": r_response, "closing": r_closing, "sources": r_sources}
NAV = {"territorio": "Territorio", "dato": "Dato", "codedbias": "Coded Bias", "voces": "Voces",
       "experiencia": "Campo", "galeria": "Fotos", "lectura": "Análisis", "onlifeafro": "OnLife Afro", "fuentes": "Fuentes"}


# ---------------------------------------------------------------- utilidades
def word_count(scene):
    text = re.sub(r"\[[^\]]*\]", " ", " ".join(scene["paragraphs"]))
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


def _drop_idle_experiment(data):
    d = json.loads(json.dumps(data))
    for s in d["scenes"]:
        if s.get("type") == "algorithm":
            xp = s.get("experiment", {})
            if xp_ready(xp):
                xp["runs"] = xp_runs(xp)
            else:
                s.pop("experiment", None)
    return d


def pending(data):
    found = set()
    for t in _strings(_drop_idle_experiment(data)):
        found.update(re.findall(r"\[[^\]\[]{3,}\]", t))
    return sorted(found - ALLOWED_BRACKETS)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    data = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    m = data["meta"]
    todo = pending(data)
    photos, held = load_photos()
    if todo:
        print(f"Aviso: {len(todo)} marcadores pendientes por completar (ver check.py).")
        if args.strict:
            print("--strict: construcción cancelada."); sys.exit(1)
    if held:
        print(f"Aviso: {len(held)} foto(s) NO publicadas:")
        for k, why in held: print(f"   {k}: {why}")

    ctx = {"photos": photos}
    sections, n = [], 0
    for s in data["scenes"]:
        if s["type"] == "marquee":
            sections.append(f'<div class="band" id="{e(s["id"])}">{marquee(s["items"], s.get("style","dark"), s.get("reverse",False), s.get("big",False))}</div>')
            continue
        n += 1
        tone = "dark" if s["type"] in DARK else "light"
        inner = RENDER[s["type"]](s, n, ctx)
        inner = inner.replace("<h1 ", f'<h1 id="{s["id"]}-t" ', 1) if "<h1 " in inner else inner.replace("<h2", f'<h2 id="{s["id"]}-t"', 1)
        sections.append(f'<section class="scene {tone} t-{s["type"]}" id="{e(s["id"])}" aria-labelledby="{e(s["id"])}-t">{inner}</section>')
    nav = "".join(f'<a href="#{k}">{v}</a>' for k, v in NAV.items())
    page = f"""<!doctype html>
<html lang="{e(m['lang'])}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(m['title'])}</title>
<meta name="description" content="{e(m['description'])}">
<meta name="author" content="{e(m['author'])}">
<meta name="theme-color" content="#1E120A">
<meta property="og:title" content="{e(m['title'])}"><meta property="og:description" content="{e(m['description'])}"><meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,800;1,9..144,500&family=Inter:wght@400;500;600;700&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<script>document.documentElement.className='js'</script>
</head>
<body>
<a class="skip" href="#lectura">Saltar al análisis</a>
<header class="topbar"><a class="brand" href="#gancho">¿Y si conectarse no fuera suficiente?</a><nav aria-label="Navegación de la narrativa">{nav}</nav><div class="progress" aria-hidden="true"></div></header>
<main>
{chr(10).join(sections)}
</main>
<dialog id="lightbox" aria-label="Foto ampliada"><form method="dialog"><button class="close" aria-label="Cerrar">✕</button></form><img alt=""><p></p></dialog>
<footer><strong>{e(m['author'])}</strong> · {e(m['program'])} · {e(m['university'])} · {e(m['year'])}</footer>
<script src="assets/main.js" defer></script>
</body>
</html>
"""
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    (OUT / ".nojekyll").write_text("")
    cnt = sum(len(v) for v in photos.values())
    print(f"Listo: {OUT / 'index.html'}  ({cnt} foto(s) publicadas)")


if __name__ == "__main__":
    main()
