// Builds "Computer Vision & Automation" deck (pptxgenjs, structured: theme + layouts + sections).
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const lu = require("react-icons/lu");
const { applyTheme } = require(process.env.APPLY_THEME || (process.env.PPTX_SKILL + "/scripts/apply_theme.js"));

const ROOT = path.resolve(__dirname, "..");
const DEMO = path.join(ROOT, "demo/outputs");
const ASSETS = path.join(__dirname, "assets");
const OUT = path.join(ROOT, "CV_and_Automation.pptx");
const DATA = fs.existsSync(path.join(__dirname, "data.json")) ? JSON.parse(fs.readFileSync(path.join(__dirname, "data.json"))) : {};

const THEME = {
  name: "Flyover",
  headFontFace: "Arial",
  bodyFontFace: "Arial",
  colors: {
    dk1: "101828", lt1: "FFFFFF", dk2: "0B1F33", lt2: "F2F4F7",
    accent1: "F5A300", accent2: "D92D20", accent3: "12B76A", accent4: "475467",
    accent5: "98A2B3", accent6: "B54708", hlink: "B54708", folHlink: "475467",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Computer Vision & Automation";
pres.author = "Thithiksha, Arul, DPD";
const C = pres.SchemeColor;
const INK = C.text1, NAVY = C.text2, WHITE = C.background1, LIGHT = C.background2;
const AMBER = C.accent1, RED = C.accent2, GREEN = C.accent3, SLATE = C.accent4, MUTED = C.accent5, AMBER_DK = C.accent6;
const W = 13.333, MX = 0.6;

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: WHITE },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: MX, y: 0.42, w: 7.0, h: 0.3, fontSize: 12, bold: true, color: AMBER_DK, charSpacing: 2, margin: 0, valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 0.78, w: W - 2 * MX, h: 0.75, fontSize: 30, bold: true, color: NAVY, margin: 0, valign: "top", align: "left" }, text: "" } },
    { text: { text: "Computer Vision & Automation  |  20XW97", options: { x: MX, y: 7.02, w: 7, h: 0.28, fontSize: 10, color: MUTED, margin: 0 } } },
  ],
  slideNumber: { x: W - MX - 0.6, y: 7.02, w: 0.6, h: 0.28, fontSize: 10, color: MUTED, align: "right", margin: 0 },
});
pres.defineSlideMaster({
  title: "DARK",
  background: { color: NAVY },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: MX, y: 0.42, w: 9, h: 0.3, fontSize: 12, bold: true, color: AMBER, charSpacing: 2, margin: 0, valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 0.78, w: W - 2 * MX, h: 0.75, fontSize: 30, bold: true, color: WHITE, margin: 0, valign: "top", align: "left" }, text: "" } },
  ],
  slideNumber: { x: W - MX - 0.6, y: 7.02, w: 0.6, h: 0.28, fontSize: 10, color: MUTED, align: "right", margin: 0 },
});
pres.defineSlideMaster({
  title: "SECTION",
  background: { color: NAVY },
  objects: [
    { placeholder: { options: { name: "number", type: "body", x: MX, y: 1.55, w: 4, h: 1.5, fontSize: 96, bold: true, color: AMBER, margin: 0, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 3.15, w: 11, h: 1.0, fontSize: 44, bold: true, color: WHITE, margin: 0, valign: "top", align: "left" }, text: "" } },
    { placeholder: { options: { name: "presenter", type: "body", x: MX, y: 4.2, w: 11, h: 0.45, fontSize: 18, color: MUTED, margin: 0, valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({ title: "BLANK_DARK", background: { color: NAVY }, objects: [] });

// ---------- helpers ----------
const iconCache = {};
async function icon(name, color) {
  const key = name + color;
  if (!iconCache[key]) {
    const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(lu[name], { color: "#" + color, size: 256 }));
    const buf = await sharp(Buffer.from(svg)).png().toBuffer();
    iconCache[key] = "image/png;base64," + buf.toString("base64");
  }
  return iconCache[key];
}

async function addImg(slide, file, x, y, w, h, opts = {}) {
  // Fit image inside the box (contain), aligned per opts.align; placeholder frame if missing.
  if (!file || !fs.existsSync(file)) {
    slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: LIGHT }, line: { color: MUTED, dashType: "dash", width: 1 }, objectName: "img-placeholder" });
    slide.addText("[ image: " + path.basename(file || "missing") + " ]", { x, y, w, h, align: "center", valign: "middle", fontSize: 12, color: SLATE, isTextBox: true });
    return { x, y, w, h };
  }
  const m = await sharp(file).metadata();
  const r = m.width / m.height;
  let iw = w, ih = w / r;
  if (ih > h) { ih = h; iw = h * r; }
  const ix = opts.align === "right" ? x + w - iw : opts.align === "left" ? x : x + (w - iw) / 2;
  const iy = opts.valign === "top" ? y : y + (h - ih) / 2;
  slide.addImage({ path: file, x: ix, y: iy, w: iw, h: ih, altText: opts.alt || path.basename(file), objectName: opts.name || "image" });
  return { x: ix, y: iy, w: iw, h: ih };
}

function T(slide, text, o) { slide.addText(text, Object.assign({ isTextBox: true, margin: 0, color: INK, fontSize: 16, valign: "top" }, o)); }

const STAGES = ["PIXELS", "DETECT", "TRACK", "MEASURE", "ACT"];
function chips(slide, active, dark = false) {
  // Motif: the five-stage pipeline, current stage(s) highlighted.
  const cw = 0.92, gap = 0.08, y = 0.42, h = 0.3;
  const x0 = W - MX - (STAGES.length * cw + (STAGES.length - 1) * gap);
  STAGES.forEach((s, i) => {
    const on = active.includes(s);
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x0 + i * (cw + gap), y, w: cw, h, rectRadius: 0.15,
      fill: { color: on ? AMBER : dark ? "1D3550" : LIGHT }, line: { type: "none" }, objectName: "stage-chip-" + s });
    slide.addText(s, { x: x0 + i * (cw + gap), y, w: cw, h, align: "center", valign: "middle", fontSize: 9, bold: true, charSpacing: 1,
      color: on ? INK : dark ? MUTED : SLATE, margin: 0, isTextBox: true });
  });
}

function card(slide, x, y, w, h, fill = LIGHT) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { type: "none" }, objectName: "card" });
}

function stat(slide, x, y, w, big, label, o = {}) {
  T(slide, big, { x, y, w, h: 0.85, fontSize: o.size || 44, bold: true, color: o.color || NAVY, valign: "bottom" });
  T(slide, label, { x, y: y + 0.92, w, h: o.lh || 0.7, fontSize: 14, color: o.lcolor || SLATE });
}

async function iconCircle(slide, x, y, d, name, bg, fg) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { type: "none" }, objectName: "icon-bg" });
  const p = d * 0.22;
  slide.addImage({ data: await icon(name, fg), x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p, altText: name.replace(/^Lu/, "") + " icon" });
}

function source(slide, text, dark = false) {
  T(slide, text, { x: MX, y: 6.62, w: W - 2 * MX, h: 0.3, fontSize: 10, color: dark ? MUTED : MUTED, valign: "bottom" });
}

const dget = (k, fallback = "—") => (DATA[k] !== undefined && DATA[k] !== null ? DATA[k] : fallback);

// ---------- slides ----------
async function build() {
  // 1. Title
  pres.addSection({ title: "Opening" });
  let s = pres.addSlide({ masterName: "BLANK_DARK", sectionTitle: "Opening" });
  T(s, "COMPUTER VISION (20XW97)  ·  COURSE PRESENTATION", { x: MX, y: 1.5, w: 8, h: 0.35, fontSize: 13, bold: true, color: AMBER, charSpacing: 2 });
  s.addText("Computer Vision & Automation", { x: MX, y: 2.0, w: 8.2, h: 1.9, fontSize: 52, bold: true, color: WHITE, fontFace: THEME.headFontFace, margin: 0, valign: "top", isTextBox: true });
  T(s, "Where computer vision automates real work, and a deep dive into speed enforcement on Coimbatore's GD Naidu Flyover", { x: MX, y: 4.05, w: 7.8, h: 1.3, fontSize: 20, color: "D0D5DD" });
  T(s, "Thithiksha   ·   Arul   ·   DPD", { x: MX, y: 5.75, w: 7, h: 0.4, fontSize: 18, bold: true, color: WHITE });
  // speed-limit sign
  s.addShape(pres.shapes.OVAL, { x: 9.0, y: 1.75, w: 3.6, h: 3.6, fill: { color: WHITE }, line: { color: RED, width: 22 }, objectName: "speed-sign" });
  s.addText("60", { x: 9.0, y: 1.75, w: 3.6, h: 3.6, fontSize: 110, bold: true, color: INK, align: "center", valign: "middle", margin: 0, isTextBox: true });
  T(s, "km/h  ·  posted limit on the flyover", { x: 8.6, y: 5.6, w: 4.4, h: 0.35, fontSize: 13, color: MUTED, align: "center" });
  s.addNotes(`[~30 s]
Good morning. Our topic is Computer Vision and Automation.
We'll do this in two moves. First, a quick tour of where computer vision already automates real work: factories, farms, hospitals, warehouses, roads and airports, each with real numbers and an honest reality check.
Then we go deep on one local problem and build the whole solution: detecting speeding vehicles on Coimbatore's GD Naidu Flyover using only a camera. The 60 on this slide is the flyover's posted speed limit, and the deep dive builds towards one question: did a vehicle cross 60, and can a computer decide that by itself?
We'll finish with a live demo.`);

  // 2. Agenda
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Opening" });
  s.addText("AGENDA", { placeholder: "kicker" });
  s.addText("From the big picture to one working system", { placeholder: "title" });
  const parts = [
    ["01", "CV automation today", "Six domains, real deployments"],
    ["02", "How machines see", "Pixels, CNNs, YOLO detection, metrics"],
    ["03", "From detections to speed", "Tracking, homography, speed, error analysis"],
    ["04", "Closing the loop", "Automation, deployment, live demo, results"],
  ];
  const pw = (W - 2 * MX - 3 * 0.3) / 4;
  parts.forEach(([n, a, b], i) => {
    const x = MX + i * (pw + 0.3);
    card(s, x, 1.95, pw, 2.3, i === 0 ? LIGHT : LIGHT);
    T(s, n, { x: x + 0.3, y: 2.05, w: 1.5, h: 0.8, fontSize: 40, bold: true, color: AMBER, valign: "bottom" });
    T(s, a, { x: x + 0.3, y: 2.95, w: pw - 0.5, h: 0.62, fontSize: 17, bold: true, color: NAVY });
    T(s, b, { x: x + 0.3, y: 3.6, w: pw - 0.5, h: 0.6, fontSize: 13, color: SLATE });
  });
  T(s, "Deep dive (02–04): one pipeline, five stages, built and demoed on the GD Naidu Flyover", { x: MX, y: 4.55, w: W - 2 * MX, h: 0.35, fontSize: 15, bold: true, color: NAVY });
  const icons4 = ["LuScanSearch", "LuCrosshair", "LuRoute", "LuRuler", "LuSiren"];
  const desc4 = ["Image as numbers", "Find vehicles", "Keep identity", "Pixels → km/h", "Rule → evidence"];
  const bw4 = 2.05, g4 = 0.46, x04 = MX;
  for (let i = 0; i < 5; i++) {
    const x = x04 + i * (bw4 + g4);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.1, w: bw4, h: 1.25, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" }, objectName: "stage" });
    s.addImage({ data: await icon(icons4[i], HEX.accent1), x: x + 0.22, y: 5.32, w: 0.45, h: 0.45, altText: STAGES[i] });
    T(s, STAGES[i], { x: x + 0.8, y: 5.28, w: bw4 - 0.9, h: 0.5, fontSize: 14, bold: true, color: WHITE, valign: "middle" });
    T(s, desc4[i], { x: x + 0.22, y: 5.85, w: bw4 - 0.35, h: 0.35, fontSize: 12, color: "D0D5DD" });
    if (i < 4) s.addImage({ data: await icon("LuArrowRight", HEX.accent5), x: x + bw4 + 0.08, y: 5.58, w: 0.3, h: 0.3, altText: "arrow" });
  }
  s.addNotes(`[~40 s]
Here's the plan. First, the big picture: six domains where computer vision is already automating real work, each with a real deployment and an honest reality check.
Then we go deep on one of them, automated speed enforcement, and build it stage by stage: pixels, detection, tracking, measurement and action. The five boxes at the bottom are that pipeline, and the small chips at the top right of later slides show where we are in it.
We finish with a live demo of the system and its results.`);

  // ===== Section 01: CV automation today =====
  pres.addSection({ title: "01 CV automation today" });
  s = pres.addSlide({ masterName: "SECTION", sectionTitle: "01 CV automation today" });
  s.addText("01", { placeholder: "number" });
  s.addText("Where CV automates today", { placeholder: "title" });
  s.addText("Six domains, real deployments, real numbers", { placeholder: "presenter" });
  s.addNotes(`[~10 s]
Before we build anything, let's look at where computer vision already replaces human eyes in real, deployed systems.`);

  // Overview grid
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 CV automation today" });
  s.addText("THE LANDSCAPE", { placeholder: "kicker" });
  s.addText("Every industry runs the same loop: see, decide, act", { placeholder: "title" });
  const dom = [
    ["LuFactory", "Manufacturing", "Defect inspection on the line", "Detection · anomaly detection"],
    ["LuSprout", "Agriculture", "Spray only the weeds", "Classification · detection"],
    ["LuStethoscope", "Healthcare", "Screening scans and X-rays", "Classification · segmentation"],
    ["LuPackage", "Logistics & retail", "Picking, sorting, checkout", "Detection · segmentation · OCR"],
    ["LuCar", "Mobility", "Driverless navigation", "Detection · tracking · segmentation"],
    ["LuLandmark", "Public sector", "Traffic enforcement, ID checks", "Detection · ANPR · face recognition"],
  ];
  const tw = (W - 2 * MX - 2 * 0.3) / 3, th = 2.0;
  for (let i = 0; i < dom.length; i++) {
    const x = MX + (i % 3) * (tw + 0.3), y = 1.95 + Math.floor(i / 3) * (th + 0.3);
    card(s, x, y, tw, th, i === 5 ? "FEF0C7" : LIGHT);
    await iconCircle(s, x + 0.3, y + 0.3, 0.65, dom[i][0], NAVY, HEX.accent1);
    T(s, dom[i][1], { x: x + 1.15, y: y + 0.32, w: tw - 1.35, h: 0.6, fontSize: 18, bold: true, color: NAVY, valign: "middle" });
    T(s, dom[i][2], { x: x + 0.3, y: y + 1.08, w: tw - 0.6, h: 0.35, fontSize: 15, color: INK });
    T(s, dom[i][3], { x: x + 0.3, y: y + 1.46, w: tw - 0.6, h: 0.35, fontSize: 12, bold: true, color: AMBER_DK });
  }
  T(s, [{ text: "Common pattern: ", options: { bold: true, color: NAVY } }, { text: "camera → model → decision → action, with no human checking each item. Highlighted: where our deep dive sits." }],
    { x: MX, y: 6.35, w: W - 2 * MX, h: 0.4, fontSize: 14, color: SLATE });
  s.addNotes(`[~1 min]
Here's the map. Six domains where vision is already automating work at scale. The applications look different, a weed, a tumour, a parcel, a pedestrian, but the structure is always the same: a camera senses, a model decides, and a machine or a system acts, with no person checking each individual item.
The orange line under each tile is the CV task underneath. They're the same handful of tasks we'll explain in the theory section: classification, detection, segmentation, tracking and text or face recognition.
We'll spend one slide on each, with a real deployment, a real number, and a reality check, because none of these are as simple as the marketing suggests. The highlighted tile, public sector traffic enforcement, is where our deep dive and demo sit.`);

  const domain = async (d) => {
    s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 CV automation today" });
    s.addText(d.kicker, { placeholder: "kicker" });
    s.addText(d.title, { placeholder: "title" });
    // stat card
    card(s, MX, 1.95, 3.9, 2.45, NAVY);
    T(s, d.stat, { x: MX + 0.3, y: 2.05, w: 3.3, h: 1.05, fontSize: d.statSize || 54, bold: true, color: d.statColor || AMBER, valign: "bottom" });
    T(s, d.statLabel, { x: MX + 0.3, y: 3.15, w: 3.3, h: 1.15, fontSize: 14, color: "D0D5DD" });
    // sense -> decide -> act
    const fx0 = MX + 3.9 + 0.35, fw3 = (W - MX - fx0 - 2 * 0.35) / 3;
    const lab = ["SENSE", "DECIDE", "ACT"], ic = ["LuScanEye", "LuBrain", "LuZap"];
    for (let i = 0; i < 3; i++) {
      const x = fx0 + i * (fw3 + 0.35);
      card(s, x, 1.95, fw3, 2.45);
      await iconCircle(s, x + 0.25, 2.15, 0.55, ic[i], NAVY, HEX.accent1);
      T(s, lab[i], { x: x + 0.95, y: 2.15, w: fw3 - 1.1, h: 0.55, fontSize: 12, bold: true, color: AMBER_DK, charSpacing: 2, valign: "middle" });
      T(s, d.flow[i], { x: x + 0.25, y: 2.85, w: fw3 - 0.45, h: 1.45, fontSize: 14, color: INK });
      if (i < 2) s.addImage({ data: await icon("LuArrowRight", HEX.accent5), x: x + fw3 + 0.04, y: 3.05, w: 0.27, h: 0.27, altText: "arrow" });
    }
    // CV tasks + second example
    card(s, MX, 4.65, 3.9, 0.95);
    T(s, "CV TASKS", { x: MX + 0.3, y: 4.72, w: 3.3, h: 0.28, fontSize: 11, bold: true, color: SLATE, charSpacing: 2 });
    T(s, d.tasks, { x: MX + 0.3, y: 5.0, w: 3.4, h: 0.5, fontSize: 14, bold: true, color: NAVY, valign: "middle" });
    card(s, fx0, 4.65, W - MX - fx0, 0.95);
    T(s, d.also, { x: fx0 + 0.3, y: 4.65, w: W - MX - fx0 - 0.6, h: 0.95, fontSize: 14, color: INK, valign: "middle" });
    // reality check
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 5.8, w: W - 2 * MX, h: 0.75, rectRadius: 0.08, fill: { color: "FEF0C7" }, line: { type: "none" }, objectName: "reality-check" });
    s.addImage({ data: await icon("LuTriangleAlert", HEX.accent6), x: MX + 0.25, y: 5.97, w: 0.4, h: 0.4, altText: "reality check" });
    T(s, [{ text: "Reality check: ", options: { bold: true, color: AMBER_DK } }, { text: d.reality, options: { color: INK } }], { x: MX + 0.85, y: 5.8, w: W - 2 * MX - 1.1, h: 0.75, fontSize: 14, valign: "middle" });
    source(s, "Sources: " + d.source);
    s.addNotes(d.notes);
  };

  await domain({
    kicker: "DOMAIN 1 · MANUFACTURING", title: "Manufacturing: every part inspected, not a sample",
    stat: "400+", statLabel: "AI applications in use at BMW Group; its AIQX platform checks parts on the assembly line in fractions of a second",
    flow: ["Cameras along the line, synced to each car's position", "Deep-learning model checks each component: present, correct, undamaged", "Flags the car for rework at once; data goes back to quality teams"],
    tasks: "Detection · anomaly detection",
    also: [{ text: "Also: ", options: { bold: true, color: NAVY } }, { text: "weld-seam, paint and PCB solder-joint inspection. Same idea: a camera at every station instead of a human spot-check." }],
    reality: "defects are rare, so there are few 'bad' images to train on. Teams learn what 'normal' looks like (anomaly detection) or generate synthetic defects.",
    source: "BMW Group / Axis Communications case study (AIQX).",
    notes: `[~1 min]
Manufacturing was one of the first places vision automation paid off. BMW's AIQX platform puts cameras along the assembly line. Each image is matched to the exact vehicle passing that point, and a deep-learning model checks whether each component is there, correct and undamaged, in a fraction of a second. If something's wrong, the car is flagged for rework immediately. BMW reports more than 400 AI applications across its operations.
The shift is from sampling to 100% inspection: a human checks one part in a hundred, a camera checks every one.
The honest catch: defects are rare, so you have thousands of good images and only a handful of bad ones. That's why industrial inspection leans on anomaly detection, where you learn what normal looks like and flag anything that isn't.`,
  });

  await domain({
    kicker: "DOMAIN 2 · AGRICULTURE", title: "Agriculture: cameras spray the weed, not the field",
    stat: "59%", statLabel: "average herbicide saved by John Deere See & Spray users across 1M+ acres in the US (2024)",
    flow: ["Cameras on the sprayer boom scan the ground at driving speed", "Model separates weed from crop, frame by frame", "Only the nozzle above the weed fires, in milliseconds"],
    tasks: "Classification · detection",
    also: [{ text: "Scale: ", options: { bold: true, color: NAVY } }, { text: "≈ 8 million gallons of herbicide mix not sprayed in 2024. Also: fruit-picking robots, yield counting, disease spotting from drone images." }],
    reality: "59% is the vendor's figure. An independent Iowa State study measured 44–87% depending on the field; savings depend on how many weeds there are.",
    source: "John Deere news release (Sep 2024); Iowa State University study via Grainews.",
    notes: `[~1 min]
Agriculture is a great example of perception driving a physical action. John Deere's See & Spray mounts cameras along the sprayer boom. As the tractor drives, a model classifies every plant as crop or weed, and only the nozzle directly above a weed fires.
Across more than a million acres in 2024, Deere reports an average herbicide saving of 59%, about 8 million gallons of mix not sprayed. That's less chemical in the soil and lower cost for the farmer.
Reality check: that's the manufacturer's number. An independent Iowa State study found anywhere from 44 to 87% savings, because it depends on how weedy the field is. Same lesson as our speed demo: always ask who measured it and under what conditions.`,
  });

  await domain({
    kicker: "DOMAIN 3 · HEALTHCARE", title: "Healthcare: AI screens, the doctor decides",
    stat: "1,451", statLabel: "AI-enabled medical devices authorised by the US FDA (to Dec 2025); 76% are for radiology imaging",
    flow: ["Retinal camera or chest X-ray captures the image", "Classifier scores disease likelihood, e.g. diabetic retinopathy in ~20 s", "Refers the patient to a specialist or moves the scan up the reading queue"],
    tasks: "Classification · segmentation",
    also: [{ text: "India: ", options: { bold: true, color: NAVY } }, { text: "Qure.ai's chest X-ray AI screens for TB at ~150 sites in 24 states; TB notifications up 30–40% where used. IDx-DR (2018): first FDA-cleared autonomous AI diagnosis." }],
    reality: "IDx-DR's 87% sensitivity means about 1 in 8 cases is missed. These tools triage and screen; a clinician remains responsible.",
    source: "US FDA AI-enabled device list; IDx-DR pivotal trial (AAO, 2018); Qure.ai / press coverage.",
    notes: `[~1 min]
Healthcare is where vision automation is most regulated and most cautious. The US FDA has now authorised over 1,400 AI-enabled devices, and three quarters of them are in radiology, so they're vision models reading images.
The milestone was IDx-DR in 2018, the first autonomous AI diagnosis: a retinal camera plus a classifier that decides in about 20 seconds whether a diabetic patient needs a specialist, without a doctor reading the image. Closer to home, Qure.ai's chest X-ray model screens for tuberculosis at around 150 sites in 24 Indian states, and TB notifications rose 30 to 40% where it was deployed, because more cases get flagged early.
Reality check: IDx-DR's sensitivity was 87%, so roughly one case in eight is missed. That's why these are screening tools; the responsibility stays with the clinician.`,
  });

  await domain({
    kicker: "DOMAIN 4 · LOGISTICS & RETAIL", title: "Logistics & retail: picking scales, checkout struggled",
    stat: "1,000+", statColor: RED, statLabel: "remote staff labelled and reviewed video behind Amazon's camera-based Just Walk Out checkout",
    flow: ["Camera looks into a tote of mixed products", "Detects and segments each item, picks a grasp point (Amazon Sparrow)", "Robot arm picks the item and places it for packing"],
    tasks: "Detection · segmentation · OCR",
    also: [{ text: "2024: ", options: { bold: true, color: NAVY } }, { text: "Amazon removed Just Walk Out from its US Fresh grocery stores, keeping it in smaller Amazon Go stores. Parcel-label OCR and barcode sorting are routine." }],
    reality: "checkout had to get every item, shopper and hand movement right. The hard cases went to humans, and the system improved more slowly than planned.",
    source: "Supply Chain Dive (Sparrow, 2022); CNBC and The Batch (Apr 2024) on Just Walk Out.",
    notes: `[~1 min]
Logistics shows both sides. In warehouses, vision works well: Amazon's Sparrow robot looks into a bin of mixed products, detects and segments each one among millions of possible items, chooses where to grip, and picks it. Parcel sorting by reading labels and barcodes is completely routine.
Retail checkout is the cautionary tale. Just Walk Out used ceiling cameras to work out what each shopper took. In 2024 Amazon removed it from its US Fresh grocery stores. Reports said more than 1,000 remote workers were labelling video and reviewing cases the system couldn't handle.
The lesson: a controlled bin is a solved problem; a crowded store with people blocking each other is not. Same question as the flyover: how often is the system right without a human?`,
  });

  await domain({
    kicker: "DOMAIN 5 · MOBILITY", title: "Mobility: driverless taxis at commercial scale",
    stat: "500K", statLabel: "paid driverless rides per week by Waymo across 10 US cities (Mar 2026), up 10× from ~50K in May 2024",
    flow: ["360° cameras, plus LiDAR and radar", "Detects, tracks and predicts every road user; plans a path", "Steers, brakes and accelerates, many times per second"],
    tasks: "Detection · tracking · segmentation",
    also: [{ text: "Link to our demo: ", options: { bold: true, color: NAVY } }, { text: "the same detect-then-track loop you'll see on the flyover footage, running at much higher stakes and with prediction added." }],
    reality: "not vision alone. Waymo fuses cameras with LiDAR and radar and drives only in cities it has mapped in detail.",
    source: "Waymo co-CEO remarks (Claims Journal, Feb 2026); industry reports (Mar 2026).",
    notes: `[~1 min]
Mobility is the most demanding version of the loop. Waymo now gives about half a million paid driverless rides a week across ten US cities, roughly ten times more than in May 2024.
Every fraction of a second the car senses with cameras, LiDAR and radar, detects and tracks every road user (the same detect-then-track idea we'll use on the flyover), predicts where each one will go, plans a path, and acts on the steering and brakes.
Reality check: it isn't vision alone. Waymo fuses cameras with LiDAR and radar for depth and redundancy, and it only operates in cities it has mapped in detail. When a wrong decision can kill someone, one sensor isn't enough.`,
  });

  await domain({
    kicker: "DOMAIN 6 · PUBLIC SECTOR, INDIA", title: "Public sector: India already runs CV at scale",
    stat: "726", statLabel: "AI traffic cameras in Kerala's Safe Kerala project; daily violations fell from 4.5 lakh to 2.1 lakh, per the state",
    flow: ["Roadside cameras watch every lane, day and night", "Detect helmetless riding, triple riding, phone use; read the number plate", "Evidence goes to a control room, which issues an e-challan"],
    tasks: "Detection · ANPR · face recognition",
    also: [{ text: "DigiYatra: ", options: { bold: true, color: NAVY } }, { text: "face-recognition boarding at 24 airports with ~1.9 crore app users (Nov 2025). Your face replaces the boarding pass and ID check." }],
    reality: "the violation figures are the department's own claim, and face and plate data raise consent and retention questions. Next: one such system, end to end.",
    source: "Onmanorama / Kerala Kaumudi (2023); Ministry of Civil Aviation via Swarajya (2025).",
    notes: `[~1 min]
Finally, the public sector, and this is where India is already deploying at scale. Kerala's Safe Kerala project installed 726 AI cameras that detect helmetless riding, triple riding and phone use, read the number plate, and send evidence to a control room that issues the challan. The state says daily violations fell from about 4.5 lakh to 2.1 lakh.
At 24 airports, DigiYatra uses face recognition so your face replaces the boarding pass and ID check; about 1.9 crore people have signed up.
Reality check: those traffic numbers are the department's own claim, and storing faces and number plates raises real questions about consent and retention.
That brings us to our deep dive: one of these enforcement systems, on one road in Coimbatore, built end to end.`,
  });

  // 2. Problem
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "01 CV automation today" });
  s.addText("DEEP DIVE · THE PROBLEM", { placeholder: "kicker" });
  s.addText("Tamil Nadu's longest flyover has a speeding problem", { placeholder: "title" });
  // schematic of the flyover
  const fy = 2.25, fx0 = MX + 0.2, fx1 = W - MX - 0.2;
  s.addShape(pres.shapes.LINE, { x: fx0, y: fy, w: fx1 - fx0, h: 0, line: { color: NAVY, width: 6 }, objectName: "flyover-line" });
  for (let i = 1; i <= 12; i++) {
    const x = fx0 + (i * (fx1 - fx0)) / 13;
    s.addShape(pres.shapes.LINE, { x, y: fy + 0.12, w: 0, h: 0.3, line: { color: MUTED, width: 1.5, dashType: "dash" }, objectName: "junction" });
  }
  [fx0, fx1].forEach((x) => s.addShape(pres.shapes.OVAL, { x: x - 0.13, y: fy - 0.13, w: 0.26, h: 0.26, fill: { color: AMBER }, line: { color: NAVY, width: 2 }, objectName: "terminus" }));
  T(s, "Uppilipalayam", { x: fx0 - 0.1, y: fy - 0.55, w: 3, h: 0.3, fontSize: 14, bold: true, color: NAVY });
  T(s, "Goldwins", { x: fx1 - 3 + 0.1, y: fy - 0.55, w: 3, h: 0.3, fontSize: 14, bold: true, color: NAVY, align: "right" });
  T(s, "Elevated over Avinashi Road  ·  4 lanes  ·  bypasses ~12 junctions (dashed)", { x: MX, y: fy + 0.5, w: W - 2 * MX, h: 0.3, fontSize: 13, color: SLATE, align: "center" });
  const cards2 = [
    ["10.1 km", "Tamil Nadu's longest flyover, opened 9 Oct 2025", NAVY],
    ["60 km/h", "Posted speed limit on the elevated corridor", NAVY],
    ["3 killed", "Car off the flyover hit a parked truck near Goldwins, days after opening", RED],
  ];
  const cw2 = (W - 2 * MX - 2 * 0.3) / 3;
  cards2.forEach(([big, lab, col], i) => {
    const x = MX + i * (cw2 + 0.3);
    card(s, x, 3.35, cw2, 2.2);
    stat(s, x + 0.35, 3.45, cw2 - 0.7, big, lab, { color: col, lh: 0.8 });
  });
  T(s, [{ text: "Why it matters: ", options: { bold: true, color: NAVY } }, { text: "on a long, uninterrupted, elevated stretch, drivers misjudge speed. Police say the flyover tempts drivers well past 60 km/h." }],
    { x: MX, y: 5.8, w: W - 2 * MX, h: 0.6, fontSize: 16, color: INK });
  source(s, "Sources: Wikipedia, G. D. Naidu Elevated Expressway; The Week (9 Oct 2025); Lokmat Times; BizzBuzz.");
  s.addNotes(`[~1 min]
Our deep dive is the GD Naidu Elevated Expressway on Avinashi Road: 10.1 kilometres, four lanes, from Uppilipalayam to Goldwins. It opened on 9 October 2025 and it's the longest flyover in Tamil Nadu. It skips about twelve signals, which is exactly why people speed on it.
The posted limit is 60 km/h. Within days of opening, a car coming off the flyover near Goldwins hit a parked truck and three people died. Witnesses said vehicles routinely ignore the limit.
On an elevated road with no junctions, you lose your sense of speed, so 90 can feel like 60. A traffic officer with a radar gun can't cover 10 km. That's an automation problem, and the sensor that can solve it is a camera.`);

  // 3. Status check
  s = pres.addSlide({ masterName: "DARK", sectionTitle: "01 CV automation today" });
  s.addText("DEEP DIVE · REALITY CHECK", { placeholder: "kicker" });
  s.addText("AI enforcement is already installed here, and still in trial", { placeholder: "title" });
  const st3 = [["44", "AI-enabled cameras along the flyover"], ["16", "digital display boards"], ["₹3 Cr", "approximate project cost"], ["3+ months", "in trial, no fines issued"]];
  st3.forEach(([b, l], i) => {
    const x = MX + (i % 2) * 3.15, y = 1.95 + Math.floor(i / 2) * 2.0;
    stat(s, x, y, 2.9, b, l, { color: AMBER, lcolor: "D0D5DD", size: 40 });
  });
  // accuracy bars
  const bx = 7.35, bw = W - MX - bx;
  T(s, "Reported system accuracy during trial", { x: bx, y: 2.0, w: bw, h: 0.35, fontSize: 16, bold: true, color: WHITE });
  [["Early trial", 0.2, RED], ["After tuning", 0.8, AMBER]].forEach(([lab, v, col], i) => {
    const y = 2.65 + i * 1.05;
    T(s, lab, { x: bx, y, w: 2.5, h: 0.3, fontSize: 14, color: "D0D5DD" });
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: y + 0.38, w: bw, h: 0.42, fill: { color: "1D3550" }, line: { type: "none" }, objectName: "bar-track" });
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: y + 0.38, w: bw * v, h: 0.42, fill: { color: col }, line: { type: "none" }, objectName: "bar-fill" });
    T(s, Math.round(v * 100) + "%", { x: bx + bw * v + 0.12, y: y + 0.38, w: 1, h: 0.42, fontSize: 18, bold: true, color: WHITE, valign: "middle" });
  });
  T(s, "Problems reported: misidentified violations, e.g. seat-belt detection errors", { x: bx, y: 4.85, w: bw, h: 0.6, fontSize: 14, color: "D0D5DD" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 5.75, w: W - 2 * MX, h: 0.8, rectRadius: 0.08, fill: { color: "1D3550" }, line: { type: "none" }, objectName: "question-card" });
  T(s, [{ text: "Today's question:  ", options: { bold: true, color: AMBER } }, { text: "how does such a system work, and why isn't 80% good enough to fine people?", options: { color: WHITE } }],
    { x: MX + 0.3, y: 5.75, w: W - 2 * MX - 0.6, h: 0.8, fontSize: 18, valign: "middle" });
  source(s, "Sources: BizzBuzz; The Hawk; NewKerala (2026) on the GD Naidu Flyover AI speed-enforcement trial.", true);
  s.addNotes(`[~1 min]
This isn't hypothetical. The State Highways Department has installed 44 AI cameras and 16 display boards on this flyover, for about 3 crore rupees.
More than three months after installation, the system was still in trial and no fines had been issued. The reason was accuracy: it reportedly started at around 20%, with misidentified violations, and was tuned up to about 80%.
80% sounds good until you remember that one in five tickets would go to the wrong person. That's the tension in this whole talk: automating perception is easy to demo and hard to trust.
So today we'll show how a system like this works, stage by stage, where it breaks, and then a working version of it.`);

  // ===== Section 1 =====
  pres.addSection({ title: "02 How machines see" });
  s = pres.addSlide({ masterName: "SECTION", sectionTitle: "02 How machines see" });
  s.addText("02", { placeholder: "number" });
  s.addText("How machines see", { placeholder: "title" });
  s.addText("Pixels and detection", { placeholder: "presenter" });
  chips(s, ["PIXELS", "DETECT"], true);
  s.addNotes(`[~10 s]
Let's start at the bottom: what does a camera actually give a computer?`);

  // 5. Pixels
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 How machines see" });
  s.addText("PIXELS", { placeholder: "kicker" });
  s.addText("To a computer, an image is just a grid of numbers", { placeholder: "title" });
  chips(s, ["PIXELS"]);
  const px5 = await addImg(s, path.join(ASSETS, "pixels.png"), MX, 1.95, 8.9, 3.4, { align: "left", valign: "top", alt: "Traffic frame with a zoomed crop showing pixel values" });
  T(s, [{ text: "Zoom on the car: ", options: { bold: true, color: NAVY } }, { text: "bright roof ≈ 230, dark rear window ≈ 90. A sharp jump in value is an edge." }],
    { x: MX, y: px5.y + px5.h + 0.15, w: 8.9, h: 0.35, fontSize: 14, color: SLATE });
  const rx5 = 9.9, rw5 = W - MX - rx5;
  [["1920×1080×3", "≈ 6.2 M numbers per 1080p frame"], ["× 30 FPS", "≈ 187 M numbers per second"], ["0 – 255", "intensity per channel (R, G, B)"]].forEach(([b, l], i) => {
    T(s, b, { x: rx5, y: 1.95 + i * 1.12, w: rw5, h: 0.5, fontSize: 24, bold: true, color: NAVY, valign: "bottom" });
    T(s, l, { x: rx5, y: 2.48 + i * 1.12, w: rw5, h: 0.5, fontSize: 13, color: SLATE });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 5.85, w: W - 2 * MX, h: 0.7, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" }, objectName: "callout" });
  T(s, [{ text: "Every CV task ", options: { bold: true, color: AMBER } }, { text: "is a function that turns this array into a decision.", options: { color: WHITE } }],
    { x: MX + 0.3, y: 5.85, w: W - 2 * MX - 0.6, h: 0.7, fontSize: 17, valign: "middle" });
  s.addNotes(`[~1 min]
A camera doesn't give us "a car". It gives us a 3D array: height, width, and three colour channels, each value from 0 to 255. On the left is a frame from the traffic-camera clip we use in the demo, and the zoom shows the real pixel values on one car: the bright roof around 230, the dark rear window around 90. That sharp jump is an edge, and edges are what the next slides build on.
One 1080p frame is about 6.2 million numbers. At 30 frames per second, that's nearly 190 million numbers every second.
Everything in computer vision, whether it's classical image processing or deep learning, is a function that takes this array and produces something useful: a mask, a box, a label, or here, a speed. The rest of the talk is that function, one stage at a time.`);

  // 6. Background subtraction
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 How machines see" });
  s.addText("CLASSICAL CV", { placeholder: "kicker" });
  s.addText("Classical CV sees motion, not vehicles", { placeholder: "title" });
  chips(s, ["DETECT"]);
  const im6 = await addImg(s, path.join(DEMO, "background_subtraction.png"), MX, 1.85, 7.7, 3.9, { align: "left", valign: "top", alt: "Frame and background-subtraction foreground mask side by side" });
  T(s, [{ text: "How it works: ", options: { bold: true, color: NAVY } }, { text: "model the static road (MOG2 background model); pixels that differ from it are 'foreground'." }],
    { x: MX, y: Math.min(im6.y + im6.h + 0.2, 5.9), w: 7.7, h: 0.6, fontSize: 14, color: INK });
  T(s, [{ text: "Still useful for: ", options: { bold: true, color: NAVY } }, { text: "counting traffic or parking occupancy, where identity and class don't matter." }],
    { x: MX, y: Math.min(im6.y + im6.h + 0.95, 6.0), w: 7.7, h: 0.6, fontSize: 14, color: INK });
  const rx6 = 8.75, rw6 = W - MX - rx6;
  T(s, "Where it breaks", { x: rx6, y: 1.9, w: rw6, h: 0.35, fontSize: 16, bold: true, color: NAVY });
  const br6 = [["LuSun", "Shadows move with the car → oversized blobs"], ["LuMoon", "Headlights & night glare → false motion"], ["LuVibrate", "Camera shake on a flyover → whole frame 'moves'"], ["LuCombine", "Two close cars merge into one blob"], ["LuTag", "No labels: car, bus or bike?"]];
  for (let i = 0; i < br6.length; i++) {
    const y = 2.4 + i * 0.68;
    await iconCircle(s, rx6, y, 0.48, br6[i][0], LIGHT, HEX.dk2);
    T(s, br6[i][1], { x: rx6 + 0.65, y, w: rw6 - 0.65, h: 0.48, fontSize: 14, valign: "middle" });
  }
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: rx6, y: 5.95, w: rw6, h: 0.55, rectRadius: 0.08, fill: { color: "FEF0C7" }, line: { type: "none" }, objectName: "verdict" });
  T(s, "Fast, no training, too fragile for fines", { x: rx6 + 0.2, y: 5.95, w: rw6 - 0.4, h: 0.55, fontSize: 14, bold: true, color: AMBER_DK, valign: "middle" });
  s.addNotes(`[~1.5 min]
Before deep learning, the standard approach to traffic video was background subtraction. You build a statistical model of the empty road (OpenCV's MOG2 is a common choice), and any pixel that differs from it is marked as foreground. On the right of the image you see the mask: white blobs where things are moving.
It's fast and needs no training data, but look at the failure list. Shadows move with the vehicle and inflate the blob. At night, headlight glare creates motion where there's no car. A flyover vibrates, so the whole frame can look like it's moving. Two cars close together merge into one blob. And it never tells you what the blob is.
For counting traffic it's often fine; for issuing a fine to a specific vehicle it isn't. We need a method that recognises vehicles, not just motion.`);

  // 7. CNN
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 How machines see" });
  s.addText("DEEP LEARNING", { placeholder: "kicker" });
  s.addText("CNNs learn their own feature detectors from data", { placeholder: "title" });
  chips(s, ["DETECT"]);
  await addImg(s, path.join(ASSETS, "convolution.gif"), MX, 1.95, 7.6, 3.4, { align: "left", valign: "top", alt: "Animated 3x3 kernel sliding over pixels to build a feature map" });
  T(s, [{ text: "Convolution: ", options: { bold: true, color: NAVY } }, { text: "slide a small kernel over the image, multiply and sum at each position. High output = the pattern is present here." }],
    { x: MX, y: 5.55, w: 7.6, h: 0.75, fontSize: 14 });
  const rx7 = 8.75, rw7 = W - MX - rx7;
  const lv = [["Early layers", "edges, corners, colour blobs"], ["Middle layers", "parts: wheels, windows, plates"], ["Deep layers", "whole objects: car, bus, truck"]];
  for (let i = 0; i < lv.length; i++) {
    const [a, b] = lv[i];
    const y = 1.95 + i * 1.25;
    card(s, rx7, y, rw7, 1.0, i === 2 ? "FEF0C7" : LIGHT);
    T(s, a, { x: rx7 + 0.25, y: y + 0.15, w: rw7 - 0.5, h: 0.35, fontSize: 15, bold: true, color: NAVY });
    T(s, b, { x: rx7 + 0.25, y: y + 0.5, w: rw7 - 0.5, h: 0.4, fontSize: 14, color: SLATE });
    if (i < 2) s.addImage({ data: await icon("LuArrowDown", HEX.accent5), x: rx7 + rw7 / 2 - 0.12, y: y + 1.0, w: 0.25, h: 0.25, altText: "arrow" });
  }
  T(s, "Kernels are learned by training, not hand-written. YOLOv8 is pre-trained on COCO: 118k images, 80 classes.", { x: rx7, y: 5.75, w: rw7, h: 0.75, fontSize: 13, color: SLATE });
  s.addNotes(`[~1.5 min]
Convolutional neural networks fix this by learning what to look for. The core operation is convolution: take a small grid of weights called a kernel, slide it across the image, and at every position multiply and add. In the animation the kernel is a Sobel filter, and the output lights up exactly where dark meets bright: a vertical edge.
The key difference from classical CV is that a CNN learns thousands of these kernels from data instead of us designing them. Stacked in layers, early kernels find edges, middle layers combine them into parts like wheels and windows, and deep layers respond to whole objects.
We don't train from scratch. YOLOv8 comes pre-trained on COCO, 118 thousand images with 80 classes, and those classes already include car, motorcycle, bus and truck. That's why our demo needed no training at all.`);

  // 8. YOLO
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 How machines see" });
  s.addText("OBJECT DETECTION", { placeholder: "kicker" });
  s.addText("YOLO finds every vehicle in a single pass", { placeholder: "title" });
  chips(s, ["DETECT"]);
  await addImg(s, path.join(DEMO, "frame_detections.png"), MX, 1.85, 7.6, 4.3, { align: "left", valign: "top", alt: "YOLOv8 detections with class and confidence" });
  const rx8 = 8.75, rw8 = W - MX - rx8;
  const st8 = [["1", "Grid", "Image split into cells at 3 scales; each cell predicts boxes"], ["2", "Predict", "Per box: x, y, w, h + class scores (car 0.91)"], ["3", "NMS", "Keep the best box, drop overlapping duplicates (IoU > threshold)"]];
  st8.forEach(([n, a, b], i) => {
    const y = 1.95 + i * 1.12;
    s.addShape(pres.shapes.OVAL, { x: rx8, y, w: 0.5, h: 0.5, fill: { color: NAVY }, line: { type: "none" }, objectName: "step" });
    T(s, n, { x: rx8, y, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle" });
    T(s, a, { x: rx8 + 0.7, y: y - 0.02, w: rw8 - 0.7, h: 0.35, fontSize: 16, bold: true, color: NAVY });
    T(s, b, { x: rx8 + 0.7, y: y + 0.33, w: rw8 - 0.7, h: 0.65, fontSize: 14, color: SLATE });
  });
  const ch8 = [["3.2 M", "parameters"], ["37.3", "mAP COCO"], ["8.7 G", "FLOPs"]];
  const cw8 = (rw8 - 0.3) / 3;
  ch8.forEach(([b, l], i) => {
    const x = rx8 + i * (cw8 + 0.15);
    card(s, x, 5.4, cw8, 1.05);
    T(s, b, { x, y: 5.48, w: cw8, h: 0.5, fontSize: 22, bold: true, color: NAVY, align: "center", valign: "middle" });
    T(s, l, { x, y: 5.98, w: cw8, h: 0.35, fontSize: 12, color: SLATE, align: "center" });
  });
  T(s, "YOLOv8n (nano), as used in our demo. Source: Ultralytics docs.", { x: MX, y: 6.3, w: 7.6, h: 0.3, fontSize: 11, color: MUTED });
  s.addNotes(`[~1.5 min]
Object detection answers two questions at once: what is in the image, and where. The output is a bounding box, a class and a confidence score, like the boxes on this frame.
YOLO, "You Only Look Once", does it in a single forward pass of the network. The image is divided into grid cells at three scales. Each cell predicts box coordinates and class scores. That produces many overlapping candidate boxes for the same car, so a final step called non-maximum suppression keeps the highest-confidence box and removes others that overlap it too much.
One honest detail in this frame: the green bus is labelled "truck". COCO's bus and truck classes get confused, so in our code each vehicle's class is a majority vote over its whole track, and boxes are de-duplicated across classes.
We use YOLOv8 nano, the smallest model: 3.2 million parameters, 37.3 mAP on COCO, small enough to run on a laptop CPU. That trade-off between size and accuracy comes back in the deployment section.`);

  // 9. Metrics
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "02 How machines see" });
  s.addText("EVALUATION", { placeholder: "kicker" });
  s.addText("Detectors are scored on overlap, not 'accuracy'", { placeholder: "title" });
  chips(s, ["DETECT"]);
  // IoU diagram
  const gx = MX + 0.3, gy = 2.2;
  s.addShape(pres.shapes.RECTANGLE, { x: gx, y: gy, w: 2.4, h: 1.7, fill: { color: "D1E0F0" }, line: { color: NAVY, width: 2.5 }, objectName: "ground-truth" });
  s.addShape(pres.shapes.RECTANGLE, { x: gx + 0.9, y: gy + 0.6, w: 2.4, h: 1.7, fill: { color: "FEF0C7", transparency: 30 }, line: { color: AMBER, width: 2.5 }, objectName: "prediction" });
  s.addShape(pres.shapes.RECTANGLE, { x: gx + 0.9, y: gy + 0.6, w: 1.5, h: 1.1, fill: { color: AMBER }, line: { type: "none" }, objectName: "overlap" });
  T(s, "Ground truth", { x: gx, y: gy - 0.38, w: 2.4, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  T(s, "Prediction", { x: gx + 0.9, y: gy + 2.38, w: 2.4, h: 0.3, fontSize: 12, bold: true, color: AMBER_DK, align: "right" });
  T(s, [{ text: "IoU = ", options: { bold: true, color: NAVY } }, { text: "overlap ÷ union", options: { color: INK } }], { x: gx + 3.7, y: gy + 0.5, w: 3.2, h: 0.45, fontSize: 22 });
  T(s, "IoU ≥ 0.5 → counts as a correct detection (true positive)", { x: gx + 3.7, y: gy + 1.05, w: 3.0, h: 0.8, fontSize: 14, color: SLATE });
  // P/R cards
  const rx9 = 8.0, rw9 = W - MX - rx9;
  [["Precision", "TP ÷ (TP + FP)", "Of vehicles flagged, how many were real?"], ["Recall", "TP ÷ (TP + FN)", "Of the real vehicles, how many did we catch?"], ["mAP", "avg AP · IoU 0.5–0.95", "Single quality score: 37.3 for YOLOv8n"]].forEach(([a, f, d], i) => {
    const y = 1.9 + i * 1.32;
    card(s, rx9, y, rw9, 1.15);
    T(s, a, { x: rx9 + 0.25, y: y + 0.12, w: 1.6, h: 0.4, fontSize: 17, bold: true, color: NAVY });
    T(s, f, { x: rx9 + 1.8, y: y + 0.14, w: rw9 - 2.0, h: 0.4, fontSize: 14, color: AMBER_DK, bold: true, align: "right" });
    T(s, d, { x: rx9 + 0.25, y: y + 0.58, w: rw9 - 0.5, h: 0.45, fontSize: 14, color: SLATE });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 5.8, w: W - 2 * MX, h: 0.7, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" }, objectName: "callout" });
  T(s, [{ text: "For enforcement, precision comes first: ", options: { bold: true, color: AMBER } }, { text: "every false positive is an innocent driver fined.", options: { color: WHITE } }],
    { x: MX + 0.3, y: 5.8, w: W - 2 * MX - 0.6, h: 0.7, fontSize: 17, valign: "middle" });
  s.addNotes(`[~1.5 min]
How do we know a detector is good? Not with a single "accuracy" number. First, a predicted box only counts as correct if it overlaps the true box enough. That's Intersection over Union: overlap area divided by combined area. The usual threshold is 0.5.
Then two numbers. Precision: of everything we flagged, how much was real? Recall: of everything that was really there, how much did we find? mAP averages precision across classes and across IoU thresholds from 0.5 to 0.95. That's the 37.3 on the previous slide.
For speed enforcement these aren't equally important. Missing a speeder (low recall) means one gets away. A false positive (low precision) means an innocent person gets a fine. That's why the flyover system stayed in trial at 80%.
That's detection. Next: why detection alone can't measure speed.`);

  // ===== Section 2 =====
  pres.addSection({ title: "03 From detections to speed" });
  s = pres.addSlide({ masterName: "SECTION", sectionTitle: "03 From detections to speed" });
  s.addText("03", { placeholder: "number" });
  s.addText("From detections to speed", { placeholder: "title" });
  s.addText("Tracking and measurement", { placeholder: "presenter" });
  chips(s, ["TRACK", "MEASURE"], true);
  s.addNotes(`[~10 s]
We can now find vehicles in a frame. To measure speed we need two more things: memory and a ruler.`);

  // 10. No memory
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 From detections to speed" });
  s.addText("WHY TRACKING", { placeholder: "kicker" });
  s.addText("Detection has no memory; tracking adds identity", { placeholder: "title" });
  chips(s, ["TRACK"]);
  const fw = 3.0, fh = 1.55, fg = 0.45, fx = MX + 1.95;
  const rows10 = [["Detection only", ["car", "car", "car"], SLATE, "Same car? Unknown. No speed possible."], ["With tracking", ["#7", "#7", "#7"], AMBER, "One identity → a trajectory → a speed."]];
  for (let r = 0; r < rows10.length; r++) {
    const [lab, tags, col, note] = rows10[r];
    const y = 2.0 + r * 2.15;
    T(s, lab, { x: MX, y: y + 0.5, w: 1.75, h: 0.6, fontSize: 15, bold: true, color: NAVY });
    for (let i = 0; i < 3; i++) {
      const x = fx + i * (fw + fg);
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: fw, h: fh, fill: { color: LIGHT }, line: { color: "D0D5DD", width: 1 }, objectName: "frame" });
      // road lanes
      s.addShape(pres.shapes.LINE, { x: x + 0.2, y: y + fh - 0.25, w: fw - 0.4, h: 0, line: { color: "D0D5DD", width: 1.5, dashType: "dash" }, objectName: "lane" });
      const cx = x + 0.3 + i * 0.75;
      s.addShape(pres.shapes.RECTANGLE, { x: cx, y: y + 0.45, w: 1.05, h: 0.7, fill: { color: WHITE }, line: { color: r ? AMBER : SLATE, width: 2.5 }, objectName: "box" });
      s.addImage({ data: await icon("LuCar", HEX.dk2), x: cx + 0.3, y: y + 0.55, w: 0.45, h: 0.45, altText: "car" });
      T(s, tags[i], { x: cx, y: y + 0.12, w: 1.3, h: 0.3, fontSize: 13, bold: true, color: r ? AMBER_DK : SLATE });
      T(s, "t" + (i ? " + " + i : ""), { x, y: y + fh + 0.05, w: fw, h: 0.28, fontSize: 11, color: MUTED, align: "center" });
      if (r && i < 2) s.addShape(pres.shapes.LINE, { x: cx + 1.05, y: y + 0.8, w: fw + fg - 0.3, h: 0, line: { color: AMBER, width: 1.5, dashType: "sysDot", endArrowType: "triangle" }, objectName: "trajectory" });
    }
    T(s, note, { x: fx, y: y + fh + 0.35, w: 3 * fw + 2 * fg, h: 0.3, fontSize: 14, color: r ? NAVY : SLATE, bold: !!r });
  }
  s.addNotes(`[~1 min]
YOLO processes every frame independently. In frame t it says "car", in t+1 "car", in t+2 "car". It has no idea these are the same car, and speed is about the same object moving over time.
So we add tracking: give every vehicle a persistent ID, here number 7, and follow it from frame to frame. Once we have an identity, we have a trajectory, a list of positions over time. A trajectory plus a clock gives us speed.
The tricky part is that tracking has to survive the real world: missed detections, cars hidden behind trucks, and many similar-looking cars side by side.`);

  // 11. ByteTrack
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 From detections to speed" });
  s.addText("MULTI-OBJECT TRACKING", { placeholder: "kicker" });
  s.addText("ByteTrack: predict, match, then rescue weak boxes", { placeholder: "title" });
  chips(s, ["TRACK"]);
  const st11 = [
    ["Predict", "Kalman filter estimates each track's next box from its velocity"],
    ["Match", "High-confidence boxes ↔ predictions by IoU (Hungarian assignment)"],
    ["Rescue", "Low-confidence boxes matched to leftover tracks: keeps occluded cars"],
    ["Update", "Unmatched boxes → new IDs; tracks lost ~1 s → deleted"],
  ];
  st11.forEach(([a, b], i) => {
    const y = 1.95 + i * 1.08;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y, w: 1.55, h: 0.82, rectRadius: 0.08, fill: { color: i === 2 ? AMBER : NAVY }, line: { type: "none" }, objectName: "step" });
    T(s, a, { x: MX, y, w: 1.55, h: 0.82, fontSize: 15, bold: true, color: i === 2 ? INK : WHITE, align: "center", valign: "middle" });
    T(s, b, { x: MX + 1.75, y, w: 4.2, h: 0.82, fontSize: 14, color: INK, valign: "middle" });
  });
  T(s, "↻ repeats every frame", { x: MX, y: 6.25, w: 4, h: 0.3, fontSize: 12, color: MUTED });
  await addImg(s, path.join(DEMO, "tracking_preview.gif"), 6.75, 1.95, W - MX - 6.75, 3.55, { align: "right", valign: "top", alt: "Vehicles keeping stable track IDs across frames" });
  const ch11 = [["80.3", "MOTA"], ["77.3", "IDF1"], ["30 FPS", "on MOT17"]];
  const cw11 = (W - MX - 6.75 - 0.3) / 3;
  ch11.forEach(([b, l], i) => {
    const x = 6.75 + i * (cw11 + 0.15);
    card(s, x, 5.65, cw11, 0.85);
    T(s, b, { x, y: 5.68, w: cw11, h: 0.45, fontSize: 20, bold: true, color: NAVY, align: "center", valign: "middle" });
    T(s, l, { x, y: 6.12, w: cw11, h: 0.3, fontSize: 12, color: SLATE, align: "center" });
  });
  s.addNotes(`[~2 min]
We use ByteTrack, a tracker published at ECCV 2022. Every frame it runs four steps.
Predict: each existing track has a Kalman filter, a constant-velocity motion model, that predicts where its box should be in the new frame.
Match: we compare those predictions with YOLO's high-confidence detections using IoU, and the Hungarian algorithm finds the best one-to-one assignment.
Rescue: this is ByteTrack's key idea. Most trackers throw away low-confidence detections. ByteTrack does a second matching round with them against the tracks that are still unmatched. A car half-hidden behind a bus gets a low score but it's still a real car, so its ID survives.
Update: leftover detections start new tracks, and tracks unseen for about a second are deleted.
On the MOT17 benchmark it reports 80.3 MOTA at 30 frames per second. In code it's one line from the supervision library.`);

  // 12. Homography
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 From detections to speed" });
  s.addText("CAMERA GEOMETRY", { placeholder: "kicker" });
  s.addText("A homography turns pixels into metres", { placeholder: "title" });
  chips(s, ["MEASURE"]);
  const hw = 5.0;
  const hb = await addImg(s, path.join(DEMO, "homography_before.png"), MX, 1.9, hw, 3.3, { align: "left", valign: "top", alt: "Camera view with 4 calibration points on the road" });
  const ha = await addImg(s, path.join(DEMO, "homography_after.png"), MX + hw + 0.8, 1.9, 2.6, 3.3, { align: "left", valign: "top", alt: "Bird's-eye view of the road zone after warping" });
  s.addImage({ data: await icon("LuArrowRight", HEX.accent1), x: MX + hw + 0.2, y: 3.25, w: 0.45, h: 0.45, altText: "warp arrow" });
  T(s, "Camera view: 4 points on the road", { x: MX, y: hb.y + hb.h + 0.1, w: hw, h: 0.3, fontSize: 12, color: SLATE });
  T(s, "Bird's-eye view (metres)", { x: ha.x, y: ha.y + ha.h + 0.1, w: 2.8, h: 0.3, fontSize: 12, color: SLATE });
  const rx12 = 9.35, rw12 = W - MX - rx12;
  T(s, "The problem", { x: rx12, y: 1.95, w: rw12, h: 0.35, fontSize: 16, bold: true, color: NAVY });
  T(s, "Perspective shrinks distance: 1 m near the camera spans many more pixels than 1 m far away.", { x: rx12, y: 2.3, w: rw12, h: 0.95, fontSize: 14, color: SLATE });
  T(s, "The fix", { x: rx12, y: 3.35, w: rw12, h: 0.35, fontSize: 16, bold: true, color: NAVY });
  T(s, "Map 4 road points to a rectangle of known size. 4 point pairs → 8 equations → the 3×3 matrix H.", { x: rx12, y: 3.7, w: rw12, h: 0.95, fontSize: 14, color: SLATE });
  card(s, rx12, 4.8, rw12, 0.75, "FEF0C7");
  T(s, [{ text: "p′ ∝ H · p", options: { fontSize: 20, bold: true, breakLine: true } }, { text: "p = [x, y, 1]ᵀ  (homogeneous)", options: { fontSize: 12, color: SLATE } }], { x: rx12, y: 4.8, w: rw12, h: 0.75, color: INK, align: "center", valign: "middle" });
  T(s, dget("calib_note", "Zone calibrated from lane markings (assumed lane width)."), { x: MX, y: 5.85, w: W - 2 * MX, h: 0.6, fontSize: 13, color: SLATE });
  s.addNotes(`[~1.5 min]
Now we can follow a car in pixels, but speed needs metres. The camera's perspective is the problem: a car near the camera moves many pixels per metre, and a car far away moves only a few. The same speed would look different depending on where the car is.
The fix is a homography: a 3×3 matrix that maps one plane to another. We click four points on the road that form a rectangle in the real world, for example lane markings, and tell the computer the real width and length of that rectangle in metres. Four point pairs give eight equations, enough to solve for H. OpenCV does this with getPerspectiveTransform.
Apply H to every car's position and we get the bird's-eye view on the right, where one unit is one metre everywhere. ${dget("calib_note_spoken", "For our footage the real size comes from standard lane widths; on the real flyover you'd measure it on site.")}`);

  // 13. Speed
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 From detections to speed" });
  s.addText("SPEED ESTIMATION", { placeholder: "kicker" });
  s.addText("Speed is metres travelled per second of video", { placeholder: "title" });
  chips(s, ["MEASURE"]);
  card(s, MX, 1.9, W - 2 * MX, 1.15, NAVY);
  T(s, [{ text: "v  =  ", options: { color: WHITE } }, { text: "|Δy|", options: { color: AMBER } }, { text: "  ÷  ", options: { color: WHITE } }, { text: "(N ÷ FPS)", options: { color: AMBER } }, { text: "  ×  3.6", options: { color: WHITE } }],
    { x: MX + 0.4, y: 1.9, w: 7, h: 1.15, fontSize: 30, bold: true, valign: "middle" });
  T(s, "Δy: metres moved in the bird's-eye view\nN: frames in the window (~1 s)\n× 3.6: m/s → km/h", { x: 8.2, y: 1.98, w: W - MX - 8.4, h: 1.0, fontSize: 13, color: "D0D5DD", valign: "middle" });
  T(s, "Worked example from our demo  ·  " + dget("ex_label", "track #—"), { x: MX, y: 3.35, w: 8, h: 0.35, fontSize: 16, bold: true, color: NAVY });
  const ex = [[dget("ex_dy", "—") + " m", "distance in zone"], [dget("ex_n", "—") + " frames", "at " + dget("fps", "—") + " FPS = " + dget("ex_t", "—") + " s"], [dget("ex_ms", "—") + " m/s", "Δy ÷ time"], [dget("ex_kmh", "—") + " km/h", dget("ex_verdict", "vs 60 km/h limit")]];
  const ew = (W - 2 * MX - 3 * 0.5) / 4;
  for (let i = 0; i < 4; i++) {
    const x = MX + i * (ew + 0.5), last = i === 3, over = String(dget("ex_verdict", "")).includes("over");
    card(s, x, 3.85, ew, 1.6, last ? (over ? "FEE4E2" : "D1FADF") : LIGHT);
    T(s, ex[i][0], { x: x + 0.2, y: 4.0, w: ew - 0.4, h: 0.7, fontSize: 28, bold: true, color: last ? (over ? RED : GREEN) : NAVY, align: "center", valign: "middle" });
    T(s, ex[i][1], { x: x + 0.2, y: 4.75, w: ew - 0.4, h: 0.5, fontSize: 14, color: SLATE, align: "center" });
    if (i < 3) s.addImage({ data: await icon("LuArrowRight", HEX.accent5), x: x + ew + 0.1, y: 4.48, w: 0.3, h: 0.3, altText: "arrow" });
  }
  T(s, "Why a 1-second window? A single frame-to-frame step is a few cm and dominated by box jitter; averaging over ~30 frames gives a stable reading.", { x: MX, y: 5.8, w: W - 2 * MX, h: 0.6, fontSize: 14, color: SLATE });
  s.addNotes(`[~1.5 min]
With metres and a clock, speed is simple arithmetic. For each tracked vehicle we keep its position in the bird's-eye view over the last second of frames. Speed is the distance it moved divided by the time, and the time is the number of frames divided by the frame rate. Multiply metres per second by 3.6 to get kilometres per hour.
Here's a real vehicle from our run: ${dget("ex_spoken", "it moved Δy metres over N frames")}.
Why one second and not frame to frame? Between two consecutive frames a car moves maybe 50 centimetres, and the box edge wobbles by a similar amount. Averaging over about thirty frames smooths that out. The cost is that a new vehicle needs about half a second before we trust its speed.`);

  // 14. Errors
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "03 From detections to speed" });
  s.addText("ERROR ANALYSIS", { placeholder: "kicker" });
  s.addText("Small measurement errors become wrong fines", { placeholder: "title" });
  chips(s, ["MEASURE"]);
  T(s, "What the system reads for a car truly doing 60 km/h", { x: MX, y: 1.9, w: 7.2, h: 0.35, fontSize: 15, bold: true, color: NAVY });
  s.addChart(pres.charts.BAR, [{ name: "Reading (km/h)", labels: ["No error", "Box jitter ±0.5 m", "Zone length 4% off", "FPS assumed 30, really 25"], values: [60, 61.8, 62.4, 72] }], {
    x: MX, y: 2.3, w: 7.2, h: 3.6, barDir: "bar", catAxisOrientation: "maxMin", valAxisMinVal: 0, valAxisMaxVal: 80, valAxisMajorUnit: 20,
    chartColors: [HEX.dk2, HEX.accent1, HEX.accent1, HEX.accent2], varyColors: true, invertIfNegative: false,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelFontSize: 12, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt",
    catAxisLabelColor: HEX.accent4, valAxisLabelColor: HEX.accent5, catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E4E7EC", size: 0.75 }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 60,
  });
  T(s, "Above 60 → flagged. Every non-zero error here would fine a legal driver.", { x: MX, y: 6.0, w: 7.2, h: 0.5, fontSize: 13, color: SLATE });
  const rx14 = 8.3, rw14 = W - MX - rx14;
  T(s, "Mitigations", { x: rx14, y: 1.9, w: rw14, h: 0.35, fontSize: 15, bold: true, color: NAVY });
  const mit = [["LuRuler", "Survey the calibration zone on site, not from assumptions"], ["LuTimer", "Read real frame timestamps; never assume FPS"], ["LuLayers", "Median over a window; drop ID-switched tracks"], ["LuScale", "Enforcement tolerance, e.g. flag only above limit + margin"]];
  for (let i = 0; i < mit.length; i++) {
    const y = 2.4 + i * 0.95;
    await iconCircle(s, rx14, y, 0.55, mit[i][0], LIGHT, HEX.dk2);
    T(s, mit[i][1], { x: rx14 + 0.75, y: y - 0.05, w: rw14 - 0.75, h: 0.65, fontSize: 14, valign: "middle" });
  }
  s.addNotes(`[~1.5 min]
This is where it's easy to oversell, so let's be precise. Speed equals distance over time, so any error in distance or time goes straight into the speed.
Box jitter of half a metre over one second adds about 1.8 km/h. If the calibration zone is 4% off, say 52 metres assumed when it's really 50, every speed is 4% high and a car at 60 reads 62.4. The worst is time. Our own demo clip runs at 25 frames per second, not 30. If the code had assumed 30, every speed is 20% high, and a legal driver at 60 shows as 72.
Every one of these would fine someone who did nothing wrong. So we calibrate on site, read real timestamps, use the median over a window, drop tracks whose ID switched, and real systems add an enforcement tolerance above the limit.
That's tracking and measurement. Next, we close the loop.`);

  // ===== Section 3 =====
  pres.addSection({ title: "04 Closing the loop" });
  s = pres.addSlide({ masterName: "SECTION", sectionTitle: "04 Closing the loop" });
  s.addText("04", { placeholder: "number" });
  s.addText("Closing the loop", { placeholder: "title" });
  s.addText("Automation, deployment and live demo", { placeholder: "presenter" });
  chips(s, ["ACT"], true);
  s.addNotes(`[~10 s]
We now have a number, a speed in km/h. Automation is what happens next, without a human in the loop.`);

  // 15. Automation
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Closing the loop" });
  s.addText("AUTOMATION", { placeholder: "kicker" });
  s.addText("Automation turns a measurement into an action", { placeholder: "title" });
  chips(s, ["ACT"]);
  const fl = [["LuGauge", "Measure", "Speed per track"], ["LuScale", "Decide", "v > 60 km/h ?"], ["LuCamera", "Evidence", "Snapshot: box, ID, speed, time"], ["LuDatabase", "Record", "Append to violations log"], ["LuMegaphone", "Act", "Alert / display board / e-challan"]];
  const flw = 2.0, flg = 0.4, flx = (W - (5 * flw + 4 * flg)) / 2;
  for (let i = 0; i < 5; i++) {
    const x = flx + i * (flw + flg);
    card(s, x, 2.0, flw, 2.35, i === 1 ? "FEF0C7" : LIGHT);
    await iconCircle(s, x + (flw - 0.8) / 2, 2.25, 0.8, fl[i][0], NAVY, HEX.accent1);
    T(s, fl[i][1], { x, y: 3.2, w: flw, h: 0.35, fontSize: 16, bold: true, color: NAVY, align: "center" });
    T(s, fl[i][2], { x: x + 0.12, y: 3.58, w: flw - 0.24, h: 0.55, fontSize: 13, color: SLATE, align: "center" });
    if (i < 4) s.addImage({ data: await icon("LuArrowRight", HEX.accent5), x: x + flw + 0.06, y: 3.03, w: 0.28, h: 0.28, altText: "arrow" });
  }
  const cols15 = [["In our demo", ["Rule check every frame", "Red box + live counter", "Evidence JPEG", "CSV violation log"], GREEN, "LuCircleCheck"],
    ["A production system adds", ["Number-plate reading", "Human review of every case", "e-challan integration", "Display-board warnings"], SLATE, "LuSquareDashed"]];
  const c15w = (W - 2 * MX - 0.4) / 2;
  for (let c = 0; c < 2; c++) {
    const x = MX + c * (c15w + 0.4);
    T(s, cols15[c][0], { x, y: 4.8, w: c15w, h: 0.35, fontSize: 15, bold: true, color: NAVY });
    for (let i = 0; i < 4; i++) {
      const y = 4.8 + i * 0.42, xx = x + (i % 2) * (c15w / 2);
      const yy = 5.3 + Math.floor(i / 2) * 0.6;
      s.addImage({ data: await icon(cols15[c][3], c ? HEX.accent4 : HEX.accent3), x: xx, y: yy + 0.04, w: 0.28, h: 0.28, altText: c ? "planned" : "done" });
      T(s, cols15[c][1][i], { x: xx + 0.4, y: yy, w: c15w / 2 - 0.45, h: 0.38, fontSize: 14, valign: "middle" });
    }
  }
  s.addNotes(`[~1.5 min]
Classic automation is sense, think, act. Vision is the sensing; this slide is the thinking and acting.
For every tracked vehicle, every frame, a simple rule runs: is the speed above 60? If yes, we capture evidence: a snapshot with the box, the ID, the measured speed and the timestamp. We record it in a log, and then something acts on it: an alert, a "slow down" message on one of the flyover's display boards, or in a full system an e-challan.
I want to be clear about scope. Our demo does the green column: the rule, the red box, the evidence images and the CSV log. A production system adds number-plate reading, a human reviewing every case before a fine is issued, and integration with the e-challan system. The human review is not optional. It's the answer to the 80% problem.`);

  // 16. Architecture
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Closing the loop" });
  s.addText("SYSTEM ARCHITECTURE", { placeholder: "kicker" });
  s.addText("The whole system is five open-source blocks", { placeholder: "title" });
  chips(s, STAGES);
  const ar = [["LuCamera", "Camera", "video frames", "OpenCV", dget("fps", "30") + " FPS"], ["LuCrosshair", "Detect", "YOLOv8n", "Ultralytics", dget("t_detect", "—") + " ms"], ["LuRoute", "Track", "ByteTrack", "supervision", dget("t_track", "—") + " ms"], ["LuRuler", "Measure", "Homography", "OpenCV / NumPy", dget("t_speed", "—") + " ms"], ["LuSiren", "Act", "Rule engine", "Python", "< 1 ms"]];
  const aw = 2.05, ag = 0.46, ax = (W - (5 * aw + 4 * ag)) / 2;
  for (let i = 0; i < 5; i++) {
    const x = ax + i * (aw + ag);
    card(s, x, 2.0, aw, 2.95, i === 4 ? "FEF0C7" : LIGHT);
    await iconCircle(s, x + 0.25, 2.25, 0.7, ar[i][0], NAVY, HEX.accent1);
    T(s, ar[i][1], { x: x + 0.25, y: 3.12, w: aw - 0.4, h: 0.35, fontSize: 17, bold: true, color: NAVY });
    T(s, ar[i][2], { x: x + 0.25, y: 3.5, w: aw - 0.4, h: 0.35, fontSize: 14, color: INK });
    T(s, ar[i][3], { x: x + 0.25, y: 3.85, w: aw - 0.4, h: 0.3, fontSize: 12, color: SLATE });
    T(s, ar[i][4], { x: x + 0.25, y: 4.3, w: aw - 0.4, h: 0.45, fontSize: 20, bold: true, color: AMBER_DK, valign: "middle" });
    if (i < 4) s.addImage({ data: await icon("LuArrowRight", HEX.accent5), x: x + aw + 0.08, y: 3.3, w: 0.3, h: 0.3, altText: "arrow" });
  }
  T(s, "Orange: measured time per frame on " + dget("cpu_label", "a laptop CPU"), { x: ax, y: 5.07, w: 10, h: 0.3, fontSize: 12, color: MUTED });
  const outs = [["LuMonitor", "Live overlay", "boxes, IDs, km/h, HUD"], ["LuFileWarning", "Evidence", "one JPEG per violator"], ["LuFileText", "Logs", "vehicles.csv · violations.csv"]];
  const ow = (W - 2 * MX - 2 * 0.4) / 3;
  for (let i = 0; i < 3; i++) {
    const x = MX + i * (ow + 0.4);
    await iconCircle(s, x, 5.75, 0.6, outs[i][0], LIGHT, HEX.dk2);
    T(s, outs[i][1], { x: x + 0.8, y: 5.72, w: ow - 0.8, h: 0.33, fontSize: 15, bold: true, color: NAVY });
    T(s, outs[i][2], { x: x + 0.8, y: 6.05, w: ow - 0.8, h: 0.33, fontSize: 13, color: SLATE });
  }
  s.addNotes(`[~1 min]
Here's the full system as it runs in the demo. Frames come from the camera or a video file through OpenCV. YOLOv8 nano detects vehicles, ByteTrack from the supervision library assigns IDs, the homography and speed module converts positions to km/h, and the rule engine decides and records.
The orange numbers are what we measured per frame on ${dget("cpu_label", "a laptop CPU")}. Detection is by far the most expensive stage; everything after it is almost free. That matters for the next slide.
The outputs are a live annotated view, one evidence image per violating vehicle, and two CSV logs. Every block is open source, and the whole pipeline is about 200 lines of Python.`);

  // 17. Real-time
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Closing the loop" });
  s.addText("DEPLOYMENT", { placeholder: "kicker" });
  s.addText("Real time means a 33 ms budget per frame", { placeholder: "title" });
  card(s, MX, 1.9, 3.6, 2.15, NAVY);
  T(s, "33 ms", { x: MX + 0.3, y: 2.0, w: 3.0, h: 0.95, fontSize: 48, bold: true, color: AMBER, valign: "bottom" });
  T(s, "per frame at 30 FPS: detect + track + measure + act", { x: MX + 0.3, y: 3.0, w: 3.0, h: 0.85, fontSize: 14, color: "D0D5DD" });
  card(s, MX, 4.3, 3.6, 2.15);
  T(s, dget("fps_meas", "—") + " FPS", { x: MX + 0.3, y: 4.4, w: 3.0, h: 0.95, fontSize: 44, bold: true, color: NAVY, valign: "bottom" });
  T(s, "end-to-end in our demo on " + dget("cpu_label", "a laptop CPU") + "; camera runs at 25 FPS", { x: MX + 0.3, y: 5.4, w: 3.0, h: 0.85, fontSize: 14, color: SLATE });
  const cx17 = 4.6, cw17 = 4.9;
  T(s, "YOLOv8 size vs CPU speed (640 px)", { x: cx17, y: 1.9, w: cw17, h: 0.35, fontSize: 15, bold: true, color: NAVY });
  s.addChart(pres.charts.BAR, [{ name: "CPU ms / image", labels: ["v8n  ·  mAP 37.3", "v8s  ·  mAP 44.9", "v8m  ·  mAP 50.2"], values: [80.4, 128.4, 234.7] }], {
    x: cx17, y: 2.3, w: cw17, h: 3.6, barDir: "col", valAxisMinVal: 0, valAxisMaxVal: 250, valAxisMajorUnit: 50,
    chartColors: [HEX.accent1, HEX.accent5, HEX.accent5], varyColors: true,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0 \"ms\"", dataLabelFontSize: 12, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt",
    catAxisLabelColor: HEX.accent4, valAxisLabelColor: HEX.accent5, catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E4E7EC", size: 0.75 }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 70,
  });
  T(s, "Ultralytics benchmark: CPU ONNX, per image. Bigger = more accurate, slower.", { x: cx17, y: 6.0, w: cw17, h: 0.45, fontSize: 11, color: MUTED });
  const rx17 = 9.9, rw17 = W - MX - rx17;
  T(s, "Levers to fit the budget", { x: rx17, y: 1.9, w: rw17, h: 0.35, fontSize: 15, bold: true, color: NAVY });
  ["Smallest model that's accurate enough", "Lower input resolution", "Process every 2nd frame (speed still works)", "Edge GPU, e.g. NVIDIA Jetson", "INT8 quantisation / TensorRT"].forEach((t, i) => {
    T(s, t, { x: rx17 + 0.3, y: 2.38 + i * 0.78, w: rw17 - 0.3, h: 0.68, fontSize: 14, valign: "middle" });
    s.addShape(pres.shapes.OVAL, { x: rx17, y: 2.38 + i * 0.78 + 0.27, w: 0.14, h: 0.14, fill: { color: AMBER }, line: { type: "none" }, objectName: "dot" });
  });
  s.addNotes(`[~1 min]
At 30 frames per second, everything has to finish in 33 milliseconds per frame, or the system falls behind the camera. On our machine we measured ${dget("fps_meas", "—")} frames per second end to end.
The chart is the core trade-off, from Ultralytics' own benchmarks on CPU: the nano model takes about 80 ms per image at 37.3 mAP; the medium model is three times slower for about 13 points more mAP. For speed estimation, nano is accurate enough on cars, which are large, distinct objects.
If you need more headroom: use a smaller input, process every second frame (speed is computed over a one-second window, so that still works), move to an edge GPU like a Jetson, or quantise the model to 8-bit integers.`);

  // 18. Limits
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "04 Closing the loop" });
  s.addText("LIMITATIONS & ETHICS", { placeholder: "kicker" });
  s.addText("What this system cannot (yet) do", { placeholder: "title" });
  const lim = [
    ["LuCloudRain", "Environment", "Night, rain, glare and headlights reduce detection confidence; COCO is mostly daylight imagery."],
    ["LuRuler", "Geometry", "Flyover vibration and camera drift break calibration; curves and slopes violate the flat-road assumption."],
    ["LuScale", "Legal grade", "Fines need certified, audited accuracy. The flyover trial (20% → 80%) shows how high that bar is."],
    ["LuLock", "Privacy", "Vehicle images and plates are personal data: retention limits, access control, purpose limitation."],
  ];
  const lw = (W - 2 * MX - 0.4) / 2, lh = 2.05;
  for (let i = 0; i < 4; i++) {
    const x = MX + (i % 2) * (lw + 0.4), y = 1.95 + Math.floor(i / 2) * (lh + 0.3);
    card(s, x, y, lw, lh);
    await iconCircle(s, x + 0.35, y + 0.35, 0.75, lim[i][0], NAVY, HEX.accent1);
    T(s, lim[i][1], { x: x + 1.35, y: y + 0.38, w: lw - 1.7, h: 0.4, fontSize: 18, bold: true, color: NAVY });
    T(s, lim[i][2], { x: x + 1.35, y: y + 0.85, w: lw - 1.7, h: 1.05, fontSize: 14, color: SLATE });
  }
  s.addNotes(`[~1 min]
Four limits we want to state honestly.
Environment: our model was trained mostly on daylight images. Night, rain and headlight glare all reduce confidence.
Geometry: a flyover vibrates, and a camera that shifts by a few pixels breaks the calibration. Our method also assumes a flat road, and real roads curve and slope.
Legal grade: a demo isn't evidence. Fines require certified, audited accuracy. The real system on this flyover spent months in trial for exactly this reason.
Privacy: images of vehicles and number plates are personal data, so storing them needs limits on retention, access and purpose.
Now, let's see it run.`);

  // 19. Demo
  pres.addSection({ title: "Demo & results" });
  s = pres.addSlide({ masterName: "SECTION", sectionTitle: "Demo & results" });
  s.addText("LIVE", { placeholder: "number" });
  s.addText("Speed check demo", { placeholder: "title" });
  s.addText("YOLOv8n + ByteTrack + homography  ·  limit 60 km/h, then a 50 km/h test", { placeholder: "presenter" });
  const watch = [["IDs stay stable", "as cars pass each other"], ["Speed settles", "after ~0.5 s of tracking"], ["Red box + snapshot", "the moment v > limit"]];
  watch.forEach(([a, b], i) => {
    const x = MX + i * 4.05;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.15, w: 3.75, h: 1.15, rectRadius: 0.08, fill: { color: "1D3550" }, line: { type: "none" }, objectName: "watch-card" });
    T(s, "Watch for " + (i + 1), { x: x + 0.25, y: 5.25, w: 3.3, h: 0.3, fontSize: 11, bold: true, color: AMBER, charSpacing: 1 });
    T(s, a, { x: x + 0.25, y: 5.55, w: 3.3, h: 0.35, fontSize: 16, bold: true, color: WHITE });
    T(s, b, { x: x + 0.25, y: 5.88, w: 3.3, h: 0.3, fontSize: 13, color: "D0D5DD" });
  });
  s.addNotes(`[5-10 min | DEMO CHECKLIST]
BEFORE THE TALK (see cv-automation-ppt/demo/README.md)
- cd cv-automation-ppt/demo, then activate the venv (pip install -r requirements.txt done beforehand; no internet needed on stage)
- Dry run: python speed_detection.py --show  (window opens, FPS > 10)
- Plug in the charger (CPU slows on battery); close heavy apps
- Backups ready in a video player: outputs/annotated.mp4 and outputs/demo_limit50/annotated.mp4

DURING THE DEMO (Alt+Tab out of PowerPoint; these notes stay in Presenter View)
1. python calibrate.py --check  -> show the yellow 4-point zone: "this is the homography from the homography slide; 30 m along the road, 14 m across"
2. python speed_detection.py --show  (limit 60, the flyover limit)
   - Point at the HUD: FPS, vehicles, violations
   - SPACE pauses: show stable IDs and km/h labels; boxes only appear inside the zone (by design)
   - Say: "this road is urban traffic, 30 to 55 km/h, so at 60 nobody gets flagged, and that's the correct answer"
3. python speed_detection.py --show --limit 50 --out outputs/demo_limit50
   - Car #7 turns red at about 58 km/h, around 8 s in. Pause on it.
4. Open outputs/demo_limit50/violations/ (evidence JPEGs) and violations.csv
5. Q quits

SAY
"Same code, one parameter changed. Everything you saw is the five stages from the roadmap: about 200 lines of Python, no training."
Then back to PowerPoint, next slide: Results.`);

  // 20. Results
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Demo & results" });
  s.addText("RESULTS", { placeholder: "kicker" });
  s.addText(dget("results_title", "Results"), { placeholder: "title" });
  const rs = [[dget("n_vehicles"), "vehicles tracked"], [dget("median_speed") + " km/h", "median speed"], [dget("n_viol"), "above 60 km/h (" + dget("n_viol50") + " above 50)"], [dget("fps_meas") + " FPS", "processing speed (CPU)"]];
  const rsw = (W - 2 * MX - 3 * 0.3) / 4;
  rs.forEach(([b, l], i) => {
    const x = MX + i * (rsw + 0.3);
    card(s, x, 1.9, rsw, 1.3, i === 2 ? "FEE4E2" : LIGHT);
    T(s, String(b), { x: x + 0.25, y: 1.95, w: rsw - 0.5, h: 0.7, fontSize: 32, bold: true, color: i === 2 ? RED : NAVY, valign: "bottom" });
    T(s, l, { x: x + 0.25, y: 2.68, w: rsw - 0.4, h: 0.45, fontSize: 13, color: SLATE });
  });
  T(s, "Peak speed per vehicle (n = " + dget("n_vehicles") + ")", { x: MX, y: 3.35, w: 7.2, h: 0.35, fontSize: 15, bold: true, color: NAVY });
  const hist = DATA.hist || { labels: ["—"], under: [0], over: [0] };
  s.addChart(pres.charts.BAR, [{ name: "≤ 50 km/h", labels: hist.labels, values: hist.under }, { name: "> 50 km/h (flagged in test run)", labels: hist.labels, values: hist.over }], {
    x: MX, y: 3.7, w: 7.2, h: 2.75, barDir: "col", barGrouping: "stacked", barGapWidthPct: 25,
    chartColors: [HEX.dk2, HEX.accent1], showLegend: true, legendPos: "t", legendFontSize: 12, legendColor: HEX.accent4, legendFontFace: "+mn-lt",
    catAxisLabelColor: HEX.accent4, valAxisLabelColor: HEX.accent5, catAxisLabelFontSize: 11, valAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valAxisTitle: "vehicles", showValAxisTitle: true, valAxisTitleFontSize: 11, valAxisTitleColor: HEX.accent5, catAxisTitle: "km/h", showCatAxisTitle: true, catAxisTitleFontSize: 11, catAxisTitleColor: HEX.accent5,
    valGridLine: { color: "E4E7EC", size: 0.75 }, catGridLine: { style: "none" },
  });
  const vx = 8.25, vw = W - MX - vx;
  T(s, "Auto-captured evidence", { x: vx, y: 3.35, w: vw, h: 0.35, fontSize: 15, bold: true, color: NAVY });
  const vi = await addImg(s, path.join(DEMO, "violation_example.png"), vx, 3.75, vw, 2.2, { align: "left", valign: "top", alt: "Evidence snapshot of a vehicle above the speed limit" });
  T(s, dget("viol_caption", ""), { x: vx, y: vi.y + vi.h + 0.08, w: vw, h: 0.45, fontSize: 12, color: SLATE });
  source(s, dget("results_source", "Footage and calibration: see demo README."));
  s.addNotes(`[~1.5 min]
${dget("results_spoken", "Summarise the numbers on this slide.")}
Two honest caveats. First, this is public traffic-camera footage of an urban road, not the flyover, and the calibration uses assumed lane dimensions, so treat the absolute speeds as estimates. Second, we haven't measured ground-truth speeds with a radar, so this shows the pipeline works, not that it's certified-accurate. That validation is exactly what the real flyover system has been doing during its trial.`);

  // 21. Takeaways
  pres.addSection({ title: "Close" });
  s = pres.addSlide({ masterName: "DARK", sectionTitle: "Close" });
  s.addText("TAKEAWAYS", { placeholder: "kicker" });
  s.addText("Three things to remember", { placeholder: "title" });
  const tk = [["Every domain runs the same loop: see, decide, act", "Factories, farms, hospitals, roads: detect, track or classify, apply a rule, then act. Our speed system is ~200 lines of open-source blocks."],
    ["The model is the easy part", "Calibration, frame timing, night, rain and vibration decide whether the number is right."],
    ["Precision before scale", "Just Walk Out, the flyover trial, 87% screening sensitivity: keep a human in the loop until accuracy is proven."]];
  tk.forEach(([a, b], i) => {
    const y = 1.95 + i * 1.5;
    T(s, "0" + (i + 1), { x: MX, y, w: 1.2, h: 1.0, fontSize: 48, bold: true, color: AMBER, valign: "top" });
    T(s, a, { x: MX + 1.4, y: y + 0.05, w: 10.5, h: 0.45, fontSize: 22, bold: true, color: WHITE });
    T(s, b, { x: MX + 1.4, y: y + 0.55, w: 10.5, h: 0.7, fontSize: 16, color: "D0D5DD" });
  });
  s.addNotes(`[~45 s]
Three things to take away.
One: whether it's a weed, a tumour, a parcel or a speeding car, every system we showed runs the same loop: see, decide, act. Our speed system is that loop in about 200 lines of open-source code, with no training.
Two: the model is the easy part. Whether the speed is right depends on calibration, frame timing and conditions like night, rain and vibration.
Three: precision before scale. Amazon pulled Just Walk Out, the flyover cameras spent months in trial, and screening AI still misses about one case in eight. When the output affects a person, keep a human in the loop until accuracy is proven.`);

  // 22. References
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Close" });
  s.addText("REFERENCES", { placeholder: "kicker" });
  s.addText("Sources", { placeholder: "title" });
  const refsA = [
    "Jocher, G. et al. Ultralytics YOLOv8 (2023), docs.ultralytics.com",
    "Zhang, Y. et al. ByteTrack. ECCV 2022",
    "Lin, T.-Y. et al. Microsoft COCO. ECCV 2014",
    "Redmon, J. et al. You Only Look Once. CVPR 2016",
    "Hartley & Zisserman. Multiple View Geometry, 2nd ed.",
    "Zivkovic, Z. Adaptive GMM background subtraction (MOG2). ICPR 2004",
    "Roboflow supervision: speed-estimation example, github.com/roboflow/supervision",
    "Wikipedia: G. D. Naidu Elevated Expressway; The Week (9 Oct 2025)",
    "Lokmat Times: three killed near GD Naidu Flyover (2025)",
    "BizzBuzz; The Hawk; NewKerala (2026): flyover AI cameras in trial",
  ];
  if (DATA.footage_ref) refsA.push("Demo footage: cars.mp4, github.com/kraten/vehicle-speed-check");
  const refsB = [
    "BMW Group / Axis Communications: AIQX quality inspection case study",
    "John Deere news release (18 Sep 2024): See & Spray 59% average savings",
    "Grainews: Iowa State University See & Spray field study",
    "US FDA: Artificial Intelligence-Enabled Medical Devices list (Dec 2025)",
    "American Academy of Ophthalmology (2018): IDx-DR FDA clearance",
    "Qure.ai qXR TB screening in India: press coverage",
    "Supply Chain Dive (2022): Amazon Sparrow robot",
    "CNBC; DeepLearning.AI The Batch (Apr 2024): Just Walk Out removed from Fresh",
    "Claims Journal (Feb 2026): Waymo weekly paid rides",
    "Onmanorama; Kerala Kaumudi (2023): Safe Kerala AI cameras",
    "Swarajya (2025): DigiYatra at 24 airports",
  ];
  const colW = (W - 2 * MX - 0.5) / 2;
  T(s, "Technical & deep dive", { x: MX, y: 1.85, w: colW, h: 0.35, fontSize: 14, bold: true, color: NAVY });
  T(s, "Domains", { x: MX + colW + 0.5, y: 1.85, w: colW, h: 0.35, fontSize: 14, bold: true, color: NAVY });
  T(s, refsA.map((r, i) => ({ text: r, options: { bullet: { type: "number" }, breakLine: i < refsA.length - 1 } })), { x: MX, y: 2.3, w: colW, h: 4.5, fontSize: 12, color: INK, paraSpaceAfter: 4 });
  T(s, refsB.map((r, i) => ({ text: r, options: { bullet: { type: "number", numberStartAt: refsA.length + 1 }, breakLine: i < refsB.length - 1 } })), { x: MX + colW + 0.5, y: 2.3, w: colW, h: 4.5, fontSize: 12, color: INK, paraSpaceAfter: 4 });
  s.addNotes("Reference slide. No need to read out; leave up briefly if asked about sources.");

  // 23. Thank you
  s = pres.addSlide({ masterName: "BLANK_DARK", sectionTitle: "Close" });
  T(s, "Thank you", { x: MX, y: 2.0, w: 8, h: 1.2, fontSize: 60, bold: true, color: WHITE, valign: "bottom" });
  T(s, "Questions?", { x: MX, y: 3.3, w: 8, h: 0.7, fontSize: 32, color: AMBER });
  T(s, "Thithiksha   ·   Arul   ·   DPD", { x: MX, y: 5.0, w: 8, h: 0.4, fontSize: 18, bold: true, color: WHITE });
  T(s, "Computer Vision (20XW97)", { x: MX, y: 5.45, w: 8, h: 0.35, fontSize: 14, color: MUTED });
  s.addShape(pres.shapes.OVAL, { x: 9.3, y: 2.0, w: 3.0, h: 3.0, fill: { color: WHITE }, line: { color: RED, width: 18 }, objectName: "speed-sign" });
  s.addText("60", { x: 9.3, y: 2.0, w: 3.0, h: 3.0, fontSize: 92, bold: true, color: INK, align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addNotes(`[closing]
Thank you. We're happy to take questions, on the theory or on the code.
Likely questions:
- Why not radar? Radar is accurate but per-lane and expensive; one camera covers several lanes and also gives evidence images. Real systems often fuse both.
- How accurate is it? Without radar ground truth we can't claim a number. The error analysis slide shows how to bound it.
- Number plates? Needs a higher-resolution camera and an OCR stage (for example a plate detector followed by an OCR model). That's the next extension.
- Night? Needs IR illumination or a model fine-tuned on night footage.`);

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
}

build().catch((e) => { console.error(e); process.exit(1); });
