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