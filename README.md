<h3 align="center">
  <img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/logos/exports/1544x1544_circle.png" width="100" alt="Catppuccin logo"/><br/>
  Apple Cursors for Linux
</h3>

<p align="center">
  Standard and Catppuccin variants of
  <a href="https://github.com/ful1e5/apple_cursor">Apple Cursors</a>.
</p>

## Themes

The build produces the standard black and white Apple cursor themes, plus
light and dark Catppuccin themes for Latte, Frappe, Macchiato, and Mocha.
All Catppuccin variants use the mauve accent.

Each package includes:

- XCursor binaries for Linux desktops and applications
- Scalable SVG cursors for KDE Plasma 6.2 and newer

The standard themes are packaged as `macOS.tar.xz` and
`macOS-White.tar.xz`. Catppuccin packages use the
`macOS-Catppuccin-<Flavor>[-Dark].tar.xz` naming scheme.

KDE automatically uses `cursors_scalable/` where supported and falls back to
the bundled `cursors/` directory elsewhere.

## Install a release

1. Download a `.tar.xz` archive from the
   [latest release](https://github.com/Syndrizzle/apple-cursor-catppuccin/releases/latest).
2. Extract it into your user icon directory:

   ```bash
   mkdir -p ~/.local/share/icons
   tar -xJf macOS-Catppuccin-Mocha.tar.xz -C ~/.local/share/icons
   ```

3. Select the cursor theme in your desktop environment's appearance settings.

For a system-wide installation, extract the archive into `/usr/share/icons`
instead.

## Build from source

### Prerequisites

- Node.js 16.16 or newer
- Python 3.8 or newer
- npm
- [clickgen](https://github.com/ful1e5/clickgen)
- `tar` with XZ support

### Build

```bash
git clone https://github.com/Syndrizzle/apple-cursor-catppuccin.git
cd apple-cursor-catppuccin

npm install --no-package-lock
python3 -m pip install -r requirements.txt
npm run build
```

The completed theme archives are written to `bin/`. Each unpacked theme in
`themes/` contains both `cursors/` and `cursors_scalable/`. Intermediate PNGs
are written to `bitmaps/`.

To remove generated files:

```bash
npm run clean
```

## Release

GitHub Actions builds the cursor packages for pushes and pull requests. To
publish a release whose notes come from `CHANGELOG.md`, push a version tag:

```bash
git tag v0.2.0
git push origin main v0.2.0
```

## Uninstall

Remove the installed theme directory from `~/.local/share/icons`, `~/.icons`,
or `/usr/share/icons`, depending on where it was installed.

## Acknowledgements

- [ful1e5](https://github.com/ful1e5) for the original Apple Cursors and build tools
- [Catppuccin](https://github.com/catppuccin/catppuccin) for the color palette
- [KDE](https://invent.kde.org/plasma/breeze) for the scalable SVG cursor format

<p align="center">
  <a href="LICENSE">GNU GPL license</a>
</p>
