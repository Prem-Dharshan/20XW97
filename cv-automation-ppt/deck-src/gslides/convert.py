"""deck.json (recorded pptxgenjs calls) -> Google Slides batchUpdate requests, one file per slide."""
import base64, hashlib, json, os, sys
REPO = "/home/user/20XW97"
RAW = "https://raw.githubusercontent.com/Prem-Dharshan/20XW97/claude/intelligent-bardeen-8vtchx/"
GS = "cv-automation-ppt/gslides"
THEME = {"dk1": "101828", "lt1": "FFFFFF", "dk2": "0B1F33", "lt2": "F2F4F7", "accent1": "F5A300", "accent2": "D92D20",
         "accent3": "12B76A", "accent4": "475467", "accent5": "98A2B3", "accent6": "B54708"}
S = 10 / 13.333          # page scale: 13.333in deck -> 10in Google Slides page
E = 914400
INX, INY = 0.1, 0.05     # Slides default text insets (in), compensated so text sits where pptx put it
deck = json.load(open("deck.json"))
os.makedirs(f"{REPO}/{GS}/icons", exist_ok=True)

def hexc(c):
    c = THEME[c[1:]] if c.startswith("@") else c
    f = lambda v: round(int(v, 16) / 255, 2)
    return {"red": f(c[0:2]), "green": f(c[2:4]), "blue": f(c[4:6])}

def pt(v):
    r = round(v * 72, 1)
    return int(r) if r == int(r) else r

def props(page, x, y, w, h):
    return {"pageObjectId": page, "size": {"width": {"magnitude": max(pt(w), 0.1), "unit": "PT"}, "height": {"magnitude": max(pt(h), 0.1), "unit": "PT"}},
            "transform": {"scaleX": 1, "scaleY": 1, "translateX": pt(x), "translateY": pt(y), "unit": "PT"}}

def runs_of(text, o):
    """Return list of paragraphs, each a list of (text, opts)."""
    paras, cur = [], []
    if isinstance(text, str):
        for i, line in enumerate(text.split("\n")):
            paras.append([(line, {})])
        return paras
    num = (o.get("_numStart") or 1)
    for r in text:
        ro = r.get("options", {})
        t = r["text"]
        if ro.get("bullet", {}) and isinstance(ro.get("bullet"), dict) and ro["bullet"].get("type") == "number":
            start = ro["bullet"].get("numberStartAt", 1)
            t = f"{start + len(paras)}. " + t
        cur.append((t, ro))
        if ro.get("breakLine"):
            paras.append(cur); cur = []
    if cur: paras.append(cur)
    return paras

def text_reqs(page, oid, text, o):
    reqs = []
    x, y, w, h = o["x"] * S - INX, o["y"] * S - INY, o["w"] * S + 2 * INX, o["h"] * S + 2 * INY
    paras = runs_of(text, o)
    full = "\n".join("".join(t for t, _ in p) for p in paras)
    if not full.strip(): return []
    reqs.append({"createShape": {"objectId": oid, "shapeType": "TEXT_BOX", "elementProperties": props(page, x, y, w, h)}})
    reqs.append({"insertText": {"objectId": oid, "text": full}})
    base = {"fontSize": {"magnitude": round(o.get("fontSize", 18) * S, 2), "unit": "PT"}, "foregroundColor": {"opaqueColor": {"rgbColor": hexc(o.get("color", "000000"))}}}
    bf = "fontSize,foregroundColor"
    if o.get("bold"): base["bold"] = True; bf += ",bold"
    reqs.append({"updateTextStyle": {"objectId": oid, "textRange": {"type": "ALL"}, "style": base, "fields": bf}})
    # per-run overrides
    idx = 0
    for p in paras:
        for t, ro in p:
            n = len(t.encode("utf-16-le")) // 2
            st, f = {}, []
            if "bold" in ro: st["bold"] = bool(ro["bold"]); f.append("bold")
            if "color" in ro: st["foregroundColor"] = {"opaqueColor": {"rgbColor": hexc(ro["color"])}}; f.append("foregroundColor")
            if "fontSize" in ro: st["fontSize"] = {"magnitude": round(ro["fontSize"] * S, 2), "unit": "PT"}; f.append("fontSize")
            if f and n:
                reqs.append({"updateTextStyle": {"objectId": oid, "textRange": {"type": "FIXED_RANGE", "startIndex": idx, "endIndex": idx + n}, "style": st, "fields": ",".join(f)}})
            idx += n
        idx += 1
    ps, pf = {}, []
    al = {"left": "START", "center": "CENTER", "right": "END"}.get(o.get("align"), "START")
    if al != "START": ps["alignment"] = al; pf.append("alignment")
    if o.get("paraSpaceAfter"): ps["spaceBelow"] = {"magnitude": o["paraSpaceAfter"] * S, "unit": "PT"}; pf.append("spaceBelow")
    if pf: reqs.append({"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"}, "style": ps, "fields": ",".join(pf)}})
    va = {"top": "TOP", "middle": "MIDDLE", "bottom": "BOTTOM"}.get(o.get("valign"), "TOP")
    if va != "TOP": reqs.append({"updateShapeProperties": {"objectId": oid, "shapeProperties": {"contentAlignment": va}, "fields": "contentAlignment"}})
    return reqs

def shape_reqs(page, oid, shape, o):
    x, y, w, h = o["x"] * S, o["y"] * S, o["w"] * S, o["h"] * S
    ln = o.get("line", {})
    if shape == "LINE":
        r = [{"createLine": {"objectId": oid, "category": "STRAIGHT", "elementProperties": props(page, x, y, w, h)}}]
        lp = {"lineFill": {"solidFill": {"color": {"rgbColor": hexc(ln.get("color", "000000"))}}}, "weight": {"magnitude": round(ln.get("width", 1) * S, 2), "unit": "PT"}}
        f = ["lineFill.solidFill.color", "weight"]
        if ln.get("dashType"): lp["dashStyle"] = {"dash": "DASH", "sysDot": "DOT", "sysDash": "DASH"}.get(ln["dashType"], "SOLID"); f.append("dashStyle")
        if ln.get("endArrowType"): lp["endArrow"] = "FILL_ARROW"; f.append("endArrow")
        r.append({"updateLineProperties": {"objectId": oid, "lineProperties": lp, "fields": ",".join(f)}})
        return r
    r = [{"createShape": {"objectId": oid, "shapeType": shape, "elementProperties": props(page, x, y, w, h)}}]
    sp, f = {}, []
    fill = o.get("fill")
    if fill:
        sf = {"color": {"rgbColor": hexc(fill["color"])}}
        if fill.get("transparency"): sf["alpha"] = round(1 - fill["transparency"] / 100, 2)
        sp["shapeBackgroundFill"] = {"solidFill": sf}; f.append("shapeBackgroundFill.solidFill")
    if ln.get("type") == "none" or not ln:
        sp["outline"] = {"propertyState": "NOT_RENDERED"}; f.append("outline.propertyState")
    else:
        sp["outline"] = {"outlineFill": {"solidFill": {"color": {"rgbColor": hexc(ln.get("color", "000000"))}}}, "weight": {"magnitude": round(ln.get("width", 1) * S, 2), "unit": "PT"}}
        f += ["outline.outlineFill.solidFill.color", "outline.weight"]
        if ln.get("dashType"): sp["outline"]["dashStyle"] = "DASH"; f.append("outline.dashStyle")
    r.append({"updateShapeProperties": {"objectId": oid, "shapeProperties": sp, "fields": ",".join(f)}})
    return r

def img_url(o):
    if o.get("data"):
        b = base64.b64decode(o["data"].split(",", 1)[1])
        h = hashlib.sha1(b).hexdigest()[:12]
        p = f"{GS}/icons/{h}.png"
        if not os.path.exists(f"{REPO}/{p}"): open(f"{REPO}/{p}", "wb").write(b)
        return RAW + p
    return RAW + os.path.relpath(os.path.realpath(o["path"]), REPO)

charts = []
def is_chip(it): return it["kind"] == "shape" and str(it["o"].get("objectName", "")).startswith("stage-chip-")

def chip_info(items):
    """Pull the 5 chip shape+label pairs out; return (rest, active stages, dark)."""
    rest, active, dark, i = [], [], False, 0
    while i < len(items):
        it = items[i]
        if is_chip(it):
            st = it["o"]["objectName"][len("stage-chip-"):]
            if it["o"]["fill"]["color"] == "@accent1": active.append(st)
            elif it["o"]["fill"]["color"] == "1D3550": dark = True
            i += 2; continue
        rest.append(it); i += 1
    return rest, active, dark

STAGES = ["PIXELS", "DETECT", "TRACK", "MEASURE", "ACT"]
templates = {}
def template(dark):
    """A slide holding the 5 inactive chips; content slides duplicate it."""
    tid = "tplDk" if dark else "tplLt"
    if tid in templates: return tid
    reqs = [{"createSlide": {"objectId": tid, "slideLayoutReference": {"predefinedLayout": "BLANK"}}},
            {"updatePageProperties": {"objectId": tid, "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": hexc("0B1F33" if dark else "FFFFFF")}}}}, "fields": "pageBackgroundFill.solidFill.color"}}]
    cw, gap, y, h, W, MX = 0.92, 0.08, 0.42, 0.3, 13.333, 0.6
    x0 = W - MX - (5 * cw + 4 * gap)
    for i, st in enumerate(STAGES):
        x = x0 + i * (cw + gap)
        reqs += shape_reqs(tid, f"{tid}_c{i}", "ROUND_RECTANGLE", {"x": x, "y": y, "w": cw, "h": h, "fill": {"color": "1D3550" if dark else "@lt2"}, "line": {"type": "none"}})
        reqs += text_reqs(tid, f"{tid}_t{i}", st, {"x": x, "y": y, "w": cw, "h": h, "align": "center", "valign": "middle", "fontSize": 9, "bold": True, "color": "@accent5" if dark else "@accent4"})
    templates[tid] = reqs
    return tid

for n, sl in enumerate(deck, 1):
    page = f"gs_{n:02d}"
    items = [{"kind": "text", "text": t["text"], "o": t["o"]} for t in sl["layoutObjs"]] + sl["items"]
    if sl["slideNumber"]:
        sn = dict(sl["slideNumber"]); items.append({"kind": "text", "text": str(sn.pop("n")), "o": sn})
    if any(is_chip(it) for it in items):
        items, active, dark = chip_info(items)
        tid = template(dark)
        ids = {tid: page}
        for i in range(5): ids[f"{tid}_c{i}"] = f"{page}_c{i}"; ids[f"{tid}_t{i}"] = f"{page}_t{i}"
        reqs = [{"duplicateObject": {"objectId": tid, "objectIds": ids}}]
        for st in active:
            i = STAGES.index(st)
            reqs.append({"updateShapeProperties": {"objectId": f"{page}_c{i}", "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": hexc("@accent1")}}}}, "fields": "shapeBackgroundFill.solidFill"}})
            reqs.append({"updateTextStyle": {"objectId": f"{page}_t{i}", "textRange": {"type": "ALL"}, "style": {"foregroundColor": {"opaqueColor": {"rgbColor": hexc("@dk1")}}}, "fields": "foregroundColor"}})
    else:
        reqs = [{"createSlide": {"objectId": page, "slideLayoutReference": {"predefinedLayout": "BLANK"}}},
                {"updatePageProperties": {"objectId": page, "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": hexc(sl["bg"])}}}}, "fields": "pageBackgroundFill.solidFill.color"}}]
    k = 0
    for it in items:
        k += 1; oid = f"{page}_{k}"
        if it["kind"] == "text": reqs += text_reqs(page, oid, it["text"], it["o"])
        elif it["kind"] == "shape": reqs += shape_reqs(page, oid, it["shape"], it["o"])
        elif it["kind"] == "image":
            o = it["o"]
            reqs.append({"createImage": {"objectId": oid, "url": img_url(o), "elementProperties": props(page, o["x"] * S, o["y"] * S, o["w"] * S, o["h"] * S)}})
        elif it["kind"] == "chart":
            o = it["o"]; p = f"{GS}/charts/slide{n:02d}_{k}.png"
            charts.append({"slide": n, "x": o["x"], "y": o["y"], "w": o["w"], "h": o["h"], "path": p})
            reqs.append({"createImage": {"objectId": oid, "url": RAW + p, "elementProperties": props(page, o["x"] * S, o["y"] * S, o["w"] * S, o["h"] * S)}})
    json.dump(reqs, open(f"req/{n:02d}.json", "w"), ensure_ascii=False, separators=(",", ":"))
for tid, r in templates.items():
    json.dump(r, open(f"req/{tid}.json", "w"), ensure_ascii=False, separators=(",", ":"))
json.dump(charts, open("charts.json", "w"))
json.dump([s["notes"] for s in deck], open("notes.json", "w"), ensure_ascii=False)
tot = sum(os.path.getsize(f"req/{f}") for f in os.listdir("req"))
print("slides", len(deck), "templates", list(templates), "total req bytes", tot, "charts", len(charts))
