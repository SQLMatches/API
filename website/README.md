## REST API

## NOTE
Base API structure is the following
```json
{
    "data": {data here},
    "error": {error here}
}
```
All status 200 responses are inside of data.

## Index
- [Get Scoreboard](#get-scoreboard)
- [Create Match](#create-match)
- [Update Match](#update-match)
- [Upload Demo](#upload-demo)
- [End Match](#end-match)

### Get Scoreboard
``GET - https://sqlmatches.com/api/match/{match_id}/?api_key={api_key}``

**URL Parameters**

- match_id: str
    UUID of the Match.
- api_key: str
    24 byte API key.

**Response 200**

```json
# Status codes
# 0 - Finished
# 1 - Live

# Demo status codes
# 0 - No demo
# 1 - Processing
# 2 - Ready for Download

# Team sides codes
# 0 - CT
# 1 - T

{
    "match_id": "uuid4",
    "timestamp": "%m/%d/%Y-%H:%M:%S",
    "status": 0,
    "demo_status": 0,
    "map": "de_mirage",
    "team_1_name": "Ward",
    "team_2_name": "Doggy",
    "team_1_score": 7,
    "team_2_score": 0,
    "team_1_side": 0,
    "team_2_side": 1,
    "team_1": [
        {
            "name": "Ward",
            "steam_id": "76561198077228213",
            "team": 0,
            "alive": false,
            "ping": 0,
            "kills": 0,
            "headshots": 0,
            "assists": 0,
            "deaths": 0,
            "kdr": 0.0,
            "hs_percentage": 0,
            "hit_percentage": 0,
            "shots_fired": 0,
            "shots_hit": 0,
            "mvps": 0,
            "score": 0,
            "disconnected": false
        }
    ],
    "team_2": []
}
```

---

### Create Match
``POST - https://sqlmatches.com/api/match/create/?api_key={api_key}``

**URL Parameters**

- api_key: str
    24 byte API key.

**Payload**

```json
{
    "team_1_name": "Ward",
    "team_2_name": "Doggy",
    "team_1_side": 0,
    "team_2_side": 1,
    "team_1_score": 7,
    "team_2_score": 0,
    "map_name": "de_mirage"
}
```

**Response 200**

```json
{
    "match_id": "uuid4"
}
```

---

### Update Match
``POST - https://sqlmatches.com/api/match/{match_id}/?api_key={api_key}``

**URL Parameters**

- match_id: str
    UUID of the Match.
- api_key: str
    24 byte API key.

**Payload**

```json
{
    "team_1_score": 7,
    "team_2_score": 0,
    "players": [
        {
            "name": "Ward",
            "steam_id": "76561198077228213",
            "team": 0,
            "alive": false,
            "ping": 0,
            "kills": 0,
            "headshots": 0,
            "assists": 0,
            "deaths": 0,
            "shots_fired": 0,
            "shots_hit": 0,
            "mvps": 0,
            "score": 0,
            "disconnected": false
        }
    ],
    "team_1_side": 0 # Optional,
    "team_2_side": 1 # Optional,
    "end": false # Optional
}
```

**Response 200**

```json
{
    "match_id": "uuid4"
}
```

---

### Upload Demo
``POST - https://sqlmatches.com/api/match/{match_id}/?api_key={api_key}``

**URL Parameters**

- match_id: str
    UUID of the Match.
- api_key: str
    24 byte API key.

**Payload**

Raw file bytes.

**Response 200**

null

---

### End Match
``DELETE - https://sqlmatches.com/api/match/{match_id}/?api_key={api_key}``

**URL Parameters**

- match_id: str
    UUID of the Match.
- api_key: str
    24 byte API key.

**Payload**

null

**Response 200**

null

---