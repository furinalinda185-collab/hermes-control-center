# Vault — Obsidian notes

Source: `~/vault` on the Arch/Ryoku machine (vault name `vault`, 48K, 5 notes
plus `.obsidian/`). Copied here 2026-10-26 as part of the distro-hop handoff, so
the notes survive a wipe of the disk.

These are the user's own notes, not agent output. Wikilinks are kept intact
(`[[Note]]`); open them in Obsidian by pointing a vault at this directory.

| Note | What it is |
|---|---|
| [Root.md](Root.md) | Character/baseline note: class `dealer`, race blank. |
| [Commands.md](Commands.md) | Scratch list of commands: phantom_spire, local LLM (`llama-nemotron`, `klm`), Hermes local agent (`hermes-nemotron`, `/model local-nemotron`). |
| [Arduino notes.md](Arduino%20notes.md) | Circuit-board class notes: voltage/current/resistance, Ohm's law, series vs parallel, LEDs, PWM and `analogWrite()` duty cycle. |
| [Circuit board class.md](Circuit%20board%20class.md) | Empty placeholder (created 2026-10-11); likely where lecture notes were meant to land. |
| [Api keys.md](Api%20keys.md) | **Redacted on purpose.** Holds the OpenCode (`oc_sk_…`) key. The real value lives in `~/.hermes/.env` → `secrets/env.enc`. |

## Editing rules

- Do not add plaintext keys, tokens, or passphrases to these notes. This
  directory is in git, and git history is forever.
- The live vault stays at `~/vault`; re-copy after real edits instead of letting
  the two drift. There is no sync job.
- `Api keys.md` is redacted here and will be redacted again if you re-copy it.
  Keep the real key only in `.env` + the encrypted blob, or move it to a password
  manager.
