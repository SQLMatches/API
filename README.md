![DNH Logo](https://camo.githubusercontent.com/742c455547018630cf337754b6e93a16e880dbd2/68747470733a2f2f63646e2e646973636f72646170702e636f6d2f6174746163686d656e74732f3433353630313839363836323930383433372f3533383532363832363139323936313533362f6e626664666864666864686468642e706e67)

# Big improvements coming to the web panel.

# Setup

### Game Server
- Move sqlmatch.smx into addons/sourcemod/plugins
- Edit addons/sourcemod/configs/databases.cfg
```
"sql_matches"
 {
    "driver"            "mysql"
    "host"                "ip"
    "database"            "db"
    "user"                "user"
    "pass"                "pass"
    //"timeout"            "0"
    "port"            "3306"
}
```
### Web Server
- Upload files inside of the web server folder into your web server.
- Enter your steam api key & database details into config.php

# Preview
[Live Demo](https://districtnine.host/dev/demos/sql-matches/)
### Matches Page
![SQL Matches Preview](https://i.gyazo.com/808a02364cb93fd701812f6eca085c6d.png)

### Scoreboard Page
![SQL Matches Preview](https://i.gyazo.com/c93fbcfe488347b5925d091ac86825a4.png)
