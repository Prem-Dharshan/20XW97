# Deck source

Regenerates `../CV_and_Automation.pptx` (26 slides, speaker notes included).

```bash
npm install
python3 make_data.py      # numbers from ../demo/outputs -> data.json
node build.js             # writes ../CV_and_Automation.pptx
```

`build.js` applies the deck's colour theme with the pptx skill's `apply_theme.js`; set `APPLY_THEME=/path/to/apply_theme.js` (or `PPTX_SKILL`). Without it, edit the slides directly in PowerPoint instead.

`assets/` holds the generated convolution GIF (`make_conv_gif.py`) and the pixel-zoom image (`make_pixels.py`, made from `../demo/outputs/frame_raw.png`). The other images come from `../demo/outputs/`.
