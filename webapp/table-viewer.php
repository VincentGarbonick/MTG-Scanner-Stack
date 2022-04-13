<html>
<head>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
  <link rel="stylesheet" href="home.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@200&display=swap" rel="stylesheet">
  <link rel="shortcut icon" type="image/jpg" href="origin-symbol.png"/>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant:wght@500&display=swap" rel="stylesheet">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  <script>
    $(document).ready(function()
    {
      var smallImgDir = "./demo-img/demo-img-med/";
      var rowInfo = "";
      var filePath = "";
      $("tr").click(function()
      {
        rowInfo = $(this).find("th#cardNameRow").text();
        filePath = smallImgDir + rowInfo + ".jpg";
        //alert(filePath);

        $("#sidebarImage").attr("src", filePath);
      });
    });

    $(document).ready(function () {
  $('#dtBasicExample').DataTable();
  $('.dataTables_length').addClass('bs-select');  
    });
  </script>

  <title>Table Viewer</title>
</head>
<body>
    <div class="sidebar-left">
        <a href="home.html">
            <img class="sidebar-image" src="origin-symbol.png">
        </a>
        <form action="visual-spoiler.php">
          <button class="btn-hover color-2 center">Visual Spoiler</button>
        </form>
        <form action="call-API.php" method="post">
          <button class="btn-hover color-3 center" id="price-button" name="price-button">Refresh Prices</button>
        </form>
        <form action="call-API.php" method="post">
          <button class="btn-hover color-5 center" id="export-button" name="export-button">Export Cards</button>
        </form>
    </div>
    <div class="sidebar-right text-center">
        <img src="./demo-img/demo-img-med/Flickerwisp.jpg" class="center sidebar-image-spec" style="padding-top: 10px;" id="sidebarImage">
    </div>    
    <div class="text-center" style="font-family: 'Raleway', sans-serif;">
        <!--<input type="text" id="cardSearchBar" onkeyup="searchTable()" placeholder="Search for names..">-->
        <div class="table-wrapper-scroll-y my-custom-scrollbar">
            <!-- TODO: GET FILTER/SEARCH TABLE STUFF, USING EITHER BOOTSTRAP OR SOMETHING ELSE -->
            <table id="dtBasicExample" class="table table-responsive table-bordered table-striped mb-0" style="font-family: 'Raleway', sans-serif">
              <thead>
                <tr>
                  <th class="table-header-text" scope="col">Card Name</th>
                  <th class="table-header-text" scope="col">Quantity</th>
                  <th class="table-header-text" scope="col">Price</th>
                  <th class="table-header-text" scope="col">Foil Price</th>
                </tr>
              </thead>
              <tbody>
                <?php
                    $hostname = "localhost";
                    $username = "root";
                    $pass = "";
                    $dbName = "magic";
                    $tableName = "mtgCards";

                    $conn = mysqli_connect($hostname, $username, $pass, $dbName);

                    $query = "SELECT * FROM $tableName";

                    $result = mysqli_query($conn,$query);
                    
                    $row = mysqli_fetch_array($result);
                    
                    $num_rows = mysqli_num_rows($result);
                    $num_fields = mysqli_num_fields($result);

                    for ($row_num = 0; $row_num < $num_rows; $row_num++) {
                        print "<tr align = 'center' class=\"highlight\">";
                        $values = array_values($row);
                        for ($index = 0; $index < $num_fields; $index++){
                            $value = htmlspecialchars($values[2 * $index + 1]);
                            if($index == 2 || $index == 3)
                            {
                              echo "<th>"."$". number_format($value,2,".",",")."</th>";
                            }
                            else if($index != 0)
                            {
                              echo "<th>".$value."</th>";
                            }
                            else 
                            {
                              // first index will be name...tag with cardNameRow so we can grab with jQuery
                              print "<th id=\"cardNameRow\">" . $value . "</th> ";
                            }
                        }
                        print "</tr>";
                        $row = mysqli_fetch_array($result);
                    } 
                  // TODO: some kind of export to text function
                ?>
              </tbody>
            </table>
        </div>   
    </div>
</body>
</html>
