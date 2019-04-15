![DNH Logo](https://camo.githubusercontent.com/742c455547018630cf337754b6e93a16e880dbd2/68747470733a2f2f63646e2e646973636f72646170702e636f6d2f6174746163686d656e74732f3433353630313839363836323930383433372f3533383532363832363139323936313533362f6e626664666864666864686468642e706e67)

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
- Configure config.php.

# Preview
[Live Demo](https://districtnine.host/dev/demos/sql-matches/)
### Matches Page
![SQL Matches Preview](https://i.imgur.com/p9fSWGv.png)

### Scoreboard Page
![SQL Matches Preview](https://i.imgur.com/LXYXr1j.png)
