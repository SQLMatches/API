### Development status
Re-write in python coming soon.

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
![SQL Matches Preview](https://i.imgur.com/c4Zxyvt.png)

### Scoreboard Page
![SQL Matches Preview](https://i.imgur.com/pAi46az.png)
