# Google Slides version

The Google Slides copy of the deck was built natively through the Slides API, from the same `../build.js`.

1. Record the deck: run `../build.js` with `NODE_PATH` pointing at `mock/` (plus real `react`, `react-dom`, `react-icons`, `sharp`) and `APPLY_THEME=mock/noop_theme.js`, `MOCK_OUT=deck.json`. The mock `pptxgenjs` writes every slide element to JSON instead of a .pptx.
2. `python3 convert.py` turns `deck.json` into `req/NN.json` batchUpdate requests (page scaled 13.33 in → 10 in; icons and chart crops are served from `../../gslides/` on GitHub raw URLs).
3. Send the batches with the Slides API, then read the deck and run `finish.py` for speaker notes, slide order and template clean-up.

Known differences from the .pptx: no letter spacing (not in the Slides API) and Google's fixed corner radius on rounded rectangles.
