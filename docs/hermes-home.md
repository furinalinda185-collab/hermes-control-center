# Hermes home — anatomy and effective config

What is actually in `~/.hermes` on this machine, what matters after a hop, and
how to change it without breaking things. Snapshot date 2026-10-26.

## Layout and sizes

| Path | Size | In repo | Notes |
|---|---|---|---|
| `hermes-agent/` | 1.2 G | no | git checkout of Hermes itself; `hermes update` |
| `tools/` | 1.7 G | no | downloaded binaries (browser, media, etc.) |
| `installs/` | 1.3 G | no | per-install venvs/interpreters |
| `cache/` | 360 M | no | scratch; pruned automatically |
| `state.db` | 27 M | encrypted | session history; dump with `sqlite3 .backup` |
| `logs/` | 5.6 M | no | |
| `skills/` | 3.6 M | **yes** | 67 `SKILL.md` live; 68 in the repo (`ryoku` symlink materialized) |
| `config.yaml` | 124 K / 2,385 lines | **yes** | mostly commented defaults; ~60 active keys |
| `memories/` | 1.2 K | **yes** | `MEMORY.md`, `user.md` |
| `SOUL.md` | 667 B | **yes** | system-prompt identity |
| `.env`, `auth.json` | small | encrypted | keys and OAuth tokens |
| `cron/` | — | **yes** | `executions.db` + output; no job definitions active |

Total 4.5 G, of which ~3.7 M is irreplaceable.

## Effective configuration

Only these values are actually set; everything else in `config.yaml` is the
commented default that ships with `_config_version: 51`.

    model.default                mimo-v2.6-flash      (session in use: deepseek-v4.1-flash)
    model.provider               opencode-go
    model.base_url               https://opencode.ai/zen/go/v1
    model.api_mode               chat_completions
    memory.memory_enabled        true       (limit 2,200 chars)
    memory.user_profile_enabled  true       (limit 1,375 chars)
    skills.creation_nudge_interval 15
    agent.max_turns              150
    terminal.backend             local, cwd ".", timeout 180 s
    cron.catch_up_missed         true
    tool_loop_guardrails         on: 2 exact / 3 same-tool / 2 no-progress failures

Model alias for the local stack:

    model_aliases.local-nemotron → nemotron-3.5-lightning
                                   provider local-nemotron
                                   http://127.0.0.1:8080/v1  (context 65,536)

Provider block `providers.local-nemotron` mirrors that base URL and default
model. No API key: it is a local llama.cpp / OpenAI-compatible server.

## Secrets present (names only)

From `~/.hermes/.env`: `OPENCODE_GO_API_KEY`, `DISCORD_BOT_TOKEN`,
`BROWSERBASE_ADVANCED_STEALTH`, `BROWSERBASE_PROXIES`, `BROWSER_*_TIMEOUT`,
`CAMOFOX_URL`, `TERMINAL_*`, `*_TOOLS_DEBUG`. No literal keys inside
`config.yaml` — verified by grep. The Obsidian note that held the OpenCode key in
plaintext is redacted in `vault/`.

## Editing rules

- Change settings with `hermes config set <dot.key> <value>` (or `/config` in a
  session), then re-run `scripts/snapshot.sh`. Do not hand-edit the 2,385-line
  file and do not copy a `config.yaml` between machines: `_config_version` is
  per-install and migrations key off it.
- Add skills with `skill_manage` (or drop a `SKILL.md` under
  `~/.hermes/skills/<category>/<name>/`), then snapshot. Descriptions must stay
  under 60 chars or the index truncates the routing signal.
- Memory is capped at 2,200 chars and injected into every turn: durable facts
  only, procedures belong in skills.

## What breaks on a distro hop

1. **Absolute paths in `config.yaml`** — tool binaries, browser executable,
   `/usr/bin/...`. `hermes doctor` lists them; fix with `hermes config set`.
2. **The `ryoku` skill and the `ryoku-rashin` memory block** — point at
   `/usr/share/ryoku` and `~/.local/share/ryoku/rashin`, both absent elsewhere.
   `restore.sh --drop-ryoku` removes them.
3. **Provider auth** — `.env` and `auth.json` are restored only with
   `--with-secrets`; without them every model call 401s while the UI looks fine.
4. **`state.db`** — only restored with `--with-sessions`; a silent skip if one
   already exists (needs `--force`).
5. **Group membership** — `uucp`/`dialout` for hardware, `video`, `input`. Not in
   any file; re-add and re-login.
