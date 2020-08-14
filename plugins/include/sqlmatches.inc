#if defined _sqlmatches_included
 #endinput
#endif
#define _sqlmatches_included

#include <ripext>

typedef OnMatchCreatedFunc = function void (bool bSuccessful, HTTPStatus status, const char[] error, const char[] matchID);
typedef OnMatchEndedFunc = function void (bool bSuccessful, HTTPStatus status, const char[] error);
typedef OnMatchUpdatedFunc = function void (bool bSuccessful, HTTPStatus status, const char[] error);
typedef OnDemoUploadedFunc = function void (bool bSuccessful, HTTPStatus status, const char[] error);

/**
 * Creates a match with the JSON data passed in createData and returns the matchId in the target function
 *
 * @param apiKey 		String containing API Key
 * @param apiUrl 		String containing API Url
 * @param createData 	JSONObject containing the data to use for updating
 * @param func 			OnMatchCreatedFunc function
 * @noreturn 		
 * @error 				Invalid API Key, API Url or OnMatchCreatedFunc function
 */
native any SQLMatches_CreateMatch(const char[] apiKey, const char[] apiUrl, JSONObject createData, OnMatchCreatedFunc func);

/**
 * Ends the current match and calls the target function
 *
 * @param apiKey 		String containing API Key
 * @param apiUrl 		String containing API Url
 * @param matchID 		String containing MatchID
 * @param func 			OnMatchEndedFunc function
 * @noreturn
 * @error 				Invalid API Key, API Url, MatchID or OnMatchEndedFunc function
 */
native any SQLMatches_EndMatch(const char[] apiKey, const char[] apiUrl, const char[] matchID, OnMatchEndedFunc func);

/**
 * Updates the current match and calls the target function
 *
 * @param apiKey 		String containing API Key
 * @param apiUrl 		String containing API Url
 * @param matchID 		String containing MatchID
 * @param updateData 	JSONObject containing the data to use for updating
 * @param func 			OnMatchUpdatedFunc function
 * @noreturn
 * @error 				Invalid API Key, API Url, MatchID, JSON data or OnMatchUpdatedFunc function
 */
native any SQLMatches_UpdateMatch(const char[] apiKey, const char[] apiUrl, const char[] matchID, JSONObject updateData, OnMatchUpdatedFunc func);

/**
 * Uploads a demo and calls the target function
 *
 * @param apiKey 		String containing API Key
 * @param apiUrl 		String containing API Url
 * @param matchID 		String containing MatchID
 * @param demoName 		Filename of demo file to upload (including .dem extension)
 * @param func 			OnDemoUploadedFunc function
 * @noreturn
 * @error 				Invalid API Key, API Url, MatchID, Demo filename or OnDemoUploadedFunc function
 */
native any SQLMatches_UploadDemo(const char[] apiKey, const char[] apiUrl, const char[] matchID, char[] demoName, OnDemoUploadedFunc func);

public SharedPlugin __pl_sqlmatches =
{
	name = "sqlmatches_apistats",
	file = "sqlmatches_apistats.smx",
#if defined REQUIRE_PLUGIN
	required = 1,
#else
	required = 0,
#endif
};

#if !defined REQUIRE_PLUGIN
public void __pl_sqlmatches_apistats_SetNTVOptional()
{
	MarkNativeAsOptional("SQLMatches_CreateMatch");
	MarkNativeAsOptional("SQLMatches_EndMatch");
	MarkNativeAsOptional("SQLMatches_UpdateMatch");
	MarkNativeAsOptional("SQLMatches_UploadDemo");
}
#endif