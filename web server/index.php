<?php
require ('config.php');
?>
<!DOCTYPE html>
<html>

<?php
include ('head.php');
?>

<body>
    <a href="index.php" style="color:#000000;"><h1 class="text-center" style="margin-top:15px;"><?php echo $site_name; ?></h1></a>
    <form method="post">
    <div class="search-container" style="width:600px;margin-left:auto;margin-right:auto;"><input type="text" name="search-bar" placeholder="Search MatchID, Player Name or SteamID64" class="search-input"><button class="btn btn-light search-btn" style="color:#f1f1f1;" type="submit" name="Submit"> <i class="fa fa-search" style="color:rgb(0,0,0);"></i></button></div>
    </form>
    <div style="width:700px;margin-left:auto;margin-right:auto;margin-bottom:25px;">
    <?php
    if(isset($_POST['Submit'])) {
        $search = $_POST["search-bar"];

        $sql = "SELECT DISTINCT sql_matches_scoretotal.match_id, sql_matches_scoretotal.map, sql_matches_scoretotal.team_2, sql_matches_scoretotal.team_3
                FROM sql_matches_scoretotal INNER JOIN sql_matches
                ON sql_matches_scoretotal.match_id = sql_matches.match_id
                WHERE sql_matches.name LIKE '%".$search."%' OR sql_matches.steamid64 = '".$search."' OR sql_matches_scoretotal.match_id = '".$search."' ORDER BY sql_matches_scoretotal.match_id DESC";
        
    }else {
        $sql = "SELECT * FROM sql_matches_scoretotal ORDER BY match_id DESC LIMIT 5";          
    }

    $result = $conn->query($sql);

    if($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            if($row["team_2"] > 15) {
                $image = 'ct_icon.png';
            }elseif($row["team_2"] == 15 && $row["team_3"] == 15) {
                $image = 'tie_icon.png';
            }elseif($row["team_3"] > 15) {
                $image = 't_icon.png';
            }
            echo '<a class="text-white" href="scoreboard.php?id='.$row['match_id'].'"><div data-bs-hover-animate="pulse" class="match-box" style="background-image:url(&quot;assets/img/maps/'.$row['map'].'.png&quot;);background-position:center;background-size:cover;background-repeat:no-repeat;background-color:#F1F1F1;height:115px;margin-top:25px;"><img class="float-left" src="assets/img/'.$image.'" style="width:95px;margin-top:10px;margin-left:20px;">
            <h1 class="float-right" style="color:rgb(255,255,255);font-size:85px;margin-right:20px;">'.$row['team_2'].':'.$row['team_3'].'</h1>
            <div class="clear"></div>
            </div></a>';
        }
    } else {
        echo '<h3 class="text-center" style="font-size:30px;margin-top:10px;">No Matches Found.</h3>';
    }
    
    $conn->close();
    ?>
    </div>
    <div class="bottom"><a href="https://github.com/WardPearce/Sourcemod-SQLMatches" target="_blank">Created By Ward</a></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.2/js/bootstrap.bundle.min.js"></script>
    <script src="assets/js/bs-animation.js"></script>
</body>

</html>
