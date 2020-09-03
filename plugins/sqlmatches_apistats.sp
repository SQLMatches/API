#include <sqlmatches>

public Plugin myinfo =
{
	name = "SQLMatches API Stats",
	author = "The Doggy",
	description = "Allows developers to use the SQLMatches API in their own plugins",
	version = "1.0.0",
	url = "https://sqlmatches.com/"
};

PrivateForward g_hMatchCreatedFwd;
PrivateForward g_hMatchUpdatedFwd;
PrivateForward g_hMatchEndedFwd;
PrivateForward g_hDemoUploadedFwd;

public APLRes ASkPluginLoad2(Handle myself, bool late, char[] error, int err_max)
{
	RegPluginLibrary("sqlmatches_apistats");

	CreateNative("SQLMatches_CreateMatch", Native_CreateMatch);
	CreateNative("SQLMatches_UpdateMatch", Native_UpdateMatch);
	CreateNative("SQLMatches_EndMatch", Native_EndMatch);
	CreateNative("SQLMatches_UploadDemo", Native_UploadDemo);

	return APLRes_Success;
}

public void OnPluginStart()
{
	// Register Forwards
	g_hMatchCreatedFwd = new PrivateForward(ET_Ignore, Param_String, Param_String);
	g_hMatchUpdatedFwd = new PrivateForward(ET_Ignore, Param_String);
	g_hMatchEndedFwd = new PrivateForward(ET_Ignore, Param_String);
	g_hDemoUploadedFwd = new PrivateForward(ET_Ignore, Param_String);
}

public any Native_CreateMatch(Handle plugin, int numParams)
{
	// Setup API data
	int len;
	GetNativeStringLength(1, len);

	char[] apiKey = new char[len];
	GetNativeString(1, apiKey, len);

	GetNativeStringLength(2, len);

	char[] apiUrl = new char[len];
	GetNativeString(2, apiUrl, len);

	if(strlen(apiUrl) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to create match. Error: apiUrl cannot be empty.");
		return;
	}

	if(strlen(apiKey) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to create match. Error: apiKey cannot be empty.");
		return;
	}

	// Get JSON data
	JSONObject json = GetNativeCell(3);

	// Add function to private forward
	g_hMatchCreatedFwd.AddFunction(plugin, GetNativeFunction(4));

	// Create DataPack to store function info
	DataPack pack = new DataPack();
	pack.WriteCell(plugin);
	pack.WriteFunction(GetNativeFunction(4));
	pack.Reset();

	// Format request
	char sUrl[1024];
	Format(sUrl, sizeof(sUrl), "match/create/?api_key=%s", apiKey);

	// Send request
	HTTPClient client = new HTTPClient(apiUrl);
	client.Post(sUrl, json, HTTP_OnCreateMatch, pack);

	delete client;
	delete json;
	delete pack;
}

void HTTP_OnCreateMatch(HTTPResponse response, DataPack pack, const char[] error)
{
	HTTPStatus status = response.Status;

	if(strlen(error) > 0)
	{
		Call_StartForward(g_hMatchCreatedFwd);
		Call_PushCell(false);
		Call_PushCell(status);
		Call_PushString(error);
		Call_PushNullString();
		Call_Finish();

		g_hMatchCreatedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction());
		delete pack;
		return;
	}

	// Get response data
	JSONObject responseData = view_as<JSONObject>(response.Data);

	// Log errors if any occurred
	if(!responseData.IsNull("error"))
	{
		// Error string
		char errorInfo[1024];

		// Format errors into a single readable string
		FormatAPIError(responseData, errorInfo, sizeof(errorInfo));

		Call_StartForward(g_hMatchCreatedFwd);
		Call_PushCell(false);
		Call_PushCell(status);
		Call_PushString(errorInfo);
		Call_PushNullString();
		Call_Finish();

		// Remove function from the forward
		g_hMatchCreatedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction())

		delete pack;
		return;
	}

	// Match waas created successfully, get matchID
	JSONObject data = view_as<JSONObject>(responseData.Get("data"));
	char matchID[64];
	data.GetString("match_id", matchID, sizeof(matchID));

	// Delete json handle
	delete data;

	// Call forward
	Call_StartForward(g_hMatchCreatedFwd);
	Call_PushCell(true);
	Call_PushCell(status);
	Call_PushNullString();
	Call_PushString(matchID);
	Call_Finish();

	// Remove function from the forward
	g_hMatchCreatedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction())

	delete pack;
}

public any Native_EndMatch(Handle plugin, int numParams)
{
	int len;
	GetNativeStringLength(1, len);

	char[] apiKey = new char[len];
	GetNativeString(1, apiKey, len);

	GetNativeStringLength(2, len);

	char[] apiUrl = new char[len];
	GetNativeString(2, apiUrl, len);

	GetNativeStringLength(3, len);

	char[] matchID = new char[len];
	GetNativeString(3, matchID, len);

	if(strlen(apiUrl) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to end match. Error: apiUrl cannot be empty.");
		return;
	}

	if(strlen(apiKey) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to end match. Error: apiKey cannot be empty.");
		return;
	}

	if(strlen(matchID) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to end match. Error: matchID cannot be empty.");
		return;
	}

	// Add function to private forward
	g_hMatchEndedFwd.AddFunction(plugin, GetNativeFunction(4));

	// Create DataPack to store function info
	DataPack pack = new DataPack();
	pack.WriteCell(plugin);
	pack.WriteFunction(GetNativeFunction(4));
	pack.Reset();

	// Format request
	char sUrl[1024];
	Format(sUrl, sizeof(sUrl), "match/%s?api_key=%s", matchID, apiKey);

	// Send request
	HTTPClient client = new HTTPClient(apiUrl);
	client.Delete(sUrl, HTTP_OnEndMatch, pack);
	delete client;
	delete pack;
}

void HTTP_OnEndMatch(HTTPResponse response, DataPack pack, const char[] error)
{
	HTTPStatus status = response.Status;

	if(strlen(error) > 0)
	{
		// Call Forward
		Call_StartForward(g_hMatchEndedFwd);
		Call_PushCell(false);
		Call_PushCell(status);
		Call_PushString(error);
		Call_Finish();

		g_hMatchEndedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction());
		delete pack;
		return;
	}

	// Get response data
	JSONObject responseData = view_as<JSONObject>(response.Data);

	// Log errors if any occurred
	if(!responseData.IsNull("error"))
	{
		// Error string
		char errorInfo[1024];

		// Format errors into a single readable string
		FormatAPIError(responseData, errorInfo, sizeof(errorInfo));

		// Call forward
		Call_StartForward(g_hMatchEndedFwd);
		Call_PushCell(false);
		Call_PushCell(status);
		Call_PushString(errorInfo);
		Call_Finish();

		g_hMatchEndedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction());
		delete pack;
		return;
	}

	// Call forward
	Call_StartForward(g_hMatchEndedFwd);
	Call_PushCell(true);
	Call_PushCell(status);
	Call_PushNullString();
	Call_Finish();

	g_hMatchEndedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction());
	delete pack;
}

public any Native_UpdateMatch(Handle plugin, int numParams)
{
	int len;
	GetNativeStringLength(1, len);

	char[] apiKey = new char[len];
	GetNativeString(1, apiKey, len);

	GetNativeStringLength(2, len);

	char[] apiUrl = new char[len];
	GetNativeString(2, apiUrl, len);

	GetNativeStringLength(3, len);

	char[] matchID = new char[len];
	GetNativeString(3, matchID, len);

	if(strlen(apiUrl) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to update match. Error: apiUrl cannot be empty.");
		return;
	}

	if(strlen(apiKey) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to update match. Error: apiKey cannot be empty.");
		return;
	}

	if(strlen(matchID) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to update match. Error: matchID cannot be empty.");
		return;
	}

	// Get JSON data
	JSONObject json = GetNativeCell(4);

	// Add function to private forward
	g_hMatchUpdatedFwd.AddFunction(plugin, GetNativeFunction(5));

	// Create DataPack to store function info
	DataPack pack = new DataPack();
	pack.WriteCell(plugin);
	pack.WriteFunction(GetNativeFunction(5));
	pack.Reset();

	// Format request
	char sUrl[1024];
	Format(sUrl, sizeof(sUrl), "match/%s?api_key=%s", matchID, apiKey);

	// Send request
	HTTPClient client = new HTTPClient(apiUrl);
	client.Post(sUrl, json, HTTP_OnUpdateMatch, pack);
	delete client;
	delete pack;
	delete json;
}

void HTTP_OnUpdateMatch(HTTPResponse response, DataPack pack, const char[] error)
{
	HTTPStatus status = response.Status;

	if(strlen(error) > 0)
	{
		// Call Forward
		Call_StartForward(g_hMatchUpdatedFwd);
		Call_PushCell(false);
		Call_PushCell(status);
		Call_PushString(error);
		Call_Finish();

		g_hMatchUpdatedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction());
		delete pack;
		return;
	}

	// Get response data
	JSONObject responseData = view_as<JSONObject>(response.Data);

	// Log errors if any occurred
	if(!responseData.IsNull("error"))
	{
		// Error string
		char errorInfo[1024];

		// Format errors into a single readable string
		FormatAPIError(responseData, errorInfo, sizeof(errorInfo));

		// Call forward
		Call_StartForward(g_hMatchUpdatedFwd);
		Call_PushCell(false);
		Call_PushCell(status);
		Call_PushString(errorInfo);
		Call_Finish();

		g_hMatchUpdatedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction());
		delete pack;
		return;
	}

	// Call forward
	Call_StartForward(g_hMatchUpdatedFwd);
	Call_PushCell(true);
	Call_PushCell(status);
	Call_PushNullString();
	Call_Finish();

	g_hMatchUpdatedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction());
	delete pack;
}

public any Native_UploadDemo(Handle plugin, int numParams)
{
	int len;
	GetNativeStringLength(1, len);

	char[] apiKey = new char[len];
	GetNativeString(1, apiKey, len);

	GetNativeStringLength(2, len);

	char[] apiUrl = new char[len];
	GetNativeString(2, apiUrl, len);

	GetNativeStringLength(3, len);

	char[] matchID = new char[len];
	GetNativeString(3, matchID, len);

	GetNativeStringLength(4, len);
	char[] demoName = new char[len];
	GetNativeString(4, demoName, len);

	if(strlen(apiUrl) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to end match. Error: apiUrl cannot be empty.");
		return;
	}

	if(strlen(apiKey) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to end match. Error: apiKey cannot be empty.");
		return;
	}

	if(strlen(matchID) == 0)
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to end match. Error: matchID cannot be empty.");
		return;
	}

	if(!FileExists(demoName))
	{
		ThrowNativeError(SP_ERROR_NATIVE, "Failed to upload demo. Error: File \"%s\" does not exist.", demoName);
		return;
	}

	// Add function to private forward
	g_hDemoUploadedFwd.AddFunction(plugin, GetNativeFunction(5));

	// Create DataPack to store function info
	DataPack pack = new DataPack();
	pack.WriteCell(plugin);
	pack.WriteFunction(GetNativeFunction(5));
	pack.Reset();

	// Format request
	char sUrl[1024];
	Format(sUrl, sizeof(sUrl), "match/%s/upload?api_key=%s", matchID, apiKey);

	// Send request
	HTTPClient client = new HTTPClient(apiUrl);
	client.UploadFile(sUrl, demoName, HTTP_OnUploadDemo, pack);
	delete client;
	delete pack;
}

void HTTP_OnUploadDemo(HTTPStatus status, DataPack pack, const char[] error)
{
	if(strlen(error) > 0)
	{
		Call_StartForward(g_hDemoUploadedFwd);
		Call_PushCell(false);
		Call_PushCell(status);
		Call_PushString(error);
		Call_Finish();

		g_hDemoUploadedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction());
		delete pack;
		return;
	}

	Call_StartForward(g_hDemoUploadedFwd);
	Call_PushCell(true);
	Call_PushCell(status);
	Call_PushNullString();
	Call_Finish();

	g_hDemoUploadedFwd.RemoveFunction(pack.ReadCell(), pack.ReadFunction());
	delete pack;
}

stock FormatAPIError(JSONObject responseData, char[] buffer, int size)
{
	JSONObject errorData = view_as<JSONObject>(responseData.Get("error")); // Object that contains the errors
	char key[32]; // The key that the error message references
	char value[128]; // The error message

	// Iterate over json object/array to get all the errors that occurred
	JSONObjectKeys keys = errorData.Keys();
	while(keys.ReadKey(key, sizeof(key)))
	{
		JSONArray currentError = view_as<JSONArray>(errorData.Get(key));
		for(int i = 0; i < currentError.Length; i++)
		{
			currentError.GetString(i, value, sizeof(value));
			Format(buffer, size, "%s %s: %s", buffer, key, value);
		}
		delete currentError;
	}

	delete keys;
	delete errorData;
}
