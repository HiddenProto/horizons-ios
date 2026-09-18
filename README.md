# HORIZONS for iPad

The HORIZONS text survival game, played by touch. You are the chip, and every order you can give right now is a button.

## Install (Sideloadly)

1. Download `Horizons.ipa` from the **latest** release.
2. Open Sideloadly, plug in the iPad, drop the IPA in, sign in with your Apple ID, Start.
3. On the iPad: Settings → General → VPN & Device Management → trust your Apple ID.

A free Apple ID signature lasts 7 days; re-sideload to refresh it. Saves are kept.

## How it is built

- `game/` is a copy of the desktop game (Python). It runs unchanged inside Pyodide.
- `web/` is the touch interface, and `web/bridge.py` turns the live state into buttons.
- `ios/main.m` is a single WebView shell. It stores saves in the app's Documents folder, which the Files app can see.
- Every push to `main` builds an unsigned IPA on a macOS runner. See `.github/workflows/build.yml`.

To refresh the game from the desktop copy, run `python tools/sync_game.py`, then commit.
