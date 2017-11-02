<?php
    $files = scandir("/usr/local/data/video");
    $videos = array();

    foreach ($files as $file) {
        if (substr($file, -9, 9) == 'info.json') {
            $json = json_decode(file_get_contents("/usr/local/data/video/$file"));

            var_dump($json);
        }
    }
?>
<html>
<head>
    <title>New Task</title>
</head>
<body>
    <form method="post">
        <input type="text" name="" id="" value="" />
    </form>
</body>
</html>
