# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

import argparse

cli = argparse.ArgumentParser()

cli.add_argument("--db_username", type=str, default="")
cli.add_argument("--db_password", type=str, default="")
cli.add_argument("--db_server", type=str, default="")
cli.add_argument("--db_port", type=int, default=3306)
cli.add_argument("--db_database", type=str, default="")

cli.add_argument("--root_steam_id", type=str, default="")

cli.add_argument("--frontend_url", type=str, default="https://localhost")
cli.add_argument("--backend_url", type=str, default="https://localhost/api")

args = vars(cli.parse_args())

DATABASE = {
    "username": args["db_username"],
    "password": args["db_password"],
    "server": args["db_server"],
    "port": args["db_port"],
    "database": args["db_database"]
}

ROOT = {
    "root_steam_id": args["root_steam_id"],
    "frontend_url": args["frontend_url"],
    "backend_url": args["backend_url"]
}
