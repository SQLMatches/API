<?php
$site_name = "SQL Matches"; // Name of Site

$api_key = ""; // Steam API Key

$servername = ""; // Server IP
$username = ""; // DB Username
$password = ""; // DB Password
$dbname = ""; // DB Name

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>