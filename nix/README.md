# nix/ — ready-made bits for the NixOS rice

Target rice: https://github.com/Sly-Harvey/NixOS, pinned at commit `d1c1ce4dc6`.
Rationale, knob-by-knob justification and the install checklist live in
[docs/nixos-rice.md](../docs/nixos-rice.md).

## Files

| File | Use |
|---|---|
| `variables.laptop.nix` | replaces `hosts/<host>/variables.nix` — every knob set for this specific laptop |

## Two required edits outside the variable file

1. **Open NVIDIA module (Blackwell).** The upstream module pins the proprietary
   driver, which does not load on GB20x:

       # modules/hardware/video/nvidia.nix
       hardware.nvidia.open = false;   →   true

2. **Driver channel.** Already handled by `nvidiaChannel = "latest"` in the file
   above; if the rebuild fails on 580-era branches, this is the reason.

## Porting order

    cp variables.laptop.nix ~/nixos/hosts/<host>/variables.nix
    # edit hardware.nvidia.open, then:
    sudo nixos-rebuild switch --flake ~/nixos#<host>

## Deliberately not vendored

The upstream tree (601 files, ~197 MB once checked out with the flake inputs) is
not copied into this repo. Two reasons: it is MIT-licensed public work that
`git clone` fetches faster than this repo can serve, and a stale copy would drift.
This repo carries only the machine-specific deltas — the values that differ from
upstream — plus a pinned commit hash for reproducibility.

If the upstream repo ever disappears, the pinned commit is the thing to mirror;
note it in `docs/nixos-rice.md` before it goes.
