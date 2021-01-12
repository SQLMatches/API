# Need a larger upload size?
Visit your owner panel on [SQLMatches.com](https://sqlmatches.com) under the community tab to increase the max upload size.

#### ✨ Help show support by starring this repo! Watch it to get notifications when updated. ✨
![sellout](https://tinyurl.com/y6br8dx3)

## Setup
### Hosted version
- Visit [SQLMatches.com](https://sqlmatches.com) & follow the video.
- Follow the setup section on the [Plugin](https://github.com/SQLMatches/Plugins#setup) repo.

### Self-hosing
- Install SQLMatches with ``pip3 install SQLMatches --upgrade``.
- Create a file like [run.py](/run.py).
- Set up [uvicorn](https://www.uvicorn.org/deployment/) with Starlette.
    - I recommend running [Nginx as a reverse proxy](http://www.uvicorn.org/deployment/#running-behind-nginx).
        - [Production Config](/nginx/production.conf)
        - [Development Config](/nginx/development.conf)
    - Use a UDS (UNIX domain socket) for production.
        - e.g. `uvicorn.run(app, uds="/tmp/uvicorn.sock", log_level="warning")`
    - SSL with [Certbot](https://certbot.eff.org/).
    - Build the [Frontend](https://github.com/SQLMatches/Frontend) or run it in development mode.
        - If building, make sure to edit line [16](https://github.com/SQLMatches/API/blob/master/nginx/production.conf#L16) & [48](https://github.com/SQLMatches/API/blob/master/nginx/production.conf#L48) to the location of the built frontend.
- Run [run.py](/website/run.py) using PM2 or screen.

## Thanks to
- [WardPearce](https://github.com/WardPearce) - [backblaze](https://github.com/WardPearce/backblaze) - Contributor - Maintainer
- [encode](https://www.encode.io/) - [databases](https://www.encode.io/databases/) - [uvicorn](http://www.uvicorn.org/) - [starlette](https://www.starlette.io/)
- [Pallets Projects](https://palletsprojects.com/) - [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/)
- [Woile](https://github.com/Woile) - [starlette apispec](https://github.com/Woile/starlette-apispec)
- [Miguel Grinberg](https://github.com/miguelgrinberg) - [socketio](https://github.com/miguelgrinberg/python-socketio)
- [aio-libs](https://github.com/aio-libs) - [aiocache](https://github.com/aio-libs/aiocache) - [aiohttp](https://github.com/aio-libs/aiohttp) - [aiomysql](https://github.com/aio-libs/aiomysql) - [aiojobs](https://github.com/aio-libs/aiojobs)
- [Martin Richard](https://github.com/Martiusweb) - [asynctest](https://github.com/Martiusweb/asynctest/)
- [marshmallow code](https://github.com/marshmallow-code) - [marshmallow](https://github.com/marshmallow-code/marshmallow) - [webargs](https://github.com/marshmallow-code/webargs)
- [Steven Loria](https://github.com/sloria) - [webargs starlette](https://github.com/sloria/webargs-starlette)
- [sqlalchemy](https://www.sqlalchemy.org/)
- [Tin Tvrtković](https://github.com/Tinche) - [aiofiles](https://github.com/Tinche/aiofiles)
- [Omnilib](https://github.com/omnilib) - [aiosqlite](https://github.com/omnilib/aiosqlite)
- [MagicStack](https://github.com/MagicStack) - [asyncpg](https://github.com/MagicStack/asyncpg)
- To all the developers who helped to make these packages!