"""Build notes + ordering requests from a saved read_presentation result (slides.objectId + notes ids)."""
import json, sys
data = json.load(open(sys.argv[1]))
data = data.get("content", data)
if isinstance(data, str): data = json.loads(data)
slides = data["slides"]
notes = json.load(open("notes.json"))
ids = {s["objectId"]: s for s in slides}
reqs = []
want = [f"gs_{n:02d}" for n in range(1, len(notes) + 1)]
missing = [w for w in want if w not in ids]
print("missing slides:", missing, file=sys.stderr)
for i, sid in enumerate(want):
    if sid not in ids: continue
    nid = ids[sid]["slideProperties"]["notesPage"]["notesProperties"]["speakerNotesObjectId"]
    if notes[i].strip():
        reqs.append({"insertText": {"objectId": nid, "text": notes[i]}})
order = [{"updateSlidesPosition": {"slideObjectIds": [sid], "insertionIndex": i}} for i, sid in enumerate(want) if sid in ids]
dels = [{"deleteObject": {"objectId": s["objectId"]}} for s in slides if s["objectId"] not in want]
json.dump(reqs, open("notes_reqs.json", "w"), ensure_ascii=False, separators=(",", ":"))
json.dump(order + dels, open("order_reqs.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(reqs), "notes;", len(order), "moves;", len(dels), "deletes", [d["deleteObject"]["objectId"] for d in dels], file=sys.stderr)
