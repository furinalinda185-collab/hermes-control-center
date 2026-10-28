# Installing NixOS onto the running distro's disk, without a USB stick

Verified end to end on this laptop (Ryoku/Arch -> NixOS, 2026-10). The NixOS
manual documents this as "Installing NixOS from another Linux distribution":
no ISO, no dd, and the current system keeps working until the reboot.

## Why not dd

`dd` of an ISO onto the disk that holds the live root overwrites the extents
backing `/` while the kernel is still running from them, and what lands is a
*live installer*, not an installed system. If the goal is "NixOS on this disk",
dd is only ever the step that writes a USB stick.

## Order of work

1. **Config first, in a git repo under `$HOME`.** Flakes only see committed
   files. Clone the rice to `~/nixos`, put the host `variables.nix` and a real
   `hardware-configuration.nix` in place, commit. Uncommitted edits are silently
   invisible to `nix build` and `nixos-install`.
2. **Nix on the host:** `pacman -S nix` (Arch ships nixbld users via sysusers),
   `systemctl enable --now nix-daemon.socket`, then as the user
   `nix-channel --add https://nixos.org/channels/nixos-25.11 nixpkgs`,
   `nix-channel --update`, `nix-env -f '<nixpkgs>' -iA nixos-install-tools`.
3. **Subvolumes, not a wipe:**

       mount -o subvolid=5 /dev/<disk>p2 /mnt/bt
       btrfs subvolume create   /mnt/bt/@nixos
       btrfs subvolume snapshot /mnt/bt/@home /mnt/bt/@nixos-home

   The snapshot is instant and CoW: a 546 GiB home costs ~0 bytes until the two
   diverge. That is what makes "no backup" survivable, and Ryoku's `@home` stays
   pristine as the fallback.
4. **Mount and generate:** `@nixos` -> `/mnt/nixos`, `@nixos-home` ->
   `/mnt/nixos/home`, ESP -> `/mnt/nixos/boot`, then
   `nixos-generate-config --root /mnt/nixos`. Check the output: it must NOT
   contain `/var/log`, `/swap`, `/.snapshots` or the old package cache (those are
   the old distro's subvolumes and would be mounted read-write by the new one).
5. **Build as the user before installing:**
   `nix build .#nixosConfigurations.<host>.config.system.build.toplevel`. This
   surfaces every eval and compile error while the old system is still healthy,
   and turns `nixos-install` into a copy. Check the result holds what the boot
   needs: `kernel-modules/lib/modules/*/kernel/fs/btrfs` and `nvidia.ko.xz`.
6. **Install:** `nixos-install --root /mnt/nixos --flake ~/nixos#<host> --no-root-passwd`.
7. **Verify the bootloader separately** (see trap 1).

## Traps, in the order they bite

1. **`/etc/NIXOS` does not mean the bootloader installed.** `nixos-install`
   touches it *before* the bootloader step, and if that step produces nothing you
   still get the marker and a fully installed system that cannot boot. Verify
   `/boot/grub/grub.cfg`, `/boot/EFI/<id>/grubx64.efi`, the kernel + initrd under
   `/boot/kernels/`, and a new `efibootmgr` entry. Nothing on the ESP = it did
   not run.
2. **Never call `install-grub.sh` by hand.** It opens with
   `my $defaultConfig = $ARGV[1] or die;` and fails as a bare
   `Died at .../install-grub.pl line 19.` - the toplevel path is an argument that
   only `switch-to-configuration` supplies. Re-run the real thing:

       NIXOS_INSTALL_BOOTLOADER=1 nixos-enter --root /mnt/nixos \
         -c 'NIXOS_INSTALL_BOOTLOADER=1 /run/current-system/bin/switch-to-configuration boot'

3. **`boot.loader.grub.device = "nodev"` is correct with `efiSupport = true`** -
   it still installs to the ESP. Do not "fix" it to `/dev/nvme0n1`; that is the
   BIOS path.
4. **A shared ESP needs `boot.loader.grub.configurationLimit`.** 2 GiB minus the
   other bootloader minus Ryoku's UKIs leaves ~1.4 GiB; five generations of
   kernel+initrd (~57 MiB each here) fit, ten do not.
5. **Verify fstab by content, not by `tail`.** NixOS 26.11 makes `/etc/fstab` a
   symlink chain into the store (`/etc/static/fstab` -> `/nix/store/*-etc-fstab`),
   so it cannot be written from outside the chroot, and the generated file ends
   in several blank lines - `tail -3` shows nothing while `/home` is present. Read
   the whole file and check every mount, especially `/home`.
6. **`rsync` may not exist on the host.** Arch base has it only if pulled in;
   use `tar -C src -cf - . | tar -C dst -xf -` for the config sync.
7. **polkit cannot prompt for you.** `hyprpolkitagent` was installed but
   crash-looping (SEGV, start-limit-hit), so `pkexec` refuses with "Not
   authorized" once any earlier grant expires (~5 min). Every root step has to be
   handed to the user as one `sudo bash <script>` line; do not burn attempts on
   pkexec, and always have the script `tee` to a log so the failure is readable
   afterwards.
8. **home-manager versus the old dotfiles.** Sharing the home means activation
   meets a fully populated `~/.config`. `backupFileExtension = "backup"` plus
   `overwriteBackup = true` (already in the rice's `users.nix`) moves each
   conflict aside instead of aborting the first boot.

## Rollback

Nothing in this path writes `@` or `@home`. The old system stays bootable from
firmware (its own Limine entry) until `btrfs subvolume delete /mnt/bt/@` is run
on purpose, which frees the old OS only - `@home` and `@nixos-home` are separate
subvolumes and both keep the data.
