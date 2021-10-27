<!DOCTYPE html>
<html>
<head>
<!-- https://www.w3schools.com/php/php_ajax_database.asp -->
<style>

table {
  width: 100%;
  border-collapse: collapse;
}

table, td, th {
  border: 1px solid black;
  padding: 5px;
}

th {text-align: left;}
</style>
</head>
<body>

<?php
echo "hello"
/*
$q = intval($_GET['q']);

$hostName = "localhost";
$userName = "root";
$password = "";
$dbName = "mtg";

$conn = mysqli_connect($hostName, $userName, $password,$dbName);

mysqli_select_db($con, $dbName);
$sql="SELECT * FROM mtgnames WHERE id = '".$q."'";
$result = mysqli_query($conn,$sql);


echo "<table>
<tr>
<th>cardName</th>
<th>qty</th>
<th>price</th>
</tr>";
while($row = mysqli_fetch_array($result)) {
  echo "<tr>";
  echo "<td>" . $row['cardName'] . "</td>";
  echo "<td>" . $row['qty'] . "</td>";
  echo "<td>" . $row['price'] . "</td>";
  echo "</tr>";
}
echo "</table>";
mysqli_close($conn);
*/
?>

</body>
</html>
