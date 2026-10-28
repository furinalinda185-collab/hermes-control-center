<!-- ryoku-rashin:begin -->
## Ryoku Rashin system vault

This machine runs Ryoku (Arch Linux, Hyprland desktop). A maintained map of the
system lives at `~/.local/share/ryoku/rashin/`. Before exploring the machine or
guessing paths, read `AGENTS.md` there: it says where every config lives, which
binary owns it, and how to reload it. Write durable notes to `memory/` and
dated notes to `journal/YYYY-MM-DD.md`. For code questions prefer `prowl`
(cited code intelligence, reindexed each run): `prowl search "<question>"`,
`find`, `def`, `references`, `outline`, `impact` -- one call instead of grepping.
The `ryoku` agent skill (safety rules, a bar and dock guide, and the command
catalogue) is wired into this agent's skills directory; read it before
customising the desktop. Answer a desktop "how do I" question GUI-first: name
the Ryoku Hub page, shell picker, or QS Bar Settings before naming any command.
<!-- ryoku-rashin:end -->
§
Hardware: owns an Arduino UNO R4 WiFi (FQBN arduino:renesas_uno:unor4wifi) on /dev/ttyACM0; arduino-cli in ~/bin with the arduino:renesas_uno core installed. Give a user who just ran chown/usermod a re-login reminder.
§
Hermes Control Center: private GitHub repo furinalinda185-collab/hermes-control-center, cloned at ~/hermes-control-center (formerly hermes-brain). Holds machine inventory, ~/.hermes anatomy, vault/ (obsidian notes), AES-encrypted secrets, restore.sh, and scripts/snapshot.sh — run that after changing skills, memories, config, or notes.
§
No working polkit agent on this desktop: hyprpolkitagent segfaults (start-limit-hit) and Quickshell registers none, so pkexec cannot show an auth dialog and non-interactive sudo is impossible. Hand root work to the user as a script they run in their own terminal, with `2>&1 | tee <log>` so the output is readable afterwards.
§
NixOS installed alongside Ryoku on nvme1n1p2 btrfs: @ (Ryoku root), @home, @nixos (NixOS root), @nixos-home (CoW snapshot of @home, used as NixOS /home). The 2 GiB ESP is shared with Ryoku's Limine. Nix 2.35.4 lives in the Arch system; rice at ~/nixos, helper scripts in ~/nixos-install/, notes at ~/nixos/NOTES-local.md.