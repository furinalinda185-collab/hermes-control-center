{
  # Copy to hosts/<host>/variables.nix in the NixOS rice, replacing the upstream
  # default. Values below are for this laptop: Intel Core Ultra 9 275HX +
  # RTX 5070 Ti Mobile (Blackwell), AX211 Wi-Fi/BT, 30 GiB RAM, US locale.
  # One edit outside this file is still required: hardware.nvidia.open = true
  # in modules/hardware/video/nvidia.nix (see nix/README.md).

  username = "mamaroufaren"; # install.sh overwrites this with $USER

  # Desktop Environment
  desktop = "hyprland"; # hyprland, i3, gnome, plasma6

  # Theme & Appearance
  bar = "waybar"; # waybar, noctalia, wayle
  waybarTheme = "minimal"; # stylish, minimal
  sddmTheme = "jake_the_dog"; # astronaut, black_hole, purple_leaves, jake_the_dog, hyprland_kath
  defaultWallpaper = "evening-sky.webp"; # SUPER + SHIFT + W to change
  hyprlockWallpaper = "kurzgesagt-galaxies.webp";

  # Default Applications
  terminal = "kitty"; # kitty, alacritty, wezterm
  editor = "nixvim"; # nixvim, zed, vscode, helix, doom-emacs, nvchad, neovim
  browser = "zen-beta"; # librewolf, zen-beta, firefox, floorp
  fileManager = "yazi"; # yazi, lf, thunar
  shell = "zsh"; # bash, zsh
  games = false;

  # Hardware — laptop, hybrid Intel + NVIDIA
  hostname = "nixos"; # rename to taste; must match hosts/<dir>
  videoDriver = "nvidia"; # nvidia, amdgpu, intel, nvk
  nvidiaChannel = "latest"; # 580 is the legacy branch; Blackwell needs current
  bluetoothSupport = true; # Intel AX211
  batterySupport = true; # laptop: upower, tlp, lid

  # Localization
  timezone = "America/Los_Angeles";
  locale = "en_US.UTF-8";
  clock24h = true;
  kbdLayout = "us";
  kbdVariant = "";
  consoleKeymap = "us";
  capslockAsESC = false;
}
