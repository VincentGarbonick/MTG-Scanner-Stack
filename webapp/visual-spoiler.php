 <html>
<head>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
  <link rel="stylesheet" href="home.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@200&display=swap" rel="stylesheet">
  <link rel="shortcut icon" type="image/jpg" href="origin-symbol.png"/>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant:wght@500&display=swap" rel="stylesheet">
  <title>Visual Spoiler</title>
</head>
<body>
    <div class="sidebar-left">
        <a href="home.html">
            <img class="sidebar-image" src="origin-symbol.png">
        </a>
        <form action="table-viewer.php">
            <button class="btn-hover color-1 center">List View</button>
        </form>
    </div>
    <div class="container-fluid">
        <?php
        $hostname = "localhost";
        $username = "root";
        $pass = "";
        $dbName = "magic";
        $tableName = "mtgCards";

        $conn = mysqli_connect($hostname, $username, $pass, $dbName);

        $query = "SELECT cardName FROM $tableName";

        // get array of all names 
        $result = mysqli_query($conn,$query);
        
        // loop through all names 
        $smallImgDir = "./demo-img/demo-img-small/";
        // $smallImgDir = "./img/"; // for the "shipped mode" of the project
        $imgDir = scandir($smallImgDir);
        $i = 0;
        while($name = mysqli_fetch_array($result))
        {
            // echo $name["cardName"];
            // echo "<br>";
            
            // search through image repo 
            // TODO: better search algorithm 
            
            while($i < sizeof($imgDir))
            {
                if(substr($imgDir[$i],0,-4) == $name["cardName"])
                {
                    // build name 
                    $imgSourceName = "\"" . $smallImgDir . $imgDir[$i] . "\"";
                    echo "<img src=$imgSourceName>";
                    break;
                }
                $i++;
            }
            $i = 0;
            
        }
        //TODO: infinite scroll 


        ?>
        <!-- <img class="center" src="./demo-img/demo-img-small/Trained Caracal.jpg" style="height: 150px; width:auto;"> -->
    </div>
</body>
</html>
