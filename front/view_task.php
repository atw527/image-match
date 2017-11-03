<?php
    $db = mysqli_connect('a01-mysql-01', 'root', 'q1w2e3r4', 'image_match');
    $guid = mysql_real_escape_string($_GET['guid'], $db);

    $sql = "SELECT * FROM tasks WHERE guid = '$guid'";

?>
