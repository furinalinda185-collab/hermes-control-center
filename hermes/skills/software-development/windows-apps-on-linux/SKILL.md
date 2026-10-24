---
name: windows-apps-on-linux
description: Use when installing Windows apps under Wine on Linux.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wine, linux, windows-apps, installation]
    related_skills: [systematic-debugging]
---

# Windows applications under Wine

## When to Use

Use for Wine installs, launching Windows apps, or debugging a browser-to-Wine login handoff. For a failing app, also load systematic-debugging.

## Procedure

1. Find the vendor's official Windows installer URL and confirm it resolves to a Windows executable (`curl -I`, then `file` after download). Do not execute a community setup script without reviewing it; its prefix, package manager, GPU, and authentication assumptions may not fit this machine.
2. Discover the existing Wine version, display session, GPU, disk space, and intended target directory. Use a dedicated `WINEPREFIX` for the app, especially when the user requests installation in a particular folder. Initialize with `WINEPREFIX=<target> WINEARCH=win64 wineboot -i`, then run the official installer in that prefix.
3. Verify the install in layers: installer exit status; installed executable and shortcut; launch from the shortcut in the same prefix; visible app window; authentication; and a representative usable action. A successful installer or login page does not prove the application works. Report the last verified layer explicitly.
4. For browser-based OAuth in Wine, trace the complete handoff: app/identity-manager log → host browser opens → browser's custom-scheme prompt → Linux `x-scheme-handler/<scheme>` → handler invocation → identity-manager log and authenticated app. Test scheme dispatch with a harmless probe such as `gio open '<scheme>:/probe'` and a handler log that records only time, never the URL or token. Some callbacks use `<scheme>:/path` rather than `<scheme>://path`; accept the scheme prefix and pass the whole URI as one quoted argument. A probe confirms routing, not successful authentication; verify the real callback separately with the user's own login.
5. When a Wine modal window traps input, inspect the app's compositor/window state and terminate only that app's prefix with `WINEPREFIX=<target> wineserver -k` if needed. Do not kill the global Wine session or unrelated applications.

## Guardrails

- Keep OAuth codes, callback URLs, browser history, and credentials out of logs and chat. The user performs their own login; never claim sign-in is verified from a synthetic callback.
- Treat Wine rendering and identity-service failures as separate diagnoses. Read app and identity-manager logs before trying graphics or compatibility overrides; one can work while the other fails.
- Confirm the host browser's protocol handler and the Wine prefix independently. A browser page saying sign-in succeeded does not establish that its callback reached the app.
