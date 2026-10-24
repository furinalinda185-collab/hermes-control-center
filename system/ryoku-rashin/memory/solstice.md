# Solstice shaderpack

- Source: `~/.local/share/PrismLauncher/instances/Fabulously Optimized/minecraft/shaderpacks/solstice/`.
- Installed ZIP: sibling `solstice-v1.0.zip`. Rebuild after source and documentation
  changes; archive paths start at `shaders/`, not `solstice/`. Existing packaging
  excludes `tools/` and `__pycache__/`. Preserve Photon/Phoxel and user's active
  shader selection.
- Runtime: Iris 1.11.6, Minecraft 26.3, RTX 5070 Ti Laptop GPU, NVIDIA 615.71.09.
- Read the source pack's `NOTES.md` for incident history and validation limits.
- Checks from source folder: `python3 tools/solstice_lint.py --world all` and
  `python3 tools/solstice_render_check.py`. The latter uses system libGL/libglfw
  through ctypes with a hidden compatibility window and checks actual pixels.
  It does not emulate Iris's transformations or Minecraft draw order.
- 2026-09-30: user confirmed successful loading, then reported PNG-like items
  and darkness. Fixed alpha/depth rejection, double lightmap normalization,
  unconditional shadow tint, raw shadow comparison settings, preprocessor enums,
  missing LUT moon transmittance, held-item projection and reversed exposure.
  All 38 pairs compile/link natively; six GPU pixel regressions pass and fail on
  the old source. In-game appearance after these fixes still awaits confirmation.
- Remaining known gap: Iris menu-option warnings persist after successful loads;
  static option-name matching is not evidence of actual option discovery. Custom
  `const` sliders and unused boolean settings need separate investigation.
