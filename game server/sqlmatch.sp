#include <sdkhooks>
#include <sdktools>

new Handle:db;

public OnPluginStart()
{
	new String:buffer[1024];

	if( (db = SQL_Connect("sql_matches", true, buffer, sizeof(buffer))) == INVALID_HANDLE) SetFailState(buffer);

	Format(buffer, sizeof(buffer), "CREATE TABLE IF NOT EXISTS sql_matches_scoretotal (");
	Format(buffer, sizeof(buffer), "%s match_id bigint(20) unsigned NOT NULL AUTO_INCREMENT,", buffer);
	Format(buffer, sizeof(buffer), "%s timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,", buffer);
	Format(buffer, sizeof(buffer), "%s team_0 int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s team_1 int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s team_2 int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s team_3 int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s teamname_1 varchar(64) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s teamname_2 varchar(64) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s map varchar(128) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s PRIMARY KEY (match_id),", buffer);
	Format(buffer, sizeof(buffer), "%s UNIQUE KEY match_id (match_id));", buffer);

	if(!SQL_FastQuery(db, buffer))
	{
		SQL_GetError(db, buffer, sizeof(buffer));
		SetFailState(buffer);
	}

	Format(buffer, sizeof(buffer), "CREATE TABLE IF NOT EXISTS sql_matches (");
	Format(buffer, sizeof(buffer), "%s match_id bigint(20) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s name varchar(65) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s steamid64 varchar(64) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s team int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s alive int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s ping int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s account int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s kills int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s assists int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s deaths int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s mvps int(11) NOT NULL,", buffer);
	Format(buffer, sizeof(buffer), "%s score int(11) NOT NULL);", buffer);

	if(!SQL_FastQuery(db, buffer))
	{
		SQL_GetError(db, buffer, sizeof(buffer));
		SetFailState(buffer);
	}
	
	HookEventEx("cs_win_panel_match", cs_win_panel_match);
}

public cs_win_panel_match(Handle:event, const String:eventname[], bool:dontBroadcast)
{
	CreateTimer(0.1, delay, _, TIMER_FLAG_NO_MAPCHANGE);
}

public Action:delay(Handle:timer)
{
	new Transaction:txn = SQL_CreateTransaction();

	decl String:mapname[128];
	GetCurrentMap(mapname, sizeof(mapname));
	
	char teamname1[64];
	char teamname2[64];

	GetConVarString(FindConVar("mp_teamname_1"), teamname1, sizeof(teamname1));
	GetConVarString(FindConVar("mp_teamname_2"), teamname2, sizeof(teamname2));

	new String:buffer[512];

	Format(buffer, sizeof(buffer), "INSERT INTO sql_matches_scoretotal (team_0, team_1, team_2, team_3, teamname_1, teamname_2, map) VALUES (0, 0, 0, 0, '%s', '%s', '%s');", teamname1, teamname2, mapname);
	SQL_AddQuery(txn, buffer);

	new ent = MaxClients+1;
	
	while( (ent = FindEntityByClassname(ent, "cs_team_manager")) != -1 )
	{
		Format(buffer, sizeof(buffer), "UPDATE sql_matches_scoretotal SET team_%i = %i WHERE match_id = LAST_INSERT_ID();", GetEntProp(ent, Prop_Send, "m_iTeamNum"), GetEntProp(ent, Prop_Send, "m_scoreTotal"));
		SQL_AddQuery(txn, buffer);
	}

	new String:name[MAX_NAME_LENGTH];
	new String:steamid64[64];

	new m_iTeam;
	new m_bAlive;
	new m_iPing;
	new m_iAccount;
	new m_iKills;
	new m_iAssists;
	new m_iDeaths;
	new m_iMVPs;
	new m_iScore;

	if( (ent = FindEntityByClassname(-1, "cs_player_manager")) != -1 )
	{
		for(new i = 1; i <= MaxClients; i++)
		{
			if(!IsClientInGame(i)) continue;

			m_iTeam = GetEntProp(ent, Prop_Send, "m_iTeam", _, i);
			m_bAlive = GetEntProp(ent, Prop_Send, "m_bAlive", _, i);
			m_iPing = GetEntProp(ent, Prop_Send, "m_iPing", _, i);
			m_iAccount = GetEntProp(i, Prop_Send, "m_iAccount");
			m_iKills = GetEntProp(ent, Prop_Send, "m_iKills", _, i);
			m_iAssists = GetEntProp(ent, Prop_Send, "m_iAssists", _, i);
			m_iDeaths = GetEntProp(ent, Prop_Send, "m_iDeaths", _, i);
			m_iMVPs = GetEntProp(ent, Prop_Send, "m_iMVPs", _, i);
			m_iScore = GetEntProp(ent, Prop_Send, "m_iScore", _, i);

			Format(name, MAX_NAME_LENGTH, "%N", i);
			SQL_EscapeString(db, name, name, sizeof(name));

			if(!GetClientAuthId(i, AuthId_SteamID64, steamid64, sizeof(steamid64)))
			{
				steamid64[0] = '\0';
			}

			Format(buffer, sizeof(buffer), "INSERT INTO sql_matches");
			Format(buffer, sizeof(buffer), "%s (match_id, team, alive, ping, name, account, kills, assists, deaths, mvps, score, steamid64)", buffer);
			Format(buffer, sizeof(buffer), "%s VALUES (LAST_INSERT_ID(), '%i', '%i', '%i', '%s', '%i', '%i', '%i', '%i', '%i', '%i', '%s');", buffer, m_iTeam, m_bAlive, m_iPing, name, m_iAccount, m_iKills, m_iAssists, m_iDeaths, m_iMVPs, m_iScore, steamid64);
			SQL_AddQuery(txn, buffer);
		}
	}

	SQL_ExecuteTransaction(db, txn);

}

public onSuccess(Database database, any data, int numQueries, Handle[] results, any[] bufferData)
{
	PrintToServer("onSuccess");
}

public onError(Database database, any data, int numQueries, const char[] error, int failIndex, any[] queryData)
{
	PrintToServer("onError");
}
