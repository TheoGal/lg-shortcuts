<p align="center"><img src="docs/tiles.png" alt="LG Shortcuts tiles" width="780"></p>

<h1 align="center">LG Shortcuts</h1>

Seven small tile apps for LG webOS TVs that open LG's own screens: **LG
Settings**, **LG Quick Settings**, **LG Notifications**, **Live TV**, **LG
Account**, **LG Search** and **TV Guide**. They
are meant for custom launchers that don't offer a way to open these LG apps
themselves, but they work in LG Home too. No rooting needed (Developer Mode is
enough).

Each tile is its own package: install any, all or none.

A companion to [Home Helper](https://github.com/TheoGal/lg-homehelper), which
makes the remote's Home button open a launcher of your choice. The tiles work
with or without it.

The apps are vibe-coded and tested on a C3 with webOS 26 (firmware 43.91.26)
and [Hearth](https://github.com/rudra-avatar/Hearth) as a launcher.

## Install

You need a TV with **Developer Mode** on, and the packages you want from the
[latest release](https://github.com/TheoGal/lg-shortcuts/releases/latest):

| Package | Tile | Opens |
| --- | --- | --- |
| `io.github.theogal.lgsettings_<version>_arm.ipk` | **LG Settings** (solid gear) | LG's settings, the same as the gear in LG Home |
| `io.github.theogal.lgquicksettings_<version>_arm.ipk` | **LG Quick Settings** (outlined gear) | LG's Quick Settings panel, the same as a short press of the remote's settings button |
| `io.github.theogal.lgnotifications_<version>_arm.ipk` | **LG Notifications** (bell) | LG's notifications |
| `io.github.theogal.lglivetv_<version>_arm.ipk` | **Live TV** (TV) | The TV tuner (Live TV source) |
| `io.github.theogal.lgaccount_<version>_arm.ipk` | **LG Account** (person) | LG's account screen |
| `io.github.theogal.lgsearch_<version>_arm.ipk` | **LG Search** (magnifier) | LG's search with the on-screen keyboard, the same as the search button in LG Home |
| `io.github.theogal.lgtvguide_<version>_arm.ipk` | **TV Guide** (programme guide) | The TV programme guide |

**With webOS Dev Manager** (easiest): install
[webOS Dev Manager](https://github.com/webosbrew/dev-manager-desktop) on your
computer, add your TV, then open its Apps page and install the .ipk files.

**With the webOS CLI** (`ares-cli`), for example:

```
ares-install --device tv io.github.theogal.lgsettings_<version>_arm.ipk
```

Then add the tiles to your launcher like any other app.

## How they work

A tile has no window of its own: it asks webOS to open the LG app and exits,
so nothing keeps running. The app ids differ between webOS versions:
LG Settings tries `com.palm.app.settings`, then `com.webos.app.settings`.
LG Quick Settings opens `com.webos.app.quicksettings`, LG Notifications opens
`com.webos.app.notificationcenter`, Live TV opens `com.webos.app.livetv` and
LG Account opens `com.webos.app.lgaccount`.

Two tiles also pass launch parameters. LG Search opens `com.webos.app.voice`
with `{"activateType":"mrcu","launchMode":"vkb"}` (search with the on-screen
keyboard), then falls back to `com.webos.app.search`. TV Guide opens
`com.webos.app.livemenu` with `{"activateType":"tvguide"}`: on a C3 that is the
only value that opens the guide tab, as others froze the remote.

The icons are full squares: LG Home and launchers give every tile their own
rounded shape.

## Uninstall

Remove the tiles from LG's app menu: press **Home** to open LG Home, go to the
app list, and switch it to edit mode (highlight a tile and hold **OK**, or use
the pencil/*Edit* option at the end of the list). Select a tile and choose
*Delete*. Apps installed from a downloaded `.ipk` file don't show an uninstall
option in webOS Dev Manager, so use LG's menu.

**From a computer** (with the webOS CLI, `ares`), for example:
`ares-install --device tv --remove io.github.theogal.lgsettings`

## Build

```
pip install -r requirements.txt
python3 scripts/build.py
```

Packages land in `dist/`. Test the launcher with `sh scripts/test.sh` (needs a
C compiler). Redraw the icons with `python3 scripts/make-icons.py` (needs
Pillow and NumPy).

## License

MIT licensed. Not affiliated with LG.
