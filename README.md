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

### Matches Page
![SQL Matches Preview](https://i.gyazo.com/808a02364cb93fd701812f6eca085c6d.png)

### Scoreboard Page
![SQL Matches Preview](https://i.gyazo.com/c719312683f763ba3ecd064df92dae2e.png)
