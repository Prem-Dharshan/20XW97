// Records pptxgenjs calls (with layout placeholder options merged) to JSON for the Google Slides converter.
const fs = require("fs");
class Slide {
  constructor(master) { this.master = master; this.items = []; this.notes = ""; }
  addText(text, o = {}) {
    if (o.placeholder) {
      const ph = this.master.ph[o.placeholder];
      if (!ph) throw new Error("no placeholder " + o.placeholder);
      o = Object.assign({}, ph, o); delete o.placeholder; delete o.name; delete o.type;
    }
    this.items.push({ kind: "text", text, o: JSON.parse(JSON.stringify(o)) });
  }
  addShape(shape, o) { this.items.push({ kind: "shape", shape, o: JSON.parse(JSON.stringify(o)) }); }
  addImage(o) { this.items.push({ kind: "image", o: { ...o } }); }
  addChart(type, data, o) { this.items.push({ kind: "chart", type, data, o: JSON.parse(JSON.stringify(o)) }); }
  addNotes(t) { this.notes = t; }
}
class Pres {
  constructor() {
    this.masters = {}; this.slides = [];
    this.shapes = { RECTANGLE: "RECTANGLE", ROUNDED_RECTANGLE: "ROUND_RECTANGLE", OVAL: "ELLIPSE", LINE: "LINE" };
    this.charts = { BAR: "bar" };
    this.SchemeColor = { text1: "@dk1", text2: "@dk2", background1: "@lt1", background2: "@lt2", accent1: "@accent1", accent2: "@accent2", accent3: "@accent3", accent4: "@accent4", accent5: "@accent5", accent6: "@accent6" };
  }
  defineSlideMaster(m) {
    const ph = {}, objs = [];
    (m.objects || []).forEach((ob) => {
      if (ob.placeholder) ph[ob.placeholder.options.name] = ob.placeholder.options;
      else if (ob.text) objs.push({ kind: "text", text: ob.text.text, o: ob.text.options });
    });
    this.masters[m.title] = { bg: m.background && m.background.color, ph, objs, slideNumber: m.slideNumber };
  }
  addSection() {}
  addSlide(o) { const s = new Slide(this.masters[o.masterName]); s.masterName = o.masterName; this.slides.push(s); return s; }
  async writeFile({ fileName }) {
    const out = this.slides.map((s, i) => ({ master: s.masterName, bg: s.master.bg, layoutObjs: s.master.objs, slideNumber: s.master.slideNumber ? { ...s.master.slideNumber, n: i + 1 } : null, items: s.items, notes: s.notes }));
    fs.writeFileSync(process.env.MOCK_OUT, JSON.stringify(out));
    return fileName;
  }
}
module.exports = Pres;
