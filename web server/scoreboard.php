<?php
require ('config.php');

if(isset($_GET["id"])){
    $id = $_GET["id"];
} else {
    $id = 0;
}

$sql = "SELECT sql_matches.match_id, sql_matches_scoretotal.timestamp, sql_matches_scoretotal.map, sql_matches_scoretotal.team_2, sql_matches_scoretotal.team_3, sql_matches.steamid64, sql_matches.name, sql_matches.kills, sql_matches.deaths, sql_matches.assists, sql_matches.team
        FROM sql_matches_scoretotal INNER JOIN sql_matches
        ON sql_matches_scoretotal.match_id = sql_matches.match_id
        WHERE sql_matches_scoretotal.match_id = '".$id."' ORDER BY sql_matches.kills DESC";

$result_stats1 = $conn->query($sql);
$result_stats2 = $conn->query($sql);
$result = $conn->query($sql);
?>
<!DOCTYPE html>
<html>

<?php
include ('head.php');
?>

<body>
    <a href="index.php" style="color:#000000;"><h1 class="text-center" style="margin-top:15px;"><?php echo $site_name; ?></h1></a>
    <?php 
    if($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        echo '<div class="card pulse animated" style="width:1180px;margin-right:auto;margin-left:auto;background-color:#f1f1f1;margin-top:25px;">
        <div class="card-body"><img class="float-left" src="assets/img/ct_icon.png" style="width:125px;margin-left:172px;">
            <h1 class="float-left text-center" style="font-size:50px;margin-bottom:0px;margin-top:25px;width:540px;"><strong style="color:rgb(91,118,141);">'.$row["team_2"].'</strong>:<strong style="color:rgb(172,155,102);">'.$row["team_3"].'</strong></h1>
            <img class="float-right" src="assets/img/t_icon.png" style="width:125px;margin-bottom:5px;margin-right:172px;">
            <div class="clear"></div>
            <div style="margin-top:20px;height:69px;">
                <h1 class="text-center" style="font-size:20px;">Map: '.$row["map"].'</h1>
                <h1 class="text-center" style="font-size:20px;">Ended: '.$row["timestamp"].'</h1>
            </div>
            <div class="float-left" style="margin-top:20px;width:500px;">
                <p class="float-right" style="margin-bottom:0px;width:64px;">Assists</p>
                <p class="float-right" style="margin-bottom:0px;width:60px;">Deaths</p>
                <p class="float-right" style="margin-bottom:0px;width:47px;">Kills</p>
                <p class="float-right" style="margin-bottom:0px;width:60px;">KDR</p>
                <p class="float-right" style="margin-bottom:0px;width:200px;">Player</p>
            </div>
            <div class="float-right" style="margin-top:20px;width:500px;">
                <p class="float-right" style="margin-bottom:0px;width:64px;">Assists</p>
                <p class="float-right" style="margin-bottom:0px;width:60px;">Deaths</p>
                <p class="float-right" style="margin-bottom:0px;width:47px;">Kills</p>
                <p class="float-right" style="margin-bottom:0px;width:60px;">KDR</p>
                <p class="float-right" style="margin-bottom:0px;width:200px;">Player</p>
            </div>
            <div class="clear"></div>
            <div class="float-left" style="margin-top:0px;">
                <ul class="list-group float-left" style="width:500px;">';

                while($row = $result_stats1->fetch_assoc()) {
                    if($row['team'] == '2') { 
                        $api_url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=$api_key&steamids=".$row['steamid64']."";
                        $json = json_decode(file_get_contents($api_url), true);
    
                        if($row["kills"] && $row["deaths"] > 0){
                            $kdr = ($row["kills"]/$row["deaths"]); 
                            $kdr_roundup = round($kdr,2);
    
                        } else {
                            $kdr_roundup = $row["kills"];

                        }
                        echo '<li class="list-group-item" style="margin-top:10px;text-align:center;"><span class="float-right" style="margin-top:10px;width:39px;">'.$row["assists"].'</span><span class="float-right" style="margin-top:10px;width:39px;margin-right:20px;">'.$row["deaths"].'</span><span class="float-right" style="margin-top:10px;width:39px;margin-right:20px;">'.$row["kills"].'</span><span class="float-right" style="margin-top:10px;width:35px;margin-right:20px;">'.$kdr_roundup.'</span><a style="white-text" href="https://steamcommunity.com/profiles/'.$row["steamid64"].'" target="_blank"><img class="rounded-circle float-left" src="'.$json["response"]["players"][0]["avatarmedium"].'" style="width:45px;"><span class="float-left" style="margin-top:10px;margin-left:5px;color:#000000;">'.substr($row['name'],0,6).'</span></a></li>';
                    }
                }
                
                echo '</ul><ul class="list-group float-left" style="width:500px;margin-left:138px;">';

                while($row = $result_stats2->fetch_assoc()){
                    if($row['team'] == '3'){
                        $api_url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=$api_key&steamids=".$row['steamid64']."";
                        $json = json_decode(file_get_contents($api_url), true);
    
                        if($row["kills"] && $row["deaths"] > 0){
                            $kdr = ($row["kills"]/$row["deaths"]); 
                            $kdr_roundup = round($kdr,2);
    
                        } else {
                            $kdr_roundup = $row["kills"];
                        }
                        
                        echo '<li class="list-group-item" style="margin-top:10px;text-align:center;"><span class="float-right" style="margin-top:10px;width:39px;">'.$row["assists"].'</span><span class="float-right" style="margin-top:10px;width:39px;margin-right:20px;">'.$row["deaths"].'</span><span class="float-right" style="margin-top:10px;width:39px;margin-right:20px;">'.$row["kills"].'</span><span class="float-right" style="margin-top:10px;width:35px;margin-right:20px;">'.$kdr_roundup.'</span><a style="white-text" href="https://steamcommunity.com/profiles/'.$row["steamid64"].'" target="_blank"><img class="rounded-circle float-left" src="'.$json["response"]["players"][0]["avatarmedium"].'" style="width:45px;"><span class="float-left" style="margin-top:10px;margin-left:5px;color:#000000;">'.substr($row['name'],0,6).'</span></a></li>';
                    }
                }
                
                echo '</ul></div><div class="clear"></div></div></div>';
                
    } else {
        echo '<h4 style="margin-top:40px;text-align:center;">No Match with that ID!</h4>';
    }
    $conn->close();
    ?>
    <div class="bottom"><a href="https://github.com/WardPearce/Sourcemod-SQLMatches" target="_blank">Created By Ward</a></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.2/js/bootstrap.bundle.min.js"></script>
    <script src="assets/js/bs-animation.js"></script>
</body>

</html>
