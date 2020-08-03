## SQLMatches 0.0.3
SQLMatches is a completely free & open source CS:GO match statistics & demo recording tool.

[Consider donating to help support hosting this project!](https://www.patreon.com/wardweeb)

## Setup
### Self-hosted
- Install SQLMatches with ``pip3 install SQLMatches``.
- Create a file like [run.py](/website/run.py).
- Set up [uvicorn](https://www.uvicorn.org/deployment/) with Starlette.
    - I recommend running Nginx as a reverse proxy.
    - Also setting up a SSL with [Certbot](https://certbot.eff.org/).
- Run [run.py](/website/run.py) using PM2 or screen.
- Now install the plugin & setting the ``sm_sqlmatches_url`` CVAR to your site with '/api/' appended to it.
- Then follow the 'Hosted version' guide ignoring the 1st point.

### Hosted version
- Visit [SQLMatches.com](https://sqlmatches.com)
- Login with steam.
    - Please note you can only own one community right now, so when you login if you get redirected this is why. But you can disable your community at anytime & create a new one.
- Enter your community's name & click create.
- Install the plugin.
- Set ``sm_sqlmatches_key`` CVAR as your API key located on your community page, under 'Owner Panel'.
- Sit back and relax!


[Looking for the super ugly & out of date PHP version? Check it out here](https://github.com/WardPearce/SQLMatches/tree/Legacy-PHP)
