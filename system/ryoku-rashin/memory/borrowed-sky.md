# Borrowed Sky

- Project: `/home/mamaroufaren/Projects/phantom_spire` (the folder keeps its old name).
- Run: `python3 main.py` from the project directory.
- Checks: `python3 -m unittest discover -s tests`.
- The user prefers natural, understated dialogue with ordinary punctuation,
  specific everyday details, and distinct character voices. Avoid dash-heavy
  pauses, speeches, forced banter, heavy metaphors, and cheesy romance.
- Story and romance writing: `engine/story.py`; NPC writing: `data/npcs.json`;
  offline reply pools: `data/characters.json` and `enrich_characters()` in
  `engine/story.py`; optional LLM voice instructions: `engine/dialogue.py`.
- Keep the `offer` and `challenge` branch keys compatible with saved conversations.
- Slot 1 uses `savegame.json`; do not overwrite it during verification.
