<?php
    function getTS($filename) {
        list($frame, $ext) = explode('.', $filename);

        $seconds = floor($frame / 10);

        $ts = new stdClass();
        $ts->frame = $seconds;
        $ts->m = intdiv($seconds, 60);
        $ts->s = $seconds % 60;

        return $ts;
    }

    $db = mysqli_connect(getenv('MYSQL_HOST'), getenv('MYSQL_USER'), getenv('MYSQL_PASS'), getenv('MYSQL_DB'));
    $guid = mysqli_real_escape_string($db, $_GET['guid']);
    $distance = isset($_GET['distance']) ? (int)$_GET['distance'] : 26;

    $sql = "SELECT * FROM tasks WHERE guid = '$guid'";
    $query = $db->query($sql);

    $tasks = array();
    $task_ids = array();
    while ($row = $query->fetch_object()) {
        $tasks[$row->task_id] = $row;
        $tasks[$row->task_id]->matches = array();
        $task_ids[] = $row->task_id;
    }

    sort($task_ids);

    $ids = "'" . implode("', '", $task_ids) . "'";

    $sql = "SELECT * FROM matches WHERE task_id IN ($ids) && distance < $distance ORDER BY video_id, filename";
    $query = $db->query($sql);
    if (!$query) echo $sql;
    while ($row = $query->fetch_object()) {
        $match = $row;
        $ts = getTS($row->filename);
        $match->m = $ts->m;
        $match->s = $ts->s;
        $tasks[$row->task_id]->matches[] = $match;
    }
?>
<html>
<head>
    <title>View Task</title>

    <style>
        body {
            font-family: Verdana, Geneva, sans-se
        }

        .meta {
            float: left;
            padding: 5px;
            vertical-align: top;
        }

        .task-image {
            float: left;
        }
    </style>
</head>
<body>

<a href="/new_task.php">New Task</a> | <a href="?guid=<?=$guid?>&distance=<?=$distance-1?>">Decrease Distance</a> | <a href="?guid=<?=$guid?>&distance=<?=$distance+1?>">Increase Distance</a>

<hr />

<img src="/data/templates/<?=$guid?>.jpg" width="400"/>

<?php foreach ($tasks as $task): ?>
    <hr id="<?=$task->video_id?>" style="clear: both; " />

    <a name="<?=$task->video_id?>" href="https://youtu.be/<?=$task->video_id?>" class="task-image" target="_blank"><img src="/data/video/<?=$task->video_id?>.jpg" width="300" /></a>

    <p class="meta">
        <span class="label">Started:</span> <span class="value"><?=$task->started?></span><br />
        <span class="label">Completed:</span> <span class="value"><?=$task->completed?></span><br />
        <span class="label">Worker Host:</span> <span class="value"><?=$task->task_id?> <?=$task->host?> <?=$task->container?></span><br />
        <span class="label">Video:</span> <span class="value"><?=$task->video_id?></span><br />
        <span class="label">Exceptions:</span> <span class="value"><?=$task->exceptions?></span><br />
    </p>

    <div style="clear: both; padding: 5px; "></div>

    <?php foreach ($task->matches as $match): ?>
        <a href="https://youtu.be/<?=$match->video_id?>?t=<?=$match->m?>m<?=$match->s?>s" target="_video">
            <img src="/data/frames/<?=$match->video_id?>/<?=$match->filename?>" width="200" class="dist-<?=$match->distance?>" title="Distance: <?=$match->distance?>" />
        </a>
    <?php endforeach; ?>
<?php endforeach; ?>

</body>
</html>
