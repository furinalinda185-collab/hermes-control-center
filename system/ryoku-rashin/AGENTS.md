<!-- rashin:generated:begin -->
# Ryoku system vault

This is the shared knowledge base for every coding agent on this machine
(Arch Linux, the Ryoku desktop, managed by Ryoku). Read it before exploring
the filesystem or guessing where things live.

## The one rule

Read `desktop.md` before searching the filesystem. It maps every subsystem to
its config path, the binary that owns it, and how to reload it. Guessing paths
wastes tokens the map already spent.

To change the desktop, use the `ryoku` skill (linked into your skills dir;
`desktop.md` names its path and carries the GUI map): answer "how do I" GUI-
first, act through commands, never edit shipped files. A new bar widget is a
plugin, per the skill's `plugins.md`.

## What is here

- `system.md` generated: hardware, kernel, GPU, disks, displays.
- `desktop.md` generated: the Ryoku map (configs, owners, reload commands).
- `packages.md` generated: installed package counts, the explicit set, updates.
- `ryoku-repo.md` generated: the Ryoku source tree map (pre-indexed, ships with the system).
- `user.md` generated: where this user's config diverges from the shipped baseline.
- `habits.md` generated: this user's directories, tool stack, and shell rhythms.
- `memory/` durable notes agents author and keep across sessions.
- `journal/` dated notes, one file per day named `YYYY-MM-DD.md`.

## Rules

- The generated files are read only. Their content between the
  `rashin:generated` markers is overwritten on every reindex; edits there are
  lost. Write anything durable to `memory/` or `journal/` instead.
- Answer a "how do I" desktop question GUI-first: name the Ryoku Hub page,
  shell picker, or QS Bar Settings from desktop.md's GUI map (and the `ryoku`
  skill's `gui.md`) before the command behind it. You still act through commands.
- Changes listed in `user.md` are the user's own; never revert them to
  shipped defaults without being asked.
- This file's generated body is refreshed on every reindex; add your own prose
  outside the `rashin:generated` markers and it is kept. `CLAUDE.md` symlinks here.
<!-- rashin:generated:end -->
