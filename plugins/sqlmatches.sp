#include <sourcemod>
#include <sdktools>
#include <cstrike>
#include <ripext>

#pragma semicolon 1
#pragma newdecls required

#define PREFIX		"[SQLMatches.com]"
#define TEAM_CT 	0
#define TEAM_T 		1

bool g_bPugSetupAvailable;
bool g_bGet5Available;
bool g_bAlreadySwapped;

char g_sApiUrl[512];
char g_sApiKey[64];
char g_sMatchId[128];

ConVar g_cvApiUrl;
ConVar g_cvApiKey;

HTTPClient g_Client;

enum struct MatchUpdatePlayer
{
	int Index;
	char Username[42];
	char SteamID[64];
	int Team;
	bool Alive;
	int Ping;
	int Kills;
	int Headshots;
	int Assists;
	int Deaths;
	int ShotsFired;
	int ShotsHit;
	int MVPs;
	int Score;
	bool Disconnected;
}

MatchUpdatePlayer g_PlayerStats[MAXPLAYERS + 1];

public Plugin myinfo =
{
	name = "SQLMatches",
	author = "The Doggy, ErikMinekus, WardPearce",
	description = "Match stats and demo recording system for CS:GO",
	version = "1.0.3",
	url = "https://sqlmatches.com/"
};

public void OnAllPluginsLoaded()
{
	g_bPugSetupAvailable = LibraryExists("pugsetup");
	g_bGet5Available = LibraryExists("get5");
}

public void OnLibraryAdded(const char[] name)
{
	if(StrEqual(name, "pugsetup")) g_bPugSetupAvailable = true;
	if(StrEqual(name, "get5")) g_bGet5Available = true;
}

public void OnLibraryRemoved(const char[] name)
{
	if(StrEqual(name, "pugsetup")) g_bPugSetupAvailable = false;
	if(StrEqual(name, "get5")) g_bGet5Available = false;
}

public void OnPluginStart()
{
	//Hook Events
	HookEvent("round_start", Event_RoundStart);
	HookEvent("round_end", Event_RoundEnd);
	HookEvent("weapon_fire", Event_WeaponFired);
	HookEvent("player_hurt", Event_PlayerHurt);
	HookEvent("announce_phase_end", Event_HalfTime);
	HookEvent("player_disconnect", Event_PlayerDisconnect, EventHookMode_Pre);
	HookEvent("cs_win_panel_match", Event_MatchEnd);

	// Register ConVars
	g_cvApiKey = CreateConVar("sm_sqlmatches_key", "<API KEY>", "API key for sqlmatches API", FCVAR_PROTECTED);
	g_cvApiKey.AddChangeHook(OnAPIChanged);
	g_cvApiUrl = CreateConVar("sm_sqlmatches_url", "https://sqlmatches.com/api", "URL of sqlmatches base API route", FCVAR_PROTECTED);
	g_cvApiUrl.AddChangeHook(OnAPIChanged);

	g_cvApiKey.GetString(g_sApiKey, sizeof(g_sApiKey));
	g_cvApiUrl.GetString(g_sApiUrl, sizeof(g_sApiUrl));

	AutoExecConfig(true, "sqlmatches");

	// Create HTTP Client
	g_Client = new HTTPClient(g_sApiUrl);
	g_Client.SetHeader("Content-Type:", "application/json");
	g_Client.FollowLocation = true;
	g_Client.ConnectTimeout = 300;
	g_Client.Timeout = 300;

	// Register commands
	RegConsoleCmd("sm_creatematch", Command_CreateMatch, "Creates a match");
	RegConsoleCmd("sm_endmatch", Command_EndMatch, "Ends a match");
}

public void Event_RoundStart(Event event, const char[] name, bool dontBroadcast)
{
	if(InWarmup()) return;

	CreateMatch();
}

public void OnAPIChanged(ConVar convar, const char[] oldValue, const char[] newValue)
{
	g_cvApiUrl.GetString(g_sApiUrl, sizeof(g_sApiUrl));
	g_cvApiKey.GetString(g_sApiKey, sizeof(g_sApiKey));

	// Remove trailing backslash from '/api/'
	int len = strlen(g_sApiUrl);
	if(len > 0 && g_sApiUrl[len - 1] == '/')
		g_sApiUrl[len - 1] = '\0';

	// Log error about /api/
	if(len > 0 && StrContains(g_sApiUrl[len - 4], "/api") == -1)
		LogMessage("The API route normally ends with '/api'");

	// Recreate HTTP client with new url
	delete g_Client;
	g_Client = new HTTPClient(g_sApiUrl);
	g_Client.SetHeader("Content-Type:", "application/json");
	g_Client.FollowLocation = true;
	g_Client.ConnectTimeout = 300;
	g_Client.Timeout = 300;
}

public void OnConfigsExecuted()
{
	g_cvApiKey.GetString(g_sApiKey, sizeof(g_sApiKey));
	g_cvApiUrl.GetString(g_sApiUrl, sizeof(g_sApiUrl));

	// Remove trailing backslash from '/api/'
	int len = strlen(g_sApiUrl);
	if(len > 0 && g_sApiUrl[len - 1] == '/')
		g_sApiUrl[len - 1] = '\0';

	// Log error about /api/
	if(len > 0 && StrContains(g_sApiUrl[len - 4], "/api") == -1)
		LogMessage("The API route normally ends with '/api'");

	// Recreate HTTP Client with new url
	delete g_Client;
	g_Client = new HTTPClient(g_sApiUrl);
	g_Client.SetHeader("Content-Type:", "application/json");
	g_Client.FollowLocation = true;
	g_Client.ConnectTimeout = 300;
	g_Client.Timeout = 300;
}

public void OnClientPutInServer(int Client)
{
	ResetVars(Client);
	g_PlayerStats[Client].Index = Client;
}

void ResetVars(int Client)
{
	g_PlayerStats[Client].Index = 0;
	g_PlayerStats[Client].Username = "";
	g_PlayerStats[Client].SteamID = "";
	g_PlayerStats[Client].Team = 0;
	g_PlayerStats[Client].Alive = false;
	g_PlayerStats[Client].Ping = 0;
	g_PlayerStats[Client].Kills = 0;
	g_PlayerStats[Client].Headshots = 0;
	g_PlayerStats[Client].Assists = 0;
	g_PlayerStats[Client].Deaths = 0;
	g_PlayerStats[Client].ShotsFired = 0;
	g_PlayerStats[Client].ShotsHit = 0;
	g_PlayerStats[Client].MVPs = 0;
	g_PlayerStats[Client].Score = 0;
	g_PlayerStats[Client].Disconnected = false;
}

public Action Command_CreateMatch(int client, int args)
{
	CreateMatch();
}

public Action Command_EndMatch(int client, int args)
{
	EndMatch();
}

void CreateMatch()
{
	if(InMatch()) return;

	if(strlen(g_sApiUrl) == 0)
	{
		LogError("Failed to create match. Error: ConVar sm_sqlmatches_url cannot be empty.");
		return;
	}

	if(strlen(g_sApiKey) == 0)
	{
		LogError("Failed to create match. Error: ConVar sm_sqlmatches_key cannot be empty.");
		return;
	}

	// Format request
	char sUrl[1024];
	Format(sUrl, sizeof(sUrl), "match/create/?api_key=%s", g_sApiKey);

	// Setup JSON data
	char sTeamNameCT[64];
	char sTeamNameT[64];
	char sMap[24];
	JSONObject json = new JSONObject();

	// Set names if pugsetup or get5 are available
	if(g_bGet5Available || g_bPugSetupAvailable)
	{
		FindConVar("mp_teamname_1").GetString(sTeamNameCT, sizeof(sTeamNameCT));
		FindConVar("mp_teamname_2").GetString(sTeamNameT, sizeof(sTeamNameT));
	}
	else // Otherwise just use garbage values
	{
		sTeamNameCT = "1";
		sTeamNameT = "2";
	}

	json.SetString("team_1_name", sTeamNameCT);
	json.SetString("team_2_name", sTeamNameT);

	// Set team sides
	json.SetInt("team_1_side", 0);
	json.SetInt("team_2_side", 1);

	// Set team score
	json.SetInt("team_1_score", 0);
	json.SetInt("team_2_score", 0);

	// Set map
	GetCurrentMap(sMap, sizeof(sMap));
	json.SetString("map_name", sMap);

	// Send request
	g_Client.Post(sUrl, json, HTTP_OnCreateMatch);

	// Delete handle
	delete json;
}

void HTTP_OnCreateMatch(HTTPResponse response, any value, const char[] error)
{
	if(strlen(error) > 0)
	{
		LogError("HTTP_OnCreateMatch - Error string - Failed! Error: %s", error);
		return;
	}

	if (response.Data == null) {
		// Invalid JSON response
		return;
	}

	// Get response data
	JSONObject responseData = view_as<JSONObject>(response.Data);

	// Log errors if any occurred
	if(response.Status != HTTPStatus_OK)
	{
		char errorInfo[1024];
		responseData.GetString("error", errorInfo, sizeof(errorInfo));
		LogError("HTTP_OnCreateMatch - Invalid status code - Failed! Error: %s", errorInfo);
		return;
	}

	// Match waas created successfully, store match id and restart game
	JSONObject data = view_as<JSONObject>(responseData.Get("data"));
	data.GetString("match_id", g_sMatchId, sizeof(g_sMatchId));
	PrintToServer("%s Match %s created successfully.", PREFIX, g_sMatchId);
	PrintToChatAll("%s Match has been created", PREFIX);
	ServerCommand("tv_record \"%s\"", g_sMatchId);
}

void EndMatch()
{
	if(!InMatch()) return;

	if(strlen(g_sApiUrl) == 0)
	{
		LogError("Failed to end match. Error: ConVar sm_sqlmatches_url cannot be empty.");
		return;
	}

	if(strlen(g_sApiKey) == 0)
	{
		LogError("Failed to end match. Error: ConVar sm_sqlmatches_key cannot be empty.");
		return;
	}

	// Format request
	char sUrl[1024];
	Format(sUrl, sizeof(sUrl), "match/%s?api_key=%s", g_sMatchId, g_sApiKey);

	// Send request
	g_Client.Delete(sUrl, HTTP_OnEndMatch);
}

void HTTP_OnEndMatch(HTTPResponse response, any value, const char[] error)
{
	if(strlen(error) > 0)
	{
		LogError("HTTP_OnEndMatch - Error string - Failed! Error: %s", error);
		return;
	}

	// Get response data
	JSONObject responseData = view_as<JSONObject>(response.Data);

	// Log errors if any occurred
	if(response.Status != HTTPStatus_OK)
	{
		// Error string
		char errorInfo[1024];
		responseData.GetString("error", errorInfo, sizeof(errorInfo));
		LogError("HTTP_OnEndMatch - Invalid status code - Failed! Error: %s", errorInfo);
		return;
	}

	// End match
	PrintToServer("%s Match ended successfully.", PREFIX);
	PrintToChatAll("%s Match has ended, stats will no longer be recorded.", PREFIX);
	if(FindConVar("tv_enable").IntValue == 1)
		UploadDemo(g_sMatchId);
	g_sMatchId = "";
}

void UpdateMatch(int team_1_score = -1, int team_2_score = -1, const MatchUpdatePlayer[] players, int size = -1, bool dontUpdate = false, int team_1_side = -1, int team_2_side = -1, bool end = false)
{
	if(!InMatch() && end == false) return;

	if(strlen(g_sApiUrl) == 0)
	{
		LogError("Failed to update match. Error: ConVar sm_sqlmatches_url cannot be empty.");
		return;
	}

	if(strlen(g_sApiKey) == 0)
	{
		LogError("Failed to update match. Error: ConVar sm_sqlmatches_key cannot be empty.");
		return;
	}

	// Set scores if not passed in manually
	if(team_1_score == -1)
		team_1_score = CS_GetTeamScore(CS_TEAM_CT);
	if(team_2_score == -1)
		team_2_score = CS_GetTeamScore(CS_TEAM_T);

	// Create and set json data
	JSONObject json = new JSONObject();
	json.SetInt("team_1_score", team_1_score);
	json.SetInt("team_2_score", team_2_score);

	// Format and set players data
	if(!dontUpdate)
	{
		JSONArray playersArray = GetPlayersJson(players, size);
		json.Set("players", playersArray);
		delete playersArray;
	}

	// Set optional data
	if(team_1_side != -1)
		json.SetInt("team_1_side", team_1_side);
	if(team_2_side != -1)
		json.SetInt("team_2_side", team_2_side);
	if(end)
		json.SetBool("end", end);

	// Format request
	char sUrl[1024];
	Format(sUrl, sizeof(sUrl), "match/%s/?api_key=%s", g_sMatchId, g_sApiKey);

	// Send request
	g_Client.Post(sUrl, json, HTTP_OnUpdateMatch);
	delete json;
}

void HTTP_OnUpdateMatch(HTTPResponse response, any value, const char[] error)
{
	if(strlen(error) > 0)
	{
		LogError("HTTP_OnUpdateMatch - Error string - Failed! Error: %s", error);
		return;
	}

	// Get response data
	JSONObject responseData = view_as<JSONObject>(response.Data);

	// Log errors if any occurred
	if(response.Status != HTTPStatus_OK)
	{
		// Error string
		char errorInfo[1024];
		responseData.GetString("error", errorInfo, sizeof(errorInfo));
		LogError("HTTP_OnUpdateMatch - Invalid status code - Failed! Error: %s", errorInfo);
		return;
	}

	PrintToServer("%s Match updated successfully.", PREFIX);
}

void UploadDemo(const char[] demoName)
{
	if(strlen(g_sApiUrl) == 0)
	{
		LogError("Failed to upload demo. Error: ConVar sm_sqlmatches_url cannot be empty.");
		return;
	}

	if(strlen(g_sApiKey) == 0)
	{
		LogError("Failed to upload demo. Error: ConVar sm_sqlmatches_key cannot be empty.");
		return;
	}

	char formattedDemo[128];
	Format(formattedDemo, sizeof(formattedDemo), "%s.dem", demoName);
	if(!FileExists(formattedDemo))
	{
		LogError("Failed to upload demo. Error: File \"%s\" does not exist.", formattedDemo);
		return;
	}

	if(FileSize(formattedDemo) < 5000024)
	{
		LogError("Demo file must be larger then 5 mb.");
		return;
	}

	// Format request
	char sUrl[1024];
	Format(sUrl, sizeof(sUrl), "match/%s/upload/?api_key=%s", g_sMatchId, g_sApiKey);

	// Send request
	g_Client.UploadFile(sUrl, formattedDemo, HTTP_OnUploadDemo);

	PrintToServer("%s Uploading demo...", PREFIX);
}

void HTTP_OnUploadDemo(HTTPStatus status, DataPack pack, const char[] error)
{
	if(strlen(error) > 0 || status != HTTPStatus_OK)
	{
		LogError("HTTP_OnUploadDemo Failed! Error: %s", error);
		return;
	}

	PrintToServer("%s Demo uploaded successfully.", PREFIX);
}

public void Event_RoundEnd(Event event, const char[] name, bool dontBroadcast)
{
	UpdatePlayerStats(g_PlayerStats, sizeof(g_PlayerStats));
	UpdateMatch(.players = g_PlayerStats, .size = sizeof(g_PlayerStats));
}

public void Event_WeaponFired(Event event, const char[] name, bool dontBroadcast)
{
	int Client = GetClientOfUserId(event.GetInt("userid"));
	if(!InMatch() || !IsValidClient(Client)) return;

	int iWeapon = GetEntPropEnt(Client, Prop_Send, "m_hActiveWeapon");
	if(!IsValidEntity(iWeapon)) return;

	if(GetEntProp(iWeapon, Prop_Send, "m_iPrimaryAmmoType") != -1 && GetEntProp(iWeapon, Prop_Send, "m_iClip1") != 255) g_PlayerStats[Client].ShotsFired++; //should filter knife and grenades
}

public void Event_PlayerHurt(Event event, const char[] name, bool dontBroadcast)
{
	int Client = GetClientOfUserId(event.GetInt("attacker"));
	if(!InMatch() || !IsValidClient(Client)) return;

	if(event.GetInt("hitgroup") >= 0)
	{
		g_PlayerStats[Client].ShotsHit++;
		if(event.GetInt("hitgroup") == 1) g_PlayerStats[Client].Headshots++;
	}
}

/* This has changed  */
public void Event_HalfTime(Event event, const char[] name, bool dontBroadcast)
{
	if(!InMatch()) return;

	if (!g_bAlreadySwapped)
	{
		LogMessage("Event_HalfTime(): Starting team swap...");

		UpdateMatch(.team_1_side = 1, .team_2_side = 0, .players = g_PlayerStats, .dontUpdate = false);

		g_bAlreadySwapped = true;
	}
	else
		LogError("Event_HalfTime(): Teams have already been swapped!");
}

public Action Event_PlayerDisconnect(Event event, const char[] name, bool dontBroadcast)
{
	if(!InMatch()) return Plugin_Continue;

	// If the client isn't valid or isn't currently in a match return
	int Client = GetClientOfUserId(event.GetInt("userid"));
	if(!IsValidClient(Client)) return Plugin_Handled;

	// If the client's steamid isn't valid return
	char sSteamID[64];
	event.GetString("networkid", sSteamID, sizeof(sSteamID));
	if(sSteamID[7] != ':') return Plugin_Handled;
	if(!GetClientAuthId(Client, AuthId_SteamID64, sSteamID, sizeof(sSteamID))) return Plugin_Handled;

	UpdatePlayerStats(g_PlayerStats, sizeof(g_PlayerStats));
	UpdateMatch(.players = g_PlayerStats, .size = sizeof(g_PlayerStats));

	// Reset client vars
	ResetVars(Client);

	return Plugin_Continue;
}

public Action Event_MatchEnd(Event event, const char[] name, bool dontBroadcast)
{
	if(!InMatch()) return;

	UpdateMatch(.players = g_PlayerStats, .size = sizeof(g_PlayerStats), .end = true);
	if(FindConVar("tv_enable").IntValue == 1)
		UploadDemo(g_sMatchId);
	g_sMatchId = "";
}

stock void RestartGame(int delay)
{
	ServerCommand("mp_restartgame %d", delay);
}

stock bool InWarmup()
{
  return GameRules_GetProp("m_bWarmupPeriod") != 0;
}

stock bool InMatch()
{
	return !StrEqual(g_sMatchId, "") && !InWarmup();
}

stock void UpdatePlayerStats(MatchUpdatePlayer[] players, int size)
{
	int ent = FindEntityByClassname(-1, "cs_player_manager");

	// Iterate over players array and update values for every client
	for(int i = 0; i < size; i++)
	{
		int Client = players[i].Index;
		if(!IsValidClient(Client)) continue;

		// dumb teams :(
		if(GetClientTeam(Client) == CS_TEAM_CT)
			players[Client].Team = 0;
		else if(GetClientTeam(Client) == CS_TEAM_T)
			players[Client].Team = 1;

		players[Client].Alive = view_as<bool>(GetEntProp(ent, Prop_Send, "m_bAlive", _, Client));
		players[Client].Ping = GetEntProp(ent, Prop_Send, "m_iPing", _, Client);
		players[Client].Kills = GetEntProp(ent, Prop_Send, "m_iKills", _, Client);
		players[Client].Assists = GetEntProp(ent, Prop_Send, "m_iAssists", _, Client);
		players[Client].Deaths = GetEntProp(ent, Prop_Send, "m_iDeaths", _, Client);
		players[Client].MVPs = GetEntProp(ent, Prop_Send, "m_iMVPs", _, Client);
		players[Client].Score = GetEntProp(ent, Prop_Send, "m_iScore", _, Client);

		GetClientName(Client, players[Client].Username, sizeof(MatchUpdatePlayer::Username));
		GetClientAuthId(Client, AuthId_SteamID64, players[Client].SteamID, sizeof(MatchUpdatePlayer::SteamID));
	}
}

stock JSONArray GetPlayersJson(const MatchUpdatePlayer[] players, int size)
{
	JSONArray json = new JSONArray();

	for(int i = 0; i < size; i++)
	{
		if(!IsValidClient(players[i].Index)) continue;
		JSONObject player = new JSONObject();

		player.SetString("name", players[i].Username);
		player.SetString("steam_id", players[i].SteamID);
		player.SetInt("team", players[i].Team);
		player.SetBool("alive", players[i].Alive);
		player.SetInt("ping", players[i].Ping);
		player.SetInt("kills", players[i].Kills);
		player.SetInt("headshots", players[i].Headshots);
		player.SetInt("assists", players[i].Assists);
		player.SetInt("deaths", players[i].Deaths);
		player.SetInt("shots_fired", players[i].ShotsFired);
		player.SetInt("shots_hit", players[i].ShotsHit);
		player.SetInt("mvps", players[i].MVPs);
		player.SetInt("score", players[i].Score);
		player.SetBool("disconnected", IsClientInGame(players[i].Index));

		json.Push(player);
		delete player;
	}

	return json;
}

stock bool IsValidClient(int client)
{
	if (client >= 1 &&
	client <= MaxClients &&
	IsClientConnected(client) &&
	IsClientInGame(client) &&
	!IsFakeClient(client) &&
	(GetClientTeam(client) == CS_TEAM_CT || GetClientTeam(client) == CS_TEAM_T))
		return true;
	return false;
}
