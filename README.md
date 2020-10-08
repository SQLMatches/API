## Not considered production ready!

[![GitHub issues](https://img.shields.io/github/issues/WardPearce/SQLMatches)](https://github.com/WardPearce/SQLMatches/issues)
[![GitHub license](https://img.shields.io/github/license/WardPearce/SQLMatches)](https://github.com/WardPearce/SQLMatches/blob/master/LICENSE)
[![Actions Status](https://github.com/WardPearce/SQLMatches/workflows/Website/badge.svg)](https://github.com/WardPearce/SQLMatches/actions)
[![Actions Status](https://github.com/WardPearce/SQLMatches/workflows/Plugins/badge.svg)](https://github.com/WardPearce/SQLMatches/actions)

## SQLMatches 0.0.11
SQLMatches is a completely free & open source CS:GO match statistics & demo recording tool. If you need any help feel free to ask on our [discord](https://discord.gg/guYFTjt), please don't open a issue unless if its code related.

[Consider donating to help support hosting this project!](https://www.patreon.com/wardweeb)

## Index
- [Website](#Website)
    - [Self-hosted](#self-hosted)
    - [Hosted version](#hosted-version)
    - [API DOCS](/website/README.md)
    - [Adding more map images](#adding-more-map-images)
- [Sourcemod setup](#sourcemod-setup)
- [Supported database engines](#supported-database-engines)
- [Legacy version](#legacy-version)

## Website
### Self-hosted
- Install SQLMatches with ``pip3 install SQLMatches``.
- Create a file like [run.py](/website/run.py).
- Set up [uvicorn](https://www.uvicorn.org/deployment/) with Starlette.
    - I recommend running Nginx as a reverse proxy.
    - Also setting up a SSL with [Certbot](https://certbot.eff.org/).
- Run [run.py](/website/run.py) using PM2 or screen.
- Then follow the '[Hosted version](#hosted-version)' guide ignoring the 1st point.

### Hosted version
- Visit [SQLMatches.com](https://sqlmatches.com)
- Login with steam.
    - Please note you can only own one community right now, so when you login if you get redirected this is why. But you can disable your community at anytime & create a new one.
- Enter your community's name & click create.
- [Install the plugin](#sourcemod-setup).
- Set ``sm_sqlmatches_key`` CVAR as your API key located on your community page, under 'Owner Panel'.
- Enable GOTV ``tv_enable 1``.
- Disable auto record ``tv_autorecord 0``.
- Disable hibernation ``sv_hibernate_when_empty 0``
- Feel free increase the demo tick rate, but the demo can not be larger then 80 mb.
- The demo won't upload if its smaller then 5 mb.
- Sit back and relax!

### Adding more map images
- Fork the repo.
- Add the new images to [here](/website/SQLMatches/frontend/assets/img/maps).
- Add the full map name & file name [here](/website/SQLMatches/__init__.py#L46).
- Open a PR.

## Sourcemod setup
- Install [SourceMod](https://www.sourcemod.net/downloads.php?branch=stable) Version >= 1.10.
- Install [REST in Pawn](https://github.com/ErikMinekus/sm-ripext/releases).
- Install the SQLMatches plugin.
    - [Download](https://github.com/WardPearce/SQLMatches/suites/1184973926/artifacts/17373316)

## Supported database engines
- MySQL (Fully tested)
- Postgresql (Not tested)
- SQLite (Not tested)

## Legacy version
[Looking for the super ugly & out of date PHP version? Check it out here](https://github.com/WardPearce/SQLMatches/tree/Legacy-PHP)
