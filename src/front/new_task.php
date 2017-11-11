<?php
    function getGUID() {
        $charid = strtolower(md5(uniqid(rand(), true)));
        $hyphen = chr(45);// "-"
        $uuid =
             substr($charid, 0, 8).$hyphen
            .substr($charid, 8, 4).$hyphen
            .substr($charid,12, 4).$hyphen
            .substr($charid,16, 4).$hyphen
            .substr($charid,20,12);
        return $uuid;
    }

    if (isset($_POST['submit'])) {
        $db = mysqli_connect(getenv('MYSQL_HOST'), getenv('MYSQL_USER'), getenv('MYSQL_PASS'), getenv('MYSQL_DB'));
        $guid = getGUID();

        // Set a maximum height and width
        $width = 1920;
        $height = 1920;

        list($width_orig, $height_orig) = getimagesize($_FILES['template']['tmp_name']);

        $ratio_orig = $width_orig/$height_orig;

        if ($width/$height > $ratio_orig) {
           $width = $height*$ratio_orig;
        } else {
           $height = $width/$ratio_orig;
        }

        $image_p = imagecreatetruecolor($width, $height);
        $image = imagecreatefromjpeg($_FILES['template']['tmp_name']);
        imagecopyresampled($image_p, $image, 0, 0, 0, 0, $width, $height, $width_orig, $height_orig);
        imagejpeg($image_p, "/usr/local/data/templates/$guid.jpg", 100);

        foreach ($_POST['videos'] as $video_id => $selected) {
            $video_id = mysqli_real_escape_string($db, $video_id);
            $sql = "INSERT INTO tasks (guid, video_id, template) VALUES ('$guid', '$video_id', '$guid.jpg')";
            $db->query($sql);
        }

        header('Location: view_task.php?guid=' . $guid . "&distance=20");

        exit();
    }

    $files = scandir("/usr/local/data/video");
    $videos = array();

    foreach ($files as $file) {
        if (substr($file, -9, 9) == 'info.json') {
            $json = json_decode(file_get_contents("/usr/local/data/video/$file"));

            $video = array();
            $video['id'] = $json->id;
            $video['title'] = $json->title;
            $video['date'] = date('Y-m-d', strtotime($json->upload_date));
            $video['thumbnail'] = $json->thumbnails[0]->url;

            $videos[$json->upload_date] = $video;
        }
    }

    ksort($videos);
    $videos = array_reverse($videos);
?>
<html>
<head>
    <title>New Task</title>

    <style>
        body {
            font-family: Verdana, Geneva, sans-se
        }

        .row-video {
            padding: 10px;
            clear: both;
        }

        .vcheck {
            display: table-cell;
            vertical-align: middle;
            width: 2em;
        }

        .thumbnail {
        }

        .title {
            vertical-align: top;
        }

        .date {
            vertical-align: top;
            color: #333;
        }
        .video-id {
            vertical-align: top;
            color: #333;
        }
    </style>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script>
    $(document).ready(function(){
        $("#selectall").click(function(){
            //alert("just for check");
            if(this.checked){
                $('.vcheck').each(function(){
                    this.checked = true;
                })
            }else{
                $('.vcheck').each(function(){
                    this.checked = false;
                })
            }
        });
    });
    </script>
</head>
<body>
    <form method="post" enctype="multipart/form-data">
        <input type="checkbox" id="selectall" value="1" />

        <label for="template">Image Template:</label>
        <input type="file" name="template" id="template" />
        <?php foreach ($videos as $video): ?>
            <div class="row-video">
                <h3 class="title"><?=$video['title']?></h3>
                <input type="checkbox" class="vcheck" name="videos[<?=$video['id']?>]" id="videos-<?=$video['id']?>" value="1" />
                <label for="videos-<?=$video['id']?>"><img class="thumbnail" src="/data/video/<?=$video['id']?>.jpg" width="100" /></label>
                <span class="date"><?=$video['date']?></span>
                <span class="video-id"><?=$video['id']?></span>
            </div>
        <?php endforeach;?>

        <input type="submit" name="submit" value="Submit" />
    </form>
</body>
</html>
